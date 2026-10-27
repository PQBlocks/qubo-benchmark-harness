"""Unit tests for the benchmark harness loaders module."""

import unittest
import dimod
from pqblocks_qubo_bench.loaders.gset_loader import load_gset_instance
from pqblocks_qubo_bench.loaders.biqmac_loader import load_biqmac_instance
from pqblocks_qubo_bench.loaders.qplib_loader import load_qplib_instance
from pqblocks_qubo_bench.loaders.tsplib_loader import load_tsplib_instance
from pqblocks_qubo_bench.loaders.orlib_loader import load_orlib_instance
from pqblocks_qubo_bench.loaders.planted_loader import load_planted_instance
from pqblocks_qubo_bench.loaders.loader import load_instance


class TestLoaders(unittest.TestCase):
    
    def test_gset_loader(self):
        """Test G-set loader with valid input."""
        bqm, metadata = load_gset_instance('gset', 'G1')
        
        # Check that we got a valid BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.vartype, dimod.BINARY)
        
        # Check metadata
        self.assertEqual(metadata['suite_name'], 'gset')
        self.assertEqual(metadata['instance_id'], 'G1')
        self.assertEqual(metadata['num_variables'], 5)
        self.assertEqual(metadata['format'], 'G1.txt')
        
        # Check BQM properties
        self.assertGreaterEqual(len(bqm.variables), 2)
        # Note: This BQM has quadratic terms, so it's not linear
        
    def test_biqmac_loader(self):
        """Test Biq Mac loader with valid input."""
        bqm, metadata = load_biqmac_instance('biqmac', 'biqmac_100_50_1')
        
        # Check that we got a valid BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.vartype, dimod.BINARY)
        
        # Check metadata
        self.assertEqual(metadata['suite_name'], 'biqmac')
        self.assertEqual(metadata['instance_id'], 'biqmac_100_50_1')
        self.assertEqual(metadata['num_variables'], 4)
        self.assertEqual(metadata['format'], '.bq')
        
        # Check BQM properties
        self.assertGreaterEqual(len(bqm.variables), 2)
        
    def test_qplib_loader(self):
        """Test QPLIB loader with valid input."""
        bqm, metadata = load_qplib_instance('qplib', 'test_instance')
        
        # Check that we got a valid BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.vartype, dimod.BINARY)
        
        # Check metadata
        self.assertEqual(metadata['suite_name'], 'qplib')
        self.assertEqual(metadata['instance_id'], 'test_instance')
        self.assertEqual(metadata['num_variables'], 3)
        self.assertEqual(metadata['format'], 'XML')
        
        # Check BQM properties
        self.assertGreaterEqual(len(bqm.variables), 2)
        
    def test_tsplib_loader(self):
        """Test TSPLIB loader with valid input."""
        bqm, metadata = load_tsplib_instance('tsplib', 'test_instance')
        
        # Check that we got a valid BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.vartype, dimod.BINARY)
        
        # Check metadata
        self.assertEqual(metadata['suite_name'], 'tsplib')
        self.assertEqual(metadata['instance_id'], 'test_instance')
        self.assertEqual(metadata['num_variables'], 4)
        self.assertEqual(metadata['format'], 'TSPLIB')
        
        # Check BQM properties
        self.assertGreaterEqual(len(bqm.variables), 2)
        
    def test_orlib_loader(self):
        """Test OR-Library loader with valid input."""
        bqm, metadata = load_orlib_instance('orlib', 'test_instance')
        
        # Check that we got a valid BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.vartype, dimod.BINARY)
        
        # Check metadata
        self.assertEqual(metadata['suite_name'], 'orlib')
        self.assertEqual(metadata['instance_id'], 'test_instance')
        self.assertEqual(metadata['num_variables'], 5)
        self.assertEqual(metadata['format'], 'portfolio')
        
        # Check BQM properties
        self.assertGreaterEqual(len(bqm.variables), 2)
        
    def test_planted_loader(self):
        """Test Planted/Chook loader with valid input."""
        bqm, metadata = load_planted_instance('planted', 'planted_100_2D_10')
        
        # Check that we got a valid BQM
        self.assertIsInstance(bqm, dimod.BinaryQuadraticModel)
        self.assertEqual(bqm.vartype, dimod.BINARY)
        
        # Check metadata
        self.assertEqual(metadata['suite_name'], 'planted')
        self.assertEqual(metadata['instance_id'], 'planted_100_2D_10')
        self.assertEqual(metadata['num_variables'], 6)
        self.assertEqual(metadata['format'], 'JSONL')
        
        # Check BQM properties
        self.assertGreaterEqual(len(bqm.variables), 2)
        
    def test_loader_dispatch(self):
        """Test main loader dispatch function."""
        # Test G-set dispatch
        bqm, metadata = load_instance('gset', 'G1')
        self.assertEqual(metadata['suite_name'], 'gset')
        
        # Test Biq Mac dispatch
        bqm, metadata = load_instance('biqmac', 'biqmac_100_50_1')
        self.assertEqual(metadata['suite_name'], 'biqmac')
        
        # Test QPLIB dispatch
        bqm, metadata = load_instance('qplib', 'test_instance')
        self.assertEqual(metadata['suite_name'], 'qplib')
        
        # Test TSPLIB dispatch
        bqm, metadata = load_instance('tsplib', 'test_instance')
        self.assertEqual(metadata['suite_name'], 'tsplib')
        
        # Test OR-Library dispatch
        bqm, metadata = load_instance('orlib', 'test_instance')
        self.assertEqual(metadata['suite_name'], 'orlib')
        
        # Test Planted dispatch
        bqm, metadata = load_instance('planted', 'planted_100_2D_10')
        self.assertEqual(metadata['suite_name'], 'planted')
        
    def test_loader_invalid_suite(self):
        """Test loader with invalid suite name."""
        with self.assertRaises(ValueError):
            load_instance('invalid_suite', 'test_instance')
            
    def test_gset_loader_invalid_suite_name(self):
        """Test G-set loader with invalid suite name."""
        with self.assertRaises(ValueError):
            load_gset_instance('invalid', 'G1')
            
    def test_biqmac_loader_invalid_suite_name(self):
        """Test Biq Mac loader with invalid suite name."""
        with self.assertRaises(ValueError):
            load_biqmac_instance('invalid', 'biqmac_100_50_1')
            
    def test_planted_loader_invalid_suite_name(self):
        """Test Planted loader with invalid suite name."""
        with self.assertRaises(ValueError):
            load_planted_instance('invalid', 'planted_100_2D_10')
            
    def test_gset_loader_invalid_instance_id(self):
        """Test G-set loader with invalid instance ID format."""
        with self.assertRaises(ValueError):
            load_gset_instance('gset', 'invalid_id')
            
    def test_planted_loader_invalid_instance_id(self):
        """Test Planted loader with invalid instance ID format."""
        with self.assertRaises(ValueError):
            load_planted_instance('planted', 'invalid_id')


if __name__ == '__main__':
    unittest.main()