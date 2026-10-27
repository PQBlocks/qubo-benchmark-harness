"""Tests for batch benchmark execution."""

import os
import tempfile
import unittest
import csv
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.batch import load_batch_config, execute_batch, get_solver_by_id
from pqblocks_qubo_bench.pipeline import BenchmarkPipeline


class TestBatchExecution(unittest.TestCase):
    """Test cases for batch benchmark execution."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create a mock configuration
        self.config = [
            ("mock-solver", "mock-suite", "mock-instance-1"),
            ("mock-solver", "mock-suite", "mock-instance-2"),
            ("mock-solver", "mock-suite", "mock-instance-3")
        ]
        
        # Create a mock pipeline
        self.pipeline = MagicMock(spec=BenchmarkPipeline)
        self.pipeline.benchmark_config = {}
        
        # Mock benchmark card
        self.mock_card = {
            "metrics": {
                "success_probability": 0.5,
                "time_to_solution_99_seconds": 1.0
            }
        }
        self.pipeline.run.return_value = self.mock_card

    def test_load_batch_config(self):
        """Test loading batch configuration from CSV."""
        # Create a temporary CSV file
        csv_path = os.path.join(self.test_dir, "batch_config.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["solver", "suite", "instance"])  # Header
            writer.writerow(["solver1", "suite1", "instance1"])
            writer.writerow(["solver2", "suite2", "instance2"])
        
        # Load configuration
        config = load_batch_config(csv_path)
        
        # Verify the configuration
        self.assertEqual(len(config), 2)
        self.assertEqual(config[0], ("solver1", "suite1", "instance1"))
        self.assertEqual(config[1], ("solver2", "suite2", "instance2"))

    def test_load_batch_config_no_header(self):
        """Test loading batch configuration from CSV without header."""
        # Create a temporary CSV file without header
        csv_path = os.path.join(self.test_dir, "batch_config_no_header.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["solver1", "suite1", "instance1"])
            writer.writerow(["solver2", "suite2", "instance2"])
        
        # Load configuration
        config = load_batch_config(csv_path)
        
        # Verify the configuration
        self.assertEqual(len(config), 2)
        self.assertEqual(config[0], ("solver1", "suite1", "instance1"))
        self.assertEqual(config[1], ("solver2", "suite2", "instance2"))

    def test_execute_batch(self):
        """Test executing a batch of benchmarks."""
        # Execute batch
        with patch('pqblocks_qubo_bench.batch.load_instance') as mock_load_instance:
            # Mock instance loading
            mock_bqm = MagicMock()
            mock_instance_metadata = {"num_variables": 100, "num_edges": 200}
            mock_load_instance.return_value = (mock_bqm, mock_instance_metadata)
            
            # Mock solver
            with patch('pqblocks_qubo_bench.batch.get_solver_by_id') as mock_get_solver:
                mock_solver = MagicMock()
                mock_get_solver.return_value = mock_solver
                
                summary = execute_batch(self.config, self.pipeline, self.test_dir)
        
        # Verify the summary
        self.assertEqual(summary["total_benchmarks"], 3)
        self.assertEqual(summary["successful_benchmarks"], 3)
        self.assertEqual(summary["failed_benchmarks"], 0)
        self.assertEqual(summary["success_rate"], 1.0)
        
        # Verify pipeline was called correctly
        self.assertEqual(self.pipeline.run.call_count, 3)
        
        # Verify results were recorded
        self.assertEqual(len(summary["results"]), 3)
        for result in summary["results"]:
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["success_probability"], 0.5)
            self.assertEqual(result["tts"], 1.0)

    def test_execute_batch_with_failure(self):
        """Test executing a batch of benchmarks with a failure."""
        # Modify pipeline mock to raise an exception on the second call
        def side_effect(*args, **kwargs):
            if self.pipeline.run.call_count == 2:
                raise Exception("Test failure")
            return self.mock_card
            
        self.pipeline.run.side_effect = side_effect
        
        # Execute batch
        with patch('pqblocks_qubo_bench.batch.load_instance') as mock_load_instance:
            # Mock instance loading
            mock_bqm = MagicMock()
            mock_instance_metadata = {"num_variables": 100, "num_edges": 200}
            mock_load_instance.return_value = (mock_bqm, mock_instance_metadata)
            
            # Mock solver
            with patch('pqblocks_qubo_bench.batch.get_solver_by_id') as mock_get_solver:
                mock_solver = MagicMock()
                mock_get_solver.return_value = mock_solver
                
                summary = execute_batch(self.config, self.pipeline, self.test_dir)
        
        # Verify the summary
        self.assertEqual(summary["total_benchmarks"], 3)
        self.assertEqual(summary["successful_benchmarks"], 2)
        self.assertEqual(summary["failed_benchmarks"], 1)
        self.assertEqual(summary["success_rate"], 2/3)
        
        # Verify pipeline was called correctly
        self.assertEqual(self.pipeline.run.call_count, 3)
        
        # Verify results and failures were recorded
        self.assertEqual(len(summary["results"]), 2)
        self.assertEqual(len(summary["failures"]), 1)
        self.assertEqual(summary["failures"][0]["status"], "failed")


if __name__ == '__main__':
    unittest.main()