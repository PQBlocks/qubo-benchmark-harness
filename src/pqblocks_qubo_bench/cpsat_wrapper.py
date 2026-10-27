"""
CP-SAT solver wrapper for benchmark harness.
"""

import os
import sys
import dimod
from .base import BaselineWrapper
from ortools.sat.python import cp_model
import numpy as np

_this_dir = os.path.dirname(os.path.abspath(__file__))
_bench_harness_src = os.path.dirname(_this_dir)
if _bench_harness_src not in sys.path:
    sys.path.insert(0, _bench_harness_src)


class CPSATWrapper(BaselineWrapper):
    """
    Wrapper for Google OR-Tools CP-SAT solver.
    """

    def __init__(self, bqm: dimod.BinaryQuadraticModel, seed: int):
        """
        Initialize with problem and deterministic seed.
        
        Args:
            bqm: The binary quadratic model to solve
            seed: Deterministic seed for reproducibility
        """
        super().__init__(bqm, seed)
        # Convert to BINARY vartype if needed
        self.binary_bqm = self.bqm.change_vartype(dimod.BINARY, inplace=False)

    def sample(self, **parameters) -> dimod.SampleSet:
        """
        Execute CP-SAT solver and return SampleSet with energies, samples, timing info.
        
        Args:
            **parameters: Algorithm-specific parameters
                - max_time: Time limit in seconds (default: 30)
                - num_workers: Number of search workers/threads (default: 4)
                
        Returns:
            dimod.SampleSet with solutions and timing information
        """
        # Get parameters with defaults
        max_time = parameters.get('max_time', 30)
        num_workers = parameters.get('num_workers', 4)
        
        # Create CP-SAT model
        model = cp_model.CpModel()
        
        # Create boolean variables for each BQM variable
        x = {v: model.NewBoolVar(str(v)) for v in self.binary_bqm.variables}
        
        # Calculate dynamic scaling factor based on minimum absolute non-zero coefficient
        all_coeffs = []
        for coeff in self.binary_bqm.linear.values():
            if coeff != 0:
                all_coeffs.append(abs(coeff))
        for coeff in self.binary_bqm.quadratic.values():
            if coeff != 0:
                all_coeffs.append(abs(coeff))
        
        # Determine scaling factor to prevent precision loss
        if all_coeffs:
            min_abs_coeff = min(all_coeffs)
            # Calculate scaling factor to ensure smallest coefficient is at least 1e-6 after scaling
            scaling_factor = max(1, 10**6 / min_abs_coeff) if min_abs_coeff < 10**-6 else 10**6
        else:
            scaling_factor = 10**6  # Default scaling factor if no non-zero coefficients
        
        # Linear terms
        linear_terms = []
        for var, coeff in self.binary_bqm.linear.items():
            int_coeff = int(coeff * scaling_factor)
            linear_terms.append(int_coeff * x[var])
        
        # Quadratic terms - need to linearize
        quadratic_terms = []
        y_vars = {}  # auxiliary variables for linearization
        
        for (i, j), coeff in self.binary_bqm.quadratic.items():
            int_coeff = int(coeff * scaling_factor)
            
            # Create auxiliary variable for x_i * x_j
            y_var = model.NewBoolVar(f'y_{i}_{j}')
            y_vars[(i, j)] = y_var
            
            # Add linearization constraints
            # y_ij <= x_i
            model.Add(y_var <= x[i])
            # y_ij <= x_j
            model.Add(y_var <= x[j])
            # y_ij >= x_i + x_j - 1
            model.Add(y_var >= x[i] + x[j] - 1)
            
            # Add to quadratic terms
            quadratic_terms.append(int_coeff * y_var)
        
        # Objective: minimize sum of linear and quadratic terms
        if linear_terms or quadratic_terms:
            model.Minimize(sum(linear_terms) + sum(quadratic_terms))
        
        # Create solver and set parameters
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_time
        solver.parameters.num_search_workers = num_workers
        solver.parameters.random_seed = self.seed
        
        # Solve
        status = solver.Solve(model)
        
        # Get solution
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            solution_dict = {v: solver.Value(x[v]) for v in self.binary_bqm.variables}
            
            # Convert back to original vartype if needed
            if self.bqm.vartype == dimod.SPIN:
                sample = {v: 2 * solution_dict[v] - 1 for v in self.bqm.variables}
            else:
                sample = solution_dict
            
            # Calculate energy using original BQM
            energy = self.bqm.energy(sample)
            
            # Store timing and parameters in info
            info = {
                'max_time': max_time,
                'num_workers': num_workers,
                'status': status,
                'wall_time': solver.WallTime(),
                'user_time': solver.UserTime(),
                'deterministic_time': solver.deterministic_time,
                'scaling_factor': scaling_factor  # Include scaling factor in info for debugging
            }
            
            # Return SampleSet
            return dimod.SampleSet.from_samples(
                [sample], 
                vartype=self.bqm.vartype, 
                energy=[energy],
                info=info
            )
        else:
            # No solution found
            # Return empty SampleSet with appropriate info
            info = {
                'max_time': max_time,
                'num_workers': num_workers,
                'status': status,
                'wall_time': solver.WallTime(),
                'user_time': solver.UserTime(),
                'deterministic_time': solver.deterministic_time,
                'scaling_factor': scaling_factor  # Include scaling factor in info for debugging
            }
            
            # Create an empty sample set
            return dimod.SampleSet.from_samples(
                [], 
                vartype=self.bqm.vartype,
                energy=[],
                info=info
            )

    def get_default_params(self) -> dict:
        """
        Return hyperparameter dictionary.
        
        Returns:
            Dictionary of default parameters for the solver
        """
        return {
            'max_time': 30,
            'num_workers': 4
        }