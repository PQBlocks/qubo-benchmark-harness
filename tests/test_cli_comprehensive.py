"""Test module for CLI comprehensive tests."""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.cli import main, load_config, merge_config_with_env, merge_config_with_cli_args, get_solver_by_id


class TestCLIComprehensive(unittest.TestCase):
    
    def test_cli_argument_parsing(self):
        """Test that CLI argument parsing works correctly."""
        # Test help command
        test_args = ['pqblocks_qubo_bench', '--help']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
    
    def test_cli_config_file_loading(self):
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
    
    def test_cli_env_var_override(self):
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
    
    def test_cli_solver_initialization(self):
        """Test that solvers can be initialized correctly."""
        # Test mock solver initialization
        solver = get_solver_by_id('mock-solver')
        self.assertIsNotNone(solver)
        self.assertEqual(solver.__class__.__name__, 'MockSolver')


if __name__ == '__main__':
    unittest.main()