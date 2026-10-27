# Testing & Test Suite Documentation

> Test suite coverage, execution procedures, and verification breakdown for `pqblocks-qubo-bench`.

---

## 1. Test Suite Summary

The test suite contains **80 tests** covering all modules of the benchmarking harness.

- **Status**: 80 passed, 0 failed, 1 warning (numba compiler informational warning)
- **Runtime**: ~6.0 seconds
- **Statement Coverage**: 72% across 931 statements
- **Python Matrix**: Fully verified on Python 3.11, 3.12, 3.13, and 3.14

---

## 2. Test File Breakdown

| Test File | Tests | Focus Area |
|---|---|---|
| `test_baseline_wrapper.py` | 5 | Base abstract wrapper contract and dimod BQM handling |
| `test_batch_comprehensive.py` | 3 | Batch configuration validation, schema checks, and error paths |
| `test_batch_execution.py` | 4 | Multi-problem batch orchestration and summary collection |
| `test_batch_module.py` | 2 | Batch runner parameter validation |
| `test_bench_harness.py` | 13 | Benchmark loaders (G-set, BiqMac, QPLIB, TSPLIB, OR-Library, Planted) |
| `test_card.py` | 3 | Result metadata serialization and catalog card generation |
| `test_cli_additional_coverage.py` | 5 | CLI argument parsing edge cases and help flags |
| `test_cli_comprehensive.py` | 4 | End-to-end CLI command invocation |
| `test_cli_module.py` | 4 | Subcommand routing and configuration ingestion |
| `test_cpsat_wrapper.py` | 6 | CP-SAT solver initialization, time bounds, and solution extraction |
| `test_gap.py` | 6 | Optimality gap calculation and near-zero denominator edge cases |
| `test_mqlib_wrapper_module.py` | 3 | MQLib binary wrapper initialization and parameter retrieval |
| `test_optimized_metrics.py` | 4 | Statistical confidence interval calculation for TTS |
| `test_optimized_metrics_module.py` | 6 | Metric boundary condition checks |
| `test_pipeline_additional_coverage.py` | 5 | Pipeline orchestrator error handling |
| `test_pipeline_module.py` | 4 | Pipeline execution workflow |
| `test_sqa_wrapper.py` | 3 | Simulated Quantum Annealing wrapper and sampling |

---

## 3. Running the Tests

To run the complete test suite:

```bash
pytest -v
```

To run with coverage reporting:

```bash
pytest --cov=pqblocks_qubo_bench --cov-report=term
```

---

## 4. Test Fixtures and Isolation

- Test fixtures for SQA and external baselines are located in `tests/fixtures/`.
- Tests run in clean isolated virtual environments without requiring external network connectivity or pre-installed system packages.
