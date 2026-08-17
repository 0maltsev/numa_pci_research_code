# Baseline Integrity Matrix

The treatment ladder is strictly incremental. “May differ” means a declared placement field can differ; all other fields/actions must be byte-identical by value or linked to the same content digest within a comparison block.

## Permitted differences

| Field or action | B0 OS defaults | B1 CPU only | B2 CPU + memory | B3 complete placement |
|---|---|---|---|---|
| Logical queue→worker and ownership catalog index | Frozen topology-blind `ReferenceMapping` R0 | Exactly B0/R0 | Exactly B1/R0 | May select another admitted controllable finite entry/worker within the same catalogs/inventories |
| Primary owner cardinality/share | D03: k=1/share=1 | Same | Same | Same; qualified shared-owner profiles are secondary only |
| Data-plane physical-context affinity | No experiment-selected affinity beyond safety cpuset/frontend-required documented default | Deterministic topology-blind CPU rule; applied after faulting | Exactly B1 assignments | Jointly selected feasible context→PU mapping |
| B0/B1 initializer CPU | D21 smallest stable OS CPU ID after exclusions | Exactly B0 | Not the B0/B1 invariant initializer | Not the B0/B1 invariant initializer |
| Material allocation/process | Fresh | Fresh | Fresh | Fresh |
| Memory policy before faulting | Ordinary OS policy | Exactly B0 ordinary policy | Explicit CPU-access-share aggregate-node rule preserving B1 CPUs; no NIC input | Explicit feasible desired/requested distributions from admitted complete plan |
| Page repair after observation | Forbidden | Forbidden | Forbidden; placement mismatch invalidates B2 | Forbidden; placement mismatch invalidates B3 |
| Payload/descriptor/ring/state object identity | Common topology-independent inventory and capacities | Same inventory/capacities | Same inventory/capacities; fresh bound instance | May select location-qualified object from same inventory/capacity contract |
| Logical-role→physical-context grouping | Common RTC/staged semantics and inventory; observed default realization | Deterministic assignment respecting same grouping | Exactly B1 | May choose only grouping admitted by same RTC/staged/co-execution predicates |
| Ownership-share setting action | Reference entry action or explicit no-action by control class | Same | Same | May request only selected direct/validated-indirect entry; observed-only always no-action |
| Desired/requested/applied/observed fields | All four retained; delegated controls explicitly no-action/default | All four retained | All four retained | All four retained |
| Planner status admitted | Baseline construction/read-back valid | CPU-only construction valid | CPU-relative memory construction valid | Only `Feasible` at required fidelity; `Search-Limited`, `Cap-Limited`, `Data-Incomplete`, or fallback are not pooled |

## Fields and actions that never differ within a block

| Domain | Frozen equality proof |
|---|---|
| Source/build | Same repository revision, dependency set, compiler/linker identities and flags, link order, build type, binary/shared-library digests. |
| Packet/application path | Same parser, response operation, state semantics, stages, RTC/staged mode, batching/burst limit, buffer lifecycle, ring algorithm/capacity, error handling. |
| Frontend profile | Same DPDK or AF_XDP profile/version, driver/mode, copy/zero-copy behavior, descriptors/ring lengths, frame/buffer sizes, polling/wakeup/interrupt behavior, and no hidden fallback. |
| NIC and steering | Same NIC/port/BDF, firmware/driver/link, fixed RX/TX queue pairs/counts, RSS key/table/hash fields, flows, descriptor counts, MTU, offloads, moderation. Queue identity is never swapped as a “placement” shortcut. |
| Inventories/capacities | Same logical roles, physical contexts, PUs available, ownership cardinalities/catalog digest, pool/ring/state counts and usable capacities, page size/source, CPU exclusions, SMT/isolation rules. |
| Traffic | Same TG build/path, packet bytes, exact sequence set, flow list/bindings, trace/burst schedule, offered-work rule and resolved rate. No latency-adaptive rate. |
| Timing | Same timestamp source/layer/clock, conversion/wrap handling, qualification domain, capture filter, and overhead procedure. |
| Protocol/telemetry | Same reset, phase order, warm-up, measurement, drain, cooldown, fixed schedule, randomization seed rule, acceptance gates, counter catalog/scope/interval/multiplexing policy. |

## Baseline proofs in records

- `ReferenceMapping` proves R0 without PCIe/NUMA/cost inputs.
- `PageInitializationRecord` proves process/allocation freshness, initializer identity, order, default/requested policy, fault completion, and affinity timing.
- `PageEquivalenceRecord` separately proves order-independent B0/B1 object-wise dTV; `Pair-Pending` never changes execution.
- `CPUAccessProfile` and `LocationQualifiedObject` prove B2's accessor-share rule and desired/requested/observed page distinction.
- `PlacementPlan`, `AppliedPlacement`, and `ObservedPlacement` prove B3 desired/requested/applied/observed separation and prevent the applicator or validator from changing the plan.
- `FrontendRunRecord`, `SequenceManifest`, `TrafficGenerationRecord`, `ClockQualification`, and `TelemetryRecord` prove non-placement equality.
- `AcceptanceRecord`, `AggregatedDataset`, and `StatisticalAnalysisArtifact` retain policy-specific failures and pair attrition; an invalid B2 is never recoded B1, and an invalid B3 is never pooled as fallback.
