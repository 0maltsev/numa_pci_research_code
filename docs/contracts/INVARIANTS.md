# Scientific and Data Invariants

These invariants apply to every later component. A schema-valid record can still be scientifically invalid if a cross-record invariant fails.

## Record and evidence invariants

1. Every record carries schema version, stable record ID, producer identity/version, creation time and clock domain, campaign/stage ID, input content digests, canonical-content digest, structured status/errors, validity domain, and immutable provenance.
2. Canonical content is UTF-8 NFC JSON with lexicographically sorted object keys, schema-declared array order, no whitespace, no `null`, and no raw JSON numbers. A numeric datum is a canonical decimal string plus an explicit controlled unit and typed availability state.
3. `Known` numeric zero, `Unknown`, `Missing`, `Unsupported`, and `NotApplicable` are distinct. None may be silently converted to another.
4. Raw artifacts are immutable. Derived artifacts list raw/derived source IDs and digests and never overwrite sources. Failed correctness data remain archived but are `ScientificallyExcluded`.
5. Test data are `NON_MEASUREMENT_TEST_FIXTURE` and `NotMeasurement`. They cannot enter campaign indexes, results, estimates, or manuscript tables.
6. A consumer rejects an unsupported schema, digest mismatch, unknown mandatory unit, stale input, or request outside the producer's validity domain.

## Baseline and lifecycle invariants

1. B0 is OS scheduling and ordinary memory-policy behavior inside the common safety cpuset, with the frozen reference logical mapping and topology-blind initializer.
2. B1 differs from B0 only by deterministic data-plane physical-context CPU affinity after common allocation/faulting.
3. B2 preserves every B1 CPU and reference mapping and adds only CPU-access-share-relative memory binding on fresh objects. NIC/PCIe locality cannot select the B2 node.
4. B3 changes only declared placement decisions over the common finite inventories and catalog. It cannot change queue/RSS identities, resource counts/capacities, packet logic, rate, trace, batching, offloads, clocks, correctness gates, or any other non-placement invariant.
5. Every attempt uses a new process and fresh material allocations. It follows reset → allocate → fault → own page observation → affinity/ownership → independent read-back → fixed warm-up → committed-set measurement → drain/post-validation → cooldown/teardown/rollback.
6. B0/B1 use D21: the smallest stable OS CPU identifier in the initialization cpuset after functional exclusions. The initializer receives no NIC BDF, PCIe ancestry, NUMA identity/distance, page location, cost model, or latency input and finishes faulting before data-plane affinity.
7. Desired, requested, applied, and observed placement are separate facts. An accepted request is not proof of observation. Observed-only ownership has no setting action and is never called applied.
8. Every mutation requires apply authorization, a prior-state journal entry, dependency order, independent read-back, reverse rollback, and dirty-host status. Dry-run is the default. A dirty host admits no further scientific run.

## Ownership, topology, and planning invariants

1. D03 primary ownership is single-owner for every controllable non-null direction: `k=1`, share `1`.
2. Ownership choices come only from finite, versioned, stable-order catalogs. No continuous share simplex is searched. Direct, validated-indirect, observed-only, and unsupported controls retain different semantics.
3. Typed graph objects and directional relations are not interchangeable. Unknown locality never becomes zero distance or NUMA node 0.
4. RTC poller/worker roles share one physical execution context, consume one slot, and sum service. Staged roles use distinct contexts/slots.
5. Hard eligibility, ownership, capacity, occupancy, SMT, exclusivity, sharing-consistency, and isolation constraints are never softened into costs.
6. Planner ties and candidate exposure are deterministic. `Search-Limited`, `Cap-Limited`, and `Data-Incomplete` make no infeasibility claim.
7. Only the independent exact-small checker may emit `Proven-Infeasible`, and only after raw finite enumerators and the complete Cartesian product are exhausted with visited count equal to product size and feasible count zero. Budget expiration is `Exact-Budget-Exceeded`.

## Page-equivalence invariants

1. Each B0/B1 attempt independently emits an immutable `PageInitializationRecord`; it never stores pair dTV.
2. Exactly one missing mate creates a new `Pair-Pending` record. It never delays measurement, changes random order, or causes a rerun.
3. A final `PageEquivalenceRecord` is a new immutable artifact over the sorted immutable input digests. It is order-independent and uses no latency.
4. Every mandatory object must join with compatible coverage. `Pair-Equivalent` requires object-wise `dTV <= tau_mem`; otherwise the record is `Page-Equivalence-Failed` or `Page-Equivalence-Unsupported`.
5. The final page gate changes only RQ1 pair admission. It does not retroactively recode an individually valid attempt or another contrast.

## Packet, clock, and correctness invariants

1. The expected sequence set is committed before receipt and is independent of the first/last received packet. Arbitrary finite sets are permitted.
2. Every expectation gets exactly one final category. A sequence is latency-valid only when exactly one candidate passes format, payload, binding, and timestamp checks.
3. Missing initial, internal, and terminal subsets; corruption; duplicates; ambiguity; out-of-range responses; and reordering are distinct and fully reconciled with raw receive count.
4. Counter and timestamp wrap is extended before subtraction or aggregation. Ring occupancy uses monotonically extended sequences and detects lapping/overwrite.
5. Primary timestamps share one qualified TG clock domain. No intermediate per-packet rounding occurs. Invalid observations never enter latency order statistics.

## Quantile and statistical invariants

1. D11 nearest rank is `k_p=max(1,ceil(p*N))` on one-indexed, stably sorted valid latencies, without interpolation. `p=0` is the minimum, `p=1` the maximum, and `N=0` is undefined.
2. A bounded histogram returns the complete first cumulative bin containing `k_p`; an underflow/overflow primary rank is inadmissible. p99.99 is exploratory.
3. A complete run is the experimental and calibration unit. Packets are never statistical repetitions or split units.
4. D12 uses only the stated complete-run nonnegative-ridge objective: unpenalized fit-only condition intercepts, no global intercept, nonnegative coefficients, positive finite lambda grid, minimum fold-size-weighted admissible CV log-MSE, and larger-lambda exact-tie choice.
5. Folds are condition-stratified and placement-relation blocked. Each participating condition has at least two independent relations; every validation condition occurs in training. Failure is `Condition-Coverage-Insufficient` then `Calibration-Failed`, not estimator substitution.
6. Seen-condition validation may use training-fitted intercepts for absolute log-MSE. Unseen-condition validation never invents or fits an intercept and reports only within-condition rank, top choice, and regret over independent relations.
7. D23 fixes the sole primary estimand to the conditional mean accepted-pair B3/B2 log p99.9 ratio at frozen `l*`; the paired t-test for the weak conditional mean null is the only confirmatory decision rule.
8. `A_bj` is immutable and performance-blind. Adjacent-pair indicators are `A_1_0=A_B1j*A_B0j*E_mem_j`, `A_2_1=A_B2j*A_B1j`, and `A_3_2=A_B3j*A_B2j`.
9. Failed latency is not imputed; runs are not substituted or outcome-dependently rerun; the schedule is not extended based on effects, p-values, intervals, or percentile stability.
10. Planned/attempted/accepted counts, adjacent-pair completion, categorized policy failures, and the policy causing every incomplete block are mandatory. Differential attrition limits interpretation even when the conditional estimand exists.
