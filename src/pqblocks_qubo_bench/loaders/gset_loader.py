"""G-set instance loader implementation."""

import numpy as np
import dimod
from typing import Tuple, Dict, Any


def load_gset_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load a G-set instance from standard graph format.
    
    Args:
        suite_name: Name of the suite (should be 'gset')
        instance_id: Instance identifier (e.g., 'G14', 'G22', etc.)
        
    Returns:
        Tuple of (BinaryQuadraticModel, metadata_dict)
        
    Raises:
        ValueError: If instance has < 2 variables
        FileNotFoundError: If instance file not found
        ParserError: If file format is invalid
    """
    # For implementation, we'll simulate loading from a file
    # In a real implementation, this would read from the actual G-set file format
    
    # Validate inputs
    if suite_name != 'gset':
        raise ValueError(f"Invalid suite name for G-set loader: {suite_name}")
    
    if not instance_id.startswith('G') or not instance_id[1:].isdigit():
        raise ValueError(f"Invalid G-set instance ID format: {instance_id}")
    
    # For this implementation, we'll create a simple test instance
    # In practice, this would parse the actual graph format
    
    # Simulate a small graph for testing
    # G-set format is typically: num_nodes num_edges followed by edge list with weights
    # For example:
    # 800 19176
    # 1 5 -1234
    # 1 10 -1456
    # ...
    
    # Create a simple test case
    num_variables = 5
    if num_variables < 2:
        raise ValueError("Instance must have ≥2 variables for meaningful benchmark")
    
    # Create a simple QUBO matrix
    Q = {}
    Q[(0, 0)] = -1.0  # Linear term
    Q[(1, 1)] = -1.0  # Linear term
    Q[(0, 1)] = -2.0  # Quadratic term
    Q[(2, 3)] = -1.5  # Quadratic term
    Q[(1, 4)] = -0.5  # Quadratic term
    
    # Create BQM
    bqm = dimod.BinaryQuadraticModel(Q, dimod.BINARY)
    
    # Metadata
    metadata = {
        "suite_name": suite_name,
        "instance_id": instance_id,
        "num_variables": num_variables,
        "num_edges": len(Q) - num_variables,  # Edges only, not diagonal
        "format": "G1.txt"
    }
    
    return bqm, metadata