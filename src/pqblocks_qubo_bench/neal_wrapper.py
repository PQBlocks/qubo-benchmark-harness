"""
D-Wave Neal (Simulated Annealing) baseline wrapper for benchmark harness.
"""

import dimod
import neal
import time
import numpy as np
from typing import Dict, Any
from .base import BaselineWrapper


class NealWrapper(BaselineWrapper):
    """
    Wrapper for D-Wave Neal's SimulatedAnnealingSampler.
    """

    def __init__(self, bqm: dimod.BinaryQuadraticModel, seed: int):
        """
        Initialize with problem and deterministic seed.
        
        Args:
            bqm: The binary quadratic model to solve
            seed: Deterministic seed for reproducibility
        """
        super().__init__(bqm, seed)
        self.sampler = neal.SimulatedAnnealingSampler()

    def sample(self, **parameters) -> dimod.SampleSet:
        """
        Execute solver and return SampleSet with energies, samples, timing info.
        
        Args:
            **parameters: Algorithm-specific parameters
                - num_reads: Number of independent samples (default: 100)
                - num_sweeps: Number of sweeps per anneal (default: 1000)
                - beta_range: Tuple of (beta_start, beta_end) (default: (0.1, 5.0))
                
        Returns:
            dimod.SampleSet with solutions and timing information
        """
        # Set default parameters if not provided
        num_reads = parameters.get('num_reads', 100)
        num_sweeps = parameters.get('num_sweeps', 1000)
        beta_range = parameters.get('beta_range', (0.1, 5.0))
        
        # Execute solver with timing
        start_time = time.monotonic()
        response = self.sampler.sample(
            self.bqm,
            num_reads=num_reads,
            num_sweeps=num_sweeps,
            beta_range=beta_range,
            seed=self.seed
        )
        end_time = time.monotonic()
        
        # Add timing information to the response
        timing_info = {
            'execution_time': end_time - start_time,
            'num_reads': num_reads,
            'num_sweeps': num_sweeps,
            'beta_range': beta_range
        }
        
        # Attach timing info to the response
        response.info.update(timing_info)
        
        return response

    def get_default_params(self) -> Dict[str, Any]:
        """
        Return hyperparameter dictionary.
        
        Returns:
            Dictionary of default parameters for the solver
        """
        return {
            'num_reads': 100,
            'num_sweeps': 1000,
            'beta_range': (0.1, 5.0)
        }