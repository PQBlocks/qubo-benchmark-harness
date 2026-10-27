import unittest
import dimod
from pqblocks_qubo_bench.base import BaselineWrapper


class ConcreteBaselineWrapper(BaselineWrapper):
    """Concrete implementation for testing the base class."""
    
    def sample(self, **parameters):
        """Dummy implementation."""
        return dimod.SampleSet.from_samples([{0: 1}], dimod.BINARY, energy=0.0)
    
    def get_default_params(self):
        """Dummy implementation."""
        return {}


class TestBaselineWrapper(unittest.TestCase):
    
    def test_nan_detection_linear(self):
        """Test that NaN in linear coefficients raises ValueError."""
        with self.assertRaises(ValueError) as context:
            bqm = dimod.BinaryQuadraticModel({0: float('nan'), 1: -2.0}, {(0, 1): -2.0}, 0.0, dimod.BINARY)
            ConcreteBaselineWrapper(bqm, seed=42)
        self.assertIn("Invalid coefficient nan", str(context.exception))
        
    def test_inf_detection_linear(self):
        """Test that Inf in linear coefficients raises ValueError."""
        with self.assertRaises(ValueError) as context:
            bqm = dimod.BinaryQuadraticModel({0: float('inf'), 1: -2.0}, {(0, 1): -2.0}, 0.0, dimod.BINARY)
            ConcreteBaselineWrapper(bqm, seed=42)
        self.assertIn("Invalid coefficient inf", str(context.exception))
        
    def test_nan_detection_quadratic(self):
        """Test that NaN in quadratic coefficients raises ValueError."""
        with self.assertRaises(ValueError) as context:
            bqm = dimod.BinaryQuadraticModel({0: -1.0, 1: -2.0}, {(0, 1): float('nan')}, 0.0, dimod.BINARY)
            ConcreteBaselineWrapper(bqm, seed=42)
        self.assertIn("Invalid coefficient nan", str(context.exception))
        
    def test_inf_detection_quadratic(self):
        """Test that Inf in quadratic coefficients raises ValueError."""
        with self.assertRaises(ValueError) as context:
            bqm = dimod.BinaryQuadraticModel({0: -1.0, 1: -2.0}, {(0, 1): float('inf')}, 0.0, dimod.BINARY)
            ConcreteBaselineWrapper(bqm, seed=42)
        self.assertIn("Invalid coefficient inf", str(context.exception))
        
    def test_valid_bqm_initialization(self):
        """Test that valid BQM initializes without error."""
        bqm = dimod.BinaryQuadraticModel({0: -1.0, 1: -2.0}, {(0, 1): -2.0}, 0.0, dimod.BINARY)
        wrapper = ConcreteBaselineWrapper(bqm, seed=42)
        self.assertIsInstance(wrapper, BaselineWrapper)


if __name__ == '__main__':
    unittest.main()