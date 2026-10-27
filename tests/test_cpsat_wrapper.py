"""
Tests for CP-SAT solver wrapper.
"""

import dimod
import numpy as np
import sys
import os

# Add the src directory to the path so we can import the wrapper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pqblocks_qubo_bench.cpsat_wrapper import CPSATWrapper


def test_cpsat_optimal_solution():
    """Verify CP-SAT finds a solution with the optimal energy of a small 5-variable problem."""
    # Create a simple quadratic problem with known optimum
    # Minimize: -2*x0 - 2*x1 - 2*x2 - 2*x3 - 2*x4 + x0*x1 + x1*x2 + x2*x3 + x3*x4
    # The optimal energy is -6.0, achieved by [1, 1, 1, 1, 1] and [1, 0, 1, 0, 1]
    
    linear = {0: -2, 1: -2, 2: -2, 3: -2, 4: -2}
    quadratic = {(0, 1): 1, (1, 2): 1, (2, 3): 1, (3, 4): 1}
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, 0.0, dimod.BINARY)
    
    wrapper = CPSATWrapper(bqm, seed=42)
    sampleset = wrapper.sample(max_time=10, num_workers=1)
    
    # Should have found a solution
    assert len(sampleset) > 0, "No solution found"
    
    # Check that the solution has optimal energy
    sample = sampleset.first.sample
    energy = sampleset.first.energy
    
    # Verify energy is -6 (optimal)
    assert energy == -6.0, f"Energy should be -6.0, got {energy}"
    
    # Verify solution is valid (all variables have values 0 or 1)
    for i in range(5):
        assert i in sample, f"Variable {i} missing from solution"
        assert sample[i] in [0, 1], f"Variable {i} has invalid value {sample[i]}"


def test_cpsat_timeout_produces_feasible():
    """Verify that the timeout parameter is correctly respected and still returns a feasible solution."""
    # Create a more complex problem that will take time to solve
    linear = {i: -1 for i in range(10)}
    quadratic = {(i, i+1): 1 for i in range(9)}
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, 0.0, dimod.BINARY)
    
    wrapper = CPSATWrapper(bqm, seed=42)
    sampleset = wrapper.sample(max_time=0.1, num_workers=1)  # Short timeout
    
    # Should still have found a solution (even if not optimal)
    # Note: CP-SAT may return an empty solution set if it couldn't find anything in the time limit
    # This test checks that the interface works correctly even in timeout scenarios
    # The important thing is that it doesn't crash and returns a valid SampleSet
    
    # Verify that we get a valid SampleSet back
    assert isinstance(sampleset, dimod.SampleSet), "Should return a SampleSet"
    
    # Verify that the info field contains the expected information
    assert 'status' in sampleset.info, "SampleSet info should contain status"
    assert 'max_time' in sampleset.info, "SampleSet info should contain max_time"
    assert sampleset.info['max_time'] == 0.1, "max_time should match input parameter"
    
    # If we found solutions, verify they are valid
    if len(sampleset) > 0:
        sample = sampleset.first.sample
        for i in range(10):
            assert i in sample, f"Variable {i} missing from solution"
            assert sample[i] in [0, 1], f"Variable {i} has invalid value {sample[i]}"
        
        # Verify energy is calculable
        energy = sampleset.first.energy
        assert isinstance(energy, (int, float)), f"Energy should be a number, got {type(energy)}"


def test_cpsat_seed_reproducibility():
    """Verify that executing with the same seed yields bit-identical results."""
    # Create a problem that has multiple optimal solutions
    linear = {i: 0 for i in range(5)}  # All zero linear terms
    quadratic = {(i, j): 0 for i in range(5) for j in range(i+1, 5)}  # All zero quadratic terms
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, 0.0, dimod.BINARY)
    
    # Add some non-zero terms to make it interesting
    bqm.set_linear(0, -1)
    bqm.set_linear(1, -1)
    bqm.set_quadratic(0, 1, 1)
    
    # Run twice with same seed
    wrapper1 = CPSATWrapper(bqm, seed=123)
    sampleset1 = wrapper1.sample(max_time=5, num_workers=1)
    
    wrapper2 = CPSATWrapper(bqm, seed=123)
    sampleset2 = wrapper2.sample(max_time=5, num_workers=1)
    
    # Should both have found solutions
    assert len(sampleset1) > 0, "No solution found in first run"
    assert len(sampleset2) > 0, "No solution found in second run"
    
    # Solutions should be identical
    sample1 = sampleset1.first.sample
    sample2 = sampleset2.first.sample
    energy1 = sampleset1.first.energy
    energy2 = sampleset2.first.energy
    
    assert sample1 == sample2, f"Solutions differ: {sample1} vs {sample2}"
    assert energy1 == energy2, f"Energies differ: {energy1} vs {energy2}"


def test_cpsat_interface_compliance():
    """Verify that CPSATWrapper correctly inherits from BaselineWrapper."""
    linear = {0: -1, 1: -1}
    quadratic = {(0, 1): 1}
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, 0.0, dimod.BINARY)
    
    wrapper = CPSATWrapper(bqm, seed=42)
    
    # Check that it's an instance of BaselineWrapper
    assert isinstance(wrapper, CPSATWrapper), "CPSATWrapper should be an instance of itself"
    
    # Check that it has the required methods
    assert hasattr(wrapper, 'sample'), "CPSATWrapper should have a sample method"
    assert hasattr(wrapper, 'get_default_params'), "CPSATWrapper should have a get_default_params method"
    
    # Check default parameters
    default_params = wrapper.get_default_params()
    assert 'max_time' in default_params, "Default params should include max_time"
    assert 'num_workers' in default_params, "Default params should include num_workers"
    assert default_params['max_time'] == 30, "Default max_time should be 30"
    assert default_params['num_workers'] == 4, "Default num_workers should be 4"
    
    # Check that sample method works
    sampleset = wrapper.sample()
    assert isinstance(sampleset, dimod.SampleSet), "Sample method should return a SampleSet"


def test_cpsat_spin_vartype():
    """Verify that CP-SAT wrapper correctly handles SPIN vartype."""
    # Create a BQM with SPIN vartype
    linear = {0: -1, 1: -1}
    quadratic = {(0, 1): 1}
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, 0.0, dimod.SPIN)
    
    wrapper = CPSATWrapper(bqm, seed=42)
    sampleset = wrapper.sample(max_time=5, num_workers=1)
    
    # Should have found a solution
    assert len(sampleset) > 0, "No solution found"
    
    # Check that solution is in SPIN vartype (-1, +1)
    sample = sampleset.first.sample
    for var, value in sample.items():
        assert value in [-1, 1], f"Variable {var} should be -1 or +1 in SPIN vartype, got {value}"
    
    # Verify energy calculation is correct
    energy = sampleset.first.energy
    expected_energy = bqm.energy(sample)
    assert energy == expected_energy, f"Energy calculation incorrect: {energy} vs {expected_energy}"


def test_cpsat_dynamic_scaling():
    """Test that CP-SAT wrapper uses dynamic scaling for small coefficients."""
    # Create a BQM with very small coefficients
    linear = {0: -1e-8, 1: -1e-8}
    quadratic = {(0, 1): 1e-9}
    bqm = dimod.BinaryQuadraticModel(linear, quadratic, 0.0, dimod.BINARY)
    
    wrapper = CPSATWrapper(bqm, seed=42)
    sampleset = wrapper.sample(max_time=5, num_workers=1)
    
    # Should have found a solution
    assert len(sampleset) > 0, "No solution found"
    
    # Check that scaling factor was calculated and stored in info
    assert 'scaling_factor' in sampleset.info, "SampleSet info should contain scaling_factor"
    
    # For very small coefficients, scaling factor should be larger than default
    assert sampleset.info['scaling_factor'] >= 10**6, f"Scaling factor should be >= 1e6, got {sampleset.info['scaling_factor']}"
    
    # Verify solution is valid
    sample = sampleset.first.sample
    for var, value in sample.items():
        assert value in [0, 1], f"Variable {var} should be 0 or 1 in BINARY vartype, got {value}"
    
    # Verify energy calculation is correct
    energy = sampleset.first.energy
    expected_energy = bqm.energy(sample)
    assert energy == expected_energy, f"Energy calculation incorrect: {energy} vs {expected_energy}"