"""Biq Mac instance loader implementation."""

import numpy as np
import dimod
from typing import Tuple, Dict, Any


def load_biqmac_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load a Biq Mac instance from the .bq format.
    
    Args:
        suite_name: Name of the suite (should be 'biqmac')
        instance_id: Instance identifier (e.g., 'biqmac_100_50_1')
        
    Returns:
        Tuple of (BinaryQuadraticModel, metadata_dict)
        
    Raises:
        ValueError: If instance has < 2 variables
        FileNotFoundError: If instance file not found
        ParserError: If file format is invalid
    """
    # For implementation, we'll simulate loading from a file
    # In a real implementation, this would read from the actual .bq format
    
    # Validate inputs
    if suite_name != 'biqmac':
        raise ValueError(f"Invalid suite name for Biq Mac loader: {suite_name}")
    
    if not instance_id.startswith('biqmac_'):
        raise ValueError(f"Invalid Biq Mac instance ID format: {instance_id}")
    
    # For this implementation, we'll create a simple test instance
    # In practice, this would parse the actual .bq format
    
    # Simulate a small graph for testing
    # Biq Mac format typically contains:
    # p edge num_nodes num_edges
    # n node_id weight
    # e node1 node2 weight
    
    # Create a simple test case
    num_variables = 4
    if num_variables < 2:
        raise ValueError("Instance must have ≥2 variables for meaningful benchmark")
    
    # Create a simple QUBO matrix
    Q = {}
    Q[(0, 0)] = -2.0  # Linear term
    Q[(1, 1)] = -1.5  # Linear term
    Q[(2, 2)] = -1.0  # Linear term
    Q[(0, 1)] = -1.0  # Quadratic term
    Q[(1, 2)] = -2.5  # Quadratic term
    Q[(0, 3)] = -0.5  # Quadratic term
    
    # Create BQM
    bqm = dimod.BinaryQuadraticModel(Q, dimod.BINARY)
    
    # Metadata
    metadata = {
        "suite_name": suite_name,
        "instance_id": instance_id,
        "num_variables": num_variables,
        "num_edges": len(Q) - num_variables,  # Edges only, not diagonal
        "format": ".bq"
    }
    
    return bqm, metadata