# Security Notes & Posture

> Security scope, threat considerations, and memory safety for `pqblocks-qubo-bench`.

---

## 1. Non-Cryptographic Classification

> [!NOTE]
> **Domain Classification**: Quantum-inspired classical optimisation: not cryptography, no security claim.

`pqblocks-qubo-bench` is an evaluation harness for combinatorial optimization and benchmark metrics. It does not implement, expose, or validate cryptographic primitives, key encapsulation mechanisms, digital signatures, or confidential data handling.

---

## 2. Input Validation & File Ingestion

- **Benchmark Parsing**: Instance loaders parse structured text files (such as edge lists or matrix representations). All loaders validate line formats, variable count boundaries ($\ge 2$ variables), and integer ranges to prevent malformed files from triggering parser crashes.
- **Batch Schemas**: Batch execution definitions are validated against formal JSON schemas (`jsonschema`) before execution to reject unexpected properties or malformed solver configurations.
- **Subprocess Safety**: External solver invocations (e.g. MQLib or external command-line solvers) pass explicit argument vectors without invoking a system shell (`shell=False`), preventing shell injection.

---

## 3. Resource & Memory Bounds

- Combinatorial optimization problems with large variable counts ($N > 100,000$) can require extensive memory for dense quadratic bias matrices ($O(N^2)$ space). Users executing benchmarks on massive graphs should allocate sufficient system RAM or utilize sparse BQM structures.
- Solvers are wrapped with configurable timeout limits to prevent unbounded CPU execution on intractable NP-hard instances.
