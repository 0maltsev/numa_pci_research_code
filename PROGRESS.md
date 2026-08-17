# Implementation Progress

No experimental source path, measurement, or result exists in this repository.

| Milestone | Status | Evidence / blocker |
|---:|---|---|
| 1. Freeze schemas, decisions, and scientific protocol | Complete | 48 v1 record schemas plus shared definitions cover C01–C24; the typed D01–D23 ledger, campaign template, RQ/baseline maps, invariants, taxonomy, six ADRs, and deterministic validation suite are complete. |
| 2. Acquire and curate topology fixtures | Pending | Starts only after M1; no fixture capture performed. |
| 3. Topology inspector | Pending | No implementation started. |
| 4. Graph builder and serializer | Pending | No implementation started. |
| 5. Planner, cost evaluator, and exact reference | Pending | No implementation started. |
| 6. Applicator, initializer, and pair state machines | Pending | No implementation started. |
| 7. Traffic, sequence, clock, and correctness core | Pending | No implementation started. |
| 8. Ring, pool, worker, and frontend abstractions | Pending | No implementation started. |
| 9. Telemetry and result ingestion | Pending | No implementation started. |
| 10. Statistical analysis and reporting | Pending | No implementation started. |
| 11. Stand qualification | Pending | Requires physical TG/SUT and gate resolution. |
| 12. Frontend integration and baselines | Pending | Requires M11 and qualified frontend. |
| 13. Calibration and pilot | Pending | Requires qualified integrated stand. |
| 14. Confirmatory execution | Pending | Forbidden until all required gates are frozen. |
| 15. Ablation and robustness execution | Pending | Requires accepted core campaign. |
| 16. Final analysis and artifact audit | Pending | Requires immutable real data. |
| 17. Manuscript results and conclusion | Pending | Requires audited analysis outputs. |

## Milestone 1 acceptance checklist

- [x] Every C01–C24 contract maps to one or more v1 schemas and all required test classes.
- [x] Every RQ and primary/key-secondary output maps to stored fields.
- [x] D01–D23 appear exactly once; frozen decisions cannot be unresolved defaults.
- [x] Canonical serialization and digest replay are deterministic.
- [x] All contract and build tests pass.
- [x] No privileged operation, host configuration, measurement, or experimental result was produced.

## Milestone 1 verification evidence

- Direct contract suite: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py' -v` — 19 tests passed.
- Build configuration: `cmake -S . -B build` — succeeded with AppleClang 15 and Python 3.14.
- Minimal build: `cmake --build build` — succeeded; no production source target exists.
- CTest: `ctest --test-dir build --output-on-failure` — 1/1 test passed.
- Protocol source digests replay against all nine mandated scientific source files; ledger and campaign canonical digests regenerate byte-identically.

## Remaining decision gates

- Frozen: D03, D11, D12, D21, D23.
- Pending qualification: D01, D02, D09, D13, D18, D20, D22.
- Blocked on the physical testbed: D04, D05, D06, D07, D08, D10, D14, D16, D17, D19.
- Unresolved scientific decision: D15.

Milestone 2 is schema-ready but has not started. It still requires captured fixture access and a privacy/provenance review; no final benchmark stand is required.
