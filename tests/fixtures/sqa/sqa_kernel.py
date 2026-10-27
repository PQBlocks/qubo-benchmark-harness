import numpy as np
from numba import njit

# Define constants for clamping
MIN_EXP_INPUT = -709.0
MAX_EXP_INPUT = 709.0

@njit(nopython=True, fastmath=True)
def _sqa_kernel_inner_loop(s, h, J_sym, num_sweeps, beta, gamma_0, gamma_f, P):
    """
    Numba JIT-compiled implementation of the SQA inner loop.
    
    Parameters:
    - s: array, shape (P, N) - Initial spin states for all replicas.
    - h: array, shape (N,) - Local field values.
    - J_sym: array, shape (N, N) - Symmetric coupling matrix.
    - num_sweeps: int - Number of sweeps.
    - beta: float - Inverse temperature.
    - gamma_0: float - Initial transverse field.
    - gamma_f: float - Final transverse field.
    - P: int - Number of Trotter replicas.
    
    Returns:
    - s: array, shape (P, N) - Final spin states for all replicas.
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
                # Using a manual loop for dot product to ensure float64 precision
                local_field = h[i]
                for j in range(N):
                    local_field += J_sym[i, j] * s[k, j]
                
                delta_E_prob = -2.0 * s[k, i] * local_field
                
                # Calculate delta_H_trotter
                s_prev = s[(k-1) % P, i]
                s_next = s[(k+1) % P, i]
                delta_H_trotter = 2.0 * J_perp * s[k, i] * (s_prev + s_next)
                
                # Calculate delta_S
                delta_S = (beta / P) * delta_E_prob + beta * delta_H_trotter
                
                # Metropolis acceptance
                if delta_S <= 0.0:
                    s[k, i] *= -1
                else:
                    # Clamp delta_S to prevent overflow in exp
                    clamped_delta_S = min(max(-delta_S, MIN_EXP_INPUT), MAX_EXP_INPUT)
                    # Only evaluate exp(-delta_S) if delta_S > 0
                    # This prevents overflow
                    if np.random.random() < np.exp(clamped_delta_S):
                        s[k, i] *= -1
    
    return s