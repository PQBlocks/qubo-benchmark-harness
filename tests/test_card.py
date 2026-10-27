import unittest
import sys
import os
import jsonschema

# Add the src directory to the path so we can import bench_harness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.card import generate_benchmark_card, validate_benchmark_card, BENCHMARK_CARD_SCHEMA


class TestCard(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.solver_metadata = {
            "solver_id": "test-solver",
            "solver_name": "Test Solver",
            "hardware": {
                "cpu": "Intel i7",
                "gpu": "NVIDIA RTX 3080",
                "threads_allocated": 8
            }
        }
        
        self.instance_metadata = {
            "suite_name": "TestSuite",
            "instance_id": "test_instance_1",
            "num_variables": 100,
            "num_edges": 300
        }
        
        self.execution_stats = {
            "num_independent_runs": 100,
            "average_single_run_time_seconds": 0.5,
            "total_elapsed_time_seconds": 50.0
        }
        
        self.metrics = {
            "target_energy": -10.0,
            "success_probability": 0.85,
            "time_to_solution_99_seconds": 2.5,
            "tts_95_confidence_interval": [2.0, 3.0],
            "best_energy_found": -9.5,
            "reference_gap": 0.05
        }
    
    def test_generate_benchmark_card_success_probability_zero(self):
        """Test generate_benchmark_card when success_probability is 0.0"""
        # Modify metrics to have zero success probability
        metrics_zero_prob = self.metrics.copy()
        metrics_zero_prob["success_probability"] = 0.0
        
        # Generate card
        card = generate_benchmark_card(
            self.solver_metadata,
            self.instance_metadata,
            self.execution_stats,
            metrics_zero_prob
        )
        
        # Check that time_to_solution_99_seconds is None
        self.assertIsNone(card["metrics"]["time_to_solution_99_seconds"])
        
        # Check that tts_95_confidence_interval is [None, None]
        self.assertEqual(card["metrics"]["tts_95_confidence_interval"], [None, None])
    
    def test_validate_benchmark_card_valid(self):
        """Test validate_benchmark_card with a valid card"""
        # Generate a valid card
        card = generate_benchmark_card(
            self.solver_metadata,
            self.instance_metadata,
            self.execution_stats,
            self.metrics
        )
        
        # Validate the card - should not raise an exception
        try:
            validate_benchmark_card(card)
        except jsonschema.ValidationError:
            self.fail("validate_benchmark_card raised ValidationError unexpectedly!")
    
    def test_validate_benchmark_card_invalid(self):
        """Test validate_benchmark_card with an invalid card"""
        # Generate a valid card
        card = generate_benchmark_card(
            self.solver_metadata,
            self.instance_metadata,
            self.execution_stats,
            self.metrics
        )
        
        # Modify it to make it invalid (missing required field)
        del card["metadata"]["solver_id"]
        
        # Validate the card - should raise an exception
        with self.assertRaises(jsonschema.ValidationError):
            validate_benchmark_card(card)


if __name__ == '__main__':
    unittest.main()