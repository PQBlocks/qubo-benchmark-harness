# pqblocks-qubo-bench

> Standardized benchmarking harness, instance loaders, and metric evaluators for quantum-inspired optimization algorithms and classical baseline solvers.

[![CI](https://github.com/PQBlocks/qubo-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/PQBlocks/qubo-bench/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

> [!NOTE]
> **Domain Classification**: Quantum-inspired classical optimisation: not cryptography, no security claim.

---

## Overview

`pqblocks-qubo-bench` is an evaluation harness and benchmark suite designed to compare quantum-inspired heuristic solvers (such as Simulated Bifurcation, Simulated Annealing, and Quantum Annealing) against established classical solvers (such as Google OR-Tools CP-SAT, MQLib, and D-Wave Neal).

It provides:
- **Time-to-Solution (TTS) Engine**: Statistically rigorous computation of Time-to-Solution at arbitrary target success probabilities (e.g. 99% confidence), accounting for run failure distributions and runtime variance.
- **Reference Optimality Gap**: Standardized percentage gap calculation between heuristic solutions and known ground-truth or reference bounds ($E_{\text{found}} - E_{\text{ref}}) / |E_{\text{ref}}|$.
- **Standard Benchmark Loaders**: Native loaders for standard benchmark suites including Stanford G-set, BiqMac, QPLIB, TSPLIB, OR-Library, and planted-solution instances.
- **Unified Solver Wrappers**: Baseline wrappers conforming to the dimod `BinaryQuadraticModel` interface for CP-SAT, OpenJij, D-Wave Neal, and MQLib.

---

## Installation

```bash
pip install pqblocks-qubo-bench
```

### Dependencies

Requires Python 3.11+, `dimod`, `numpy`, `PyYAML`, and `jsonschema`.
Optional solver baselines:
- `ortools` (Google CP-SAT solver)
- `dwave-neal` (Classical simulated annealing baseline)
- `openjij` (Simulated quantum annealing baseline)
- `MQLib` (External C++ Max-Cut heuristic solver, optional)

---

## Quickstart

```python
from pqblocks_qubo_bench.tts_engine import calculate_tts

# Timing data: list of (runtime_seconds, success_boolean) tuples
runs = [(0.012, True), (0.015, False), (0.011, True), (0.014, True)]

# Calculate Time-To-Solution for 99% target confidence
tts = calculate_tts(runs, target_prob=0.99)
print(f"Calculated TTS (99% target): {tts:.4f}s")
```

---

## Benchmark Instance Loading

Load standard problem instances directly into `dimod.BinaryQuadraticModel`:

```python
from pqblocks_qubo_bench.loaders import load_instance

# Load a benchmark problem (G-set, BiqMac, QPLIB, etc.)
bqm, meta = load_instance("gset", "G1")
print(f"Loaded {meta['instance_id']} from {meta['suite_name']} with {len(bqm.variables)} variables")
```

---

## Architecture and Subpackages

- `pqblocks_qubo_bench.tts_engine`: Core statistical engine for calculating Time-to-Solution and success probabilities.
- `pqblocks_qubo_bench.gap`: Relative and absolute reference gap calculations with zero-energy handling.
- `pqblocks_qubo_bench.loaders`: Standard benchmark loaders (`gset_loader`, `biqmac_loader`, `qplib_loader`, `tsplib_loader`, `orlib_loader`, `planted_loader`).
- `pqblocks_qubo_bench.cpsat_wrapper`: CP-SAT exact/heuristic baseline integration.
- `pqblocks_qubo_bench.mqlib_wrapper`: MQLib heuristic solver integration.
- `pqblocks_qubo_bench.sqa_wrapper`: Simulated Quantum Annealing benchmark wrapper.
- `pqblocks_qubo_bench.batch`: Batch benchmark execution and orchestration.

---

## Fair Benchmarking Disclaimer

When comparing heuristic solvers (such as Simulated Bifurcation or Simulated Annealing) against baseline solvers:
- Solvers must be compared under equal computational work (e.g., sample counts, read counts, and iteration budgets must be explicitly stated).
- Heuristic point solutions must report both mean energy, best energy, and Time-to-Solution (TTS).
- External baselines (MQLib, CP-SAT) must specify timeout and thread allocations.

---

## Verification & Testing

Every commit and release is verified across Python 3.11, 3.12, 3.13, and 3.14.

```bash
pytest
```

---

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
