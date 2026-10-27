# Autonomous Agent Integration Guide

> Operational patterns and integration instructions for AI and autonomous software agents interacting with `pqblocks-qubo-bench`.

---

## 1. Package Purpose

`pqblocks-qubo-bench` provides standardized metrics, instance loaders, and baseline wrappers for benchmarking quantum-inspired optimization algorithms against classical solvers.

---

## 2. Key Modules & APIs

| Module | Core Function / Class | Usage |
|---|---|---|
| `pqblocks_qubo_bench.tts_engine` | `calculate_tts(runs, target_prob=0.99)` | Calculate statistical Time-to-Solution from timing/success tuples |
| `pqblocks_qubo_bench.gap` | `calculate_gap(e_found, e_ref)` | Compute percentage optimality gap relative to reference ground truth |
| `pqblocks_qubo_bench.loaders` | `load_instance(suite_name, instance_id)` | Load benchmark instances into `dimod.BinaryQuadraticModel` |
| `pqblocks_qubo_bench.cpsat_wrapper` | `CPSATWrapper(bqm, seed)` | Wrap Google OR-Tools CP-SAT as a baseline solver |
| `pqblocks_qubo_bench.batch` | `run_batch(config_dict)` | Orchestrate batch benchmark runs across multiple instances |

---

## 3. Best Practices for Agents

1. **Deterministic Seeds**: Always supply explicit integer seeds (`seed=42`) when initializing wrappers to ensure bit-identical reproducibility.
2. **Handle Near-Zero Reference Energies**: Always use `calculate_gap` rather than manually calculating `(e_found - e_ref) / e_ref`; `calculate_gap` safely handles division by near-zero reference bounds.
3. **Format Support**: When loading instances, supported suite names include `'gset'`, `'biqmac'`, `'qplib'`, `'tsplib'`, `'orlib'`, and `'planted'`.
4. **Equal-Work Comparisons**: When reporting performance comparisons between algorithms, verify that total sweeps, read counts, and iteration budgets are documented.
