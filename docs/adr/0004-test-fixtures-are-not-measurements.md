# ADR 0004: Test-fixture and non-measurement-data policy

- Status: Accepted
- Date: 2026-08-17

## Context

Synthetic values are necessary to exercise malformed input, loss, wrap, pair-order, planner status, and statistical formulas, but could be mistaken for hardware evidence or results.

## Decision

Every synthetic record uses `data_classification=NON_MEASUREMENT_TEST_FIXTURE`, `artifact_class=TestFixture`, and `scientific_disposition=NotMeasurement`. Fixtures use reserved fixture IDs and a test clock domain. They never enter a physical campaign index, accepted-run dataset, estimate, result table, figure, or manuscript claim.

Milestone 1 tests construct fixtures in memory. Repository protocol records use `ProtocolDefinition`, not measurement classification. No placeholder result, dummy NIC, topology, queue, timestamp, counter, rate, duration, coefficient, tau_mem, or effect size is permitted.

## Consequences

Tests can be exhaustive without producing pseudo-results. Any future fixture export retains the label and separate hierarchy. A pipeline that encounters fixture-classified input while producing a measurement/result artifact must fail closed.
