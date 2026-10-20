# AGENTS.md

Instructions for any coding agent (Claude Code, the Claude Agent SDK, Codex, or similar) working in this repository.

## Mission

This repository implements the experimental system specified by the frozen scientific contract in `paper_contract/`.

The system evaluates topology-aware placement of NIC queues, packet and descriptor memory, event rings, I/O contexts, workers, and processing units on multi-socket NUMA/PCIe hosts.

The scientific entry point is `paper_contract/EXPERIMENT_SPEC.md`. Milestone 1 (schemas, decision ledger, protocol) is complete. The current status of every milestone is in `PROGRESS.md` and `PLAN.md`.

## Start of every session

1. Read `PROGRESS.md` and the relevant `PLAN.md` rows to find milestone status and dependencies.
2. Run the verification commands below and confirm everything passes before changing anything.
3. If the user has not named a milestone, propose the next startable one (see "Milestone order") and wait for confirmation.
4. Load only the sources the reading map lists for that milestone. `EXPERIMENT_SPEC.md` is about 137 KB; read the listed sections rather than the whole file.

## Verification commands

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py' -v
cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure
```

All must pass before a milestone is reported complete. Never delete, skip, or weaken an existing test to make it pass. If a test encodes an expectation that a milestone legitimately supersedes, change it in the same change set and explain why in the milestone report.

## Authority and source of truth

Use the following precedence:

1. explicit user instructions;
2. this `AGENTS.md`;
3. `paper_contract/EXPERIMENT_SPEC.md`;
4. `paper_contract/PRE_IMPLEMENTATION_DECISIONS.md`;
5. formal manuscript sections in `paper_contract/manuscript/sections/`;
6. other repository documentation.

Files under `paper_contract/` are immutable imported evidence. Do not silently edit them. A scientific-contract change requires an explicit versioned update and a new checksum manifest.

`tests/test_contracts.py` pins SHA-256 digests of nine `paper_contract/` files (the spec, the decision register, the claim matrix, and the six `.tex` sections). If that test fails, a contract file has changed: stop and tell the user. Do not update the pinned digests to make the test pass.

## ID namespaces

Several ID families look alike. Always qualify them in code, records, and reports.

| ID | Meaning | Defined in |
|---|---|---|
| M1–M17 | Implementation milestones | `PLAN.md`; spec §13 |
| C01–C24 | Implementation contracts (producer/consumer records) | spec §5.2; `docs/contracts/CONTRACT_MAP.md` |
| claim C01–C72 | Manuscript claims; unrelated to contracts C01–C24 | `paper_contract/CLAIM_EVIDENCE_MATRIX.md` |
| D01–D23 | Decision gates | `PRE_IMPLEMENTATION_DECISIONS.md`; `protocol/v1/decision-gates.json` |
| U01–U06 | Unresolved testbed inputs | `CLAIM_EVIDENCE_MATRIX.md` |
| RQ1–RQ6 | Research questions | spec §1.2; `docs/contracts/RQ_FIELD_MATRIX.md` |
| B0–B3 | Placement policies | spec §6; `docs/contracts/BASELINE_MATRIX.md` |
| T-STD | The seven mandatory test classes | `docs/contracts/CONTRACT_MAP.md` |

"Spec §N" means `EXPERIMENT_SPEC.md`. Spec §5.3 lists components as numbered items 1–14 (item 1 topology inspector … item 14 result aggregator). Manuscript files are offset by one from paper sections: `05_problem_statement.tex` is paper §4, `06_topology_model.tex` §5, `07_cost_model.tex` §6, `08_placement_algorithm.tex` §7, `09_system_design.tex` §8, and `10_experimental_methodology.tex` §9. Paper §1–3 and §10 exist only in `paper_contract/manuscript/main.pdf`.

## Milestone order

Follow the dependency column in `PLAN.md`, not numeric order. A milestone is startable when every listed dependency is `Complete`.

| M | Depends on | Can an agent complete it alone? |
|---:|---|---|
| 2 | M1 | No. Needs hwloc XML and sysfs captures from real Linux host(s) and a privacy/provenance review, supplied by the user. The agent may prepare the capture checklist, fixture layout, redaction tooling, and checksum manifest. |
| 3 | M1–M2 | Yes, once M2 fixtures exist. |
| 4 | M3 | Yes. |
| 5 | M1, M4 | Yes. D13 numeric budgets come from this milestone's own off-stand benchmark. |
| 6 | M1, M5 | Yes, with mock backends only. |
| 7 | M1 | Yes. Startable now. |
| 8 | M1, M7 | Yes. |
| 9 | M1–M2 | Needs counter fixtures. |
| 10 | M1, M9 | Yes, with labeled non-measurement fixtures. |
| 11–15 | Physical stand | No. Needs a qualified TG/SUT pair and resolved gates. |
| 16–17 | Real data | No. M17 also needs manuscript sources (`main.tex`, sections 01–04 and 11, `references.bib`) that are not in this repository. |

Gate rule: a gate listed for a milestone blocks only the scope `PLAN.md` says it blocks. Off-stand and fixture work proceeds while physical-use gates remain `BlockedOnTestbed`; represent those gates as typed states in code and records. Stop and report when a gate blocks the milestone's own deliverable, for example D15 before the M13 power calculation.

## Reading map

For every milestone, read its `PLAN.md` row and spec §13 row, its spec §5.2 registry rows, the matching rows in `CONTRACT_MAP.md` and `ERROR_TAXONOMY.md`, and `docs/contracts/INVARIANTS.md`. Then add:

| M | Contracts | Spec sections | Manuscript (`sections/`) | Schemas (`schemas/v1/`) |
|---:|---|---|---|---|
| 2 | C01 inputs | §3.3, §4, §12.2, §13.1 | 06 | raw-topology-observation, environment-manifest |
| 3 | C01 | §4, §5.3 item 1 | 06 | raw-topology-observation, environment-manifest |
| 4 | C02, C05 | §4, §5.3 item 2 | 06 | topology-snapshot, serialized-graph |
| 5 | C04, C08, C09 | §5.3 item 4, §5.4, §9.6 (exact-small paragraphs) | 05, 07, 08 | ownership-catalog, reference-mapping, cpu-access-profile, workload-spec, placement-plan, candidate-search-audit, queue-binding, execution-binding, capacity-check, cost-term-value, exact-reference-result |
| 6 | C10, C11, C12, C21 | §2.3, §5.3 items 5, 7, 12, §6, §9.0–9.1, §10.1 | 09; 10 (initialization and policy subsections) | applied-placement, page-initialization-record, page-equivalence-record, location-qualified-object, observed-placement, acceptance-record, run-record, phase-record |
| 7 | C17–C20 | §3.4, §5.3 items 10–11, §8.1–8.3, §8.6–8.7, §10.1 (packet gates) | 10 (measurement chain, packet accounting) | traffic-generation-record, sequence-manifest, packet-expectation, packet-observation, timestamp-record, timestamp-evidence, clock-qualification, oracle-report, response-category |
| 8 | C13–C16 | §2.2, §5.3 items 6–9, §10.3 | 05 (execution contexts), 09 | frontend-profile, frontend-capability-profile, frontend-run-record, memory-object-record, ring-record, worker-record |
| 9 | C22, C23 (ingestion) | §8.4–8.5, §5.3 items 13–14 | 09 (telemetry) | telemetry-record, counter-sample, aggregated-dataset |
| 10 | C23, C24 | §1.2–1.3, §9, §11 | 10 (statistics) | aggregated-dataset, analysis-plan, primary-analysis-record, statistical-analysis-artifact |

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

The development machine is macOS. Off-stand milestones (M2–M10) must configure, build, and pass tests without Linux-only headers or libraries (libnuma, DPDK, libbpf/libxdp, perf_event). Put Linux adapters behind a CMake option that is off by default, and record that choice in an ADR when the first adapter appears.

`tools/canonical_json.py` is the reference canonicalizer (ADR 0003). Any C++ record producer needs a cross-language test proving byte-identical canonical output and digests.

## Decisions to bring to the user

Propose these as a draft ADR in `docs/adr/` with `Status: Proposed` and wait for approval before acting:

* adding any third-party dependency (C++ test framework, C++ JSON library, hwloc or libnuma linkage, Python packages such as numpy or scipy for M10);
* new top-level directories, or the source layout for the first C++ code;
* changing the shape or version of an existing v1 schema;
* changing any decision-gate state or resolved value;
* any value the protocol leaves to the investigator, especially D15 (smallest scientifically relevant effect).

## Schema and protocol-record workflow

* `schemas/v1/*.json` and `schemas/v1/schema-index.json` are generated by `tools/generate_schemas.py`. Never hand-edit them. Change the generator, run `python3 tools/generate_schemas.py`, then run the tests; they assert that generated output equals the committed files.
* `protocol/v1/decision-gates.json` and `campaigns/templates/v1/campaign.json` are generated by `tools/generate_protocol_records.py` in the same way.
* ADR 0003 forbids silently reinterpreting v1 bytes. Adding a new record type is additive. Changing an existing record type needs an ADR and a version decision.
* Gate state changes go into the ledger generator with evidence digests, never into `paper_contract/PRE_IMPLEMENTATION_DECISIONS.md`.

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

Never execute experiments on an unqualified host. The development machine is never a qualified host.

## Development workflow

Work on one milestone at a time.

Before implementing a milestone:

1. read its inputs, outputs, dependencies, and verification criteria;
2. map it to contracts C01–C24;
3. identify unresolved decision gates;
4. stop if a gate blocks the milestone's own deliverable (see the gate rule under "Milestone order");
5. prepare tests before production implementation.

After each milestone:

1. run unit, contract, and applicable fixture tests;
2. verify schema and digest stability;
3. update the milestone's status in both `PLAN.md` and `PROGRESS.md` using `Pending`, `In progress`, `Blocked`, or `Complete`; `tests/test_documentation.py` checks that the two files agree and that no milestone is `Complete` before its dependencies;
4. record architecture decisions in `docs/adr/`;
5. report changed files, tests, unresolved gates, and the next startable milestone.

`PROGRESS.md` is the implementation progress file. Never edit `paper_contract/PAPER_PROGRESS.md`; it belongs to the manuscript project.

Do not start the next milestone automatically. Do not commit or push unless the user asks.

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

Synthetic values are allowed only in tests and must be labeled `NON_MEASUREMENT_TEST_FIXTURE`: set `meta.data_classification = NON_MEASUREMENT_TEST_FIXTURE`, `meta.artifact_class = TestFixture`, and `meta.scientific_disposition = NotMeasurement` (ADR 0004). They must never appear as experimental results.

Do not fabricate hardware manifests, measurements, counters, timestamps, placement success, or performance results.

No `results/` directory may exist until real confirmatory data exist; a test enforces this.

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

## Known gaps to close in their milestone

* M5: no schema yet records planner quality against the exact-small reference: the normalized optimality gap (paper eq. 38), the missed-feasibility rate, and the locality-only comparator. Add a record type for them.
* M5: `CostTermValue.term_id` is a free string. Freeze the vocabulary of the eleven unloaded primitives (T0) and the capacity-bearing resources (E_L) from `07_cost_model.tex`.
* Spec text written for the original paper repository says "this repository contains no experimental source code" and refers to a "Codex session". Read these as historical; they do not forbid implementation here.
* `paper_contract/manuscript/main.pdf` and `paper_contract/PAPER_PROGRESS.md` are not covered by the digest test.

## Completion rule

Implementation is not complete merely because it compiles.

A milestone is complete only when its contract outputs, invariants, error states, provenance, tests, and verification criteria from `EXPERIMENT_SPEC.md` are satisfied.

Confirmatory execution is forbidden until all required testbed, calibration, timestamp, correctness, and decision gates are frozen.
