# Benchmarks & Performance Verification

> Measured performance, throughput metrics, and evaluation methodology for `pqblocks-qubo-bench`.

---

> [!NOTE]
> **Domain Classification**: Quantum-inspired classical optimisation: not cryptography, no security claim.

---

## 1. Metric Evaluation Engine Benchmarks

Measurements conducted on Linux x86_64 using Python 3.14.8 (`numba 0.61.0`, `numpy 2.2.0`). All measurements reflect real wall-clock executions over 50,000 continuous iterations.

| Operation | Microseconds / Op | Throughput (ops/sec) | Description |
|---|---|---|---|
| `calculate_tts` | 5.92 µs | 168,833 ops/sec | Statistical Time-to-Solution calculation with 99% target probability |
| `calculate_gap` | 0.16 µs | 6,339,211 ops/sec | Reference optimality gap evaluation with zero-division handling |
| `load_instance` | 13.36 µs | 74,851 ops/sec | Standard instance loader lookup and BQM instantiation |

---

## 2. Time-To-Solution (TTS) Methodology

Time-to-Solution evaluates the expected computational time required for a stochastic heuristic solver to discover an optimal or target solution with high confidence ($P_{\text{target}}$, typically 99%):

$$\text{TTS} = \tau_{\text{run}} \cdot \frac{\ln(1 - P_{\text{target}})}{\ln(1 - P_{\text{succ}})}$$

Where:
- $\tau_{\text{run}}$: Mean or median runtime of a single solver execution.
- $P_{\text{succ}}$: Empirical success probability (fraction of runs reaching the ground truth or threshold energy).
- $P_{\text{target}}$: Desired target confidence (default: 0.99).

If no runs reach the target, `calculate_tts` gracefully returns infinity ($\infty$) or handles zero-variance runs without raising numerical exceptions.

---

## 3. Equal-Work Benchmarking Guidelines

A common pitfall in quantum-inspired benchmark comparisons is contrasting unequal computational work (e.g., comparing 1 read of an algorithm against 100 reads of another, or comparing wall-clock time on mismatched GPU vs CPU hardware).

`pqblocks-qubo-bench` enforces standard reporting rules:
1. **Work Normalization**: State total sweeps, Trotter replicas, and read counts for all annealing solvers.
2. **Deterministic Seeds**: All wrapper runs record an explicit integer seed (`seed=42`) for bit-level reproducibility where supported.
3. **Hardware Disclosure**: State CPU architecture, core count, SIMD vectorization, and BLAS backend.

---

## 4. Reproducing the Measurements

To reproduce these microbenchmarks:

```bash
python3 -c "
import time
from pqblocks_qubo_bench.tts_engine import calculate_tts
from pqblocks_qubo_bench.gap import calculate_gap
from pqblocks_qubo_bench.loaders import load_instance

runs = [(0.012, True), (0.015, False), (0.011, True), (0.014, True)]
N = 50000

t0 = time.perf_counter()
for _ in range(N):
    calculate_tts(runs, 0.99)
print(f'calculate_tts: {((time.perf_counter()-t0)/N)*1e6:.2f} us')

t0 = time.perf_counter()
for _ in range(N):
    calculate_gap(-5.0, -6.0)
print(f'calculate_gap: {((time.perf_counter()-t0)/N)*1e6:.2f} us')

N_load = 5000
t0 = time.perf_counter()
for _ in range(N_load):
    load_instance('gset', 'G1')
print(f'load_instance: {((time.perf_counter()-t0)/N_load)*1e6:.2f} us')
"
```
