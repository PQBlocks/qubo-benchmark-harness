import numpy as np

class SimulatedQuantumAnnealingSampler:
    """
    A sampler for Simulated Quantum Annealing (SQA) that handles input validation
    and matrix normalization as per the specification.
    """
    
    def sample_ising(self, h, J, num_sweeps=1000, beta=5.0, gamma_0=None, gamma_f=1e-8, P=32):
        """
        Sample from an Ising model using Simulated Quantum Annealing.
        
        Parameters:
        - h: array-like, shape (N,) - Local field values.
        - J: array-like, shape (N, N) - Coupling matrix.
        - num_sweeps: int - Number of sweeps (default: 1000).
        - beta: float - Inverse temperature (default: 5.0).
        - gamma_0: float - Initial transverse field (default: auto-derived).
        - gamma_f: float - Final transverse field (default: 1e-8).
        - P: int - Number of Trotter replicas (default: 32).
        
        Returns:
        - samples: array, shape (num_samples, N) - Sampled spin states.
        - energies: array, shape (num_samples,) - Energies of sampled states.
        """
        # Handle single spin case immediately
        N = len(h)
        if N == 1:
            # Bypass Trotter matrix allocation overhead
            optimal_state = np.sign(-h[0])
            # Return the trivial optimal state
            return np.array([[optimal_state]]), np.array([h[0] * optimal_state])
        
        # For N > 1, we need to validate inputs first
        # Input validation
        h, J = self._validate_inputs(h, J, num_sweeps)
        
        # Matrix normalization
        J_upper = np.triu(J, k=1)
        J_sym = J_upper + J_upper.T
        
        # Auto-derive gamma_0 if not provided
        if gamma_0 is None:
            gamma_0 = 1.1 * np.max(np.abs(h) + np.sum(np.abs(J_sym), axis=1))
        
        # Initialize the spin states for all replicas
        s = np.random.choice([-1, 1], size=(P, N))
        
        # Run the SQA algorithm using the JIT-compiled kernel
        # We need to import the kernel function here to avoid circular imports
        try:
            from .sqa_kernel import _sqa_kernel_inner_loop
            s = _sqa_kernel_inner_loop(s, h, J_sym, num_sweeps, beta, gamma_0, gamma_f, P)
        except ImportError:
            # If relative import fails, try absolute import
            try:
                from sqa_kernel import _sqa_kernel_inner_loop
                s = _sqa_kernel_inner_loop(s, h, J_sym, num_sweeps, beta, gamma_0, gamma_f, P)
            except ImportError:
                # If both imports fail, use the pure-Python reference implementation
                s = self._sqa_inner_loop(s, h, J_sym, num_sweeps, beta, gamma_0, gamma_f, P)
        
        # For now, we'll just return the final state of the first replica
        # In a full implementation, we might want to sample from all replicas
        final_samples = s[0:1, :]  # Shape (1, N)
        final_energies = np.array([self._calculate_energy(final_samples[0], h, J_sym)])
        
        return final_samples, final_energies
    
    def _sqa_inner_loop(self, s, h, J_sym, num_sweeps, beta, gamma_0, gamma_f, P):
        """
        Pure-Python reference implementation of the SQA inner loop.
        """
        N = s.shape[1]
        
        for t in range(num_sweeps):
            # Calculate current gamma
            gamma_t = max(gamma_0 * (1 - t / num_sweeps), gamma_f)
            
            # Calculate J_perp with safeguard
            x = (beta * gamma_t) / P
            x = max(x, 1e-15)  # Clamp to prevent ln(0)
            J_perp = -0.5 * np.log(np.tanh(x)) / beta
            
            # Sequential sweep over replicas and spins
            for k in range(P):
                for i in range(N):
                    # Calculate delta_E_prob
                    local_field = h[i] + np.dot(J_sym[i], s[k])
                    delta_E_prob = -2 * s[k, i] * local_field
                    
                    # Calculate delta_H_trotter
                    s_prev = s[(k-1) % P, i]
                    s_next = s[(k+1) % P, i]
                    delta_H_trotter = 2 * J_perp * s[k, i] * (s_prev + s_next)
                    
                    # Calculate delta_S
                    delta_S = (beta / P) * delta_E_prob + beta * delta_H_trotter
                    
                    # Metropolis acceptance
                    if delta_S <= 0:
                        s[k, i] *= -1
                    else:
                        # Only evaluate exp(-delta_S) if delta_S > 0
                        # This prevents overflow
                        if np.random.random() < np.exp(-delta_S):
                            s[k, i] *= -1
        
        return s
    
    def _calculate_energy(self, state, h, J_sym):
        """
        Calculate the energy of a state.
        """
        energy = np.dot(h, state)
        energy += 0.5 * np.dot(state, np.dot(J_sym, state))
        return energy
    
    def _validate_inputs(self, h, J, num_sweeps):
        """
        Validate inputs according to the Edge-Case Ledger.
        """
        # Convert to numpy arrays for easier handling
        h = np.asarray(h, dtype=np.float64)
        J = np.asarray(J, dtype=np.float64)
        
        # 1. Empty Input: N=0
        if len(h) == 0:
            raise ValueError("Empty input: h must not be empty (N=0).")
        
        # 2. Dimension Mismatch
        if len(h) != J.shape[0] or J.shape[0] != J.shape[1]:
            raise ValueError(f"Dimension mismatch: len(h)={len(h)}, J.shape={J.shape}. "
                             "J must be a square matrix with dimensions matching len(h).")
        
        # 3. NaN / Inf
        if not np.isfinite(h).all() or not np.isfinite(J).all():
            raise ValueError("NaN or Inf values detected in h or J. All values must be finite.")
        
        # 4. Negative/Zero Sweeps
        if num_sweeps <= 0:
            raise ValueError(f"Negative or zero sweeps: num_sweeps={num_sweeps}. Must be positive.")
        
        # Return validated arrays
        return h, J