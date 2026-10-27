"""Additional comprehensive tests for Pipeline module to improve code coverage."""

import unittest
import os
import sys
import tempfile
import numpy as np
import dimod
import jsonschema
import json

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.pipeline import BenchmarkPipeline, load_instance, get_reference_energy
from pqblocks_qubo_bench.test_data.mock_solver import MockSolver
from pqblocks_qubo_bench.test_data.mock_instances import MOCK_BQM, MOCK_INSTANCE_METADATA, MOCK_REFERENCE_ENERGY
from pqblocks_qubo_bench.card import generate_benchmark_card, validate_benchmark_card, BENCHMARK_CARD_SCHEMA
from pqblocks_qubo_bench.gap import calculate_gap


class TestPipelineAdditionalCoverage(unittest.TestCase):
    
    def test_pipeline_with_zero_success_probability(self):
        """Test pipeline behavior when success probability is zero."""
        # Create a config that will result in zero success probability
        config = {
            'benchmark': {
                'min_runs': 5,
                'max_runs': 5,
                'seed': 42
            }
        }
        
        # Initialize the pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Create a mock solver that always returns wrong results
        # We'll mock the sample method to return samples with high energy
        solver = MockSolver(MOCK_BQM)
        
        # Mock the solver's sample method to return high energy samples
        def mock_sample(**kwargs):
            # Return samples with energy much higher than reference
            samples = [{'energy': 100.0, 'sample': {'x0': 0, 'x1': 1}} for _ in range(10)]
            return dimod.SampleSet.from_samples(
                [s['sample'] for s in samples], 
                'BINARY', 
                energies=[s['energy'] for s in samples]
            )
        
        solver.sample = mock_sample
        
        # Run the pipeline
        card = pipeline.run(solver, 'MockSuite', 'mock_2var')
        
        # Check that we got a card
        self.assertIsInstance(card, dict)
        
        # Check that success probability is 0
        self.assertEqual(card['metrics']['success_probability'], 0.0)
        
        # Check that TTS is None when success probability is 0
        self.assertIsNone(card['metrics']['time_to_solution_99_seconds'])
    
    def test_pipeline_with_reference_gap_calculation(self):
        """Test pipeline with reference gap calculation."""
        # Create a config
        config = {
            'benchmark': {
                'min_runs': 5,
                'max_runs': 5,
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
        
        # Check that reference gap is calculated
        self.assertIn('reference_gap', card['metrics'])
        
        # Validate the card
        validate_benchmark_card(card)
    
    def test_pipeline_card_validation(self):
        """Test that pipeline generates valid benchmark cards."""
        # Create a config
        config = {
            'benchmark': {
                'min_runs': 5,
                'max_runs': 5,
                'seed': 42
            }
        }
        
        # Initialize the pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Create a mock solver
        solver = MockSolver(MOCK_BQM)
        
        # Run the pipeline
        card = pipeline.run(solver, 'MockSuite', 'mock_2var')
        
        # Validate the card using jsonschema
        validator = jsonschema.Draft7Validator(BENCHMARK_CARD_SCHEMA)
        # This should not raise an exception
        validator.validate(card)
    
    def test_pipeline_with_output_path(self):
        """Test pipeline with output path saving."""
        # Create a config
        config = {
            'benchmark': {
                'min_runs': 5,
                'max_runs': 5,
                'seed': 42
            }
        }
        
        # Initialize the pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Create a mock solver
        solver = MockSolver(MOCK_BQM)
        
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'test_card.json')
            
            # Run the pipeline with output path
            card = pipeline.run(solver, 'MockSuite', 'mock_2var', output_path=output_path)
            
            # Check that the file was created
            self.assertTrue(os.path.exists(output_path))
            
            # Read and validate the saved card
            with open(output_path, 'r') as f:
                saved_card = json.load(f)
            
            # Check that it matches the returned card
            self.assertEqual(card, saved_card)
    
    def test_pipeline_with_exception_handling(self):
        """Test pipeline exception handling."""
        # Create a config
        config = {
            'benchmark': {
                'min_runs': 5,
                'max_runs': 5,
                'seed': 42
            }
        }
        
        # Initialize the pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Create a mock solver that raises an exception
        solver = MockSolver(MOCK_BQM)
        
        # Mock the solver's sample method to raise an exception
        def failing_sample(**kwargs):
            raise RuntimeError("Test exception")
        
        solver.sample = failing_sample
        
        # Run the pipeline - should not raise an exception
        card = pipeline.run(solver, 'MockSuite', 'mock_2var')
        
        # Check that we got a card
        self.assertIsInstance(card, dict)
        
        # Check that execution stats are still recorded
        self.assertIn('execution_stats', card)
        self.assertEqual(card['execution_stats']['num_independent_runs'], 5)


if __name__ == '__main__':
    unittest.main()