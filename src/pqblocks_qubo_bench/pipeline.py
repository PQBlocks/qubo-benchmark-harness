"""Benchmark Pipeline Orchestrator for the QUBO benchmarking system."""

import logging
import time
import json
import os
import subprocess
import platform
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
import dimod

from .base import BaselineWrapper
from .card import generate_benchmark_card, validate_benchmark_card
from .metrics import calculate_tts, calculate_confidence_interval, calculate_gap

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_instance_name(suite_name: str, instance_id: str) -> str:
    """
    Get the full instance name for logging purposes.
    
    Args:
        suite_name: Name of the instance suite
        instance_id: Identifier of the instance within the suite
        
    Returns:
        Full instance name string
    """
    return f"{suite_name}/{instance_id}"


def load_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load an instance using the pqblocks_qubo_bench.loaders module."""
    if suite_name == "MockSuite":
        from .test_data.mock_instances import MOCK_BQM, MOCK_INSTANCE_METADATA
        return MOCK_BQM, MOCK_INSTANCE_METADATA
    try:
        from pqblocks_qubo_bench.loaders.loader import load_instance as _li
        return _li(suite_name, instance_id)
    except Exception:
        # Fallback to minimal valid BQM
        return dimod.BinaryQuadraticModel.empty(dimod.SPIN), {"num_variables": 0}


def get_reference_energy(suite_name: str, instance_id: str) -> Optional[float]:
    """Get reference energy for an instance."""
    if suite_name == "MockSuite":
        from .test_data.mock_instances import MOCK_REFERENCE_ENERGY
        return MOCK_REFERENCE_ENERGY
    try:
        from pqblocks_qubo_bench.loaders.loader import get_reference_energy as _gre
        return _gre(suite_name, instance_id)
    except Exception:
        return None


def get_cpu_model():
    """Return a real CPU model string using lscpu."""
    try:
        result = subprocess.run(
            ["lscpu"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if line.startswith("Model name:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    m = platform.machine()
    p = platform.processor()
    if p:
        return p
    if m:
        return m
    return "unknown"


class BenchmarkPipeline:
    """
    Benchmark Pipeline Orchestrator that ties together all components of the 
    benchmark harness system.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the benchmark pipeline.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.benchmark_config = config.get("benchmark", {})
        self.loader_config = config.get("loader", {})
        self.metrics_config = config.get("metrics", {})
        self.output_config = config.get("output", {})
        
        # Set up random number generator with seed for reproducibility
        self.rng = np.random.default_rng(self.benchmark_config.get("seed", 42))

    def run(
        self, 
        solver: BaselineWrapper, 
        suite_name: str, 
        instance_id: str,
        output_path: Optional[str] = None,
        reference_energy: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Run the full benchmark pipeline for a solver on a specific instance.
        
        Args:
            solver: The solver to benchmark
            suite_name: Name of the instance suite
            instance_id: Identifier of the instance within the suite
            output_path: Path to save the benchmark card (optional)
            reference_energy: Reference energy for the instance (optional)
            
        Returns:
            Benchmark card dictionary
        """
        logger.info(f"Starting benchmark pipeline for {suite_name}/{instance_id}")
        
        # Get the real BQM from the solver (the solver was constructed with the real problem)
        actual_bqm = getattr(solver, "bqm", None)
        if actual_bqm is None:
            raise ValueError("Solver does not have a 'bqm' attribute")
        
        bqm = actual_bqm
        # Create instance metadata from the real BQM and the provided suite/instance IDs
        instance_metadata = {
            "suite_name": suite_name,
            "instance_id": instance_id,
            "num_variables": len(bqm.variables),
            "num_edges": len(bqm.quadratic),
        }
        
        # Get solver metadata
        solver_metadata = {
            "solver_id": solver.__class__.__name__,
            "solver_name": solver.__class__.__name__,
            "hardware": {
                "cpu": get_cpu_model(),
                "gpu": None,
                "threads_allocated": os.cpu_count() or 1
            }
        }
        
        # Get solver parameters
        params = solver.get_default_params()
        logger.info(f"Using solver parameters: {params}")
        
        # Run solver multiple times to collect statistics
        runs = []
        successful_runs = 0
        best_energy = float('inf')
        total_start_time = time.monotonic()
        
        min_runs = self.benchmark_config.get("min_runs", 100)
        max_runs = self.benchmark_config.get("max_runs", 1000)
        timeout_seconds = self.benchmark_config.get("timeout_seconds", 3600)
        
        for i in range(max_runs):
            # Check if we've exceeded the timeout
            if time.monotonic() - total_start_time > timeout_seconds:
                logger.warning(f"Timeout exceeded after {i} runs")
                break
                
            try:
                # Run the solver
                run_start_time = time.monotonic()
                sample_set = solver.sample(**params)
                run_end_time = time.monotonic()
                
                # Calculate runtime
                runtime = run_end_time - run_start_time
                
                # Get the best energy from this run
                # sample_set.data(fields=['energy']) returns an iterator of Sample namedtuples
                run_best_energy = float('inf')
                for sample in sample_set.data(fields=['energy']):
                    if sample.energy < run_best_energy:
                        run_best_energy = sample.energy
                
                # Update best energy found
                if run_best_energy < best_energy:
                    best_energy = run_best_energy
                
                # Check if this run was successful (found target energy)
                success = run_best_energy <= reference_energy if reference_energy is not None else False
                
                if success:
                    successful_runs += 1
                
                # Store run data
                runs.append((runtime, success))
                
                # If we've reached the minimum number of runs and have some successes,
                # we might be able to estimate TTS
                if i >= min_runs - 1 and successful_runs > 0:
                    # For now, we continue to collect all runs up to max_runs
                    # In a more sophisticated implementation, we might stop early based on
                    # confidence in the TTS estimate
                    pass
                    
            except Exception as e:
                logger.error(f"Solver failed on run {i+1}: {e}")
                # Record this as a failed run with maximum time
                runs.append((timeout_seconds, False))
                
                # Continue with the next run rather than aborting
                continue
        
        total_end_time = time.monotonic()
        total_elapsed_time = total_end_time - total_start_time
        
        logger.info(f"Completed {len(runs)} runs in {total_elapsed_time:.2f} seconds")
        logger.info(f"Successful runs: {successful_runs}/{len(runs)}")
        
        # Calculate metrics
        execution_stats = {
            "num_independent_runs": len(runs),
            "average_single_run_time_seconds": np.mean([runtime for runtime, _ in runs]),
            "total_elapsed_time_seconds": total_elapsed_time
        }
        
        success_probability = successful_runs / len(runs) if runs else 0.0
        
        # Calculate TTS
        tts_point_estimate = calculate_tts(runs, target_prob=self.benchmark_config.get("success_threshold", 0.99))
        
        # Calculate confidence interval
        if len(runs) >= 100:  # Only calculate CI if we have enough runs
            ci_lower, ci_upper = calculate_confidence_interval(
                runs,
                target_prob=self.benchmark_config.get("success_threshold", 0.99),
                bootstrap_iterations=self.benchmark_config.get("bootstrap_iterations", 1000),
                seed=self.benchmark_config.get("seed", 42)
            )
        else:
            ci_lower, ci_upper = None, None
        
        # Calculate reference gap
        reference_gap = calculate_gap(best_energy, reference_energy)
        
        # Prepare metrics dictionary
        metrics = {
            "target_energy": reference_energy,
            "success_probability": success_probability,
            "time_to_solution_99_seconds": tts_point_estimate,
            "tts_95_confidence_interval": [ci_lower, ci_upper] if ci_lower is not None else [None, None],
            "best_energy_found": best_energy,
            "reference_gap": reference_gap
        }
        
        # Generate benchmark card
        card = generate_benchmark_card(
            solver_metadata=solver_metadata,
            instance_metadata=instance_metadata,
            execution_stats=execution_stats,
            metrics=metrics
        )
        
        # Validate the benchmark card
        try:
            validate_benchmark_card(card)
            logger.info("Benchmark card validated successfully")
        except Exception as e:
            logger.error(f"Benchmark card validation failed: {e}")
            raise
        
        # Save the benchmark card if output path is provided
        if output_path:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save card to file
            with open(output_path, 'w') as f:
                json.dump(card, f, indent=2 if self.output_config.get("pretty_print", True) else None)
            logger.info(f"Benchmark card saved to {output_path}")
        
        return card