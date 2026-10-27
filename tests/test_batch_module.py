"""Test module for Batch module."""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.batch import load_batch_config, execute_batch, get_solver_by_id


class TestBatchModule(unittest.TestCase):
    
    def test_load_batch_config(self):
        """Test that batch configuration loading works correctly."""
        # Create a temporary CSV config file
        csv_content = """solver,suite,instance
mock-solver,MockSuite,mock_2var
mock-solver,MockSuite,mock_2var
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            config_path = f.name
        
        try:
            # Load the config
            config = load_batch_config(config_path)
            self.assertEqual(len(config), 2)
            self.assertEqual(config[0][0], 'mock-solver')
            self.assertEqual(config[0][1], 'MockSuite')
            self.assertEqual(config[0][2], 'mock_2var')
        finally:
            # Clean up
            os.unlink(config_path)
    
    def test_get_solver_by_id(self):
        """Test that solvers can be initialized correctly."""
        # Import a mock BQM
        import dimod
        bqm = dimod.BinaryQuadraticModel({0: -1.0, 1: -1.0}, {(0, 1): 2.0}, 0.0, dimod.BINARY)
        
        # Test mock solver initialization
        solver = get_solver_by_id('mock-solver', bqm, 42)
        self.assertIsNotNone(solver)
        self.assertEqual(solver.__class__.__name__, 'MockSolver')
        
        # Test unknown solver
        with self.assertRaises(ValueError):
            get_solver_by_id('unknown-solver', bqm, 42)


if __name__ == '__main__':
    unittest.main()