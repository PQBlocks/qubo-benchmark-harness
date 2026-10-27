"""Test module for Optimized Metrics module."""

import unittest
import os
import sys
import numpy as np

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.optimized_metrics import (
    calculate_tts_optimized, 
    calculate_confidence_interval_optimized,
    _deterministic_bootstrap_sample,
    _xorshift32
)


class TestOptimizedMetricsModule(unittest.TestCase):
    
    def test_calculate_tts_optimized_p_zero(self):
        """Test TTS calculation when success probability is 0."""
        runs = [(0.1, False), (0.2, False), (0.3, False)]
        tts = calculate_tts_optimized(runs)
        self.assertIsNone(tts)
    
    def test_calculate_tts_optimized_p_one(self):
        """Test TTS calculation when success probability is 1."""
        runs = [(0.1, True), (0.2, True), (0.3, True)]
        tts = calculate_tts_optimized(runs)
        expected = float(np.mean([0.1, 0.2, 0.3]))
        self.assertAlmostEqual(tts, expected, places=10)
    
    def test_calculate_tts_optimized_normal(self):
        """Test normal TTS calculation."""
        runs = [(0.1, True), (0.2, False), (0.3, True), (0.4, False)]
        tts = calculate_tts_optimized(runs)
        # p = 0.5, avg_runtime = 0.25
        # TTS = 0.25 * ln(1-0.99) / ln(1-0.5) = 0.25 * ln(0.01) / ln(0.5)
        expected = 0.25 * np.log(0.01) / np.log(0.5)
        self.assertAlmostEqual(tts, expected, places=10)
    
    def test_deterministic_bootstrap_sample_p_one(self):
        """Test bootstrap sample calculation when p_boot = 1."""
        indices = np.array([0, 1, 2])
        runtimes = np.array([0.1, 0.2, 0.3])
        successes = np.array([1, 1, 1])
        total_runs = 3
        boundary_half_width = 0.5
        
        avg_runtime, p_boot_regularized, ln_1_minus_p = _deterministic_bootstrap_sample(
            indices, runtimes, successes, total_runs, boundary_half_width)
        
        expected_avg = float(np.mean([0.1, 0.2, 0.3]))
        self.assertAlmostEqual(avg_runtime, expected_avg, places=10)
        self.assertEqual(p_boot_regularized, 1.0)
        self.assertEqual(ln_1_minus_p, 0.0)
    
    def test_deterministic_bootstrap_sample_p_zero(self):
        """Test bootstrap sample calculation when p_boot = 0."""
        indices = np.array([0, 1, 2])
        runtimes = np.array([0.1, 0.2, 0.3])
        successes = np.array([0, 0, 0])
        total_runs = 3
        boundary_half_width = 0.5
        
        avg_runtime, p_boot_regularized, ln_1_minus_p = _deterministic_bootstrap_sample(
            indices, runtimes, successes, total_runs, boundary_half_width)
        
        expected_avg = float(np.mean([0.1, 0.2, 0.3]))
        expected_p_reg = 0.5 / 3  # boundary_half_width / total_runs
        expected_ln = np.log(1 - expected_p_reg)
        
        self.assertAlmostEqual(avg_runtime, expected_avg, places=10)
        self.assertAlmostEqual(p_boot_regularized, expected_p_reg, places=10)
        self.assertAlmostEqual(ln_1_minus_p, expected_ln, places=10)
    
    def test_xorshift32(self):
        """Test Xorshift32 PRNG implementation."""
        # Test that it doesn't produce zero (which would break the PRNG)
        state = 1  # Initialize state
        for i in range(100):
            state, rand_val = _xorshift32(state)
            self.assertNotEqual(rand_val, 0, "Xorshift32 produced zero")
            self.assertLess(rand_val, 2**32, "Xorshift32 produced value >= 2^32")


if __name__ == '__main__':
    unittest.main()