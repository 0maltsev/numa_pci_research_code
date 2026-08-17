# NUMA/PCIe Topology-Aware Placement Benchmark

This repository implements the experimental system defined by the immutable scientific contract in `paper_contract/`. Its purpose is to determine whether jointly placing NIC queues, RX/TX payload and descriptor memory, event rings, I/O contexts, workers, application state, and physical execution contexts improves run-level p99.9 external turnaround latency on multi-socket NUMA/PCIe systems.

The causal treatment is placement. DPDK and AF_XDP are candidate frontend profiles, not treatments; neither is selected until decision gate D01 is qualified. Packets are observations within a run, never independent statistical repetitions.

## Current scope

Milestone 1 freezes schemas, decision states, invariants, error semantics, the campaign template, and scientific-analysis fields. It contains no topology inspector, planner, packet frontend, benchmark data path, privileged configuration backend, physical-host integration, measurements, or experimental results.

The repository deliberately separates two environments:

- **Off-stand implementation:** schema validation, deterministic digest replay, fixture-only contract checks, and later pure domain logic. These actions require no root privileges and make no host changes.
- **Physical execution:** Milestones 11–15 only, after stand qualification and all required gates are frozen. A qualified TG/SUT pair, explicit apply authorization, prior-state journal, independent read-back, rollback, and a clean-host determination are mandatory. Confirmatory execution is forbidden before those conditions hold.

Synthetic data may exist only inside tests, must carry `NON_MEASUREMENT_TEST_FIXTURE`, and is scientifically inadmissible.

## Repository map

- `paper_contract/`: immutable imported scientific evidence.
- `schemas/v1/`: JSON Schema Draft 2020-12 record contracts and the schema index.
- `protocol/v1/decision-gates.json`: typed D01–D23 decision ledger.
- `protocol/v1/rq-field-map.json`: machine-readable RQ-to-record-field map.
- `campaigns/templates/v1/campaign.json`: non-executable versioned campaign template.
- `docs/contracts/`: contract, invariant, error, RQ, and baseline specifications.
- `docs/adr/`: Milestone 1 architecture decisions.
- `tools/`: off-stand schema generation, canonical JSON, and validation tools.
- `tests/`: non-measurement contract tests.

## Build and test

The minimal build establishes C++20 and CMake without adding production components:

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

The contract suite can also run directly with the Python standard library:

```sh
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Schema generation is deterministic and is an explicit maintenance action:

```sh
python3 tools/generate_schemas.py
python3 tools/generate_protocol_records.py
```

These commands create protocol definitions only; they do not probe, configure, or benchmark the host.

## Scientific non-negotiables

D03 fixes single-owner primary operation (`k=1`, share `1`). D11 fixes one-indexed nearest-rank quantiles without interpolation. D12 fixes the complete-run nonnegative-ridge estimator and admissible condition-stratified, placement-relation-blocked folds. D21 fixes the topology-blind B0/B1 initializer CPU rule. D23 fixes the conditional accepted-pair estimand and mandatory attrition report. All other decisions remain typed gates until their declared evidence and freeze points are satisfied.
