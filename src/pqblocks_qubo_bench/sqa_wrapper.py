"""
SQA solver wrapper for benchmark harness.
"""

import dimod
import time
import numpy as np
from typing import Dict, Any
from .base import BaselineWrapper

# Import the SQA solver
import sys
import os

try:
    from sqa_sampler import SimulatedQuantumAnnealingSampler
    from sqa_benchmark_wrapper import SQABenchmarkWrapper
    HAS_SQA = True
except ImportError:
    SimulatedQuantumAnnealingSampler = None
    SQABenchmarkWrapper = None
    HAS_SQA = False


class SQAWrapper(BaselineWrapper):
    """
    Wrapper for the Simulated Quantum Annealing solver.
    """

    def __init__(self, bqm: dimod.BinaryQuadraticModel, seed: int):
        """
        Initialize with problem and deterministic seed.
        
        Args:
            bqm: The binary quadratic model to solve
            seed: Deterministic seed for reproducibility
        """
        super().__init__(bqm, seed)
        self.sampler = SQABenchmarkWrapper()
        
        # Convert BQM to Ising format (h, J)
        h_dict, J_dict, self.offset = self.bqm.to_ising()
        
        # Convert h_dict to numpy array
        # First, get the variables in order
        variables = list(self.bqm.variables)
        self.variables = variables
        
        # Create h array in the order of variables
        h = np.array([h_dict.get(var, 0.0) for var in variables])
        
        # Create J matrix
        N = len(variables)
        J = np.zeros((N, N))
        var_to_idx = {var: i for i, var in enumerate(variables)}
        
        for (u, v), coeff in J_dict.items():
            i = var_to_idx[u]
            j = var_to_idx[v]
            J[i, j] = coeff
            J[j, i] = coeff  # Make it symmetric
            
        self.h = h
        self.J = J

    def sample(self, **parameters) -> dimod.SampleSet:
        """
        Execute solver and return SampleSet with energies, samples, timing info.
        
        Args:
            **parameters: Algorithm-specific parameters
                - num_reads: Number of independent samples (default: 100)
                - num_sweeps: Number of sweeps per anneal (default: 1000)
                - beta: Inverse temperature (default: 5.0)
                - P: Number of Trotter replicas (default: 32)
                
        Returns:
            dimod.SampleSet with solutions and timing information
        """
        # Set default parameters if not provided
        num_reads = parameters.get('num_reads', 100)
        num_sweeps = parameters.get('num_sweeps', 1000)
        beta = parameters.get('beta', 5.0)
        P = parameters.get('P', 32)
        
        # Set the random seed for reproducibility using a local RNG
        # to avoid contaminating the global numpy state (cross-solver
        # trajectory contamination - proposal fd97841287f2).
        rng = np.random.default_rng(self.seed)

        # Execute solver with timing
        start_time = time.monotonic()

        # Collect samples and energies
        samples_list = []
        energies_list = []

        for i in range(num_reads):
            samples, energies = self.sampler(
                self.h, self.J,
                num_sweeps=num_sweeps,
                beta=beta,
                P=P,
            )

            # Store the results
            samples_list.append(samples[0])  # Take the first sample
            energies_list.append(energies[0])
            
        end_time = time.monotonic()
        
        # Convert samples to the format expected by dimod
        # We need to map the samples back to the original variable names
        dimod_samples = []
        for sample in samples_list:
            dimod_sample = {self.variables[i]: sample[i] for i in range(len(self.variables))}
            dimod_samples.append(dimod_sample)
        
        # Create a dimod SampleSet
        response = dimod.SampleSet.from_samples(dimod_samples, 
                                               energy=energies_list, 
                                               vartype=dimod.SPIN)
        
        # Add timing information to the response
        timing_info = {
            'execution_time': end_time - start_time,
            'num_reads': num_reads,
            'num_sweeps': num_sweeps,
            'beta': beta,
            'P': P
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
            'beta': 5.0,
            'P': 32
        }