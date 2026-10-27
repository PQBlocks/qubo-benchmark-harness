"""Test module for Pipeline module."""

import unittest
import os
import sys
import tempfile
import numpy as np
import dimod

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.pipeline import BenchmarkPipeline, load_instance, get_reference_energy
from pqblocks_qubo_bench.test_data.mock_solver import MockSolver
from pqblocks_qubo_bench.test_data.mock_instances import MOCK_BQM, MOCK_INSTANCE_METADATA, MOCK_REFERENCE_ENERGY


class TestPipelineModule(unittest.TestCase):
    
    def test_load_instance(self):
        """Test that instances can be loaded correctly."""
        # Try to load the mock instance
        bqm, metadata = load_instance('MockSuite', 'mock_2var')
        
        # Check that we got a BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.num_variables, 2)
        
        # Check that we got metadata
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata['suite_name'], 'MockSuite')
        self.assertEqual(metadata['instance_id'], 'mock_2var')
    
    def test_get_reference_energy(self):
        """Test that reference energies can be retrieved."""
        # Try to get the reference energy for the mock instance
        energy = get_reference_energy('MockSuite', 'mock_2var')
        
        # Check that we got the expected energy
        self.assertEqual(energy, -1.0)
    
    def test_benchmark_pipeline_initialization(self):
        """Test that the benchmark pipeline initializes correctly."""
        # Create a simple config
        config = {
            'benchmark': {
                'min_runs': 10,
                'seed': 42
            }
        }
        
        # Initialize the pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Check that the pipeline was created
        self.assertIsNotNone(pipeline)
        
        # Check that the config was stored
        self.assertEqual(pipeline.benchmark_config['min_runs'], 10)
        self.assertEqual(pipeline.benchmark_config['seed'], 42)
    
    def test_benchmark_pipeline_run(self):
        """Test that the benchmark pipeline can run successfully."""
        # Create a simple config
        config = {
            'benchmark': {
                'min_runs': 5,
                'max_runs': 10,
                'seed': 42
            }
        }
        
        # Initialize the pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Create a mock solver
        solver = MockSolver(MOCK_BQM)
        
        # Run the pipeline
        card = pipeline.run(solver, 'MockSuite', 'mock_2var')
        
        # Check that we got a card
        self.assertIsInstance(card, dict)
        
        # Check some fields in the card
        self.assertIn('metadata', card)
        self.assertIn('benchmark_suite', card)
        self.assertIn('metrics', card)
        self.assertIn('execution_stats', card)
        
        # Check that the solver metadata is correct
        self.assertEqual(card['metadata']['solver_id'], 'MockSolver')
        
        # Check that the problem metadata is correct
        self.assertEqual(card['benchmark_suite']['suite_name'], 'MockSuite')
        self.assertEqual(card['benchmark_suite']['instance_id'], 'mock_2var')
        
        # Check that we have metrics
        self.assertIn('success_probability', card['metrics'])
        self.assertIn('time_to_solution_99_seconds', card['metrics'])


if __name__ == '__main__':
    unittest.main()