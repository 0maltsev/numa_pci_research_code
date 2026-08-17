# Error and Status Taxonomy

Statuses describe an artifact outcome; errors explain why. A record can be retained with a failure status and still be scientifically excluded. No fallback or recoding may erase the original status.

## Cross-cutting states

| Class | Values | Meaning |
|---|---|---|
| Availability | `Known`, `Unknown`, `Missing`, `Unsupported`, `NotApplicable` | `Unknown` is not yet knowable; `Missing` was expected but absent; `Unsupported` lacks capability; `NotApplicable` does not belong to this profile. Numeric zero is only `Known(value="0", unit=...)`. |
| Record status kind | `Success`, `Pending`, `Failure`, `Blocked`, `Excluded` | Machine disposition independent of the human error message. |
| Scientific disposition | `Eligible`, `ScientificallyExcluded`, `DiagnosticOnly`, `NotMeasurement` | Failed performance data remain archived as excluded; protocol and fixtures are not measurements. |
| Recovery | `NotRequired`, `Pending`, `Succeeded`, `Failed`, `Impossible` | Whether the producing stage recovered. |
| Rollback | `NotApplicable`, `NotStarted`, `Succeeded`, `Failed` | A rollback failure implies dirty-host evaluation. |
| Decision gate | `Frozen`, `PendingQualification`, `BlockedOnTestbed`, `UnresolvedScientificDecision`, `Unsupported`, `NotApplicable` | Protocol choice state, not an experimental result. Only D03, D11, D12, D21, and D23 start frozen. |

Every structured error contains an error ID, component, stage, code, severity, affected fact IDs, message, recovery status, rollback status, and scientific disposition.

## Contract terminal codes

| Contract | Declared failure, pending, or bounded-result codes | Required interpretation |
|---|---|---|
| C01 | `Source-Inaccessible`, `Host-Changed`, `Device-Disappeared`, `Partial-Collection` | Raw evidence remains inference-free; partial output is diagnostic until an explicit fallback accepts it. |
| C02 | `Duplicate-Identity`, `Contradictory-Membership`, `Dangling-Queue`, `Unit-Mismatch`, `Stale-Input` | Stop graph admission; do not repair unknowns with zeros or guessed joins. |
| C03 | `Capability-Unsupported`, `Readback-Ambiguous`, `Privilege-Missing`, `Qualification-Failed` | A surface never becomes controllable without qualification. D01 remains unresolved if mandatory capability fails. |
| C04 | `Catalog-Empty`, `Invalid-Share`, `Nonfinite-Domain`, `Control-Class-Mismatch`, `Catalog-Stale` | Reject the catalog. Primary k=1/share=1 cannot be weakened. |
| C05 | `Unsupported-Schema`, `Roundtrip-Mismatch`, `Noncanonical-Order`, `Digest-Mismatch` | Reject serialization and every dependent artifact. |
| C06 | `Run-Rejected`, `Response-Undefined`, `Feature-Missing`, `Split-Leakage`, `Condition-Coverage-Insufficient`, `Digest-Mismatch` | No packet-level replacement or split repair; coverage failure blocks fitting. |
| C07 | `Condition-Coverage-Insufficient`, `Calibration-Failed`, `Rank-Deficient`, `Topology-Scale-Zero`, `Validation-Failed`, `Out-Of-Domain` | Block confirmatory B3; never substitute an estimator or use confirmatory outcomes. |
| C08 | `Feasible`, `Search-Limited`, `Cap-Limited`, `Data-Incomplete`, `Model-Out-Of-Domain`, `Stale-Input` | Only `Feasible` carries a plan. Limited/data states are non-plans and make no infeasibility claim. |
| C09 | `Exact-Feasible`, `Proven-Infeasible`, `Exact-Budget-Exceeded`, `Exact-Execution-Error` | `Proven-Infeasible` requires full certified exhaustion. Budget/execution failure has no known optimum/infeasibility conclusion. |
| C10 | `Apply-Prerequisite-Failed`, `Privilege-Missing`, `Partial-Apply`, `Rollback-Failed`, `Host-Dirty` | Stop at first prerequisite failure; reverse rollback; dirty host blocks scientific runs. |
| C11 | `Allocation-Failed`, `Fault-Incomplete`, `Initializer-Escaped`, `Inherited-State`, `Policy-Request-Failed`, `Page-Observation-Incomplete` | Attempt evidence is retained and excluded as declared. Pair statuses do not belong here. |
| C12 | `Placement-Mismatch`, `Share-Out-Of-Range`, `Pair-Pending`, `Page-Equivalence-Failed`, `Page-Equivalence-Unsupported`, `Observation-Incomplete` | `Pair-Pending` is not an attempt failure. Final page failure affects only RQ1 unless an attempt separately fails. |
| C13 | `Queue-Create-Failed`, `Link-Changed`, `Hidden-Fallback`, `Undeclared-Copy`, `Counter-Ambiguous` | Do not recode as another frontend/baseline; invariant-path failure excludes the attempt. |
| C14 | `Capacity-Mismatch`, `Page-Source-Wrong`, `Object-Reused`, `Bounds-Violation`, `Location-Unobservable` | Never resize, reuse, or silently change the page source to salvage a run. |
| C15 | `Ring-Lapped`, `Sequence-Invalid`, `Producer-Stalled`, `Consumer-Stalled`, `Sharing-Undeclared` | Correctness failure excludes performance; no “good interval” trimming. |
| C16 | `Affinity-Escape`, `Worker-Stall`, `Service-Error`, `Response-Invalid`, `Capacity-Gate-Failed` | Exclude the attempt; never substitute a neighboring worker/run. |
| C17 | `Rate-Out-Of-Tolerance`, `Generator-Saturated`, `Link-Fault`, `Trace-Mismatch`, `Timestamp-Loss` | Policy is not credited for low latency at reduced/changed work. |
| C18 | `Clock-Step`, `Wrap-Ambiguous`, `Timestamp-Ambiguous`, `Loss-Gate-Failed`, `Qualification-Out-Of-Domain` | Invalid timestamp evidence never enters the latency sample. |
| C19 | `Manifest-Late`, `Duplicate-Expectation`, `Rule-Nonreproducible`, `Digest-Mismatch` | Expected set cannot be reconstructed from received packets after the fact. |
| C20 | `Integrity-Failed`, `Duplicate`, `Ambiguous`, `Timestamp-Invalid`, `Accounting-Mismatch` | Each expectation still receives one category; invalid responses never enter latency. |
| C21 | `Phase-Timeout`, `Gate-Failed`, `Topology-Changed`, `Rollback-Incomplete`, `Operator-Intervention` | Retain the attempt and fixed schedule slot. Do not rerun or reroll order. |
| C22 | `Event-Unavailable`, `Wrap-Ambiguous`, `Multiplexing-Gate-Failed`, `Attribution-Mismatch`, `Interval-Missing` | Unavailable is not zero; optional loss limits RQ5, mandatory loss excludes as frozen. |
| C23 | `Digest-Mismatch`, `Duplicate-Run`, `Pair-Pending-Unresolved`, `Pair-Join-Mismatch`, `Incomplete-Block`, `Quantile-Unbounded`, `Schema-Mismatch` | Preserve scheduled denominator; no packet pseudo-replication or excluded-latency reintroduction. |
| C24 | `Plan-Digest-Mismatch`, `Insufficient-Pairs`, `Attrition-Report-Incomplete`, `Assumption-Sensitive`, `Family-Violation`, `Unplanned-Analysis` | Do not issue a confirmatory decision when undefined; do not substitute a favorable method/cell/family. |

## Mandatory attrition categories

Every scheduled attempt maps to one primary category and all failed gates. Aggregation retains explicit denominators for planner (`Search-Limited`, `Cap-Limited`, `Data-Incomplete`), calibration/model admission or validity domain, apply, rollback, placement read-back, page verification, correctness, timestamp, telemetry, environment, external stand fault, and operator intervention. Campaign-wide `Calibration-Failed` has one model-admission denominator and is never multiplied into nonexistent per-block latency records.
