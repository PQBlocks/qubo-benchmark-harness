"""
MQLib baseline wrapper for benchmark harness.
"""

import dimod
import numpy as np
import subprocess
import time
import os
import tempfile
from typing import Dict, Any
from .base import BaselineWrapper


class MQLibWrapper(BaselineWrapper):
    """
    Wrapper for MQLib heuristic solver.
    """

    def __init__(self, bqm: dimod.BinaryQuadraticModel, seed: int):
        """
        Initialize with problem and deterministic seed.
        
        Args:
            bqm: The binary quadratic model to solve
            seed: Deterministic seed for reproducibility
            
        Raises:
            ValueError: If the BQM is empty (0 variables)
        """
        # Validate that BQM is not empty
        if len(bqm.variables) == 0:
            raise ValueError("BQM cannot be empty (0 variables)")
        
        # Store the original SPIN BQM for energy evaluation
        self.original_bqm_spin = bqm.copy()
        
        # Convert SPIN BQM to BINARY (QUBO) for MQLib
        # MQLib expects binary variables (0/1), not spin variables (-1/+1)
        if bqm.vartype == dimod.SPIN:
            # Convert SPIN to BINARY: s_i = 2*x_i - 1
            # Energy transformation: E_spin(s) = E_binary(x) + constant
            self.bqm_binary = bqm.copy()
            self.bqm_binary.change_vartype(dimod.BINARY, inplace=True)
            self.is_spin_problem = True
        else:
            self.bqm_binary = bqm.copy()
            self.is_spin_problem = False
            
        super().__init__(self.bqm_binary, seed)
        
        # Path to the MQLib executable
        env_mqlib = os.environ.get("MQLIB_PATH")
        candidates = [
            env_mqlib if env_mqlib else "",
            os.path.join(os.path.dirname(__file__), '..', '..', 'bin', 'MQLib'),
            os.path.join(os.getcwd(), 'bin', 'MQLib'),
            os.path.join(os.path.dirname(__file__), 'bin', 'MQLib'),
        ]
        self.mqlib_path = None
        for cand in candidates:
            if cand and os.path.exists(cand):
                self.mqlib_path = os.path.abspath(cand)
                break
        if not self.mqlib_path:
            raise FileNotFoundError("MQLib executable not found in bin/ or via MQLIB_PATH")
            
        # Store the original variable names for mapping back
        # Convert dimod Variables to list and sort with type-robust key to ensure consistent ordering
        self.original_variables = list(bqm.variables)
        self.original_variables.sort(key=lambda x: (str(type(x)), str(x)))

    def sample(self, **parameters) -> dimod.SampleSet:
        """
        Execute solver and return SampleSet with energies, samples, timing info.
        
        Args:
            **parameters: Algorithm-specific parameters
                - timeout: Time limit in seconds (default: 30)
                - heuristic_name: Name of the heuristic to use (default: "BURER2002")
                
        Returns:
            dimod.SampleSet with solutions and timing information
        """
        # Set default parameters if not provided
        timeout = parameters.get('timeout', 30)
        heuristic_name = parameters.get('heuristic_name', 'BURER2002')
        
        # Create a temporary file for the QUBO instance
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            qubo_file = f.name
            # Write the BQM in MQLib format
            self._write_qubo_file(f, self.bqm)
        
        try:
            # Execute MQLib with timing
            start_time = time.monotonic()
            
            # Run MQLib command
            cmd = [
                self.mqlib_path,
                '-fQ', qubo_file,
                '-h', heuristic_name,
                '-r', str(timeout),
                '-s', str(self.seed),
                '-ps'  # Print solution
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+10)
            end_time = time.monotonic()
            
            # Check if the command was successful
            if result.returncode != 0:
                raise RuntimeError(f"MQLib execution failed: {result.stderr}")
            
            # Parse the output and map back to original variable space
            binary_samples, binary_energy = self._parse_mqlib_output(result.stdout, self.original_variables)
            
            # If this was a SPIN problem, convert binary solution to SPIN and re-evaluate
            if self.is_spin_problem:
                # Convert binary (0/1) to spin (-1/+1): s = 2*x - 1
                spin_samples = {var: 2 * bit - 1 for var, bit in binary_samples.items()}
                
                # Re-evaluate energy using the original SPIN BQM (correct energy)
                # The binary energy from MQLib is not directly comparable
                # Create a sample dict for energy calculation
                sample_for_energy = spin_samples
                spin_energy = self.original_bqm_spin.energy(sample_for_energy)
                
                # Create a SampleSet with spin variables and correct energy
                sampleset = dimod.SampleSet.from_samples(spin_samples, vartype='SPIN', energy=spin_energy)
            else:
                # Binary problem - use MQLib energy directly
                sampleset = dimod.SampleSet.from_samples(binary_samples, vartype='BINARY', energy=binary_energy)
            
            # Add timing information
            timing_info = {
                'execution_time': end_time - start_time,
                'timeout': timeout,
                'heuristic_name': heuristic_name
            }
            sampleset.info.update(timing_info)
            
            return sampleset
            
        finally:
            # Clean up temporary file
            if os.path.exists(qubo_file):
                os.unlink(qubo_file)

    def get_default_params(self) -> Dict[str, Any]:
        """
        Return hyperparameter dictionary.
        
        Returns:
            Dictionary of default parameters for the solver
        """
        return {
            'timeout': 30,
            'heuristic_name': 'BURER2002'
        }
        
    def _write_qubo_file(self, file_handle, bqm: dimod.BinaryQuadraticModel):
        """
        Write the BQM to a file in MQLib QUBO format.
        
        MQLib MAXIMIZES QUBO problems, so we negate all coefficients to convert
        our minimization problem to a maximization problem.
        
        Args:
            file_handle: File handle to write to
            bqm: Binary quadratic model to write
        """
        # Get the quadratic and linear terms
        quadratic = bqm.quadratic
        linear = bqm.linear
        
        # Count the number of unique variables
        variables = set()
        for (u, v) in quadratic.keys():
            variables.add(u)
            variables.add(v)
        for v in linear.keys():
            variables.add(v)
            
        n = len(variables)
        # Sort variables with a type-robust key to handle mixed types (e.g., integers and strings)
        sorted_variables = sorted(variables, key=lambda x: (str(type(x)), str(x)))
        var_map = {v: i+1 for i, v in enumerate(sorted_variables)}  # MQLib uses 1-indexed variables
        
        # Count the number of data lines
        m = len(linear) + len(quadratic)
        
        # Write header
        file_handle.write(f"{n} {m}\n")
        
        # Write linear terms (NEGATED because MQLib maximizes)
        for v, bias in linear.items():
            idx = var_map[v]
            file_handle.write(f"{idx} {idx} {-bias}\n")  # NEGATE
            
        # Write quadratic terms (NEGATED because MQLib maximizes)
        for (u, v), bias in quadratic.items():
            u_idx = var_map[u]
            v_idx = var_map[v]
            # Only write upper triangular entries to avoid duplication
            if u_idx <= v_idx:
                file_handle.write(f"{u_idx} {v_idx} {-bias}\n")  # NEGATE
            else:
                file_handle.write(f"{v_idx} {u_idx} {-bias}\n")  # NEGATE
                
    def _parse_mqlib_output(self, output: str, original_variables):
        """
        Parse the output from MQLib.
        
        Args:
            output: String output from MQLib
            original_variables: List of original variable names in sorted order
            
        Returns:
            Tuple of (samples, energy)
        """
        lines = output.strip().split('\n')
        
        # Find the solution line (starts with a number)
        solution_line = None
        for line in lines:
            if line.strip() and line[0].isdigit():
                solution_line = line
                break
                
        if not solution_line:
            raise ValueError("Could not find solution in MQLib output")
            
        # Parse the solution line
        parts = solution_line.split(',')
        if len(parts) < 5:
            raise ValueError("Unexpected MQLib output format")
            
        # The energy is the 4th field
        energy = float(parts[3])
        
        # Find the solution section
        solution_start = -1
        for i, line in enumerate(lines):
            if line.strip() == "Solution:":
                solution_start = i + 1
                break
                
        if solution_start == -1:
            raise ValueError("Could not find solution section in MQLib output")
            
        # Parse the solution
        solution_str = lines[solution_start].strip()
        solution_bits = [int(x) for x in solution_str.split()]
        
        # Convert back to original variable mapping
        if len(solution_bits) != len(original_variables):
            raise ValueError(f"Mismatch between solution length ({len(solution_bits)}) and number of variables ({len(original_variables)})")
            
        samples = {var: bit for var, bit in zip(original_variables, solution_bits)}
        
        return samples, energy