# AGENTS.md

## Mission

This repository implements the experimental system specified by the frozen scientific contract in `paper_contract/`.

The system evaluates topology-aware placement of NIC queues, packet and descriptor memory, event rings, I/O contexts, workers, and processing units on multi-socket NUMA/PCIe hosts.

The primary implementation entry point is:

`paper_contract/EXPERIMENT_SPEC.md`, Milestone 1.

## Authority and source of truth

Use the following precedence:

1. explicit user instructions;
2. this `AGENTS.md`;
3. `paper_contract/EXPERIMENT_SPEC.md`;
4. `paper_contract/PRE_IMPLEMENTATION_DECISIONS.md`;
5. formal manuscript sections in `paper_contract/manuscript/sections/`;
6. other repository documentation.

Files under `paper_contract/` are immutable imported evidence. Do not silently edit them. A scientific-contract change requires an explicit versioned update and a new checksum manifest.

## Frozen scientific decisions

The implementation must preserve the following decisions exactly:

* D03: primary ownership is single-owner, with `k=1` and share `1`;
* D11: nearest-rank quantiles without interpolation;
* D12: the specified complete-run nonnegative-ridge estimator and admissible condition-stratified placement-relation-blocked folds;
* D21: topology-blind B0/B1 initialization CPU rule;
* D23: conditional accepted-pair estimand and mandatory attrition reporting.

All other decisions must be represented by typed states such as:

* `Frozen`;
* `PendingQualification`;
* `BlockedOnTestbed`;
* `UnresolvedScientificDecision`;
* `Unsupported`;
* `NotApplicable`.

Unknown, zero, missing, unsupported, and not applicable are different states.

Do not invent stand-dependent values.

## Baseline integrity

Preserve the four policies:

* B0: operating-system scheduling and memory-policy defaults;
* B1: B0 plus CPU affinity only;
* B2: B1 plus CPU-relative memory binding;
* B3: complete topology-aware placement.

All non-placement invariants must remain identical within a comparison block.

Do not allow a backend, fallback, configuration error, or missing capability to silently change the meaning of a baseline.

## Implementation defaults

Use C++20 for the low-latency core and CMake for the build unless an approved architecture decision states otherwise.

Python may be used for offline statistical analysis, report generation, and test-fixture validation. Python is not part of the measured SUT data path.

Keep scientific domain logic independent from DPDK, AF_XDP, hwloc, libnuma, sysfs, perf, and NIC-specific code through explicit interfaces.

Implement mock and fixture-backed adapters before privileged Linux or packet-I/O backends.

Do not select DPDK or AF_XDP as the primary frontend until D01 is resolved through the required qualification evidence.

## Safety

Unit and contract tests must not:

* modify host affinity or NUMA policy;
* rebind drivers;
* configure NIC queues;
* allocate persistent huge pages;
* modify IRQ affinity;
* change power or frequency controls;
* require root privileges.

Real host changes must use an explicit apply mode, prior-state journal, independent read-back, rollback, and dirty-host status.

Dry-run must be the default for configuration tools.

Never execute experiments on an unqualified host.

## Development workflow

Work on one milestone at a time.

Before implementing a milestone:

1. read its inputs, outputs, dependencies, and verification criteria;
2. map it to contracts C01–C24;
3. identify unresolved decision gates;
4. stop if a required gate is unresolved;
5. prepare tests before production implementation.

After each milestone:

1. run unit, contract, and applicable fixture tests;
2. verify schema and digest stability;
3. update `PROGRESS.md`;
4. record architecture decisions in `docs/adr/`;
5. report changed files, tests, unresolved gates, and the next milestone.

Do not start the next milestone automatically.

## Data and evidence rules

All records must have:

* schema version;
* stable record ID;
* producer identity and version;
* creation timestamp and clock domain;
* campaign or stage ID;
* input content digests;
* canonical-content digest;
* status and structured errors;
* explicit units for numeric fields.

Derived artifacts must retain provenance to immutable raw records.

Synthetic values are allowed only in tests and must be labeled `NON_MEASUREMENT_TEST_FIXTURE`. They must never appear as experimental results.

Do not fabricate hardware manifests, measurements, counters, timestamps, placement success, or performance results.

## Correctness requirements

Correctness precedes performance.

Mandatory properties include:

* deterministic schema serialization;
* exact expected-sequence accounting;
* detection of initial, internal, and terminal loss;
* corruption, duplicate, ambiguity, and reordering classification;
* wraparound-safe timestamps and counters;
* ring lapping and overwrite detection;
* immutable B0/B1 per-attempt page records;
* order-independent `Pair-Pending` to final page-equivalence transition;
* deterministic planner output and tie-breaking;
* no heuristic infeasibility claim;
* independent exact-small reference;
* no packet-level pseudoreplication;
* policy-specific acceptance and attrition accounting.

Performance data from a failed correctness run must remain archived but scientifically excluded.

## Testing requirements

Each contract must have:

* normal-path tests;
* boundary tests;
* malformed-input tests;
* missing-data tests;
* deterministic replay tests;
* digest/provenance tests;
* declared failure-status tests.

The exact-small reference must be independent of heuristic pruning, search order, candidate caps, and heuristic output.

Tests must cover both B0/B1 arrival orders and every planned failure category.

## Completion rule

Implementation is not complete merely because it compiles.

A milestone is complete only when its contract outputs, invariants, error states, provenance, tests, and verification criteria from `EXPERIMENT_SPEC.md` are satisfied.

Confirmatory execution is forbidden until all required testbed, calibration, timestamp, correctness, and decision gates are frozen.

