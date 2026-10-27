"""
Reference-Gap calculation module.
"""

import logging
from typing import Optional

# Epsilon threshold for zero-energy handling
EPSILON = 1e-8


def calculate_gap(
    e_found: float, 
    e_ref: Optional[float]
) -> Optional[float]:
    """
    Calculate the reference-gap between found energy and reference energy.
    
    Args:
        e_found: The best energy found by the solver
        e_ref: The verified global minimum or best-known reference bound
        
    Returns:
        The relative gap (E_found - E_ref) / |E_ref|, or absolute gap if E_ref is near zero,
        or None if no reference energy is provided.
    """
    # Handle case where no reference energy is provided
    if e_ref is None:
        return None
    
    # Handle zero-energy case
    if abs(e_ref) < EPSILON:
        logging.warning("Reference energy near zero; using absolute gap")
        return e_found - e_ref
    
    # Calculate relative gap
    return (e_found - e_ref) / abs(e_ref)