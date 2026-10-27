"""Instance Suite Loaders Implementation

This module implements loaders for various instance suite formats as specified in the benchmark specification.

Each loader function takes a suite name and instance ID, and returns a dimod.BinaryQuadraticModel instance and a metadata dictionary.
"""

from .loader import load_instance

__all__ = ["load_instance"]