"""
Benchmark wrapper for SQA solver to integrate with benchmark harness.
"""

import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqa_sampler import SimulatedQuantumAnnealingSampler

class SQABenchmarkWrapper:
    """
    A wrapper for the SQA solver that conforms to the benchmark harness interface.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the SQA benchmark wrapper.
        
        Parameters:
        - **kwargs: Additional parameters to pass to the SQA sampler.
        """
        self.sampler = SimulatedQuantumAnnealingSampler()
        self.kwargs = kwargs
        
    def __call__(self, h, J, **kwargs):
        """
        Solve the Ising problem using SQA.
        
        Parameters:
        - h: array-like, shape (N,) - Local field values.
        - J: array-like, shape (N, N) - Coupling matrix.
        - **kwargs: Additional parameters to pass to the sampler.
        
        Returns:
        - samples: array, shape (num_samples, N) - Sampled spin states.
        - energies: array, shape (num_samples,) - Energies of sampled states.
        """
        # Merge default kwargs with provided kwargs
        params = self.kwargs.copy()
        params.update(kwargs)
        
        # Call the SQA sampler
        return self.sampler.sample_ising(h, J, **params)
        
    def name(self):
        """
        Return the name of the solver.
        
        Returns:
        - str: Name of the solver.
        """
        return "SQA"
        
    def short_name(self):
        """
        Return the short name of the solver.
        
        Returns:
        - str: Short name of the solver.
        """
        return "sqa"
        
    def description(self):
        """
        Return a description of the solver.
        
        Returns:
        - str: Description of the solver.
        """
        return "Simulated Quantum Annealing solver"
        
    def parameters(self):
        """
        Return the parameters of the solver.
        
        Returns:
        - dict: Parameters of the solver.
        """
        return self.kwargs

# Example usage:
# wrapper = SQABenchmarkWrapper(num_sweeps=1000, beta=5.0, P=32)
# samples, energies = wrapper(h, J)