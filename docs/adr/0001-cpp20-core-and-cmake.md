# ADR 0001: C++20 core and CMake build

- Status: Accepted
- Date: 2026-08-17
- Scope: Architecture only; Milestone 1 adds no production core

## Context

The future measured data path requires predictable low-level resource control and must remain separate from offline analysis. The repository contract names C++20 and CMake as implementation defaults.

## Decision

Future low-latency domain/runtime code will use C++20 and a CMake build. `numa_pcie_contracts` is currently an interface-only target that establishes `cxx_std_20`; no topology, planning, frontend, data-path, or host-integration implementation is introduced in Milestone 1.

Python is limited to offline schema generation/validation, statistical analysis, report tooling, and explicitly labeled test fixtures. It is not part of the measured SUT path.

## Consequences

Later compiled components inherit one explicit language standard and portable build/test entry point. A change of language/build system requires a versioned ADR and must preserve schema/digest compatibility. This decision freezes no compiler, flags, ABI, NIC, or frontend; those become campaign/build-manifest data.
