"""
Test for the SQA benchmark wrapper.
"""

import unittest
import numpy as np
import dimod
import os, sys
_sqa_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'sqa')
if os.path.isdir(_sqa_dir) and _sqa_dir not in sys.path:
    sys.path.insert(0, _sqa_dir)
from pqblocks_qubo_bench.sqa_wrapper import SQAWrapper

class TestSQAWrapper(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a small Ising problem instance for testing
        # Using dicts to match dimod's expected input format
        h = {-1: -1.0, 0: 1.0, 1: 2.0, 2: -2.0}
        J = {
            (-1, 0): 1,
            (-1, 1): -1,
            (-1, 2): 2,
            (0, 1): 1,
            (0, 2): -1,
            (1, 2): -2
        }
        
        # Convert to BQM
        self.bqm = dimod.BinaryQuadraticModel.from_ising(h, J)
        
        # Set a fixed seed for reproducibility
        self.seed = 42
        
    def test_wrapper_initialization(self):
        """Test that the wrapper initializes correctly."""
        wrapper = SQAWrapper(self.bqm, self.seed)
        
        # Check that the BQM was stored correctly
        self.assertEqual(wrapper.bqm, self.bqm)
        self.assertEqual(wrapper.seed, self.seed)
        
        # Check that h, J, and variables were extracted correctly
        self.assertIsNotNone(wrapper.h)
        self.assertIsNotNone(wrapper.J)
        self.assertIsNotNone(wrapper.variables)
        
    def test_wrapper_sample(self):
        """Test that the wrapper can sample from the BQM."""
        wrapper = SQAWrapper(self.bqm, self.seed)
        
        # Sample from the BQM
        response = wrapper.sample(num_reads=10, num_sweeps=100, beta=2.0, P=4)
        
        # Check that we got a SampleSet back
        self.assertIsInstance(response, dimod.SampleSet)
        
        # Check that we have the expected number of samples
        self.assertEqual(len(response), 10)
        
        # Check that each sample has the expected number of variables
        for sample in response:
            self.assertEqual(len(sample), 4)  # 4 variables in our test problem
            
        # Check that all values are either -1 or 1 (spin values)
        for sample in response:
            for value in sample.values():
                self.assertIn(value, [-1, 1])
                
    def test_wrapper_default_params(self):
        """Test that the wrapper returns correct default parameters."""
        wrapper = SQAWrapper(self.bqm, self.seed)
        params = wrapper.get_default_params()
        
        # Check that we have the expected parameters
        self.assertIn('num_reads', params)
        self.assertIn('num_sweeps', params)
        self.assertIn('beta', params)
        self.assertIn('P', params)
        
        # Check the default values
        self.assertEqual(params['num_reads'], 100)
        self.assertEqual(params['num_sweeps'], 1000)
        self.assertEqual(params['beta'], 5.0)
        self.assertEqual(params['P'], 32)

if __name__ == '__main__':
    unittest.main()