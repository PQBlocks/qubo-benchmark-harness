# Use Cases & Integration Patterns

> Practical applications and integration scenarios for `pqblocks-qubo-bench`.

---

## 1. Comparing Quantum-Inspired Solvers Against Classical Baselines

Researchers developing quantum-inspired classical heuristics (such as Simulated Bifurcation, Simulated Annealing, or Quantum Annealing) require standard, un-skewed comparisons against established solvers.

### Workflow:
1. Load a target problem instance via `load_instance("gset", "G1")`.
2. Execute the heuristic solver with a fixed random seed.
3. Execute classical baselines (e.g. `CPSATWrapper` or `NealWrapper`) under comparable computational budgets.
4. Calculate relative optimality gaps using `calculate_gap(e_solver, e_best_known)`.

---

## 2. Rigorous Time-to-Solution (TTS) Benchmarking

In stochastic optimization, a single fast run that rarely reaches the optimum is less useful than a solver that reliably finds the optimum. Time-to-Solution penalizes algorithms with low success probabilities by projecting total time required to achieve 99% confidence:

```python
from pqblocks_qubo_bench.tts_engine import calculate_tts

# Collect wall-clock runtime and ground-truth hit flags across 100 trials
solver_trials = [(0.021, True), (0.019, False), (0.022, True), (0.020, False)]

# Project expected wall-clock time required for 99% success confidence
tts_99 = calculate_tts(solver_trials, target_prob=0.99)
print(f"Projected 99% TTS: {tts_99:.4f}s")
```

---

## 3. Standard Benchmark Instance Ingestion

Industrial and academic optimization problems frequently follow diverse standard formats (Stanford G-set graph lists, BiqMac matrices, QPLIB quadratic programs). `pqblocks_qubo_bench.loaders` standardizes ingestion into `dimod.BinaryQuadraticModel`:

```python
from pqblocks_qubo_bench.loaders import load_instance

# Load standard benchmark problem
bqm, metadata = load_instance("gset", "G1")
print(f"Parsed {metadata['instance_id']} ({len(bqm.variables)} nodes)")
```

---

## 4. Continuous Integration & Solver Regression Testing

Optimization packages can integrate `pqblocks-qubo-bench` into GitHub Actions or automated test suites to ensure that algorithmic changes, compiler flags (e.g. Numba JIT), or matrix updates do not degrade convergence probability or runtime performance.
