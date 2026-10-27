# Verification Report: pqblocks-qubo-bench

> Formal release verification report for `pqblocks-qubo-bench`.

---

## 1. Executive Summary

| Attribute | Value |
|---|---|
| **Product** | `pqblocks-qubo-bench` |
| **Package Name** | `pqblocks_qubo_bench` |
| **Version** | `0.1.0` |
| **Classification** | Quantum-inspired classical optimisation: not cryptography, no security claim |
| **Verification Status** | **PASSED** |
| **Test Matrix** | Python 3.11, 3.12, 3.13, 3.14 |
| **Test Results** | 80 passed, 0 failed, 1 warning across all supported versions |
| **Leak Gate** | 0 hits (58 files scanned) |

---

## 2. Verification Gate Results

| Check ID | Verification Item | Target | Result | Status |
|---|---|---|---|---|
| **CHK-01** | Test Suite Completeness | 80 passing tests | 80 passed, 0 failed | **PASS** |
| **CHK-02** | Python Compatibility | Python 3.11–3.14 | Clean execution on all 4 versions | **PASS** |
| **CHK-03** | Source & Wheel Build | PEP 517 / PEP 621 | Valid sdist and wheel generated | **PASS** |
| **CHK-04** | Package Integrity | `twine check --strict` | Passed without warnings | **PASS** |
| **CHK-05** | Public Leak Gate | 0 internal leaks | 0 hits across all files | **PASS** |
| **CHK-06** | Example Verification | $\ge 2$ functioning examples | `quickstart.py` & `02_benchmark_harness_evaluation.py` passed | **PASS** |
| **CHK-07** | Subpackage Consolidation | `loaders` unified | Integrated as `pqblocks_qubo_bench.loaders` | **PASS** |

---

## 3. Subpackage Verification

Per project specifications, the previously separate `loaders` package has been successfully merged as a subpackage of `pqblocks_qubo_bench`:

- `pqblocks_qubo_bench.loaders`: Exposes `load_instance` alongside format-specific parsers (`gset_loader`, `biqmac_loader`, `qplib_loader`, `tsplib_loader`, `orlib_loader`, `planted_loader`).
- All test suites verify transparent imports and instance generation.

---

## 4. Conclusion

The package `pqblocks-qubo-bench` has passed all verification requirements and is verified for release.
