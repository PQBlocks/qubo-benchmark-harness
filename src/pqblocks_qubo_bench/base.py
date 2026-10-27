"""
Baseline wrapper abstract base class for benchmark harness.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import dimod
import math


class BaselineWrapper(ABC):
    """
    Abstract base class for all solver wrappers in the benchmark harness.
    """

    def __init__(self, bqm: dimod.BinaryQuadraticModel, seed: int):
        """
        Initialize with problem and deterministic seed.
        
        Args:
            bqm: The binary quadratic model to solve
            seed: Deterministic seed for reproducibility
        """
        # Validate BQM for NaN/Inf values
        for var, coeff in bqm.linear.items():
            if math.isnan(coeff) or math.isinf(coeff):
                raise ValueError(f"Invalid coefficient {coeff} for linear variable {var}")
                
        for (u, v), coeff in bqm.quadratic.items():
            if math.isnan(coeff) or math.isinf(coeff):
                raise ValueError(f"Invalid coefficient {coeff} for quadratic interaction ({u}, {v})")
        
        self.bqm = bqm
        self.seed = seed

    @abstractmethod
    def sample(self, **parameters) -> dimod.SampleSet:
        """
        Execute solver and return SampleSet with energies, samples, timing info.
        
        Args:
            **parameters: Algorithm-specific parameters
            
        Returns:
            dimod.SampleSet with solutions and timing information
        """
        pass

    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """
        Return hyperparameter dictionary.
        
        Returns:
            Dictionary of default parameters for the solver
        """
        pass