"""Mock solver for testing the benchmark pipeline."""

import dimod
import time
from typing import Dict, Any
from ..base import BaselineWrapper


class MockSolver(BaselineWrapper):
    """
    A mock solver that quickly returns a known solution for testing.
    """
    
    def __init__(self, bqm: dimod.BinaryQuadraticModel, seed: int = 42):
        """
        Initialize with problem and deterministic seed.
        
        Args:
            bqm: The binary quadratic model to solve
            seed: Deterministic seed for reproducibility
        """
        super().__init__(bqm, seed)
        # For this mock solver, we know the optimal solution for our test instance
        # For the mock BQM: -x0 -x1 + 2*x0*x1, the optimal solution is x0=1, x1=1 with energy=-1.0
        self.optimal_solution = {0: 1, 1: 1}
        self.optimal_energy = -1.0
        
    def sample(self, **parameters) -> dimod.SampleSet:
        """
        Execute solver and return SampleSet with energies, samples, timing info.
        
        Args:
            **parameters: Algorithm-specific parameters
            
        Returns:
            dimod.SampleSet with solutions and timing information
        """
        # Simulate some computation time
        time.sleep(0.001)  # 1ms delay to simulate computation
        
        # For this mock, we always return the optimal solution
        samples = [self.optimal_solution]
        energies = [self.optimal_energy]
        
        # Create SampleSet
        sample_set = dimod.SampleSet.from_samples(samples, energy=energies, vartype=self.bqm.vartype)
        
        # Add timing information
        sample_set.info['timing'] = {'total_real_time': 0.001}
        
        return sample_set
    
    def get_default_params(self) -> Dict[str, Any]:
        """
        Return hyperparameter dictionary.
        
        Returns:
            Dictionary of default parameters for the solver
        """
        return {
            'num_reads': 100,
            'timeout': 1.0  # 1 second timeout
        }