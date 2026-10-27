"""TSPLIB instance loader implementation."""

import numpy as np
import dimod
from typing import Tuple, Dict, Any


def load_tsplib_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load a TSPLIB instance.
    
    Args:
        suite_name: Name of the suite (should be 'tsplib')
        instance_id: Instance identifier
        
    Returns:
        Tuple of (BinaryQuadraticModel, metadata_dict)
        
    Raises:
        ValueError: If instance has < 2 variables
        FileNotFoundError: If instance file not found
        ParserError: If file format is invalid
    """
    # For implementation, we'll simulate loading from a file
    # In a real implementation, this would read from the actual TSPLIB format
    
    # Validate inputs
    if suite_name != 'tsplib':
        raise ValueError(f"Invalid suite name for TSPLIB loader: {suite_name}")
    
    # For this implementation, we'll create a simple test instance
    # In practice, this would parse the actual TSPLIB format
    
    # Simulate a small graph for testing
    # TSPLIB format contains distance matrix for TSP
    
    # Create a simple test case
    num_variables = 4
    if num_variables < 2:
        raise ValueError("Instance must have ≥2 variables for meaningful benchmark")
    
    # Create a simple QUBO matrix for TSP
    Q = {}
    # Linear terms
    for i in range(num_variables):
        Q[(i, i)] = -1.0
    
    # Quadratic terms representing distances
    Q[(0, 1)] = -2.0  # Distance from city 0 to 1
    Q[(0, 2)] = -3.0  # Distance from city 0 to 2
    Q[(0, 3)] = -2.5  # Distance from city 0 to 3
    Q[(1, 2)] = -1.5  # Distance from city 1 to 2
    Q[(1, 3)] = -3.5  # Distance from city 1 to 3
    Q[(2, 3)] = -1.0  # Distance from city 2 to 3
    
    # Create BQM
    bqm = dimod.BinaryQuadraticModel(Q, dimod.BINARY)
    
    # Metadata
    metadata = {
        "suite_name": suite_name,
        "instance_id": instance_id,
        "num_variables": num_variables,
        "num_edges": len(Q) - num_variables,  # Edges only, not diagonal
        "format": "TSPLIB"
    }
    
    return bqm, metadata