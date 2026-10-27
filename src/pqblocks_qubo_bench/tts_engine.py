"""
TTS and bootstrap calculation engine.
"""

import numpy as np
from typing import List, Tuple, Optional, Union


def calculate_tts(runs: List[Tuple[float, bool]], target_prob: float = 0.99) -> Optional[float]:
    """
    Calculate the Time-to-Solution (TTS) point estimate.
    
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
        # Avoid returning 0.0 which can be mistaken for a failure or due to timer resolution
        if avg_runtime == 0.0:
            return 1e-9
        return avg_runtime
    
    # Calculate average runtime
    avg_runtime = np.mean([runtime for runtime, _ in runs])
    
    # Calculate TTS point estimate
    # TTS(s) = t_run * ln(1 - s) / ln(1 - p)
    ln_1_minus_s = np.log(1 - target_prob)
    ln_1_minus_p = np.log(1 - p)
    
    tts = avg_runtime * ln_1_minus_s / ln_1_minus_p
    return tts


def calculate_confidence_interval(
    runs: List[Tuple[float, bool]], 
    target_prob: float = 0.99, 
    bootstrap_iterations: int = 1000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Calculate bootstrap-based Confidence Interval for TTS.
    
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
    
    # Set up random number generator with seed for reproducibility
    rng = np.random.default_rng(seed)
    
    # Bootstrap resampling
    bootstrap_tts_values = []
    
    for _ in range(bootstrap_iterations):
        # Resample with replacement
        bootstrap_sample_indices = rng.choice(total_runs, size=total_runs, replace=True)
        bootstrap_sample = [runs[i] for i in bootstrap_sample_indices]
        
        # Calculate regularized success probability for bootstrap sample
        successful_runs_boot = sum(1 for _, success in bootstrap_sample if success)
        p_boot = successful_runs_boot / total_runs
        
        # Calculate average runtime for bootstrap sample
        avg_runtime_boot = np.mean([runtime for runtime, _ in bootstrap_sample])
        
        # Handle p_boot = 1 case consistently with point estimate calculation
        # When p_boot = 1, return avg_runtime_boot directly without regularization
        # This ensures statistical consistency between point estimate and bootstrap CI
        if p_boot == 1:
            tts_boot = avg_runtime_boot
        else:
            # Regularization (boundary_half_width = 0.5 as per spec)
            boundary_half_width = 0.5
            if p_boot == 0:
                p_boot_regularized = boundary_half_width / total_runs  # 0.5 / R
            else:
                p_boot_regularized = p_boot
            
            # Calculate TTS for bootstrap sample
            ln_1_minus_s = np.log(1 - target_prob)
            ln_1_minus_p = np.log(1 - p_boot_regularized)
            
            tts_boot = avg_runtime_boot * ln_1_minus_s / ln_1_minus_p
        
        bootstrap_tts_values.append(tts_boot)
    
    # Calculate 95% confidence interval (2.5th and 97.5th percentiles)
    ci_lower = np.percentile(bootstrap_tts_values, 2.5)
    ci_upper = np.percentile(bootstrap_tts_values, 97.5)
    
    return ci_lower, ci_upper