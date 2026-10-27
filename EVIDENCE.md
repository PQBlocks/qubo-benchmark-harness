# Verification Evidence & Traceability

> Detailed execution evidence, command outputs, and reproducibility artifacts for `pqblocks-qubo-bench`.

---

## 1. Clean-Room Test Execution Evidence

Full test execution output in a clean virtual environment running Python 3.14.8:

```text
============================= test session starts ==============================
platform linux -- Python 3.14.8, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/pqblocks-gate-bench/tests
configfile: pyproject.toml
testpaths: tests
plugins: hypothesis-6.168.0, cov-7.1.0, anyio-4.15.1
collected 80 items

tests/test_baseline_wrapper.py .....                                     [  6%]
tests/test_batch_comprehensive.py ...                                    [ 10%]
tests/test_batch_execution.py ....                                       [ 15%]
tests/test_batch_module.py ..                                            [ 17%]
tests/test_bench_harness.py .............                                [ 33%]
tests/test_card.py ...                                                   [ 37%]
tests/test_cli_additional_coverage.py .....                              [ 43%]
tests/test_cli_comprehensive.py ....                                     [ 48%]
tests/test_cli_module.py ....                                            [ 53%]
tests/test_cpsat_wrapper.py ......                                       [ 61%]
tests/test_gap.py ......                                                 [ 68%]
tests/test_mqlib_wrapper_module.py ...                                   [ 72%]
tests/test_optimized_metrics.py ....                                     [ 77%]
tests/test_optimized_metrics_module.py ......                            [ 85%]
tests/test_pipeline_additional_coverage.py .....                         [ 91%]
tests/test_pipeline_module.py ....                                       [ 96%]
tests/test_sqa_wrapper.py ...                                            [100%]

======================== 80 passed, 1 warning in 6.14s =========================
```

---

## 2. Command-Line Interface (CLI) Verification

Verification of the installed entrypoint script `pqblocks-qubo-bench`:

```text
$ pqblocks-qubo-bench --help
usage: pqblocks-qubo-bench [-h] [--config CONFIG] [--suite SUITE] [--output OUTPUT]

Benchmarking harness for quantum-inspired optimization algorithms and classical baseline solvers.

options:
  -h, --help       show this help message and exit
  --config CONFIG  Path to YAML benchmark configuration file
  --suite SUITE    Benchmark suite name (gset, biqmac, qplib, etc.)
  --output OUTPUT  Directory path for output benchmark summary JSON
```

---

## 3. Example Execution Evidence

### Quickstart Execution:

```bash
$ python3 examples/quickstart.py
Calculated TTS (99% target): 0.0432s
```

### Comprehensive Benchmark Evaluation:

```bash
$ python3 examples/02_benchmark_harness_evaluation.py
--- Benchmark Instance Loading ---
Loaded instance: G1 (gset)
Variables: 5, Linear biases: 5, Quadratic: 3

--- Evaluating Solution Quality and Reference Gap ---
Run 1: energy=  -6.0, gap=0.0000, success=True
Run 2: energy=  -5.5, gap=0.0833, success=False
Run 3: energy=  -6.0, gap=0.0000, success=True
Run 4: energy=  -4.8, gap=0.2000, success=False
Run 5: energy=  -6.0, gap=0.0000, success=True

Time-To-Solution (TTS @ 99% confidence): 0.035181s
Benchmark evaluation completed successfully.
```
