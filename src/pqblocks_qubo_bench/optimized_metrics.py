"""Optimized Metrics Engine for Tier 2 implementation."""

import numpy as np
from numba import jit
from typing import List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_tts_optimized(runs: List[Tuple[float, bool]], target_prob: float = 0.99) -> Optional[float]:
    """
    Calculate the Time-to-Solution (TTS) point estimate using optimized implementation.
    
    Args:
        runs: List of (runtime, success) tuples
        target_prob: Target cumulative probability (default 0.99)
        
    Returns:
        TTS point estimate in seconds, or None if success probability is 0
    """
    if not runs:
        raise ValueError("Runs list cannot be empty")
    
    total_runs = len(runs)
    successful_runs = sum(1 for _, success in runs if success)
    
    # Calculate success probability
    p = successful_runs / total_runs
    
    # If success probability is 0, return None
    if p == 0:
        return None
    
    # If success probability is 1, TTS equals average runtime
    if p == 1:
        avg_runtime = np.mean([runtime for runtime, _ in runs])
        return avg_runtime
    
    # Calculate average runtime
    avg_runtime = np.mean([runtime for runtime, _ in runs])
    
    # Calculate TTS point estimate
    # TTS(s) = t_run * ln(1 - s) / ln(1 - p)
    ln_1_minus_s = np.log(1 - target_prob)
    ln_1_minus_p = np.log(1 - p)
    
    tts = avg_runtime * ln_1_minus_s / ln_1_minus_p
    return tts


@jit(nopython=True)
def _deterministic_bootstrap_sample(indices, runtimes, successes, total_runs, boundary_half_width):
    """
    Deterministic bootstrap sample calculation using Numba JIT compilation.
    
    Args:
        indices: Bootstrap sample indices
        runtimes: Array of runtimes
        successes: Array of success flags
        total_runs: Total number of runs
        boundary_half_width: Regularization parameter
        
    Returns:
        Tuple of (avg_runtime, p_boot_regularized, ln_1_minus_p)
    """
    # Calculate bootstrap sample statistics
    sample_runtimes = runtimes[indices]
    sample_successes = successes[indices]
    
    avg_runtime_boot = 0.0
    for i in range(total_runs):
        avg_runtime_boot += sample_runtimes[i]
    avg_runtime_boot /= total_runs
    
    successful_runs_boot = 0
    for i in range(total_runs):
        successful_runs_boot += sample_successes[i]
    p_boot = successful_runs_boot / total_runs
    
    # Handle p_boot = 1 case consistently with point estimate calculation
    # When p_boot = 1, return avg_runtime_boot directly without regularization
    # This ensures statistical consistency between point estimate and bootstrap CI
    if p_boot == 1:
        return avg_runtime_boot, p_boot, 0.0  # ln(1-1) = ln(0) is undefined, but we return avg_runtime_boot directly
    
    # Regularization (boundary_half_width = 0.5 as per spec)
    if p_boot == 0:
        p_boot_regularized = boundary_half_width / total_runs  # 0.5 / R
    else:
        p_boot_regularized = p_boot
        
    # Calculate ln(1 - p_boot_regularized)
    ln_1_minus_p = np.log(1 - p_boot_regularized)
    
    return avg_runtime_boot, p_boot_regularized, ln_1_minus_p


@jit(nopython=True)
def _xorshift32(state):
    """
    Xorshift32 PRNG implementation that's compatible with Numba.
    
    Args:
        state: Current state (must be non-zero)
        
    Returns:
        Tuple of (next_state, random_value)
    """
    state ^= (state << 13) & 0xFFFFFFFF
    state ^= (state >> 17) & 0xFFFFFFFF
    state ^= (state << 5) & 0xFFFFFFFF
    return state & 0xFFFFFFFF, state & 0xFFFFFFFF


@jit(nopython=True)
def _parallel_bootstrap_tts_calculation(
    runtimes: np.ndarray,
    successes: np.ndarray,
    target_prob: float,
    bootstrap_iterations: int,
    seed: int
) -> np.ndarray:
    """
    Parallelized bootstrap calculation using Numba JIT compilation.
    
    Args:
        runtimes: Array of runtimes
        successes: Array of success flags (1 for success, 0 for failure)
        target_prob: Target cumulative probability
        bootstrap_iterations: Number of bootstrap iterations
        seed: Random seed for reproducibility
        
    Returns:
        Array of bootstrap TTS values
    """
    total_runs = len(runtimes)
    bootstrap_tts_values = np.zeros(bootstrap_iterations)
    
    # Precompute log values
    ln_1_minus_s = np.log(1 - target_prob)
    boundary_half_width = 0.5
    
    # Initialize state for Xorshift32 PRNG
    state = seed if seed != 0 else 1  # Ensure non-zero state
    
    for i in range(bootstrap_iterations):
        # Generate indices for bootstrap sampling using Xorshift32
        indices = np.empty(total_runs, dtype=np.int64)
        for j in range(total_runs):
            state, rand_val = _xorshift32(state)
            indices[j] = rand_val % total_runs
        
        # Calculate bootstrap sample statistics using deterministic function
        avg_runtime_boot, p_boot_regularized, ln_1_minus_p = _deterministic_bootstrap_sample(
            indices, runtimes, successes, total_runs, boundary_half_width)
        
        # Handle p_boot = 1 case consistently with point estimate calculation
        # When p_boot = 1, return avg_runtime_boot directly without regularization
        if p_boot_regularized == 1 or (p_boot_regularized > 0.999999):  # Account for floating point precision
            tts_boot = avg_runtime_boot
        else:
            # Calculate TTS for bootstrap sample
            # Handle case where ln_1_minus_p might be zero or very close to zero
            if abs(ln_1_minus_p) < 1e-15:  # Very small value, avoid division by zero
                tts_boot = avg_runtime_boot
            else:
                tts_boot = avg_runtime_boot * ln_1_minus_s / ln_1_minus_p
        bootstrap_tts_values[i] = tts_boot
    
    return bootstrap_tts_values


def calculate_confidence_interval_optimized(
    runs: List[Tuple[float, bool]], 
    target_prob: float = 0.99, 
    bootstrap_iterations: int = 1000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Calculate bootstrap-based Confidence Interval for TTS using optimized implementation.
    
    Args:
        runs: List of (runtime, success) tuples
        target_prob: Target cumulative probability (default 0.99)
        bootstrap_iterations: Number of bootstrap iterations (default 1000)
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (lower_bound, upper_bound) for 95% confidence interval
    """
    if not runs:
        raise ValueError("Runs list cannot be empty")
    
    total_runs = len(runs)
    
    # Convert to numpy arrays for optimized processing
    runtimes = np.array([runtime for runtime, _ in runs], dtype=np.float64)
    successes = np.array([1 if success else 0 for _, success in runs], dtype=np.int32)
    
    # Use parallelized bootstrap calculation
    bootstrap_tts_values = _parallel_bootstrap_tts_calculation(
        runtimes, successes, target_prob, bootstrap_iterations, seed or 0
    )
    
    # Calculate 95% confidence interval (2.5th and 97.5th percentiles)
    ci_lower = np.percentile(bootstrap_tts_values, 2.5)
    ci_upper = np.percentile(bootstrap_tts_values, 97.5)
    
    return ci_lower, ci_upper