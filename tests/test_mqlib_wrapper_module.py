# Test fixture marker for clean-room tests: 'bin'
"""Test module for MQLib wrapper module."""

import unittest
import os
import sys
import tempfile
import numpy as np
import dimod

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.mqlib_wrapper import MQLibWrapper


class TestMQLibWrapperModule(unittest.TestCase):
    
    def test_initialization(self):
        """Test that the wrapper initializes correctly."""
        # Create a simple BQM
        bqm = dimod.BinaryQuadraticModel({0: -1.0, 1: -1.0}, {(0, 1): 2.0}, 0.0, dimod.BINARY)
        
        # Initialize the wrapper
        wrapper = MQLibWrapper(bqm, seed=42)
        
        # Check that the wrapper was created
        self.assertIsNotNone(wrapper)
    
    def test_get_default_params(self):
        """Test that default parameters are returned correctly."""
        # Create a simple BQM
        bqm = dimod.BinaryQuadraticModel({0: -1.0, 1: -1.0}, {(0, 1): 2.0}, 0.0, dimod.BINARY)
        
        # Initialize the wrapper
        wrapper = MQLibWrapper(bqm, seed=42)
        
        # Get default parameters
        params = wrapper.get_default_params()
        
        # Check that the parameters are as expected
        self.assertIn('timeout', params)
        self.assertIn('heuristic_name', params)
    
    def test_empty_bqm_raises_value_error(self):
        """Test that an empty BQM raises a ValueError."""
        # Create an empty BQM
        bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)
        
        # Check that initializing the wrapper raises a ValueError
        with self.assertRaises(ValueError):
            MQLibWrapper(bqm, seed=42)


if __name__ == '__main__':
    unittest.main()