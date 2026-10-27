"""Test module for CLI module."""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock
from argparse import Namespace

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.cli import load_config, merge_config_with_env, merge_config_with_cli_args, get_solver_by_id


class TestCLIModule(unittest.TestCase):
    
    def test_load_config(self):
        """Test that configuration file loading works correctly."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("benchmark:\n  min_runs: 200\n  seed: 12345\n")
            config_path = f.name
        
        try:
            # Load the config
            config = load_config(config_path)
            self.assertEqual(config['benchmark']['min_runs'], 200)
            self.assertEqual(config['benchmark']['seed'], 12345)
        finally:
            # Clean up
            os.unlink(config_path)
    
    def test_merge_config_with_env(self):
        """Test that environment variables correctly override config values."""
        # Create a base config
        config = {
            'benchmark': {
                'min_runs': 100,
                'seed': 42
            }
        }
        
        # Test with environment variables
        with patch.dict(os.environ, {'BENCH_HARNESS_SEED': '999', 'OMP_NUM_THREADS': '8'}):
            merged_config = merge_config_with_env(config)
            self.assertEqual(merged_config['benchmark']['seed'], 999)
            self.assertEqual(merged_config['benchmark']['threads_per_solver'], 8)
    
    def test_merge_config_with_cli_args(self):
        """Test that CLI arguments correctly override config values."""
        # Create a base config
        config = {
            'benchmark': {
                'min_runs': 100,
                'seed': 42
            }
        }
        
        # Create mock CLI args using argparse.Namespace
        args = Namespace(min_runs=200, seed=555, threads=4)
        
        # Merge with CLI args
        merged_config = merge_config_with_cli_args(config, args)
        self.assertEqual(merged_config['benchmark']['min_runs'], 200)
        self.assertEqual(merged_config['benchmark']['seed'], 555)
        self.assertEqual(merged_config['benchmark']['threads_per_solver'], 4)
    
    def test_get_solver_by_id_unknown(self):
        """Test that get_solver_by_id raises ValueError for unknown solver ID."""
        with self.assertRaises(ValueError) as context:
            get_solver_by_id('unknown-solver')
        self.assertIn('Unknown solver ID: unknown-solver', str(context.exception))


if __name__ == '__main__':
    unittest.main()