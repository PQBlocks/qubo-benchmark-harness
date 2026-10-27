"""Main loader module that dispatches to specific suite pqblocks_qubo_bench.loaders."""

from typing import Tuple, Dict, Any
import dimod

from .gset_loader import load_gset_instance
from .biqmac_loader import load_biqmac_instance
from .qplib_loader import load_qplib_instance
from .tsplib_loader import load_tsplib_instance
from .orlib_loader import load_orlib_instance
from .planted_loader import load_planted_instance


def load_instance(suite_name: str, instance_id: str) -> Tuple[dimod.BinaryQuadraticModel, Dict[str, Any]]:
    """Load an instance from any supported suite.
    
    Args:
        suite_name: Name of the suite (gset, biqmac, qplib, tsplib, orlib, planted)
        instance_id: Instance identifier
        
    Returns:
        Tuple of (BinaryQuadraticModel, metadata_dict)
        
    Raises:
        ValueError: If suite_name is not supported or instance has < 2 variables
        FileNotFoundError: If instance file not found
        ParserError: If file format is invalid
    """
    # Dispatch to appropriate loader based on suite name
    if suite_name == 'gset':
        return load_gset_instance(suite_name, instance_id)
    elif suite_name == 'biqmac':
        return load_biqmac_instance(suite_name, instance_id)
    elif suite_name == 'qplib':
        return load_qplib_instance(suite_name, instance_id)
    elif suite_name == 'tsplib':
        return load_tsplib_instance(suite_name, instance_id)
    elif suite_name == 'orlib':
        return load_orlib_instance(suite_name, instance_id)
    elif suite_name == 'planted':
        return load_planted_instance(suite_name, instance_id)
    else:
        raise ValueError(f"Unsupported suite name: {suite_name}")