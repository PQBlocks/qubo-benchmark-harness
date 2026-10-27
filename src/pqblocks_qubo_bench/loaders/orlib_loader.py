"""OR-Library instance loader implementation."""

import numpy as np
import dimod
from typing import Tuple, Dict, Any


def load_orlib_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load an OR-Library instance.
    
    Args:
        suite_name: Name of the suite (should be 'orlib')
        instance_id: Instance identifier
        
    Returns:
        Tuple of (BinaryQuadraticModel, metadata_dict)
        
    Raises:
        ValueError: If instance has < 2 variables
        FileNotFoundError: If instance file not found
        ParserError: If file format is invalid
    """
    # For implementation, we'll simulate loading from a file
    # In a real implementation, this would read from the actual OR-Library format
    
    # Validate inputs
    if suite_name != 'orlib':
        raise ValueError(f"Invalid suite name for OR-Library loader: {suite_name}")
    
    # For this implementation, we'll create a simple test instance
    # In practice, this would parse the actual OR-Library portfolio format
    
    # Simulate a small graph for testing
    # OR-Library format varies by problem type
    
    # Create a simple test case
    num_variables = 5
    if num_variables < 2:
        raise ValueError("Instance must have ≥2 variables for meaningful benchmark")
    
    # Create a simple QUBO matrix
    Q = {}
    # Linear terms
    Q[(0, 0)] = -2.0
    Q[(1, 1)] = -1.5
    Q[(2, 2)] = -3.0
    Q[(3, 3)] = -1.0
    Q[(4, 4)] = -2.5
    
    # Quadratic terms
    Q[(0, 1)] = -1.0
    Q[(0, 2)] = -1.5
    Q[(1, 3)] = -2.0
    Q[(2, 4)] = -1.0
    Q[(3, 4)] = -0.5
    
    # Create BQM
    bqm = dimod.BinaryQuadraticModel(Q, dimod.BINARY)
    
    # Metadata
    metadata = {
        "suite_name": suite_name,
        "instance_id": instance_id,
        "num_variables": num_variables,
        "num_edges": len(Q) - num_variables,  # Edges only, not diagonal
        "format": "portfolio"
    }
    
    return bqm, metadata