"""Comprehensive tests for batch module to improve code coverage."""

import unittest
import os
import sys
import tempfile
import csv
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.batch import load_batch_config

class TestBatchComprehensive(unittest.TestCase):
    
    def test_load_batch_config_with_valid_csv(self):
        """Test load_batch_config with a valid CSV file."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['solver', 'suite', 'instance'])
            writer.writerow(['mock-solver', 'test-suite', 'test-instance'])
            temp_path = f.name
            
        try:
            config = load_batch_config(temp_path)
            self.assertEqual(len(config), 1)
            # According to the spec and implementation, load_batch_config returns tuples
            self.assertEqual(config[0][0], 'mock-solver')
            self.assertEqual(config[0][1], 'test-suite')
            self.assertEqual(config[0][2], 'test-instance')
        finally:
            os.unlink(temp_path)
            
    def test_load_batch_config_with_empty_csv(self):
        """Test load_batch_config with an empty CSV file."""
        # Create a temporary empty CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            
        try:
            config = load_batch_config(temp_path)
            self.assertEqual(config, [])
        finally:
            os.unlink(temp_path)
            
    def test_load_batch_config_with_csv_no_header(self):
        """Test load_batch_config with a CSV file that has no header."""
        # Create a temporary CSV file with no header
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['mock-solver', 'test-suite', 'test-instance'])
            temp_path = f.name
            
        try:
            config = load_batch_config(temp_path)
            self.assertEqual(len(config), 1)
            # According to the spec and implementation, load_batch_config returns tuples
            self.assertEqual(config[0][0], 'mock-solver')
            self.assertEqual(config[0][1], 'test-suite')
            self.assertEqual(config[0][2], 'test-instance')
        finally:
            os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()