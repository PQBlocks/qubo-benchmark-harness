"""Additional comprehensive tests for CLI to improve code coverage."""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock
from argparse import Namespace

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.cli import main, load_config, merge_config_with_env, merge_config_with_cli_args, get_solver_by_id


class TestCLIAdditionalCoverage(unittest.TestCase):
    
    def test_cli_run_command_with_invalid_solver(self):
        """Test CLI run command with invalid solver ID."""
        test_args = ['pqblocks_qubo_bench', 'run', '--solver', 'invalid-solver', '--suite', 'test-suite', '--instance', 'test-instance']
        with patch.object(sys, 'argv', test_args):
            # Mock the BenchmarkPipeline to avoid actual execution
            with patch('pqblocks_qubo_bench.cli.BenchmarkPipeline') as mock_pipeline:
                result = main()
                # Should return 1 for error
                self.assertEqual(result, 1)
    
    def test_cli_run_command_missing_required_args(self):
        """Test CLI run command with missing required arguments."""
        # Test missing solver
        test_args = ['pqblocks_qubo_bench', 'run', '--suite', 'test-suite', '--instance', 'test-instance']
        with patch.object(sys, 'argv', test_args):
            # Capture stderr to check error message
            from io import StringIO
            stderr_capture = StringIO()
            with patch('sys.stderr', stderr_capture):
                with patch('pqblocks_qubo_bench.cli.BenchmarkPipeline'):
                    with self.assertRaises(SystemExit) as cm:
                        main()
                    # Should exit with code 2 for argument error
                    self.assertEqual(cm.exception.code, 2)
                    # Check that error message mentions required arguments
                    self.assertIn('the following arguments are required', stderr_capture.getvalue())
    
    def test_cli_batch_command_with_invalid_config(self):
        """Test CLI batch command with invalid config file."""
        # Create a temporary non-existent config file path
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'nonexistent.csv')
            test_args = ['pqblocks_qubo_bench', 'batch', '--config', config_path]
            with patch.object(sys, 'argv', test_args):
                with patch('pqblocks_qubo_bench.cli.BenchmarkPipeline'):
                    result = main()
                    # Should return 1 for error
                    self.assertEqual(result, 1)
    
    def test_cli_batch_command_with_valid_config(self):
        """Test CLI batch command with valid config file."""
        # Create a temporary CSV config file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'batch_config.csv')
            with open(config_path, 'w') as f:
                f.write("solver,suite,instance\nmock-solver,test-suite,test-instance\n")
            
            test_args = ['pqblocks_qubo_bench', 'batch', '--config', config_path, '--output-dir', temp_dir]
            with patch.object(sys, 'argv', test_args):
                # Mock the BenchmarkPipeline.run method to avoid actual execution
                with patch('pqblocks_qubo_bench.cli.BenchmarkPipeline') as mock_pipeline_class:
                    mock_pipeline = MagicMock()
                    mock_pipeline_class.return_value = mock_pipeline
                    mock_pipeline.run.return_value = {
                        'metrics': {
                            'success_probability': 0.5,
                            'time_to_solution_99_seconds': 1.0
                        }
                    }
                    
                    result = main()
                    # Should return 0 for success
                    self.assertEqual(result, 0)
    
    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        test_args = ['pqblocks_qubo_bench', 'invalid-command']
        with patch.object(sys, 'argv', test_args):
            # Capture stderr to check error message
            from io import StringIO
            stderr_capture = StringIO()
            with patch('sys.stderr', stderr_capture):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Should exit with code 2 for argument error
                self.assertEqual(cm.exception.code, 2)
                # Check that error message mentions invalid command
                self.assertIn('invalid choice', stderr_capture.getvalue())


if __name__ == '__main__':
    unittest.main()