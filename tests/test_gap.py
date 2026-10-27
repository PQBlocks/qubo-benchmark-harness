"""Test module for gap.py"""

import unittest
import sys
import os

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.gap import calculate_gap


class TestGap(unittest.TestCase):
    
    def test_calculate_gap_with_none_reference(self):
        """Test calculate_gap when e_ref is None"""
        result = calculate_gap(10.0, None)
        self.assertIsNone(result)
    
    def test_calculate_gap_with_zero_reference(self):
        """Test calculate_gap when e_ref is near zero"""
        result = calculate_gap(5.0, 0.0)
        self.assertEqual(result, 5.0)
    
    def test_calculate_gap_with_zero_reference_negative(self):
        """Test calculate_gap when e_ref is near zero (negative case)"""
        result = calculate_gap(-3.0, 0.0)
        self.assertEqual(result, -3.0)
    
    def test_calculate_gap_with_small_reference(self):
        """Test calculate_gap when e_ref is very small but not zero"""
        result = calculate_gap(5.0, 1e-10)
        # Should use absolute gap since it's near zero (EPSILON = 1e-8)
        self.assertIsNotNone(result)
        # For reference energy near zero, we use absolute gap (e_found - e_ref)
        expected = 5.0 - 1e-10
        if result is not None:
            self.assertAlmostEqual(result, expected, delta=1e-12)
    
    def test_calculate_gap_standard_case_positive(self):
        """Test calculate_gap with standard positive inputs"""
        result = calculate_gap(10.0, 5.0)
        expected = (10.0 - 5.0) / abs(5.0)
        self.assertEqual(result, expected)
    
    def test_calculate_gap_standard_case_negative(self):
        """Test calculate_gap with standard negative inputs"""
        result = calculate_gap(-5.0, -10.0)
        expected = (-5.0 - (-10.0)) / abs(-10.0)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()