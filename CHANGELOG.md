# Changelog

All notable changes to `pqblocks-qubo-bench` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-26

### Added
- Standardized benchmarking harness for quantum-inspired and classical solvers.
- Statistical Time-To-Solution (`calculate_tts`) engine supporting arbitrary confidence targets.
- Reference optimality gap (`calculate_gap`) calculator with near-zero energy protection.
- Integrated `loaders` subpackage supporting G-set, BiqMac, QPLIB, TSPLIB, OR-Library, and planted instances.
- Baseline solver wrappers for Google OR-Tools CP-SAT, MQLib, D-Wave Neal, and SQA.
- Batch execution orchestrator with formal JSON schema validation.
- Command-line interface `pqblocks-qubo-bench` for automated pipeline execution.
- Comprehensive test suite with 80 tests passing across Python 3.11, 3.12, 3.13, and 3.14.
- Examples demonstrating quickstart TTS calculation and comprehensive benchmark evaluation.
