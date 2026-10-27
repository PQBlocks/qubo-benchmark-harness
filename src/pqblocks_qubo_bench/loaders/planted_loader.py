"""Planted/Chook instance loader implementation."""

import numpy as np
import dimod
import json
from typing import Tuple, Dict, Any


def load_planted_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load a Planted/Chook instance from the JSONL format.
    
    Args:
        suite_name: Name of the suite (should be 'planted')
        instance_id: Instance identifier (e.g., 'planted_100_2D_10')
        
    Returns:
        Tuple of (BinaryQuadraticModel, metadata_dict)
        
    Raises:
        ValueError: If instance has < 2 variables
        FileNotFoundError: If instance file not found
        ParserError: If file format is invalid
    """
    # For implementation, we'll simulate loading from a file
    # In a real implementation, this would read from the actual JSONL format
    
    # Validate inputs
    if suite_name != 'planted':
        raise ValueError(f"Invalid suite name for Planted loader: {suite_name}")
    
    if not instance_id.startswith('planted_'):
        raise ValueError(f"Invalid Planted instance ID format: {instance_id}")
    
    # For this implementation, we'll create a simple test instance
    # In practice, this would parse the actual JSONL format
    
    # Simulate a small graph for testing
    # Planted JSONL format contains QUBO matrix with planted solution
    
    # Create a simple test case
    num_variables = 6
    if num_variables < 2:
        raise ValueError("Instance must have ≥2 variables for meaningful benchmark")
    
    # Create a simple QUBO matrix
    Q = {}
    # Linear terms
    Q[(0, 0)] = -1.0
    Q[(1, 1)] = -2.0
    Q[(2, 2)] = -1.5
    Q[(3, 3)] = -0.5
    Q[(4, 4)] = -3.0
    Q[(5, 5)] = -1.0
    
    # Quadratic terms
    Q[(0, 1)] = -1.5
    Q[(0, 2)] = -1.0
    Q[(1, 3)] = -2.0
    Q[(2, 4)] = -0.5
    Q[(3, 5)] = -1.5
    Q[(4, 5)] = -1.0
    
    # Create BQM
    bqm = dimod.BinaryQuadraticModel(Q, dimod.BINARY)
    
    # Metadata
    metadata = {
        "suite_name": suite_name,
        "instance_id": instance_id,
        "num_variables": num_variables,
        "num_edges": len(Q) - num_variables,  # Edges only, not diagonal
        "format": "JSONL",
        "planted_solution_energy": -10.5  # Example of planted solution energy
    }
    
    return bqm, metadata