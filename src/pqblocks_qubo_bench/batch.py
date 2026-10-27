"""Batch benchmark execution module for the QUBO benchmarking system."""

import csv
import logging
import os
import sys
import traceback
from typing import List, Tuple, Dict, Any
import time
import itertools

from .pipeline import BenchmarkPipeline
from pqblocks_qubo_bench.loaders import load_instance
from .base import BaselineWrapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_batch_config(csv_path: str) -> List[Tuple[str, str, str]]:
    """
    Load batch configuration from a CSV file.
    
    Args:
        csv_path: Path to the CSV file containing (solver, suite, instance) tuples
        
    Returns:
        List of (solver_id, suite_name, instance_id) tuples
    """
    config = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        try:
            # Skip header if present
            header = next(reader)
            if header[0] != 'solver':
                config.append(tuple(header))  # No header, add first row
        except StopIteration:
            # Empty file, return empty config
            return config
        
        for row in reader:
            if len(row) >= 3:
                config.append((row[0], row[1], row[2]))
    
    return config


def get_solver_by_id(solver_id: str, bqm, seed: int) -> BaselineWrapper:
    """
    Get a solver instance by its ID.
    
    Args:
        solver_id: Identifier of the solver
        bqm: Binary quadratic model for the solver
        seed: Random seed for the solver
        
    Returns:
        Solver instance
        
    Raises:
        ValueError: If solver ID is unknown
    """
    # Import solver wrappers here to avoid circular imports
    if solver_id == 'mock-solver':
        from .test_data.mock_solver import MockSolver
        return MockSolver(bqm, seed=seed)
    elif solver_id == 'neal-solver':
        from .neal_wrapper import NealWrapper
        return NealWrapper(bqm, seed=seed)
    elif solver_id == 'openjij-solver':
        from .openjij_wrapper import OpenJijWrapper
        return OpenJijWrapper(bqm, seed=seed)
    elif solver_id == 'mqlib-solver':
        from .mqlib_wrapper import MQLibWrapper
        return MQLibWrapper(bqm, seed=seed)
    elif solver_id == 'cpsat-solver':
        from .cpsat_wrapper import CPSATWrapper
        return CPSATWrapper(bqm, seed=seed)
    else:
        raise ValueError(f"Unknown solver ID: {solver_id}")


def execute_batch(
    config: List[Tuple[str, str, str]], 
    pipeline: BenchmarkPipeline,
    output_dir: str
) -> Dict[str, Any]:
    """
    Execute a batch of benchmarks.
    
    Args:
        config: List of (solver_id, suite_name, instance_id) tuples
        pipeline: Benchmark pipeline instance
        output_dir: Directory to save benchmark cards
        
    Returns:
        Summary report dictionary
    """
    results = []
    failures = []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Seed generator for distinct solver seeds
    seed_counter = itertools.count(pipeline.benchmark_config.get("seed", 42))
    
    for i, (solver_id, suite_name, instance_id) in enumerate(config):
        logger.info(f"Executing benchmark {i+1}/{len(config)}: {solver_id} on {suite_name}/{instance_id}")
        
        try:
            # Load instance
            bqm, instance_metadata = load_instance(suite_name, instance_id)
            
            # Get solver with a distinct seed
            solver_seed = next(seed_counter)
            solver = get_solver_by_id(solver_id, bqm, solver_seed)
            
            # Generate output path
            output_path = os.path.join(
                output_dir, 
                f"{suite_name}_{instance_id}_{solver_id}.json"
            )
            
            # Run benchmark
            card = pipeline.run(
                solver=solver,
                suite_name=suite_name,
                instance_id=instance_id,
                output_path=output_path
            )
            
            # Record success
            results.append({
                "solver_id": solver_id,
                "suite_name": suite_name,
                "instance_id": instance_id,
                "status": "success",
                "card_path": output_path,
                "success_probability": card["metrics"]["success_probability"],
                "tts": card["metrics"]["time_to_solution_99_seconds"]
            })
            
            logger.info(f"  Success: p={card['metrics']['success_probability']:.4f}")
            
        except Exception as e:
            logger.error(f"  Failed: {e}")
            failures.append({
                "solver_id": solver_id,
                "suite_name": suite_name,
                "instance_id": instance_id,
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
            # Continue with next benchmark
            continue
    
    # Generate summary report
    total_benchmarks = len(config)
    successful_benchmarks = len(results)
    failed_benchmarks = len(failures)
    
    summary = {
        "timestamp": time.time(),
        "total_benchmarks": total_benchmarks,
        "successful_benchmarks": successful_benchmarks,
        "failed_benchmarks": failed_benchmarks,
        "success_rate": successful_benchmarks / total_benchmarks if total_benchmarks > 0 else 0,
        "results": results,
        "failures": failures
    }
    
    # Save summary report
    summary_path = os.path.join(output_dir, "batch_summary.json")
    import json
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Batch execution completed. Summary saved to {summary_path}")
    logger.info(f"Success rate: {summary['success_rate']:.2%} ({successful_benchmarks}/{total_benchmarks})")
    
    return summary