# Experimental Implementation Specification

Status: pre-implementation, pre-measurement specification  
Language: English  
Scientific entry point: this file  
Scope: future implementation and execution only; this repository contains no experimental source code or measurement results.
Decision gate: PRE_IMPLEMENTATION_DECISIONS.md; unresolved values must retain its staged status.

## 1. Goals and research questions

### 1.1 Objective

The experiment will determine whether a placement policy that jointly accounts for PCIe root/path locality, NUMA memory, NIC hardware-queue ownership, packet-buffer pools, event rings, polling or interrupt contexts, and runtime workers reduces p99.9 external wire-to-wire latency relative to progressively stronger partial controls. It must also determine when load balancing or contention makes a shortest-locality mapping insufficient.

The experiment is not a comparison of unrelated packet frameworks, application algorithms, NICs, or compiler optimizations. The causal treatment is placement. All non-placement factors are frozen within a comparison block.

### 1.2 Research questions and estimands

Let `B0` through `B3` denote the four policies in Section 6. For every policy attempt scheduled in randomized block `j`, define `A_bj=1` only when policy `b` passes every applicable mandatory performance-blind per-attempt acceptance gate; otherwise `A_bj=0`. Let `E_mem,j=1` only when the final B0/B1 `PageEquivalenceRecord` is `Pair-Equivalent`. Define `A_j^(1,0)=A_B1,j A_B0,j E_mem,j`, `A_j^(2,1)=A_B2,j A_B1,j`, and `A_j^(3,2)=A_B3,j A_B2,j`. For workload condition `l`, `Y_b(j,l)` is the run-level p99.9 external turnaround latency and enters a contrast only when the corresponding pair indicator is one.

- **RQ1 — CPU affinity:** estimate the paired `log(Y_B1/Y_B0)` and absolute difference under otherwise identical conditions.
- **RQ2 — memory binding:** estimate the paired `log(Y_B2/Y_B1)` and absolute difference, isolating the incremental effect of location-qualified RX/TX payload, descriptor, event-ring, and declared state memory after CPU affinity is fixed.
- **RQ3 — complete placement:** estimate the paired `log(Y_B3/Y_B2)` and absolute difference, isolating the incremental effect of joint PCIe/NUMA/queue-owner/queue-to-worker/pool/descriptor/ring/logical-role/physical-execution-context placement.
- **RQ4 — workload dependence:** interaction of the three increments with packet size, offered load, burst shape, flow skew, queue count, and worker count.
- **RQ5 — model explanation:** change in selected placements and measured responses when each cost term is removed, plus rank association between term values, relevant counters, and run-level p99.9.
- **RQ6 — stability:** preservation of policy ranking and cost-model ranking after predeclared workload changes and at least one topology change when the stand provides a second distinguishable NIC port/root path or a second testbed.

### 1.3 Hypotheses and sole primary estimand

There is one confirmatory estimand. A single reference condition `l*` is frozen after a performance-blind feasibility pilot using only feasibility, rate accuracy, stability, and capacity decision rules. Let `J_32={j: j was scheduled at l* and A_j^(3,2)=1}`. For `j in J_32`,

`D_j = log(Y_B3(j,l*) / Y_B2(j,l*))`, and `theta_32^acc = E[D_j | A_j^(3,2)=1, j scheduled at l*]`.

The expectation is over accepted independent pairs under the frozen testbed and randomized policy-order procedure. `exp(theta_32^acc)-1` is the conditional geometric relative change in run-level p99.9 among scheduled blocks where both B3 and B2 passed their gates. It is not an unconditional effect over all scheduled blocks. The confirmatory hypotheses are `H0: theta_32^acc >= 0` and `H1: theta_32^acc < 0`. The sole primary decision uses a one-sided paired t-test at `alpha = 0.05` on the accepted run-pair `D_j` values and the aligned upper one-sided confidence bound for `theta_32^acc`; a two-sided 95% Student interval is also reported for estimation. Pairwise label swapping is only a secondary sharp-null sensitivity.

RQ1 and RQ2 are key secondary incremental questions over the corresponding accepted-pair sets; their paired log-ratio tests form one Holm-controlled family. RQ4–RQ6, absolute differences, direct `B3/B0`, and all p99.99 analyses are secondary or exploratory. None may replace the primary estimand after outcomes are observed. Throughput, goodput, and correctness are co-constraints: a latency change is not accepted as beneficial if it is obtained by reducing valid work or changing the packet path. Policy-specific attempt acceptance and adjacent-pair completion are mandatory secondary operational-feasibility outcomes; differential attrition limits interpretation even when the conditional latency estimand is available.

### 1.4 Scope profiles

Two frontend profiles are specified:

1. **DPDK profile:** userspace driver, busy polling, explicit RX/TX queues, huge-page packet pools, and explicit logical queue ownership.
2. **AF_XDP profile:** native-driver mode where supported, with frozen copy/zero-copy, UMEM, ring, wakeup, and polling/interrupt behavior.

One profile must be declared primary after an off-stand/stand feasibility gate. All four baselines are compared within that profile. The other profile, if implemented, is an external-validity replication and never shares a primary statistical family with the first.

The primary confirmatory ownership mode is frozen as single owner for each controllable non-null direction (k=1, share 1). A shared-owner mode remains a secondary or replication profile until the frontend emits a finite versioned ownership catalog and capability evidence that its shares are directly enforceable, reproducibly indirectly controlled, or observable within a frozen validation range.

## 2. Experimental invariants

### 2.1 Freeze rule

An invariant is recorded once per experiment campaign and included by digest in every run. Changing one creates a new campaign or explicit experimental factor; it cannot be changed silently between placement policies. Every categorical value must be literal, not “default,” unless the exact default was queried and recorded.

| Domain | Values that must remain constant within a comparison block | Required proof |
|---|---|---|
| Source/build | Repository revision, dependency lock, compiler and linker identity, all flags, link order, build type, generated feature set, binary and shared-library digests | Build manifest and cryptographic checksums |
| Application | Packet parser, response operation, application state, stage count, ring algorithm, batching limit, buffer lifecycle, error handling | Configuration digest and startup self-description |
| Packet frontend | DPDK or AF_XDP profile; exact version; driver; queue API mode; descriptors/ring lengths; buffer/frame size; burst limit; polling/wakeup mode | Frontend manifest plus read-back |
| NIC | Model, PCI BDF, port, firmware, driver, link mode, negotiated speed, lane width/generation, RSS key/table, flow rules, RX/TX queue count, descriptor count, MTU, offloads, interrupt moderation | Device/driver dumps and topology snapshot |
| CPU | Online CPUs, SMT state, allowed experiment CPUs, reserved control/OS CPUs, frequency driver/governor, turbo/boost policy, C-state policy, scheduler/isolation boot parameters | Environment manifest and per-run telemetry |
| Memory | DIMM/NUMA inventory, huge-page size and count, pool capacity, allocation order, pre-fault/touch rule, memory-lock policy, swap policy, transparent huge-page policy | Inventory, allocation record, page-location validation |
| Pipeline | Logical stage structure; queue/worker/I/O-role/physical-execution-context inventories and counts; RTC versus staged role-grouping predicates; topology-agnostic reference worker and ownership-catalog indices for B0--B2; finite frozen ownership catalog and control classes; allowed B3 catalog entries; pool/ring counts and capacities; TX return path; control-plane placement | Workload, capability, ownership-catalog, and topology-independent pipeline manifests |
| Traffic | Generator revision/binary, NIC/firmware/driver, cable/switch path, packet bytes, sequence field, flow keys, traffic trace, rate schedule, burst trace, expected sequence range | Traffic manifest and trace digest |
| Timing | Timestamp source and layer, clock domain, calibration, conversion, wrap handling, synchronization profile, capture filter, measurement overhead procedure | Clock manifest and pre/post calibration records |
| Run protocol | Provisioning, warm-up, steady-state, duration/sample rule, drain, cooldown, block definition, randomization seed, validation and exclusion rules | Campaign protocol digest |
| Telemetry | Counter list, scope, event encodings, sampling interval, multiplexing policy, wrap widths, mandatory/optional designation | Telemetry schema and availability audit |

### 2.2 Frontend-specific frozen controls

For DPDK, freeze the environment abstraction layer configuration; port and queue setup; RX/TX descriptor counts; mempool count, capacity, element size, cache size, private metadata, and backing huge-page size; burst limit; offloads; multi-segment behavior; cleanup path; driver binding; IOMMU mode; RSS key and hash fields; flow rules; owner inventory/cardinality; the topology-agnostic reference ownership-catalog entries; every finite B3 entry and its share vector/control class; and whether poller and worker roles share one physical execution context.

For AF_XDP, freeze XDP driver/native/generic mode; copy or zero-copy; UMEM frame size/count/headroom; RX/TX/fill/completion ring sizes; finite allowable socket-to-queue ownership entries and the B0--B2 reference catalog index; shared-UMEM behavior; `need_wakeup`; busy-poll budget and timeout if used; interrupt moderation; XDP program/object digest; BPF map configuration; driver and kernel; and whether poller and worker roles share one physical execution context or use staged contexts.

Do not compare DPDK zero-copy busy polling against AF_XDP copy mode and attribute the difference to placement. Do not allow B3 to use a different burst size, descriptor count, or pool cache than B0–B2.

### 2.3 Allocation hygiene

Each attempted run uses a fresh process lifetime and fresh material allocations. Pools and rings are destroyed and recreated according to the same stable order. The OS page cache, allocator history, RSS table, queue state, and device counters are handled by a fixed reset protocol. Unused environment variables, command-line order, and process launch environment are normalized and recorded because layout-sensitive measurement bias is plausible. A baseline must never inherit another policy's pages, warmed queues, or mapping.

For B0 and B1, one topology-blind initialization context allocates and faults all material objects under the same default OS memory policy before data-plane affinity is applied. It selects the smallest stable OS CPU identifier in the initialization cpuset after functional exclusions and receives no NIC BDF, PCIe ancestry, NUMA-distance, page-location, cost-model, or latency input. Allocation/fault order and access pattern are identical. The initializer is not a data-plane role and produces a separate record.

For every material object m, retain desired distribution, requested policy, and observed page-distribution vector nu_obs(m) as different fields. A B0/B1 pair is eligible for RQ1 only when observation coverage is compatible and d_TV(nu_obs_B0,nu_obs_B1) = 0.5 sum_n |nu_obs_B0(n)-nu_obs_B1(n)| <= tau_mem for every mandatory object. The page method and tau_mem are selected from measurement resolution and repeated initializer behavior in a performance-blind pilot and frozen before confirmation. Unobservable mandatory location yields Page-Equivalence-Unsupported; a failed inequality yields Page-Equivalence-Failed. Neither status may be repaired after latency is inspected.

## 3. Testbed requirements

### 3.1 Physical arrangement

The confirmatory arrangement requires at least two physical hosts:

- a **traffic generation and measurement host (TG)** that transmits a sequenced request and timestamps the corresponding response in one clock domain; and
- a **multi-socket SUT** that executes the frozen packet pipeline and returns the response.

Direct links are preferred. If a switch is required, its model, firmware, path, queueing/QoS configuration, competing ports, and counters are recorded and held invariant. Unrelated traffic is prohibited on the measurement path. A third passive timestamp host is optional but cannot replace the primary one-clock turnaround metric unless its clock relation is validated.

Two hosts are mandatory because internal SUT timestamps can omit NIC, PCIe, driver, DMA, and queueing segments, and because running the generator on the SUT introduces CPU/memory/I/O contention that changes the treatment. A one-host loopback or colocated-generator mode is diagnostic only. The primary external turnaround measurement includes both physical links and the SUT; the link contribution remains constant across matched policies.

### 3.2 SUT requirements

The SUT must have:

- at least two physical CPU sockets and at least two independently identifiable NUMA memory domains;
- at least one PCIe NIC whose BDF and complete exposed ancestry are available;
- at least one eligible CPU/memory domain local or nearer to the NIC and one distinguishable remote candidate;
- controllable RX/TX queues and a method to verify per-queue activity;
- enforceable worker affinity and NUMA allocation policy;
- sufficient huge-page or UMEM capacity for identical pools in all baselines;
- isolated CPUs for packet workers plus reserved CPUs for OS/control/telemetry work; and
- stable power/frequency configuration or telemetry sufficient to reject unstable runs.

A second NIC port below a distinct root path, or a second multi-socket machine, is strongly preferred for RQ6. A single topology can complete RQ1–RQ5 but limits external validity.

### 3.3 Topology and device information to record

Record machine and boot identities; firmware/BIOS; CPU vendor/model/stepping/microcode; sockets, dies if exposed, cores, PUs, SMT, cache levels/sharing; NUMA nodes, CPU lists, memory sizes, distances, and DIMM population; socket-interconnect type and exposed link structure; PCI domains, root ports, bridges, switches, endpoint BDFs, ACS/IOMMU grouping, negotiated link generation/width, maximum payload/read-request settings where available; NIC ports, queues, RSS capabilities, MSI-X vectors, IRQs, firmware, driver, offloads, timestamp capabilities, and hardware counters. Unknown values remain explicit.

### 3.4 Time and latency measurement

The primary profile follows this explicit chain:

`TG request timestamp/transmit -> physical link -> SUT NIC ingress -> RX descriptor and payload DMA -> poll/IRQ progress -> optional event-ring handoff -> worker/application state -> response construction -> TX payload/descriptor publication and doorbell -> SUT NIC transmit -> physical link -> TG response timestamp`.

The two primary timestamps are in the same TG clock domain. Select the timestamp implementation using this decision tree:

1. use an external tap/FPGA or equivalent instrument that timestamps request egress and response ingress in one validated hardware clock when available;
2. otherwise use correlated TX/RX hardware timestamps from the same TG NIC physical hardware clock, but only if timestamp matching capacity, capture semantics, timestamp-loss behavior, and rate-dependent bias pass qualification; or
3. otherwise use TG software timestamps only for diagnostic data unless the measured error bound, timestamp loss, and perturbation are below the frozen fraction of the smallest scientifically relevant effect.

The selection, failed branches, and evidence are frozen before confirmatory execution. Fixed-path calibration is reported but not subtracted from the primary turnaround value.

One-way timestamps are secondary. They require hardware support at both ends, a synchronization method traceable to physical hardware clocks, pre/post offset and drift records, an error bound below the frozen measurement-error gate, and invalidation when that bound is exceeded. Precision Time Protocol lock alone is not sufficient evidence; offset, drift, timestamp layer, and residence behavior must be measured.

### 3.5 Isolation and environment manifest

The hosts must be isolated from unrelated users and traffic. Disable or record cron jobs, monitoring agents, frequency-changing daemons, automatic updates, and shared management traffic. Reserve control-plane CPUs and verify that packet/IRQ/control tasks do not leak onto worker CPUs. Record room/inlet and CPU/NIC temperatures when available.

The future implementation emits a machine-readable `EnvironmentManifest` with: schema version; campaign ID; host/boot IDs; collection timestamps; hardware and firmware inventory; kernel/driver/frontend/build identities; power/isolation settings; clock description; topology-snapshot digest; raw-source artifact references; missing fields; and checksums. No human-readable table may be the only environment record.

## 4. Topology-discovery requirements

Every discovered fact requires an independent validation path or an explicit “single-source” warning. Validation means a logically independent interface, a controlled probe, or read-back after application—not merely formatting the same underlying file twice.

| Fact | Primary collection | Independent validation | Failure handling |
|---|---|---|---|
| Packages, cores, PUs, cache sharing | hwloc object hierarchy and CPU sets | Linux online/present CPU lists and cache/shared-CPU maps | Stop if membership conflicts; permit unknown cache only in a named fallback |
| NUMA nodes and CPU lists | hwloc NUMA objects | Linux node CPU lists and process-visible affinity | Stop on contradictory membership |
| NUMA distances | hwloc/OS distance matrix | Pairwise unloaded memory-latency/bandwidth calibration, labeled empirical | Keep both; do not overwrite OS distance with measured latency |
| NUMA memory capacity/free space | OS node memory inventory | Allocation feasibility and post-allocation page inventory | Reject pools exceeding safe capacity |
| PCI endpoint identity | selected interface to PCI BDF join | hwloc PCI object plus sysfs device link/driver identity | Stop if port cannot resolve uniquely |
| PCIe ancestry/root path | hwloc I/O tree and sysfs parents | Device link status plus topology utility or firmware record if available | Mark collapsed root/switch details unknown; never assume node 0 |
| PCIe link generation/width | device link attributes | hardware inventory/tool read-back and bandwidth plausibility check | Record disagreement and exclude calibrated capacity term |
| NIC-to-NUMA hint | sysfs/device locality and hwloc nearest CPU set | controlled local/remote DMA or queue-processing probe | Treat `-1` as unknown, not node 0 |
| NIC ports and hardware queues | driver/frontend capability query | startup queue creation plus per-queue counters | Stop if declared queue cannot be created/observed |
| Ownership controls and service shares | versioned frontend capability probes and finite catalog construction | request/read-back tests plus per-owner progress accounting over repeated workloads | Classify each entry as direct, validated-indirect, observed-only, or unsupported; observed-only shares are frozen inputs, not B3 controls |
| RSS key/hash/indirection | device/frontend query | deterministic flow-to-queue probe and counters | Reject run if mapping differs |
| IRQ/MSI-X ownership | OS IRQ/vector mapping | counter deltas during single-queue probe and effective IRQ affinity | Use only for interrupt profiles; stop on ambiguous mandatory mapping |
| Logical-role realization and polling ownership | application/frontend role-to-physical-context self-description | OS-observed thread/context IDs, CPU masks, sampled current CPU, queue counter delta, RTC one-thread and staged-distinct-thread checks | Reject undeclared poller/worker, illegal role merge, double-counted RTC slot, staged role collapse, or CPU escape |
| Huge-page inventory | OS huge-page/node inventory | successful reservation/allocation and pool backing record | Stop on shortfall; do not change page size automatically |
| Memory policy and typed object locations | desired vector, requested/default policy, and read-back for each RX/TX payload, RX/TX descriptor where controllable, event ring, and state object | physical page-to-node inventory after the declared fault sequence; repeated topology-blind B0/B1 initializer for dTV repeatability | Reject B2/B3 if a mandatory object violates its allowed distribution; reject/mark unsupported B0/B1 pairs failing coverage or dTV; uncontrollable descriptors must be explicit before profile freeze |
| Actual physical-context affinity | effective affinity/cpuset per independently schedulable context | repeated observed CPU samples, scheduler telemetry, and role-to-context join | Reject execution outside the mask or inconsistent role/context identity |
| LLC/DDIO relation | platform capability and documented configuration | cache/uncore counters under a controlled I/O probe if available | Make cache term unavailable rather than infer behavior |
| Interconnect/PCIe counters | platform event audit | controlled direction/load probe with sign and scaling checks | Label optional or reject if designated mandatory for an RQ5 contrast |
| Snapshot consistency | host ID, boot ID, device identity, timestamps | pre-run and post-run digest of invariant topology fields | Invalidate run on change |

The topology snapshot contains raw hwloc XML, the normalized graph, relevant sysfs captures, BDF joins, CPU/node lists, queue metadata, huge-page inventory, and collection errors. It is immutable and content-addressed. CPU or NIC hotplug, a reboot, driver reload, queue-count change, firmware change, or link renegotiation creates a new snapshot and campaign block.

## 5. Future implementation decomposition

### 5.1 Common conceptual schemas

The components exchange the following records. These are schemas and invariants, not programming-language definitions.

| Record | Required content |
|---|---|
| `TopologySnapshot` | schema/snapshot/host/boot IDs; typed vertices and edges; typed attributes with unit, provenance, confidence, timestamp, and raw-source reference; validation findings; unknowns; digest |
| `FrontendProfile` | profile type/version; driver/mode; fixed RX/TX queue pairs; payload/descriptor/event-ring controls; logical worker/I/O-role and physical-execution-context inventories; RTC/staged grouping predicates; owner cardinalities; `OwnershipCatalog` reference; capabilities; required privileges; verification predicates; digest |
| `FrontendCapabilityProfile` | frontend/driver/kernel/NIC identity; each control surface; direct, validated-indirect, observable-only, or unsupported class; read-back method/coverage; privileges; qualification evidence; validity domain; schema version and digest |
| `OwnershipCatalog` | schema/version/digest and freeze time; pipeline/direction; stable finite entry indices; owner-role set; fixed dimensionless planning-share vector; cardinality; control class; requested action if any; observed-share estimator and admissible range; capability-evidence digest; primary/secondary eligibility |
| `ReferenceMapping` | topology-agnostic B0--B2 queue-to-worker map; direction-specific finite ownership-catalog indices; derived owner sets/planning shares; stable construction rule; queue/role/context/catalog inventory digests; no PCIe/NUMA/path-cost inputs |
| `CPUAccessProfile` | each material memory-object role; actual CPU accessor physical-context IDs; per-accessor nonnegative demand shares summing to one; derivation source; dominant-accessor and split-access flags; digest frozen before baseline execution |
| `WorkloadSpec` | packet bytes and on-wire length; flow keys/distribution; offered-rate rule and resolved rate; trace digest; burst model; queue/worker/I/O-role/physical-context counts; RTC/staged mode; service operation; exact expected sequence-set reference; fixed phase/sample rules |
| `CalibrationDataset` | one row per accepted complete calibration run; nearest-rank log-p99.9 response; frozen normalized feature vector/order/groups; condition and placement-relation IDs; split/fold IDs; condition-by-placement-relation coverage map; fold-admissibility findings; gate evidence; all input digests; no packet-level pseudo-replication |
| `CalibrationModelArtifact` / `CostModel` | RX/TX payload and descriptor DMA primitives; context/worker/ring/state/MMIO/cache terms; capacity-resource surcharge functions; term-ownership ledger; transformations/scales/units; exact nonnegative-ridge loss and `n_tr`; positive lambda grid; condition-stratified blocked folds and coverage audit; minimum-MSE/larger-lambda tie rule; effective coefficients; rank/collinearity actions; factorized alpha/beta with beta_top=1; seen-condition absolute validation; unseen-condition rank/top-choice/regret transfer; admission status and validity domain; seed/order/digest |
| `PlacementPlan` | snapshot/profile/workload/model/reference-map/catalog digests; completion and fallback status; per-queue RX/TX payload pools, descriptor objects, explicit null/material ring and state, worker role, finite ownership indices and derived owner sets/planning shares/control classes, role-to-physical-context map, and each active context's PU; location distributions; occupancy/service/capacity/SMT/isolation proof; cost decomposition; ordered actions; validation predicates |
| `CandidateSearchAudit` | raw/unpruned/exposed candidate counts and domain-exhaustion flag per queue; dominance certificates; cap values/expansions; search-node/depth budgets and consumption; conflict witnesses; exact neighborhood counts/passes; tie-break trace; `Feasible`/`Search-Limited`/`Cap-Limited`/`Data-Incomplete` status; external exact certificate reference only if separately present; time and peak memory |
| `AppliedPlacement` | plan digest; desired values; requested actions/values; prior-state journal; action-by-action status; explicit no-action for observable-only shares; timestamps; rollback capability; resulting configuration references |
| `PageInitializationRecord` | attempt/policy/object IDs; fresh-allocation proof; initialization context and topology-blind rule; desired/requested/default policy; allocation/fault order and pattern; start/end; immutable observed page counts/distribution/coverage; per-attempt observation-integrity status; snapshot and schema digests; no pair distance |
| `PageEquivalenceRecord` | prospective pair key and immutable input-record digests; `Pair-Pending` when exactly one mate exists; for a final record, paired B0/B1 IDs, mandatory object join, both observed vectors and coverage, per-object total-variation value, frozen tau_mem and pilot digest, maximum, and `Pair-Equivalent`, `Page-Equivalence-Failed`, or `Page-Equivalence-Unsupported`; final records supersede by reference and never mutate pending records |
| `ObservedPlacement` | independent logical-role-to-thread/context observations; physical-context CPU observations and slot accounting; page-location distributions for every material payload/descriptor/ring/state object; explicit null-object confirmation; RX/TX owner, worker, queue probes, observed service-share vector and coverage; desired/requested/observed deviations; acceptance range and pass/fail |
| `ExactReferenceResult` | raw catalog and input digests; resource limits/estimates; Cartesian size; visited/feasible/per-constraint rejection counts; best placement/value/tie trace; elapsed time/peak memory; Exact-Feasible, Proven-Infeasible, Exact-Budget-Exceeded, or execution-error status; exhaustion certificate when applicable |
| `SequenceManifest` | campaign/block/run IDs; arbitrary exact expected set or content-addressed generator rule; per-sequence request/flow binding; transmit-order digest; expected count; packet/trace digests; commitment time |
| `ClockQualification` | timestamp decision-tree branch and rejected branches; hardware/software boundary; clock IDs; resolution/quantization; wrap rule; matching capacity; rate-dependent bias; timestamp loss; calibration/error/overhead bounds; validity domain |
| `AcceptanceRecord` | immutable per-attempt performance-blind gate values and `A_bj`; missing/corrupt/duplicate/ambiguous/out-of-range counts; planner/model-domain/apply/rollback/read-back/page/correctness/timestamp/telemetry/environment evidence; one primary categorical failure reason plus all failed gates; pair key and contrast admission status (`Pair-Pending`, admitted, or excluded) by contrast |
| `AnalysisPlan` | reference condition; attempt and pair indicators; conditional accepted-pair primary estimand/hypotheses; one-sided paired t-test and aligned confidence bound; mandatory policy/pair attrition and operational-feasibility report; assumptions/diagnostics; sharp-null randomization sensitivity; frozen optional attrition weighting/bounding rules or explicit none; pilot separation; fixed attempt schedule and power inputs; quantile rule; multiplicity methods; exploratory labels; digest frozen before unblinding |
| `RunRecord` | campaign/block/run/policy/attempt IDs; all input digests; phase times; sequence/clock/acceptance references; `A_bj`; policy-specific failure category; prospective pair keys and pending/final contrast-admission references; telemetry references; validation and exclusion status; data checksums |

All records use explicit units, stable identifiers, schema versions, and content digests. “Unknown,” “not applicable,” “not collected,” and numeric zero are different values. An error record contains component, stage, severity, affected facts, recovery/rollback status, and whether scientific data may be admitted.

### 5.2 Complete implementation contract registry

Every contract below emits an immutable record with schema version, record ID, producer identity/version, creation time and clock, campaign/stage ID, all input content digests, its own canonical-content digest, status, and error list. Units are mandatory for every numeric field; dimensions that are not applicable use an explicit state rather than zero. A consumer rejects an unsupported schema, a digest mismatch, an unknown mandatory unit, or an input outside the producer's declared validity domain.

| ID / contract | Purpose; producing stage -> consuming stage | Inputs | Output and required fields; units | Invariants; version/digest | Error statuses | Verification procedure |
|---|---|---|---|---|---|---|
| C01 Topology inspector | Capture raw host facts without inference; fixture/stand discovery -> graph builder and qualification | Host/boot identity, collection policy, privilege inventory, required-source list | RawTopologyObservation: source URI/class, raw capture reference, object/source IDs, raw value, unit, provenance, collection start/end, access result | One collection epoch; read-only; source bytes and manifest are versioned and digested | Source-Inaccessible, Host-Changed, Device-Disappeared, Partial-Collection | Recollect invariant IDs; compare raw-source digest; hand-check representative fixture facts |
| C02 Normalized graph builder | Join facts into typed G_s; graph construction -> serializer, planner, calibrator | C01 records, join rules, graph schema, required-fact policy | TopologySnapshot: typed vertices/edges/attributes, source links, unit, confidence, unknown inventory, host/boot/snapshot IDs | Unique typed identity; directional relations; unknown never equals zero; schema and source-set digests | Duplicate-Identity, Contradictory-Membership, Dangling-Queue, Unit-Mismatch, Stale-Input | Independent hwloc/sysfs joins, graph invariants, golden fixtures, pre/post snapshot comparison |
| C03 Frontend capability profile | State which controls/read-backs exist; off-stand/stand frontend qualification -> catalog, planner, applicator, validator | Frontend/NIC/driver/kernel identities, control probes, privilege evidence | FrontendCapabilityProfile: surface ID, direct/indirect/observed-only/unsupported class, request/read-back methods, coverage, unit, validity domain, evidence refs | No unsupported surface becomes controllable; exact identity/version/digest ties capability to environment | Capability-Unsupported, Readback-Ambiguous, Privilege-Missing, Qualification-Failed | Functional probes, independent read-back, fault injection, repeatability under the intended workload domain |
| C04 Ownership catalog | Make owner/share decisions finite; capability qualification -> reference mapping, planner, frontend, validator | C03, role/queue inventories, cardinalities, share-observation method | OwnershipCatalog: queue/pipeline/direction, stable entry index, owner IDs, dimensionless fixed planning shares, cardinality, control class, request action, observed range/coverage, primary eligibility | Finite nonempty index set; shares sum to one for k>0; k=0 has one null entry; k=1 share is one; catalog/version/digest frozen | Catalog-Empty, Invalid-Share, Nonfinite-Domain, Control-Class-Mismatch, Catalog-Stale | Exhaustive schema validation, repeated capability/read-back probe, stable-order/digest replay |
| C05 Graph serializer | Produce deterministic portable graph; graph construction -> fixtures, planner, archive | C02 snapshot, canonical ordering and encoding rules | SerializedGraph: complete typed graph, units/provenance, source digest list, canonical-order declaration, serialization digest | Round-trip preserves every field and unknown; same input/version yields byte-identical canonical digest | Unsupported-Schema, Roundtrip-Mismatch, Noncanonical-Order, Digest-Mismatch | Serialize/deserialize/serialize round trip and cross-process digest comparison |
| C06 Calibration dataset | Construct run-level fit table and prove split/fold admissibility; accepted calibration acquisition -> estimator/model artifact | Accepted calibration runs, nearest-rank summaries, feature ledger/transforms, condition and placement-relation IDs, split/fold plan | CalibrationDataset: run/condition/placement-relation IDs, log-p99.9 response, latency unit before log, N, normalized feature vector/order/group, gate, split/fold, condition-by-placement-relation coverage map, candidate-fold and admissibility findings, all digests | One row per complete accepted run; never per packet; no confirmatory IDs; frozen feature order/transform; all replicates of a relation co-folded; each CV condition has at least two independent relations and every validation condition occurs in training | Run-Rejected, Response-Undefined, Feature-Missing, Split-Leakage, Condition-Coverage-Insufficient, Digest-Mismatch | Recompute quantile/features; assert disjoint IDs/relation blocks; independently reconstruct coverage map and every fold predicate |
| C07 Calibration model artifact | Fit and admit one reproducible score; calibration analysis -> planner and sensitivity analysis | C06, positive lambda grid, solver/tolerance, rank/collinearity and admission rules | CalibrationModelArtifact: exact objective and n_tr, folds/losses/coverage audit, selected lambda, fit-only intercepts, effective coefficients, merge/disable ledger, alpha/beta, uncertainties, seen-condition absolute metrics, unseen-condition rank/top-choice/regret metrics, validity domain/status | Nonnegative coefficients; unpenalized condition intercepts and no global intercept; minimum admissible-fold CV MSE with larger-lambda tie; no absolute MSE for unseen conditions; beta_top=1; factorization reproduces coefficients up to common scale; version/digest immutable | Condition-Coverage-Insufficient, Calibration-Failed, Rank-Deficient, Topology-Scale-Zero, Validation-Failed, Out-Of-Domain | Independent refit/replay, coefficient-factorization equality, fold/coverage audit, seen/unseen metric-domain audit, held-out metric recomputation |
| C08 Placement planner | Emit deterministic feasible plan or bounded non-plan status; planning -> applicator/validator | C02/C03/C04/C07, workload, constraints, R0 or B3 scope, CPU-access profile, budgets | PlacementPlan and CandidateSearchAudit: all assignments/catalog indices, desired distributions, proofs, cost terms, tie key, exposure/search counts, time in ns, peak bytes | Enumerates only catalog entries; all hard constraints; deterministic ties; heuristic never emits Proven-Infeasible; all input versions/digests embedded | Feasible, Search-Limited, Cap-Limited, Data-Incomplete, Model-Out-Of-Domain, Stale-Input | Deterministic replay, full constraint recomputation, catalog-membership and score-sum audit |
| C09 Exact-small reference solver | Certify optimum or finite infeasibility; off-stand exact campaign -> planner-quality analysis | Uncapped raw finite catalogs, full constraints/J/tie rule, Q/Cartesian/time/memory budgets | ExactReferenceResult: Cartesian size, visited/feasible/rejection counts, optimum/value, tie trace, elapsed ns, peak bytes, input/budget digests, exhaustion certificate | No heuristic pruning/output; every global combination checked; Proven-Infeasible only when visited equals full size | Exact-Feasible, Proven-Infeasible, Exact-Budget-Exceeded, Exact-Execution-Error | Manual minimal fixtures, independent count reconciliation, optimum/tie hand checks, certificate replay |
| C10 Placement applicator | Request only declared controls and journal rollback; integration/run setup -> validator and orchestrator | C08 plan, C03 capability, prior-state record, authorization | AppliedPlacement: desired fields, requested actions/values, no-action markers, action statuses/times, prior state, rollback plan/result | Never edits plan; observed-only share has no setting action; dependency order; journal and plan/input digests | Apply-Prerequisite-Failed, Privilege-Missing, Partial-Apply, Rollback-Failed, Host-Dirty | Independent read-back, action fault injection, reverse-order rollback and prior-state comparison |
| C11 Page initializer | Create/fault fresh objects without hidden carry-over and record one attempt; run setup -> validator/orchestrator | Policy, object inventory, default or explicit memory policy, B0/B1 initializer rule, fault order/pattern | PageInitializationRecord: fresh allocation ID, object/address-span reference/bytes, page bytes/count, context/CPU, desired/requested policy, fault coverage, start/end, immutable observed-distribution/coverage ref and integrity status; no dTV | Fresh per attempt; B0/B1 same topology-blind CPU/default policy/order and finish before data affinity; B2/B3 policy-specific; no wait for matching policy | Allocation-Failed, Fault-Incomplete, Initializer-Escaped, Inherited-State, Policy-Request-Failed, Page-Observation-Incomplete | Allocation IDs, complete coverage accounting, repeated default-policy runs, order trace and affinity timestamp comparison; assert no pair field is produced |
| C12 Observed-placement validator | Validate one attempt and, only when both immutable mates exist, evaluate page equivalence; pre/post run validation and post-pair join -> orchestrator/acceptance/aggregator | C02/C04/C08/C10/C11, independent OS/frontend/page probes, optional matching B0/B1 record, tau_mem | ObservedPlacement plus PageEquivalenceRecord: role/context/CPU, page vectors/coverage, owners, observed shares/ranges, queues, desired/requested/observed deltas; pending or final pair input digests, object join, dTV and status | Validator never mutates; every mandatory attempt fact has coverage/unit; observable-only share is not called applied; one missing mate emits Pair-Pending; final pair gate covers every mandatory object and changes only RQ1 pair admission | Placement-Mismatch, Share-Out-Of-Range, Pair-Pending, Page-Equivalence-Failed, Page-Equivalence-Unsupported, Observation-Incomplete | Independent probes, repeated CPU/page samples, per-queue traffic probe, immutable-record join and dTV recomputation in both arrival orders |
| C13 Packet-I/O frontend | Execute invariant packet path; integrated dataplane -> ring/worker/oracle/telemetry | C03/C04, profile, queue/pool bindings, packet schema, ownership entry, role/context mapping | FrontendRunRecord: port/BDF/queue handles, owner identities, mode/offloads/descriptors, per-queue counters with units/width, packet events, self-description | Same path/logic/config across B0--B3; no hidden mode fallback; B0--B2 equal R0; B3 entry belongs to catalog | Queue-Create-Failed, Link-Changed, Hidden-Fallback, Undeclared-Copy, Counter-Ambiguous | Startup self-description, driver read-back, deterministic flow probe, counter reconciliation |
| C14 Memory-pool manager | Manage typed payload/descriptor/state storage; run setup/dataplane -> frontend/worker/validator | C11 allocations, object schemas, capacities/page source, lifecycle and ownership rules | MemoryObjectRecord: typed ID/role, address reference, usable/reserved bytes, element/page bytes, count, null/material, lifecycle, desired/requested/observed locations | Identical usable capacity; no cross-run reuse; null objects allocate zero; units and bounds explicit; record version/digest | Capacity-Mismatch, Page-Source-Wrong, Object-Reused, Bounds-Violation, Location-Unobservable | Allocation/element accounting, canary/bounds checks, page record join, teardown proof |
| C15 Event-ring stage | Transfer events safely or represent no handoff; dataplane -> worker/oracle/telemetry | Ring object, producer/consumer IDs, capacity/elements, plan | RingRecord: ring ID, capacity slots/bytes, producer/consumer sequences, occupancy/high-water, generation, handoff events, null marker | Identical algorithm/capacity; monotone extended sequences; 0<=occupancy<=capacity; null only for valid RTC | Ring-Lapped, Sequence-Invalid, Producer-Stalled, Consumer-Stalled, Sharing-Undeclared | Fault-injected wrap/lapping fixtures, end-drain equality, per-event sequence reconciliation |
| C16 Worker stage | Execute invariant service and return response; dataplane -> frontend/oracle/telemetry | Worker role/context/CPU, input event, packet/state objects, service contract | WorkerRecord: request/response sequence, role/context/thread IDs, operation result, progress, cycles/time units, CPU samples, integrity status | Same service/batching; RTC one context/slot with summed demand; staged contexts distinct; deterministic response semantics | Affinity-Escape, Worker-Stall, Service-Error, Response-Invalid, Capacity-Gate-Failed | Known packet fixtures, role/thread join, sampled CPU masks, response integrity oracle |
| C17 Traffic generator | Emit committed invariant trace; run measurement -> timestamp backend/sequence/oracle | Workload, packet/flow schema, exact trace, start/phase contract, clock profile | TrafficGenerationRecord: intended and actual packets/s and bit/s, trace/flow digest, send events, link counters, generator utilization | No latency-adaptive rate; same trace digest in block; expected set committed first; unit definitions explicit | Rate-Out-Of-Tolerance, Generator-Saturated, Link-Fault, Trace-Mismatch, Timestamp-Loss | Generator loop/known receiver, actual-rate integration, manifest/transmit reconciliation |
| C18 Timestamp backend | Produce qualified raw time evidence; clock qualification/run measurement -> oracle/aggregator | Selected tier, clock/capture configuration, packets/events, qualification artifact | TimestampRecord: raw ticks, clock/epoch, direction/layer, tick unit/frequency, wrap width/extension, conversion, validity; qualification/error/overhead refs | One valid primary clock domain; extend before subtracting; no intermediate rounding; domain covers rate/volume | Clock-Step, Wrap-Ambiguous, Timestamp-Ambiguous, Loss-Gate-Failed, Qualification-Out-Of-Domain | Known-delay/pre-post trials, wrap fixtures, enabled/disabled overhead, tick-to-time replay |
| C19 Expected-sequence manifest | Commit denominator and matching keys before receipt; traffic preparation -> TG/oracle/aggregator | Campaign/block/run IDs, exact deterministic set/rule, packet/flow/trace schema | SequenceManifest: exact sequence set/rule and count, transmit order, request/flow binding, digests, commitment time | Immutable before receive analysis; independent of first/last observed packets; unique expected identity | Manifest-Late, Duplicate-Expectation, Rule-Nonreproducible, Digest-Mismatch | Independent expansion/count/digest; compare TG transmission index without using receiver state |
| C20 Correctness oracle | Classify every expectation/response and create latency-eligible set; receive processing -> acceptance/aggregator | C18/C19, all response candidates, packet/binding rules | OracleReport: per-sequence candidates/categories, valid set, missing/corrupt/duplicate/ambiguous/out-of-range/reorder counts, raw-latency refs, drain/integrity status | Exactly one final category per expectation; valid iff exactly one fully valid candidate; totals reconcile; invalid never enters latency sample | Integrity-Failed, Duplicate, Ambiguous, Timestamp-Invalid, Accounting-Mismatch | Hand-built loss/prefix/suffix/wrap/reorder fixtures and raw receive-count reconciliation |
| C21 Run orchestrator | Enforce phase/order/randomization without outcome-dependent reruns; campaign execution -> all runtime components/aggregator | Campaign matrix/order seed, policy plan, reset/init/apply/gate/warm/run/drain/cooldown rules | RunRecord/PhaseRecord: all IDs/digests, ordered phase boundaries, action/gate refs, A_bj, prospective pair key/status, attempt/exclusion/cleanup/dirty-host status | Exact per-attempt order reset->fresh allocate->fault->own page observation->affinity/ownership->read-back->warm-up->measure; Pair-Pending never delays measurement, changes order, or triggers rerun; all attempts retained | Phase-Timeout, Gate-Failed, Topology-Changed, Rollback-Incomplete, Operator-Intervention | State-machine audit in both B0/B1 arrival orders, injected failure at every phase, seed replay, fixed schedule, no latency access for gates |
| C22 Telemetry collector | Capture explanatory state with scope; calibration/run -> validator/aggregator/model | Event catalogue, scope, sample periods, widths, mandatory flags, clock | TelemetryRecord: raw/extended value, unit, scope, time, enabled/running time, wrap/reset/multiplexing/quality, phase join | Same config across policies; raw retained; unavailable not zero; overhead characterized; version/digest identifies event encoding | Event-Unavailable, Wrap-Ambiguous, Multiplexing-Gate-Failed, Attribution-Mismatch, Interval-Missing | Controlled sign/scaling probes, wrap/reset fixtures, phase-coverage and enabled/running checks |
| C23 Result aggregator | Finalize immutable pair records and build run/block/attrition summaries; post-run processing -> statistical analysis/tables | C06/C12/C18--C22, all scheduled and attempted records, acceptance index, frozen analysis plan | AggregatedDataset: per-run nearest-rank indices/values or intervals and N, A_bj, final E_mem,j and adjacent-pair indicators, policy/pair denominators, categorized failures and incomplete-block cause, rates/correctness/counters, pair keys, exclusions, provenance | Pair dTV uses only immutable records and is order-independent; Pair-Pending resolves only by a new final record; no excluded latency run; no packet as run; raw-to-derived links/digests; p99.99 exploratory | Digest-Mismatch, Duplicate-Run, Pair-Pending-Unresolved, Pair-Join-Mismatch, Incomplete-Block, Quantile-Unbounded, Schema-Mismatch | Recompute page joins/indicators and quantiles, reconcile planned/attempted/accepted/failure denominators, category totals, and pair keys independently |
| C24 Statistical analysis stage | Execute frozen conditional inference, operational-feasibility reporting, and sensitivity; analysis -> manuscript artifact package | C23, AnalysisPlan, decision-register freeze snapshot | StatisticalAnalysisArtifact: accepted-pair estimand label, primary D_j/mean/SE/t/p/one-sided bound/two-sided interval, diagnostics, fixed n/attempt/policy/pair counts, attrition rates/categories, operational-feasibility outcomes, Holm family, frozen exploratory attrition sensitivity if any, other labeled sensitivities, table/figure data | Sole conditional weak-mean-null paired t decision; accepted run pairs are units; failed-attempt latency is not imputed; no rerun/substitution; differential attrition cannot be hidden; no outcome-driven method/cell/sample substitution; exact quantile rule | Plan-Digest-Mismatch, Insufficient-Pairs, Attrition-Report-Incomplete, Assumption-Sensitive, Family-Violation, Unplanned-Analysis | Independent rerun, formula/unit tests, denominator/category reconciliation, input-attempt trace for every output cell, confirm no failed latency entered |

The registry is normative. The detailed responsibilities below add behavior but cannot weaken a registry invariant or reinterpret an error status.

### 5.3 Detailed component responsibilities

#### 1. Topology inspector

- **Inputs:** host identity, collection policy, required/optional fact list, privilege capability.
- **Outputs:** raw source captures and a provenance-rich observation set; no inferred topology.
- **Invariants:** read-only operation; one collection epoch; every missing fact has a reason.
- **Errors:** inaccessible source, inconsistent host/boot ID, device disappears, partial collection. A partial output is diagnostic only until the builder accepts a named fallback.

#### 2. Graph serializer / normalized graph builder

- **Inputs:** inspector observations, join rules, schema version.
- **Outputs:** validated `TopologySnapshot`, unknown inventory, human-readable diagram source.
- **Invariants:** distinct object types; unique BDF/queue joins; directional edges; provenance retained; no unknown-to-zero conversion.
- **Errors:** duplicate identity, contradictory membership, dangling queue, unit mismatch, cycle in a containment relation, stale observation.

#### 3. Cost-model calibrator

- **Inputs:** topology snapshot, frontend/capability/ownership-catalog profiles, calibration design, accepted complete calibration runs, frozen transforms/feature order, positive lambda grid, rank and admission rules.
- **Outputs:** `CalibrationDataset`, seven-phase record, `CalibrationModelArtifact`/`CostModel`, condition/placement-relation coverage map, fold-admissibility report, term-ownership ledger, effective coefficients, recovered alpha/beta, fold losses, seen-condition loss/residual report, unseen-condition rank/top-choice/regret report, uncertainty, validity domain, and admission status.
- **Invariants:** response is run-level log nearest-rank p99.9; the objective uses `n_tr=|C_tr|` and sums exactly over `r in C_tr`; one unpenalized condition intercept is fit/evaluated but not scored, and there is no global intercept; effective coefficients use nonnegative ridge; lambda minimizes fold-size-weighted log-MSE over condition-stratified admissible blocked folds with larger-lambda exact-tie selection; all replicates of a placement relation remain together, every CV condition has at least two independent relation groups, and every validation condition occurs in its training fold; unseen-condition transfer never uses an invented/validation-fitted intercept or absolute MSE; merge/disable follows the frozen rank rule; coefficient factorization exactly reproduces fitted placement coefficients up to the topology-group scale; confirmatory data are excluded.
- **Errors:** `Condition-Coverage-Insufficient`, `Calibration-Failed`, insufficient residualized rank, unresolved collinearity, zero topology scale, failed correctness/held-out admission, unstable clock, or out-of-domain request. Failure blocks confirmatory B3 rather than selecting another estimator.

#### 4. Placement planner

- **Inputs:** snapshot, capability profile, finite ownership catalog and digest, workload, admitted cost model, reference mapping or B3 catalog-decision scope, CPU-access profile, hard constraints, prior plan if re-planning.
- **Outputs:** `PlacementPlan` only with `Feasible`, otherwise `CandidateSearchAudit` with `Search-Limited`, `Cap-Limited`, or `Data-Incomplete`; `Proven-Infeasible` is accepted only from a separately identified exact checker and certificate, not from the heuristic.
- **Invariants:** complete RX/TX bundles retain queue/endpoint identity; every owner/share pair is derived from one finite catalog entry and no continuous share is enumerated; observable-only shares are fixed inputs rather than decisions; every logical role maps to one physical execution context and every active context to one PU; RTC roles share one occupant/slot and sum service, staged roles use distinct occupants; shared mappings are globally consistent; only certified state-independent dominance is allowed; candidate-list exhaustion and search-budget exhaustion remain distinct; all hard constraints are rechecked; deterministic tie-breaking and decomposed cost are emitted.
- **Errors/status:** `Search-Limited` after bounded construction fails even with exhausted lists; `Cap-Limited` when a candidate domain was not fully exposed; `Data-Incomplete` for an unresolved safety-critical fact; stale cost model, unsupported ownership cardinality, or no permitted fallback. A conflict witness is neither minimal nor an infeasibility certificate unless independently proved.

#### 5. Placement applicator

- **Inputs:** placement plan, current-state observation, authorization profile.
- **Outputs:** `AppliedPlacement`, prior-state journal, rollback result if needed.
- **Invariants:** desired, requested, and observed records remain distinct; an observed-only ownership share produces no setting action; dependency order; stop on first failed prerequisite; no unplanned optimization; idempotent verification of already-applied state.
- **Errors:** insufficient privilege, failed affinity/memory/queue operation, resource exhaustion, driver reset, partial apply. Any partial apply triggers reverse-order rollback.

#### 6. Packet-I/O frontend

- **Inputs:** frontend and capability profiles, finite ownership catalog, queue/pool bindings, packet format, reference or B3-selected catalog entry/worker contract, role-to-physical-context realization.
- **Outputs:** queue handles/identities, poller identities, per-queue counters, packet events, self-description.
- **Invariants:** identical packet path and logic across B0–B3; declared queue/resource counts and owner cardinalities; B0--B2 exactly use the reference catalog index; B3 changes only admitted controllable catalog fields; observed-only shares remain observations; no hidden fallback to another driver/mode.
- **Errors:** queue creation failure, link change, unsupported offload, descriptor exhaustion, undeclared copy, counter wrap without extension.

#### 7. Page initializer and memory-pool/descriptor manager

- **Inputs:** policy/attempt ID; RX/TX payload-pool and descriptor-object schemas; material/null ring and state declarations; capacities; page size/source; default or explicit memory policy; topology-blind B0/B1 initializer rule; allocation/fault order; CPU-access shares; declared location distributions.
- **Outputs:** typed material-object IDs, explicit `b_empty`/`a_empty` markers, address/size metadata, fresh-allocation proof, one immutable per-attempt `PageInitializationRecord`, desired/requested/observed page records, coverage and observation-integrity status; no pair dTV is produced here.
- **Invariants:** equal usable material capacity across policies; null ring/state objects have no allocation, bytes, slots, rate, NUMA distribution, or cost and are eligible only for no-handoff/no-state profiles; no cross-run reuse; B0/B1 use the same topology-blind CPU/default policy/order and finish faulting before data-plane affinity; B2/B3 use fresh policy-specific allocations; complete initialization before measurement; one missing pair mate does not delay the fixed attempt schedule; bounds/ownership protection.
- **Errors:** huge-page shortfall, wrong page size, descriptor placement uncontrollable when mandatory, incomplete faulting, inherited allocation, initializer escape, observed pages outside allowed nodes, or incomplete/invalid individual page observation. Pair-equivalence statuses belong to the validator/aggregator, not the initializer.

#### 8. Event-bus or ring stage

- **Inputs:** material ring capacity/element schema or explicit no-ring object, producer/consumer identities, placement plan.
- **Outputs:** event handoffs, monotonic producer/consumer sequences, high-water and overwrite/lapping telemetry.
- **Invariants:** identical algorithm/capacity across baselines; no overwrite; declared single-/multi-producer and consumer semantics; the no-ring object is admitted only for RTC and produces no allocation or telemetry reservation.
- **Errors:** lapping, invalid sequence, stalled producer/consumer, undeclared sharing, capacity mismatch.

#### 9. Runtime worker stage

- **Inputs:** worker-role ID, physical-execution-context ID and CPU assignment, queue/ring ownership, service operation, application-state mapping.
- **Outputs:** responses, role/context/thread identity evidence, progress/CPU/cycle telemetry, integrity result.
- **Invariants:** identical service operation and batching; RTC role pairs resolve to one thread/context and one slot while both service contributions are recorded; staged roles resolve to distinct contexts; no execution outside effective mask; deterministic response semantics.
- **Errors:** affinity escape, worker stall, application error, invalid response, overload beyond declared gate.

#### 10. Traffic generator

- **Inputs:** `WorkloadSpec`, clock profile, start epoch, campaign block.
- **Outputs:** transmitted sequence manifest, send timestamps, actual-rate trace, link/generator counters.
- **Invariants:** exact expected sequence set known before receive analysis; identical trace digest in a paired block; no rate adaptation based on observed SUT latency.
- **Errors:** under/over-rate beyond tolerance, timestamp loss, sequence discontinuity, generator saturation, link fault.

#### 11. Latency receiver and correctness oracle

- **Inputs:** expected sequence manifest, received packets/timestamps, packet schema, clock state.
- **Outputs:** matched observations, loss/duplicate/reorder/integrity report, latency data, acceptance predicates.
- **Invariants:** one canonical observation per expected sequence; initial/terminal missing ranges remain visible; clock wrap handled before subtraction.
- **Errors:** corrupt/ambiguous sequence, negative/out-of-range timestamp, duplicate ambiguity, clock step, unmatched response.

#### 12. Run orchestrator

- **Inputs:** campaign matrix, randomized block order, plans, phase/acceptance rules.
- **Outputs:** phase transitions, `RunRecord`, per-attempt `AcceptanceRecord` and `A_bj`, prospective pair keys/statuses, complete attempt index, exclusion reason, cleanup status.
- **Invariants:** no outcome-dependent order, delay, or rerun; all attempts retained; a `Pair-Pending` B0/B1 attempt may measure and complete before its mate; next scheduled run starts after its own validation and cooldown, not after pair-level dTV.
- **Errors:** phase timeout, failed pre/post gate, incomplete rollback, topology digest change, operator intervention. The host becomes dirty when cleanup cannot be proven.

#### 13. Telemetry collector

- **Inputs:** counter catalogue, scopes, sampling periods, wrap widths, mandatory/optional flags.
- **Outputs:** timestamped counter samples with enable/running time, wrap extension, missingness, and scope.
- **Invariants:** collection configuration identical across baselines; overhead characterized; raw values retained.
- **Errors:** multiplexing above permitted ratio, counter reset/wrap ambiguity, timestamp drift, attribution mismatch, lost mandatory interval.

#### 14. Result aggregator

- **Inputs:** complete scheduled/attempt index, immutable page/acceptance records, raw latency/correctness/counter data, frozen analysis specification.
- **Outputs:** final order-independent B0/B1 pair records; per-run summaries; `A_bj`, adjacent-pair indicators, conditional paired block dataset; policy/pair acceptance and categorized attrition tables; secondary operational-feasibility outcomes; primary one-sided paired t-test and aligned conditional mean-log-ratio confidence bound; separately labeled sharp-null and any frozen attrition sensitivity; other intervals/effect sizes, table/figure data, provenance report.
- **Invariants:** no excluded latency run reintroduced; no failed latency imputed; no packet treated as an independent run; pair admission uses immutable records and never latency; all transformations and denominators versioned; tables trace to all scheduled attempts, not only accepted pairs.
- **Errors:** digest mismatch, duplicate run ID, unresolved/mismatched pair, incomplete attrition report, schema mismatch, analysis outside the pre-specified family, or any attempt to replace or overgeneralize the frozen conditional primary estimand. Exploratory output is labeled separately.

### 5.4 Field-level records and acceptance predicates

The following nested records are mandatory. Implementations may add fields but may not merge the listed distinctions.

| Record | Mandatory fields | Acceptance predicate |
|---|---|---|
| `LocationQualifiedObject` | attempt/policy and typed object ID; role (`rx_payload`, `tx_payload`, `rx_descriptor`, `tx_descriptor`, `event_ring`, `state`); material/null flag; capacity/used bytes and slots; page size/backing source; desired NUMA vector; requested policy; allowed nodes; allocation/fault/first-touch actor; CPU accessor contexts and demand shares; immutable observed page count/vector; controllability/coverage; observation-integrity status; provenance | material vectors use snapshot node IDs and sum to one; desired/requested/observed remain distinct; observed coverage meets the per-attempt frozen gate; no pair dTV is stored in this object; capacities/page units are consistent; null ring/state has zero bytes/slots/rate, no distribution, no allocation and valid profile eligibility |
| `PageEquivalenceRecord` | pair key; B0/B1 attempt and page-record IDs/digests; state; mandatory-object join specification/results; both immutable observed vectors and coverage; frozen tau_mem/pilot digest; per-object dTV; maximum; creation time; superseded pending-record refs | one missing mate yields `Pair-Pending`; a final record is exactly one of `Pair-Equivalent`, `Page-Equivalence-Failed`, or `Page-Equivalence-Unsupported`; final computation is order-independent, uses no latency, mutates no input, triggers no rerun, and controls only RQ1 pair admission |
| `QueueBinding` | endpoint BDF; port; direction; hardware queue index; logical pipeline; paired RX/TX identity; descriptor object; payload pool; reference-map and ownership-catalog IDs/digests; selected finite entry index; derived worker/owner-role IDs and fixed planning shares; control class/request action; observed shares/range/coverage; each role's physical-context and requested/effective PU; RSS digest | BDF/port/queue join is unique; catalog is finite/frozen; k=1 share is one; B0--B2 selected index equals reference; B3 index is admitted and controllable; observed-only share is not called applied and lies in its range; observed owner/worker sets and counters match; RX/TX compatibility passes |
| `ExecutionBinding` | physical-context/occupancy-group ID; logical worker/I/O roles realized; RTC/staged mode and equality/inequality predicates; requested/effective CPU mask; chosen PU; physical-core/SMT group; occupied-slot count; per-role service contributions and sum; reserved/isolation class; observed thread/context IDs and CPU coverage | RTC roles resolve to one physical context and one occupied slot with summed service; staged independent roles resolve to distinct contexts/slots; every sample lies in the effective mask; shared identity has one mapping; execution/PU/core/SMT/exclusion capacities pass |
| `CapacityCheck` | resource ID/type; contributor IDs; each demand and unit; calibrated capacity; safety guard; total; inequality; pass/fail; calibration reference | all contributors are present once; demand and capacity units match; the exact manuscript inequality is reproducible; failure makes the plan/run inadmissible |
| `CostTermValue` | pipeline/term ID; physical-mechanism owner; owning group; initiator/target; direction/transaction class; raw value/unit/provenance; base reference; transform; scale; normalized value; component weight; group coefficient; base-or-surcharge class; load attribution; uncertainty | one mechanism has one active owner/group; base and structural proxy are mutually exclusive; surcharge subtracts unloaded response; topology coefficient is the fixed scale reference; numeric unknown is forbidden; component/group decomposition sums to total score within tolerance |
| `CandidateSearchAudit` item | queue ID and immutable endpoint identity; raw bundle; static-feasibility reasons; occupancy/resource/capacity/conflict vectors; dominance predecessor/certificate; score/tie key; cap exposure epoch; domain-exhausted flag; construction node/depth budget; selected/rejected reason; final status | removed candidates have valid state-independent certificates; cap expansion is monotone; list exhaustion is distinct from bounded-search failure; the heuristic emits no `Proven-Infeasible`; repeated input reproduces ordering and selection |
| `TimestampEvidence` | request/response sequence; raw ticks; clock/epoch ID; capture layer/direction; conversion; wrap-extension state; validity flag/reason; qualification digest | subtraction occurs only after epoch extension in one valid clock domain; no rounded intermediate; qualification domain covers the run rate and timestamp volume |
| `ResponseCategory` | expected sequence; list of all candidate response IDs; format/payload/binding/timestamp results for each; final category (`valid`, `missing`, `corrupt`, `duplicate`, `ambiguous`); out-of-range flag | exactly one category per expectation; `valid` iff exactly one candidate exists and passes every check; totals reconcile with `|E|` and raw receive count |
| `AcceptanceRecord` | block/policy/attempt IDs; every performance-blind gate; `A_bj`; primary and secondary failure categories; planner/model/apply/rollback/read-back/page/correctness/timestamp/telemetry/environment status; prospective pair keys; final pair-indicator refs; policy causing incomplete block | decision is immutable before latency summaries; every scheduled attempt appears once; failure categories and denominators reconcile; `Pair-Pending` is not a per-attempt failure; pair failure alters only its declared contrast; no recoding or neighboring-run substitution |
| `PrimaryAnalysisRecord` | `AnalysisPlan` digest; `l*`; conditional-estimand label; all planned/attempted/accepted B0--B3 counts; all adjacent-pair indicators/counts; policy-specific failure counts/rates/categories; accepted B3/B2 run IDs; both p99.9 values/counts/within-run intervals; `D_j`; fixed planned `n`, accepted `n_acc`, and attempt schedule; mean/SE/t statistic/one-sided p-value/upper confidence bound/two-sided interval; operational-feasibility outcomes; assumption diagnostics; separately labeled sharp-null and frozen attrition sensitivities; decision | only frozen `l*` and `A_j^(3,2)=1` pairs enter latency inference; estimand is not generalized to all scheduled blocks; failed latency is not imputed; packets are not replications; paired t-test alone decides the conditional weak mean null; all attempt/pair/category counts reconcile; no pilot/excluded run, extra attempt, rerun, or substitution |

### 5.5 Boundary between components

The planner never applies state. The applicator never changes a plan to “make it work.” The validator does not trust applicator status. The traffic generator determines the expected packet set before the receiver observes it. The aggregator cannot change acceptance gates or randomization. These boundaries are required for causal and correctness auditability.

## 6. Baseline definitions

### 6.1 Common baseline structure

All baselines use the same binary, frontend/capability profile, finite frozen ownership catalog, packet logic, fixed RX/TX queue pairs, RSS/flow mapping, logical worker/I/O-role and physical-execution-context inventories, ownership cardinalities, resource counts, RTC/staged grouping rules, payload/descriptor/material-ring capacities, traffic trace, exact sequence set, clock, telemetry, phase protocol, and correctness gates. B0--B2 use the same topology-agnostic `ReferenceMapping` of worker identities and catalog indices; B3 may select different logical workers and controllable finite entries only within the same inventories/catalog. The primary profile is single-owner. Each policy attempt starts from the recorded neutral prior state, new process, fresh allocations, and un-warmed queues. Hardware queues do not have abstract CPU masks: their CPU association is induced by their logical owners and the physical contexts realizing those roles. The terms “default” and “controlled” describe only placement decisions.

### 6.2 B0 — operating-system default scheduling and memory policy

- **Controlled:** only common functional invariants, the `ReferenceMapping`, the topology-blind initializer, and the campaign-wide safety cpuset excluding reserved control CPUs; fixed queue pairs, RSS, reference worker/finite ownership entries, and packet path are created by the common frontend contract.
- **Default:** no experiment-selected physical-execution-context affinity and ordinary scheduler placement within the safety cpuset; ordinary process memory policy; no explicit payload, descriptor, material-ring, or state binding; documented frontend-default IRQ/context launch behavior.
- **Verification:** record logical-role-to-thread/context realization, RTC/staged slot accounting, effective allowed masks, sampled CPUs, scheduler migrations, initializer identity/order/default memory policy, observed page distributions and coverage, IRQ/poller/completion CPUs, catalog/owner/worker identities, RSS, and per-queue counters. If the frontend cannot operate without explicit CPU assignment, archive its unmodified documented launch mapping and label it frontend default rather than OS scheduling.
- **Forbidden accidental optimization:** inheriting an affinity mask, NUMA policy, prefaulted local pool, tuned IRQ mask, or B3 RSS/queue map; launching via a tool that pins threads; using first-touch by a deliberately local worker as a hidden binding mechanism.
- **Proof package:** prior-state record, launch environment, effective masks/policies, observed CPUs/pages, queue/IRQ records, process-lifetime ID.

### 6.3 B1 — CPU affinity only

- **Controlled:** preserve the complete B0 reference worker/catalog relations; use the exact B0 topology-blind initializer and only after its faulting completes pin every data-plane physical execution context by one exact CPU-only rule. Order eligible physical cores by stable OS identifier and assign active contexts round-robin after reserved cores, respecting only functional capacity, occupancy, SMT, and isolation constraints. An RTC poller/worker is assigned once; staged contexts remain distinct.
- **Default:** the same ordinary memory policy, initialization CPU, fresh allocator/fault order, and fault pattern as B0; no PCIe, NUMA-distance, page-location, or calibrated path input; no queue/RSS/ownership change.
- **Verification:** exact role-to-context grouping, one-slot RTC and distinct-slot staged evidence, effective masks, no execution outside them, init completion before affinity request, plan generated without device/memory cost fields, actual pages observed but not repaired, and object-wise B0/B1 page equivalence within frozen tau_mem.
- **Forbidden accidental optimization:** binding memory to the worker node; selecting cores because they are near the NIC; relocating rings/pools after observing pages; changing RSS/flow rules.
- **Proof package:** CPU-only input manifest and rule output; requested/effective masks; CPU samples; both `PageInitializationRecord` objects; default memory-policy and page-distribution records; paired coverage/dTV/tau_mem record. A failed or unsupported page-equivalence gate invalidates the pair.

### 6.4 B2 — CPU affinity plus memory binding

- **Controlled:** preserve every B1 physical-context CPU assignment and the complete `ReferenceMapping`. On fresh allocations, for each material object `m`, require a nonempty, justified accessor set in the frozen `CPUAccessProfile`; sum its accessor demand shares on each NUMA node containing the B1-assigned accessor contexts, choose the node with maximum aggregate share, and break ties by the smallest stable node ID. A material object with no justified CPU accessor makes B2 undefined and must be resolved before campaign freeze; NIC locality cannot fill that gap. Request and verify this rule separately before applying the preserved data-plane affinity to RX/TX payloads, controllable RX/TX descriptors, material event rings, and material application state; null objects allocate nothing.
- **Default:** preserve the common queue/RSS/reference owner/worker map; do not inspect NIC BDF, root, or DMA path; do not change any CPU assignment; do not use the complete cost or load-aware re-planning.
- **Verification:** accessor context/share record and derivation; per-node aggregate; selected node/tie; requested per-object policy; allocation/first-touch actor; complete faulting; physical page coverage/distribution; exact B1 role/context/CPU artifacts; unchanged queue/RSS/reference map.
- **Forbidden accidental optimization:** moving workers or pools based on NIC attachment; selecting a special local queue; changing pool/ring count or capacity; leaving pages from a previous baseline.
- **Proof package:** B1 artifacts plus `CPUAccessProfile`, per-node share calculation, per-object memory policy, allowed node set, physical page coverage/distribution, allocation and first-touch actor. A predeclared secondary sensitivity compares the aggregate-node rule with dominant-accessor and demand-share-weighted interleave rules for split access; primary B2 is unchanged.

### 6.5 B3 — complete topology-aware placement

- **Controlled:** from fixed queue pairs, inventories, cardinalities, and finite catalogs, jointly select queue-to-worker and direction-specific controllable ownership-catalog indices, RX/TX payload pools, RX/TX descriptor objects, material/null event ring and state, logical-role-to-physical-context realization, and every active context's PU from the validated graph and frozen admitted cost model under hard constraints. Derived shares are not continuous decisions; observed-only shares remain frozen external inputs. All material desired distributions and requested page policies are explicit and use fresh allocations. RSS and queue identities do not change.
- **Default:** only facts/control surfaces declared unavailable in the `Full`, `NUMA`, or `CPU` fallback. The primary B3 comparison requires `Full`; fallback runs are reported separately.
- **Verification:** plan-input, capability, catalog, model, and reference-map digests; deterministic replay; `Feasible` status; desired/requested/applied/observed logical mapping and physical placement; no share-setting claim for observed-only entries; per-component/group score; per-queue owner/worker/share probe; all material page distributions; role/context/thread and PU evidence; occupancy ledger; snapshot identity.
- **Forbidden accidental optimization:** changing any non-placement invariant, using confirmatory outcome data to tune weights, dropping expensive flows, reducing offered load, enlarging buffers/rings, changing batch or offloads, accepting silent fallback.
- **Proof package:** full planner, applicator, validation, and rollback records plus common baseline evidence.

The required non-baseline cost ablation compares `B3-topology-only` (unloaded path primitives, equal zero-load queue weights, `beta_load=0`) with `B3-load-aware` (the full frozen model). A separate secondary ownership mechanism family compares: full B3; B3 with the complete reference worker/catalog mapping fixed while physical placement is optimized; and topology-aware worker/controllable-catalog mapping with every other assignment frozen at verified B2 values, only if all candidate mappings remain feasible and scientifically interpretable. Single-owner is primary. Shared-owner comparisons enumerate frozen finite entries; observed-only sharing is analyzed by its predeclared observed range and is never described as an applied share. These variants share resource counts, queue/RSS identities, packet semantics, workload, and gates and are never counted as additional primary baselines.

### 6.6 Baseline acceptance

A baseline label is accepted only when all of its per-attempt predicates pass, yielding immutable `A_bj`. A run in which B2 pages are not on their bound nodes is not recoded as B1; it is an invalid B2 attempt. B0/B1 attempts first receive independent page-observation decisions. Their RQ1 relation remains `Pair-Pending` until both immutable records exist; a final failed or unsupported object-wise page-equivalence gate excludes only that RQ1 pair rather than retroactively rejecting an otherwise valid attempt or treating it as CPU-only evidence. B0--B2 mapping deviations are invalid, not recoded. A B3 fallback, `Search-Limited`, `Cap-Limited`, `Data-Incomplete`, model-domain failure, or application/read-back failure sets `A_B3,j=0`; a campaign-wide `Calibration-Failed` status blocks confirmation and is reported as one model-admission failure rather than as fabricated per-block latency. B0's observed accidental locality is retained because it is part of the default policy, but it is documented and can motivate a stratified sensitivity analysis. Every policy-specific failure and adjacent-pair completion indicator remains in the attrition report.

## 7. Workload matrix

### 7.1 Matrix strategy

A literal full Cartesian product would consume stand time while duplicating weakly informative conditions. The campaign therefore has four tiers:

1. **Feasibility and calibration:** resolve testbed-dependent levels, timestamp behavior, saturation, service demand, RSS occupancy, and valid counter events. These runs cannot support the placement hypotheses.
2. **Confirmatory core:** all four baselines in complete randomized blocks for a reduced factorial selected by the rules below.
3. **Mechanism and ablation:** local/cross-socket constructions and cost-term removals around representative core conditions.
4. **Robustness:** burst, skew, scale, alternate topology, and optional second frontend.

The final resolved matrix and its digest are frozen before confirmatory acquisition. Missing hardware capability removes a factor with an explicit reason; it is not replaced by a guessed value.

### 7.2 Packet sizes

Define `S_min` as the minimum valid on-wire Ethernet frame for the configured packet format and generator, `S_mtu` as the largest non-jumbo frame permitted by the frozen MTU, and `S_jumbo` as the largest enabled jumbo frame if jumbo operation is part of the campaign. The initial size set is the sorted unique intersection of supported values with:

- `S_min`;
- cache-line/multiple and powers-of-two transition points between `S_min` and `S_mtu` (normally 128, 256, 512, and 1024 bytes of configured frame length when valid); and
- `S_mtu`, plus `S_jumbo` only in a separately frozen jumbo profile.

The powers-of-two levels sample changing packet-rate, descriptor, cache-line, and bandwidth regimes; they are not tuned after seeing a policy effect. The manifest states whether “bytes” means frame bytes or on-wire bytes and accounts consistently for preamble, inter-packet gap, and frame check sequence. If the generator or frontend cannot produce one level, the unsupported value is removed before the matrix freeze.

The confirmatory reduced set contains `S_min`, `S_mtu`, and the interior size whose neutral calibration is nearest the geometric midpoint in packets-per-second/bytes-per-second pressure. The full size set remains a robustness sweep.

### 7.3 Offered load

Absolute packet/s and bit/s values are testbed dependent. Resolve them separately for each packet size and queue/worker scaling regime:

1. In a neutral diagnostic placement, conduct a monotone rate search from the generator's accurately controllable minimum to the physical line limit.
2. At each rate, require stable actual rate and record goodput, loss, p99.9, queue occupancy, worker utilization, and generator saturation.
3. Fit the predeclared segmented monotone curve to locate the earliest **knee** where latency slope or loss departs from its low-load segment. Retain the fit diagnostics.
4. Define `R_low` as the smallest accurately generated rate with utilization above telemetry resolution, `R_mid` as the highest sampled rate below the knee whose normalized offered load is closest to the midpoint between `R_low` and the knee, `R_knee-` as the last stable point below the knee, and `R_high` as the highest rate at which every baseline in a blinded feasibility pass satisfies the primary loss and generator-accuracy gates.
5. Freeze the resolved rates. If `R_high < R_knee-`, investigate the stand and repeat feasibility; do not choose a policy-specific high rate.

`R_low`, `R_mid`, `R_knee-`, and `R_high` form the confirmatory load factor. A denser normalized load-versus-latency sweep is secondary. Offered and achieved rates are both reported; a policy is never credited for low latency at lower goodput.

### 7.4 Constant and bursty traffic

Constant-rate traffic is primary because it makes path and capacity effects interpretable. Bursty profiles use a content-addressed ON/OFF trace replayed identically in every paired run. Resolve the burst reference `T_drain` as the median time for the configured worker set to drain a queue from its declared high-water mark under neutral calibration. The robustness set brackets this time with ON durations `0.5 T_drain`, `T_drain`, and `2 T_drain`; OFF durations are selected to preserve the same long-run mean rate as the matched constant-rate condition. Peak rate is the smallest accurately generated rate that reaches the declared high-water mark without generator saturation. This creates short, matched, and sustained queue-pressure regimes without assuming an absolute microsecond value.

Store every inter-arrival time or a losslessly reconstructible schedule. Do not generate a new random trace for each policy. Random burst seeds are campaign inputs and appear in the block key.

### 7.5 Flows and RSS occupancy

Flow keys vary only fields included in the frozen RSS hash. Required flow regimes are:

- one flow, exposing single-queue behavior;
- the smallest generated set that assigns at least one flow to every selected queue under the recorded RSS key/table;
- the smallest set for which per-queue offered rates remain within the predeclared occupancy tolerance over repeated hash samples; and
- two skew regimes whose generated per-queue maximum-to-mean demand ratios bracket the planner's load-balancing boundary, resolved in calibration and then frozen.

Uniform and skewed assignments use exact flow lists and rate vectors. “Number of flows” is insufficient provenance; store the tuple fields, intended queue, actual probe result, and per-flow trace digest.

### 7.6 Queue and worker counts

Let `Q_max` be the minimum of the NIC/frontend queue limit, the number of observable steerable queues, and the pool/ring resource limit. Let `W_max` be the number of isolated eligible physical cores after reserving OS/control CPUs and applying the SMT policy. Test counts are sorted unique powers of two from one through each maximum, plus the exact maximum if not a power of two.

The core matrix uses `Q=W` at one, a middle scale, and the largest scale common to all baselines. The scaling matrix adds the nearest feasible `Q<W` and `Q>W` cases to exercise shared-worker and spare-worker behavior. SMT PUs are excluded until physical cores are exhausted; enabling SMT is a named sensitivity factor, never an implicit way to increase `W_max`.

### 7.7 Placement constructions

In addition to B0–B3, calibration and mechanism runs construct feasible path extremes when the topology permits:

- NIC-local pool, local poller/worker, local ring;
- NIC-local pool with remote worker;
- NIC-remote/worker-local pool;
- local pool and worker with cross-socket ring producer/consumer;
- balanced split across sockets; and
- deliberately loaded local path versus unloaded longer path.

These are mechanism probes, not extra primary baselines. They vary one declared relation at a time and must retain the common packet path.

### 7.8 Short and sustained runs

Short diagnostic runs establish functionality, rate accuracy, queue mapping, timestamp overhead, warm-up, and autocorrelation; they never enter hypothesis tests. The pilot chooses one fixed warm-up duration, measurement duration, expected request count, drain deadline, and cooldown schedule for each workload class. The measurement duration covers the larger of the pre-specified sustained-time criterion and the time needed to transmit a fixed set expected to yield at least one million valid observations under the acceptance-loss allowance. These values are frozen before confirmation. A measured run never continues until a percentile or interval “looks stable.” p99.99 remains exploratory even when ten million observations are available.

### 7.9 Reduced confirmatory matrix

The candidate confirmatory matrix crosses four baselines with three resolved packet sizes (`S_min`, selected interior, `S_mtu`), four resolved loads (`R_low`, `R_mid`, `R_knee-`, `R_high`), constant traffic, the stable uniform-flow set, and three `Q=W` scales. Bursty/skewed traffic and `Q!=W` are pre-specified interaction families. If this exceeds the stand budget, use a D-optimal or fractional-factorial reduction chosen from feasibility data using only design-matrix rank and predicted acquisition cost—not placement response. Preserve every incremental contrast and at least one interaction estimate for each RQ4 factor.

Exactly one cell is designated `l*` for the sole primary estimand. The decision rule is frozen before pilot policy labels are unblinded: choose a supported non-fragmenting request/response size representative of the target service contract, constant traffic, stable uniform RSS occupancy, `Q=W`, and the highest common rate below both the first calibrated knee and the loss/generator-fidelity gate. If more than one cell satisfies the rule, use the lexicographically smallest factor tuple. The resolved values and justification enter `AnalysisPlan`; all other cells are secondary.

## 8. Measurement and metrics

### 8.1 External wire-to-wire latency

For request sequence `i`, let `t_tx(i)` be its TG transmit timestamp and `t_rx(i)` the timestamp of its validated response in the same clock domain. Primary external turnaround latency is:

`L(i) = t_rx(i) - t_tx(i)`.

This includes the complete declared chain: TG request timestamp/transmit, outbound link, SUT NIC ingress, RX descriptor/payload DMA, polling or IRQ progress, optional event-ring handoff, worker/state access, response construction, TX payload/descriptor publication and doorbell, SUT NIC transmit, return link, and TG response timestamp. Report it as turnaround latency, not one-way SUT service time. A fixed-path loop or bypass calibration is reported beside it but is not subtracted in the primary analysis. Any internal SUT timestamps are diagnostic and cannot replace `L(i)`.

If one-way measurement is supported, define ingress and egress timestamp layers exactly, use synchronized hardware clock domains, and propagate the measured offset/drift error into each run's uncertainty. Never combine one-way and turnaround observations in one distribution.

### 8.2 Sequence coverage and packet correctness

Before transmission, the TG commits a `SequenceManifest` containing an arbitrary exact expected set `E` (or a content-addressed deterministic rule that expands to it), campaign/block/run IDs, count, packet/trace digests, transmit order, and per-sequence request/flow binding. A contiguous `[s0,s1]` is one permitted encoding, not an assumption.

For each `s in E`, let `R_s` contain all received candidate responses carrying `s`, and let `R_ok_s` contain candidates that pass packet format, immutable payload/integrity, request-response binding, and timestamp checks. Define `V = {s in E : |R_s| = |R_ok_s| = 1}`. Only `s in V` has latency `L(s)`. Report separately:

- missing count: `|R_s| = 0`;
- corrupt/invalid count: `|R_s| > 0` but `|R_ok_s| = 0`;
- duplicate count: `|R_s| > 1`, with valid and invalid copies distinguished;
- ambiguous-match or timestamp-invalid count;
- out-of-range responses whose sequence is not in `E`; and
- no-valid-response rate: `1 - |V|/|E|`.

Do not label the last quantity physical packet loss without reporting the category decomposition. Goodput counts exactly one integrity-valid response per expected request.

Do not infer `E` from the first and last observed packets. This explicitly reveals a missing initial prefix, terminal suffix, or internal subset. Reordering is computed against the committed transmit order using displaced-packet fraction, maximum displacement, and a declared inversion/run statistic. Packets can still have valid latency when reordered if they match uniquely, but the run must meet its reorder gate.

### 8.3 Percentiles and distribution summaries

For N valid latencies, retain tied values as repeated observations and stably sort them as one-indexed order statistics `L_(1) <= ... <= L_(N)`. The frozen nearest-rank estimator is `Qhat_p = L_(k_p)` with `k_p=max(1,ceil(pN))` for `0<=p<=1`. Thus p=0 is the minimum, p=1 the maximum, and every positive reported percentile uses index `ceil(pN)`. No interpolation is permitted. N=0 makes every quantile undefined and the run invalid. Invalid, corrupt, duplicate, or ambiguous responses are not in the valid set and cannot enter N.

Raw tick differences are wrap-extended, converted once without per-packet rounding, and then sorted. For a bounded-resolution histogram with ordered finite edges, bins are left-closed/right-open except the final closed-right bin. Find the first bin whose cumulative count reaches k_p and return that complete bin interval, N, and k_p; never interpolate a point inside it. If the rank falls in underflow or overflow, the interval is unbounded and that representation is inadmissible for a primary percentile. Report nearest-rank p50, p90, p99, p99.9, exploratory p99.99, and maximum. Report N beside every percentile, plus minimum, mean for completeness, interquartile range, median absolute deviation, and jitter defined as the p99–p50 spread plus the distribution of successive valid latency differences. Do not call standard deviation “jitter” without definition.

The run-level endpoint used in the primary paired estimand is p99.9. `N(1-p) >= 1000` is the minimum exceedance-count rule, so p99.9 needs at least `10^6` valid observations. Even `10^7` observations do not promote p99.99 from exploratory status in this campaign. Because packets within a run are dependent, these counts do not replace independent runs or time-dependence-aware within-run intervals.

### 8.4 Rate and efficiency metrics

- **Offered throughput:** valid transmitted packets and on-wire bits per measurement interval.
- **Received throughput:** all received response packets per interval, including duplicates identified separately.
- **Goodput:** unique, integrity-valid expected responses and their application payload bits per interval.
- **Loss/duplicate/reorder:** as defined above, with exact numerator and denominator.
- **CPU utilization:** per worker/poller/control CPU in user, system, IRQ/softirq, idle, and steal categories where applicable; also effective frequency.
- **Cycles per valid packet:** non-multiplexed or correctly scaled cycle count divided by unique valid completed packets for the same interval and scope.
- **Planner time:** graph-ready to emitted plan, separated into candidate generation, scoring, construction, and refinement.
- **Configuration overhead:** prior-state capture, application, allocation/faulting, validation, rollback, and total ready-to-run time reported separately.

### 8.5 Memory, cache, PCIe, and interconnect metrics

Audit available events before the campaign. Candidate explanatory metrics include local/remote memory accesses, NUMA migrations/faults, memory-controller reads/writes/bandwidth, LLC references/misses/occupancy, DDIO-related allocation or eviction when validated, inter-socket link traffic/utilization, PCIe read/write bytes or transactions, root-port utilization, queue descriptor starvation, RX no-buffer/drops, ring occupancy/high-water marks, and interrupt/poll statistics.

For every counter, record event name and encoding, platform source, scope (thread/core/socket/device/port/queue), unit, width, wrap rule, sample interval, enable/running time, multiplexing, reset behavior, and probe validation. A socket-wide counter is not attributed to one queue. Unsupported metrics are `not available`, not zero. RQ5 contrasts depending on an unavailable event are removed before confirmatory unblinding or reported as unresolved.

### 8.6 Timestamp contract

The clock record must state:

- hardware or software timestamp point and direction;
- physical clock identifier and clock domain;
- raw counter width, tick frequency, nominal resolution, and conversion;
- empirical timestamp repeatability and calibration method;
- queueing between timestamp point and wire, if known;
- wraparound detection and epoch extension;
- pre/post-run offset and drift for multi-clock profiles;
- timestamp loss/invalid flags; and
- overhead measured with timestamps enabled versus disabled under a diagnostic workload.

A clock step, unhandled wrap, loss above the frozen gate, or synchronization error above the campaign bound invalidates the run. Time conversion is applied once from retained raw ticks; do not round per packet before percentile calculation.

### 8.7 Raw measurement schemas

`PacketExpectation` contains run ID, expected sequence, transmit-order index, request/flow binding, intended queue, and manifest digest. `PacketObservation` contains received candidate ID, parsed sequence, observed queue where available, raw TX/RX timestamps, clock/epoch IDs, converted latency only when valid, format/payload/binding results, duplicate/reorder category, and timestamp validity. Every expectation remains present even when no response exists.

`CounterSample` contains run ID, source/event/scope IDs, raw value, extended value, unit, sample clock/timestamp, enabled/running time, wrap/reset indicator, and quality flag. `PhaseRecord` contains phase name, planned and actual boundaries, stability inputs, gate result, and reason. Raw records are immutable; derived summaries include source digests.

Raw paired timestamps are preferred. A histogram substitute declares all finite bin edges and interval closure, underflow/overflow counts, integer count width, total-count equality to `|V|`, each nearest-rank index, the first cumulative bin containing it, both returned bounds, maximum bin width around p99.9, and the interval-censoring bound on every percentile. It is called bounded-resolution, not lossless, unless exact raw latency values can be recovered. Quantization and bin-width bounds enter the sensitivity report.

## 9. Statistical protocol

### 9.0 Attempt lifecycle

Every policy attempt executes this order and records each boundary: (1) environment reset and neutral-state read-back; (2) new process and fresh material allocation; (3) identical topology-blind allocation/faulting for B0/B1 or policy-specific memory-policy/allocation/faulting for B2/B3; (4) independent per-attempt page observation, coverage/integrity validation, and immutable `PageInitializationRecord`; (5) data-plane physical-context affinity and finite ownership-catalog entry application; (6) complete independent desired/requested/observed read-back, including observed-only shares; (7) fixed warm-up and stability gate; (8) measured transmission of the committed set, drain, post-validation, cooldown, teardown, and rollback verification. A B0/B1 relation is `Pair-Pending` when its matching page record is absent. After both mates exist, the validator or aggregator performs the mandatory object join and total-variation comparison as a separate pair-level transition, emitting a new immutable final record. It never changes the attempt sequence.

No policy may reuse material pages, process state, or warmed frontend queues. The first B0/B1 attempt may measure before its mate; pair admission remains pending and does not delay, reorder, or replay the frozen schedule. A pair failure causes no rerun and affects only RQ1 eligibility unless an individual attempt also failed its own gate. If a frontend requires a different dependency order, qualification must identify the unavoidable constraint and show through repeated performance-blind page observations that applying data-plane affinity earlier does not change the B0/B1 page distribution beyond frozen tau_mem. Without that evidence, the profile is unsupported for RQ1.

### 9.1 Experimental unit and blocking

The independent experimental unit is a complete run, not a packet. A complete scheduled block fixes topology snapshot, frontend/campaign, workload trace and factor levels, queue/worker count, timestamp profile, and repetition index, then schedules B0–B3 once each in randomized order. Randomization uses a recorded seed generated before the block and is not rerolled after a failure. A failed attempt remains in the attempt index and is not replaced; later repetitions are only those already present in the frozen schedule.

For each policy define `A_bj` from per-attempt gates as in Section 1.2. The result aggregator forms `A_j^(1,0)`, `A_j^(2,1)`, and `A_j^(3,2)` only from immutable acceptance and page-pair records. The attempt index must reconcile planned blocks, attempts started/completed, accepted attempts for each policy, pair completion for each adjacent contrast, and the policy/failure category responsible for every incomplete pair.

Use an independent pilot to estimate the standard deviation `s_D` of paired `B3/B2` log ratios and the performance-blind invalid-attempt fraction. Before inspecting policy effects, specify a smallest scientifically relevant relative reduction `delta_rel` from the system's latency budget and convert it to `delta* = |log(1-delta_rel)|`. For desired power `1-beta` and one-sided `alpha=0.05`, use the initial normal-theory planning approximation:

`n = ceil(((z_(1-alpha) + z_(1-beta)) * s_D / delta*)^2)`.

Choose the final `n` as the smallest integer at or above this approximation whose one-sample noncentral-t power for standardized effect `-delta*/s_D` reaches the target after any predeclared conservative variance inflation. Record the latency-budget rationale, pilot sample, variance uncertainty, desired power, approximation, noncentral-t recomputation, inflation, and rounding. Inflate `n` by the pilot invalid-attempt fraction to create one fixed maximum attempted-block schedule. Pilot blocks are excluded. Execute exactly the frozen attempt schedule: do not add blocks based on an observed effect, p-value, confidence width, or p99 stability. If fewer than `n` blocks pass performance-blind gates, report reduced power and stop according to the schedule. If `n_acc < 2`, the variance and t statistic are undefined and no confirmatory test is reported.

### 9.2 Warm-up and steady-state detection

Warm-up begins after allocation and placement validation. The pilot chooses a conservative fixed duration that covers complete payload/descriptor/ring/state faulting, link/queue activation, the slowest mandatory telemetry behavior, and the longest observed stabilization of throughput, worker utilization, effective frequency, temperature, and queue occupancy. The duration and absolute/relative stability bands come from resolution and pilot noise, not policy differences, and are frozen before confirmation. Failure to meet the bands at the fixed warm-up boundary invalidates the attempt; the phase is not lengthened after inspecting latency.

Steady-state is checked again during and after the fixed measurement interval. A pre-specified trend test on windowed p99/goodput and the frequency/temperature envelope is a whole-run gate. Do not trim early or late windows, restart the timer, or extend the sequence set based on visual inspection.

### 9.3 Primary analysis

For each valid run, calculate p99.9 using the exact nearest-rank convention in Section 8.3. At `l*`, form `J_32={j:A_j^(3,2)=1}` and calculate `D_j=log(Y_B3/Y_B2)` only for `j in J_32`. Let `n_acc=|J_32|=sum_j A_j^(3,2)` be the accepted-pair count from the fixed attempt schedule. The primary point estimate is `mean_(j in J_32)(D_j)`, transformed for presentation as `exp(mean(D_j))-1`. It estimates `theta_32^acc=E[D_j | A_j^(3,2)=1, j scheduled at l*]`, not an unconditional effect over every scheduled block. The sole confirmatory test is the one-sided paired t-test of `H0: theta_32^acc >= 0` against `H1: theta_32^acc < 0`, with statistic `T=mean(D)/(sd(D)/sqrt(n_acc))`; reject only when `T < -t_(0.95,n_acc-1)`. Report the aligned upper one-sided 95% confidence bound `U_0.95=mean(D)+t_(0.95,n_acc-1) sd(D)/sqrt(n_acc)` and a two-sided 95% Student interval for estimation. All inputs are accepted independent run pairs, not packets.

The t procedure assumes independent blocks in the target campaign, finite variance, and an adequately Student-approximated sampling distribution for the mean. Before unblinding, freeze diagnostic definitions and thresholds for block independence, a Q--Q display, skewness, tail weight, maximum studentized residual, and leave-one-pair-out influence. Diagnostics cannot remove observations. If a threshold is exceeded, retain the paired t-test as the only confirmatory rule, label its conclusion assumption-sensitive, and report a studentized paired bootstrap-t interval plus a median/sign analysis as robustness. Do not select the analysis with the most favorable result.

Within-pair B2/B3 label swapping tests the sharp null of no pair-specific effect, not the weak conditional mean null `H0: theta_32^acc >= 0`. Retain it only as a secondary sensitivity analysis, using exact enumeration when feasible or a frozen-seed Monte Carlo approximation with a reported simulation-error bound. A block-resampled mean interval is another sensitivity only when at least 30 accepted blocks are available by the fixed schedule; do not use a bias-corrected and accelerated interval with few blocks. Estimate each run's p99.9 uncertainty separately with moving-block resampling or stationary subsampling over time-ordered valid observations; select block length from the pilot autocorrelation rule. These within-run intervals do not change the experimental unit or primary test.

RQ1 and RQ2 log ratios use their declared accepted-pair indicators and form one key-secondary Holm-controlled family. Absolute differences, direct `B3/B0`, other workload cells, p99.99, interactions, and ablations are secondary/exploratory. Report effect size and interval regardless of p-value; do not replace the primary estimand with a median, absolute difference, or more favorable cell.

The mandatory operational-feasibility report gives planned and attempted blocks; accepted attempts separately for B0--B3; complete-pair counts for B1/B0, B2/B1, and B3/B2; and policy-specific failure counts/rates. Categories are planner (`Search-Limited`, `Cap-Limited`, `Data-Incomplete`), calibration/model admission or domain, apply, rollback, placement read-back, page verification, correctness, timestamp, telemetry, and environment. It identifies the policy that made each block incomplete. A campaign-wide `Calibration-Failed` event has the model-admission denominator and is not multiplied into nonexistent run-level latency records. A policy with substantially greater attrition cannot be called practically beneficial solely from latency among its selected accepted pairs.

### 9.4 Interactions, ablations, and multiple comparisons

RQ4 uses a hierarchical model or blocked factorial contrasts with policy as a within-block factor and workload variables as fixed effect modifiers; block/campaign is a random effect where the data support it. The exact model and transformations are frozen from feasibility diagnostics. Do not select interactions based on confirmatory significance.

RQ5 has one family for removal of RX payload DMA, descriptor DMA, TX DMA, context-memory, worker-memory, ring synchronization, application-state, MMIO, cache/DDIO, congestion, and imbalance groups. Re-plan after removing the owned term, then compare selected placement, p99.9, goodput, and corresponding counters. Include the mandatory topology-only versus load-aware contrast. Correct the declared family with Holm. Counter correlations are explanatory, display uncertainty, and are not presented as causal effects.

RQ6 reports rank correlation of candidate placement costs versus held-out p99.9, policy-ranking consistency, and calibrated-weight transfer. An alternate topology is a replication, not another repeated run of the same experimental unit.

### 9.5 Outlier, missingness, and exclusion policy

Do not remove statistical outliers based on latency or counters. Exclude a run only for a predeclared correctness/placement/clock/telemetry gate, external link/host fault, incomplete block state that cannot be paired, or violated steady-state rule. Retain every attempt and reason. There are no outcome-dependent reruns, neighboring-run substitutions, or arbitrary latency imputations for failed attempts. Primary inference remains the complete accepted-pair analysis; differential attrition is reported as an interpretation limit and operational-feasibility outcome. Report a sensitivity excluding externally diagnosed interruptions only if that category was defined before acquisition.

Missing packet or failed-attempt latency is not imputed; missing packet latency is packet loss and can invalidate a loss-free confirmatory run. Missing optional counters do not invalidate latency data but reduce RQ5 evidence. Missing mandatory placement, sequence, or clock evidence invalidates the run. Never substitute a nearby policy run to complete a block. Any attrition weighting or bounding analysis is exploratory and exists only if its covariates, positivity rule, formulas, and bounds were frozen in `AnalysisPlan` before unblinding; otherwise it is omitted. Such analysis never replaces the primary test.

### 9.6 Cost-weight sensitivity

Calibrate in seven ordered phases: freeze discovery/capabilities/catalog; unloaded directed primitives; service demand and capacity; congestion/interactions; training-unit identification; held-out validation; then immutable versioned freeze. The calibration unit is one complete accepted run. For run r, response y_r is log of its nearest-rank p99.9, and x_r contains the frozen normalized component features in the term-ledger order. Condition intercepts are fit only to absorb workload/topology levels and never enter the placement score.

Let `C_tr` be the training-run set and define `n_tr=|C_tr|>0`. The sole estimator is nonnegative ridge. For each positive lambda in a finite grid frozen before response fitting, minimize over unrestricted condition intercepts `delta_c` and effective coefficients `theta_j>=0`:

`(1/n_tr) sum_(r in C_tr) (y_r - delta_(c(r)) - x_r^T theta)^2 + lambda ||theta||_2^2.`

Condition intercepts are unpenalized, there is no additional global intercept, and intercepts are used only during fitting/evaluation; they never enter the placement score. The training/validation split and cross-validation folds operate on complete runs. Let `rho(r)` be the placement-relation group. Fold construction is condition-stratified while keeping every replicate with one `rho` in the same fold. Every condition participating in cross-validation must contain at least two independent placement-relation groups, and for every validation run `r` the corresponding training side must contain at least one accepted run `r'` with `c(r')=c(r)`. No packet is a split unit. Validate this contract before response fitting. If it cannot be satisfied, return `Condition-Coverage-Insufficient` and then `Calibration-Failed`; do not move validation observations into training, invent an intercept, or select another estimator.

Lambda is the grid value with minimum fold-size-weighted validation mean squared log-error over admissible folds; an exact tie selects the larger lambda. Refit on all training runs. `CalibrationDataset` and `CalibrationModelArtifact` store the condition-by-placement-relation coverage map, candidate/accepted folds, every fold-admissibility result, grid, fold IDs, relation blocks, seeds, feature order, transforms/scales, solver/version/tolerances, objective values, intercepts, coefficients, predictions, and input/output digests. Confirmatory records are rejected as calibration inputs.

Project the training feature matrix away from condition indicators before rank diagnosis. Exactly equal columns may be merged only if the ownership ledger identifies the same mechanism; the composite coefficient is their combined effect and the original terms are non-identifiable. Rank tolerance and maximum condition number are selected from arithmetic-resolution and coefficient-repeatability fixtures in a performance-blind implementation pilot and frozen. If the residualized matrix fails, disable the last implicated term in the pre-frozen mechanism-based feature precedence, then repeat. If the topology group is removed, a required group is empty, or the final design still fails, return `Calibration-Failed`.

For group g, let `s_g=sum_j theta_gj`. Require `s_top>0`. For every enabled group set `alpha_gj=theta_gj/s_g`, `beta_top=1`, and `beta_g=s_g/s_top`. A zero-sum group has `beta_g=0` and status `Disabled-Zero-Scale`, without a fabricated simplex vector. Verify exactly within frozen arithmetic tolerance that `x^T theta = s_top sum_g beta_g sum_j alpha_gj x_gj`. Intercepts are excluded from this identity and from planning.

Partition external validation before outcomes are revealed. For `C_val^seen={r in C_val: c(r) occurs in C_tr}`, compute mean squared log-error and residuals using the intercept fitted from `C_tr`, plus within-condition Spearman rank agreement, deterministic-tie top-choice accuracy, and regret. For `C_val^new`, no fitted condition intercept exists: do not compute absolute prediction MSE/residuals and do not estimate an intercept from validation outcomes. Evaluate unseen-condition transfer only by within-condition rank, top-choice accuracy, and regret over at least two independently admissible placement relations. These transfer metrics do not by themselves add an unseen condition to the primary validity domain. Before held-out outcomes are revealed, convert timestamp resolution, replicate noise, candidate decision margin, and required validity-domain coverage into frozen applicable loss/rank/top-choice/regret/admission limits. The model reaches B3 only if every rank, factorization, within-condition held-out, and domain gate passes. Otherwise return `Calibration-Failed` and block confirmatory B3; do not substitute an estimator, refit with confirmatory outcomes, or silently use a topology-only model.

Use a term-ownership ledger so a structural proxy, calibrated base latency, congestion surcharge, explanatory counter, or reassigned group cannot charge the same physical mechanism twice. Report coefficient uncertainty, all rank/collinearity actions, term-rank correlation, held-out metrics, and residuals. Sensitivity includes:

- each term removed;
- component weights varied over their within-group simplices and joint calibration region;
- relative group coefficients varied over their joint calibration uncertainty, including each non-reference group set to zero;
- alternate training-only regularization choices;
- alternate monotone normalizations;
- unknown-cost surcharge from zero lower bound through the maximum plausible calibrated penalty; and
- one global weight vector versus predeclared workload-class vectors.

Also compare the topology-only model (unloaded primitives, equal zero-load queue weights, `beta_load=0`) with the full load-aware model.

The exact-small reference is a separate component. For each eligible fixture it constructs every queue's uncapped raw finite bundle catalog, including every finite ownership entry and every context/PU/resource alternative, and defines the full global Cartesian product. It uses no heuristic dominance, locality pruning, candidate cap, incumbent restriction, Algorithm 1 output, or Algorithm 1 search order. In stable lexicographic order it visits every global combination, reconstructs shared maps, evaluates every hard constraint in F(G_s,l), counts each rejection class, evaluates full J for every feasible combination, and selects the minimum with the manuscript tie order.

Exact eligibility requires all four limits: maximum pipelines, maximum full Cartesian size, peak-memory budget, and wall-time budget. Numerical limits are chosen during off-stand implementation benchmarking from completion behavior on manual/captured fixtures, without heuristic outputs or latency effects, and frozen before the exact campaign. A preflight estimate above a limit, or runtime expiration before certified exhaustion, returns `Exact-Budget-Exceeded`. It never returns infeasibility. `Proven-Infeasible` is legal only when all raw enumerators and the global product are exhausted, the visited count equals the full Cartesian count, and the feasible count is zero. A feasible exhaustion returns `Exact-Feasible` with the exact minimum. The artifact stores input/catalog/budget digests, estimates and limits, Cartesian/visited/feasible counts, per-constraint rejection counts, incumbent history, best placement/value, tie trace, elapsed time, peak memory, and exhaustion certificate.

Before planner evaluation, manually specified minimal fixtures verify one feasible case, a tied optimum, each hard-constraint class, a globally inconsistent shared mapping, a proven-empty universe, and budget exceedance. Compare the heuristic and a deterministic locality-only heuristic only on `Exact-Feasible` fixtures; report objective rank, normalized gap, missed-feasibility, runtime, memory, cap expansion, and fallback. `Exact-Budget-Exceeded` fixtures have no known optimum and are excluded from gap/missed-feasibility denominators. The reference evaluates the heuristic; it does not make Algorithm 1 complete.

Confirmatory outcomes never feed weight updates. A model that fails any held-out admission gate remains `Calibration-Failed`; confirmatory B3 execution does not start until a prospectively specified model passes.

## 10. Correctness and acceptance gates

### 10.1 Gate sequence

Per-attempt gates follow the lifecycle: environment/reset, fresh-allocation/fault completion, independent page-location observation and coverage, applied data-plane affinity/finite ownership entry, complete observed-placement read-back, mapping probe, warm-up, packet/ring correctness, clock, steady state, mandatory telemetry, post-run placement/snapshot, then per-attempt performance admission. A later pass cannot override an earlier failure. B0/B1 equivalence is a separate pair-level gate after both immutable records exist; before that the pair is `Pair-Pending`, and finalization neither changes randomized execution nor overrides either attempt's decision.

| Gate | Required evidence | Acceptance rule for primary confirmatory data |
|---|---|---|
| Packet integrity | Immutable header/payload checks and request-response relation | Zero corrupt/invalid responses and zero ambiguous sequence matches |
| Sequence coverage | Committed exact `E`, `PacketExpectation` index, per-sequence response categories | `|V|=|E|` for the loss-free primary comparison; missing, corrupt, invalid, and timestamp-invalid counts each zero |
| Duplicates/out-of-range | All candidate responses indexed before filtering | Zero duplicate candidates and zero out-of-range responses in the primary comparison |
| Reordering | Transmit order and matched receive order | Within the frozen protocol/measurement tolerance; exact statistics always reported |
| Ring safety | Producer/consumer sequences, high-water, overwrite/lapping flags | Zero overwrite/lapping and no impossible sequence transition |
| Progress/drain | Per-stage progress and final queue/ring state | No stalled interval above timeout; all admitted requests completed before drain deadline |
| Logical/physical execution | Role-to-thread/context evidence, requested/effective masks, observed CPUs, occupancy ledger | Every role resolves to its declared physical context; RTC poller/worker uses one context and slot with summed service; staged roles use distinct contexts/slots; every CPU sample is allowed; all execution/PU/SMT constraints pass |
| Memory placement | Per-object material/null declaration; fresh-allocation ID; desired vector; requested/default policy; initializer/fault order; observed vector and coverage | Material RX/TX payload, controllable descriptors, ring, and state pages match B2/B3 allowed distribution; null ring/state has no allocation/reservation; desired/requested/observed are distinct; metadata exceptions are frozen |
| Per-attempt page observation | Fresh-allocation and initializer record; object inventory; observed vector, coverage and integrity | Every mandatory attempt object has a valid immutable observation under the frozen method; a missing pair mate is not a failure and records Pair-Pending |
| B0/B1 page equivalence | Both immutable matching records and digests; mandatory-object join; compatible IDs/coverage; frozen tau_mem/pilot digest | After both mates exist, every mandatory object has dTV<=tau_mem for Pair-Equivalent; otherwise Page-Equivalence-Failed or Page-Equivalence-Unsupported; failure excludes only the RQ1 pair, causes no rerun, and does not change another predeclared contrast |
| RX/TX queue ownership and worker mapping | Reference/selected finite catalog index and digest, control class, flow probe, queue/worker counters, requested action if any, observed owner/cardinality/share vector and range | Every probe flow reaches its fixed queue pair; B0--B2 equal the reference index; B3 uses its declared controllable entry; single-owner share is one; indirect/observed shares pass their range; no observed-only share is called applied |
| IRQ/poller/completion ownership | IRQ/vector counters or frontend role/context self-description plus CPU evidence | Matches the direction-specific logical and physical plan; unavailable roles are explicitly not applicable rather than assigned a guessed context |
| Planner search | `CandidateSearchAudit`, catalog digest, model admission, deterministic replay, constraint proof | Only `Feasible` with admitted model admits B3; list/search exhaustion are distinct; `Search-Limited`, `Cap-Limited`, `Data-Incomplete`, and `Calibration-Failed` are not infeasible; heuristic never emits `Proven-Infeasible`; all hard constraints pass |
| Topology consistency | Pre/post invariant digest, host/boot/device IDs | Identical throughout the run |
| Timestamp integrity | Clock state, wrap extension, offset/drift, timestamp validity | No unhandled wrap/step; invalid/lost timestamp rate within frozen bound; uncertainty bound satisfied |
| Telemetry completeness | Mandatory interval coverage and quality flags | Full phase coverage for mandatory events; optional missingness labeled |
| Generator fidelity | Actual versus intended rate/trace, generator capacity | Error within calibrated generator tolerance; no generator-side saturation |
| Environment stability | frequency, thermal, background/IRQ monitoring | Within frozen envelope; no undeclared workload |

If complete physical page enumeration is unavailable, the campaign must either obtain a validated alternative with a quantitative coverage bound or declare B2/B3 verification blocked. A small sample is not silently treated as proof of complete placement.

### 10.2 Performance acceptance

Only an attempt passing all of its mandatory gates has `A_bj=1`; only contrasts whose final pair indicator is one contribute to the corresponding latency comparison. The per-attempt acceptance record is generated before the result aggregator receives latency summaries. The pair-level page record is generated from immutable non-latency inputs and may finalize after the first attempt measured. Invalid data remain archived for diagnosis but are marked `scientifically excluded` for the affected analysis. Exclusion and policy-specific failure reasons are categorical and immutable.

Intentional overload/loss runs can pass a separate exploratory gate that requires correct accounting rather than zero loss. They must not enter the primary loss-free p99.9 analysis, because missing slow packets can bias the observed tail downward.

### 10.3 Ring overwrite and lapping

Use monotonically extended producer and consumer sequence counters, not only wrapped ring indices. At all observations, occupancy must remain within `[0, capacity]`; producer progress cannot exceed consumer progress by more than capacity; slots carry generation/sequence evidence sufficient to detect overwrite; shutdown drain verifies final equality for admitted events. Any lapping or sequence reuse ambiguity invalidates the run.

## 11. Planned tables and figures

No dummy values are permitted. The future results package will produce:

1. **Environment table:** CPU/socket/NUMA/cache, memory, PCIe/NIC path, firmware/driver/frontend, clocks, power/isolation, and build digests.
2. **Typed topology diagram:** packages, NUMA nodes, cache domains, PCIe roots/ports/switches/endpoints, NIC ports, selected queues, and candidate pools/workers; unknown edges visually distinct.
3. **Pipeline and placement diagram:** desired and observed TG → RX queue/descriptor/payload → I/O context → event ring → worker/state → TX payload/descriptor/queue → TG paths for B0–B3.
4. **Experiment and attrition table:** resolved factor levels; planned/attempted blocks; accepted attempts separately for B0--B3; complete B1/B0, B2/B1, and B3/B2 pairs; policy-specific gate-failure counts/rates and the policy causing each incomplete block; no latency values in this operational/correctness view.
5. **Correctness and operational-feasibility table:** packet integrity, sequence, loss/duplicates/reorder, ring, placement, page observation/equivalence state, planner/model/apply/rollback/read-back, clock, telemetry, environment, and `Search-Limited`/`Cap-Limited`/`Data-Incomplete`/`Calibration-Failed` proportions with explicit denominators by policy/condition.
6. **Latency distribution plots:** empirical complementary CDF and percentile panels for p50, p90, p99, p99.9, and exploratory p99.99; valid/missing/corrupt/duplicate counts shown.
7. **Primary paired p99.9 plot:** the conditional accepted-pair `B3/B2` mean log-ratio effect at `l*`, transformed relative effect, one-sided upper confidence bound, two-sided estimation interval, paired run traces, accepted/planned pair counts, and paired-t assumption diagnostics; the sharp-null randomization result is labeled secondary, and RQ1/RQ2 appear in a separate key-secondary panel.
8. **Load-versus-latency curves:** offered and achieved rate against p99.9, with loss/goodput and knee annotations.
9. **Queue/worker scalability plots:** p99.9, goodput, CPU cost, and imbalance versus Q/W, distinguishing `Q<W`, `Q=W`, and `Q>W`.
10. **Cost-function and planner-quality table:** selected plan, component/group scores and coefficients, p99.9 effect and held-out ranking after each term/group removal, topology-only versus load-aware contrast, ownership/physical-placement mechanism variants, and exact-small-instance missed-feasibility/gap/runtime results versus the locality-only heuristic.
11. **Remote-access/interconnect correlation panels:** observed page/NUMA events, PCIe/inter-socket traffic, queue occupancy, and p99.9, with scope and uncertainty.
12. **Calibration plots:** measured path costs, normalization, coefficient uncertainty, condition/placement-relation coverage and admissible folds, seen-condition held-out loss/residuals, and unseen-condition rank/top-choice/regret transfer without an absolute intercept-based MSE.
13. **Planner/configuration overhead table:** graph, candidate, scoring, refinement, apply, validation, and rollback time.
14. **Sensitivity/robustness table:** frontend, topology, SMT, burst/skew, normalization, and weight sensitivity, explicitly secondary.

Every caption states the experimental unit, number of runs and packets, interval method, and whether the result is confirmatory or exploratory.

## 12. Reproducibility package

### 12.1 Required artifacts

The later implementation repository must produce and retain:

- raw and normalized topology snapshots, hwloc XML, relevant sysfs captures, BDF joins, diagrams, validation findings, and digests;
- environment manifests for TG and SUT, firmware/driver/kernel/frontend/build manifests, binary/shared-library checksums, and provisioning records;
- frontend and capability profiles, frozen finite ownership catalogs and share-control/read-back evidence, hard constraints, workload specifications, exact flow lists, RSS keys/tables, traffic traces, and sequence manifests;
- calibration design; one-row-per-accepted-run dataset; raw observations; valid/excluded index; feature order/transforms; condition-by-placement-relation coverage map; candidate/admissible fold and seed records; fold-admissibility findings; lambda grid and fold losses; rank/collinearity merge/disable ledger; effective coefficients; factorized alpha/beta; seen-condition loss/residuals; unseen-condition rank/top-choice/regret without absolute MSE; validity/admission status; uncertainty; and model digests;
- reference worker/catalog mappings, CPU-access profiles, planner decision scopes, raw/unpruned/exposed candidate counts and exhaustion flags, dominance certificates, cap expansions, search nodes/depth/budgets, conflict witnesses, exact neighborhood counts, placement outputs, per-component/group scores, tie-break trace, completion/fallback status, time, and peak memory;
- exact-small inputs and raw catalogs, resource limits/estimates, Cartesian/visited/feasible/rejection counts, best placement/value, tie trace, exhaustion certificate or Exact-Budget-Exceeded status, time, peak memory, and input/result digests;
- prior-state journals, fresh-allocation and topology-blind/policy-specific immutable per-attempt page-initialization/observation records, desired/requested/applied/observed placement records, pending and final B0/B1 dTV/tau_mem pair records, ownership-share observations, validation probes, rollback records, and dirty-host markers;
- exact `PacketExpectation` records and all received candidates; raw paired timestamps when feasible; nearest-rank N/index/tied-order semantics; if storage forces histograms, retain declared edges/closure, underflow/overflow, integer counts, total-count proof, containing-bin bounds for every rank, tail bin-width bound, and formally propagated percentile interval-censoring error; never call a binned representation lossless unless exact raw values are recoverable;
- queue/ring progress and safety logs, packet integrity/loss/reorder reports, and correctness-oracle output;
- raw counter samples with scopes, units, event encodings, wrap/multiplexing quality, and time alignment;
- run phase records, randomized block order/seed, planned and attempted block counts, all B0--B3 attempt IDs and `A_bj`, adjacent-pair indicators and states, accepted policy/pair counts, policy-specific categorized failure counts/rates and denominators, policy causing each incomplete block, exclusions, operator events, cooldown/stability evidence, and clock calibration;
- frozen analysis specification including the conditional accepted-pair estimand, operational-feasibility report, and either predeclared attrition weighting/bounding formulas or an explicit none; `PRE_IMPLEMENTATION_DECISIONS.md` freeze snapshot; analysis environment; derived datasets; table/figure inputs; statistical outputs; and provenance from every cell/point to scheduled attempt IDs; and
- a top-level cryptographic checksum manifest, schema documentation, license/access notes, and immutable campaign index.

### 12.2 Artifact hierarchy

Artifacts are keyed by campaign → topology snapshot → block → run attempt. Content-addressed immutable inputs are referenced rather than copied inconsistently. A run record contains the digests of every input and output. Derived summaries never overwrite raw data. Sensitive host identifiers, if redacted for release, retain stable pseudonyms and a private mapping audit.

### 12.3 Reproduction levels

- **Off-stand structural reproduction:** load captured topology fixtures, build the graph, replay the planner, validate deterministic output, parse stored run records, and reproduce tables/figures.
- **Fixture-based integration:** emulate failure/missing-data cases using captured hwloc/sysfs/frontend snapshots and validate application/rollback state machines without a real NIC.
- **Physical reproduction:** provision compatible TG/SUT hosts, collect a new environment snapshot, recalibrate path/cost terms, execute frozen blocks, and compare effect estimates rather than expecting identical raw latency.

## 13. Milestones for the future implementation repository

Each milestone has a category: **off-stand**, **fixture**, **physical stand**, or **analysis**. A separate Codex session can begin with this specification and the captured fixtures; it must not need the final benchmark stand for early milestones.

| # | Category | Milestone | Inputs | Outputs | Verification criteria | Dependencies |
|---:|---|---|---|---|---|---|
| 1 | Off-stand | Freeze schemas, decisions, and scientific protocol | This specification, manuscript notation, and `PRE_IMPLEMENTATION_DECISIONS.md` | Versioned conceptual/data schemas, invariant catalogue, error taxonomy, decision-gate ledger, campaign template | All 24 registry contracts map to artifacts; unknown/zero/not-applicable distinct; frozen decisions preserved; all RQs map to fields | None |
| 2 | Fixture | Acquire and curate topology fixtures | hwloc XML and captured sysfs/device/frontend snapshots from representative hosts | Immutable normal, incomplete, inconsistent, hotplug, multi-root, and virtual-function fixtures with checksums | Fixture provenance documented; no physical address/secret leakage; expected facts hand-reviewed | M1; access to any capture host, not final stand |
| 3 | Off-stand/fixture | Topology inspector | Schemas and fixtures | Raw observation records and error reports | Golden-fixture agreement; read-only; missing privilege and disappearing-device tests | M1–M2 |
| 4 | Off-stand/fixture | Graph builder and serializer | Inspector output and graph schema | Typed snapshots, validation findings, deterministic serialization and diagram source | Round-trip identity; contradictory joins rejected; unknown never becomes zero; same input yields same digest | M3 |
| 5 | Off-stand | Finite planner, cost evaluator, and independent exact reference | Graph, capability, finite ownership, manual topology, workload/constraint/reference-map/CPU-access fixtures | Complete finite RX/TX candidates, `CandidateSearchAudit`, deterministic heuristic plan/score/status, separate `ExactReferenceResult` and locality-only output | No continuous share; primary k=1/share=1; RTC/staged and every hard constraint; safe heuristic dominance; list/search distinction; no heuristic infeasibility; exact solver ignores heuristic/pruning, exhausts full product, checks manual optima/ties/infeasibility/budget, and reports certificate/counts/time/memory | M1, M4 |
| 6 | Off-stand/fixture | Applicator, page-initializer, and pair-join state machines with mock backends | Placement/action/page schemas, decision register, and captured prior states | Desired/requested/applied/observed journals, immutable fresh-allocation/page-initialization records, Pair-Pending/final dTV records, rollback protocol | Failure at every action; both B0/B1 arrival orders; first attempt may measure while pair pending; final join is immutable/order-independent/no-latency and triggers no rerun; B0/B1 identical topology-blind fault order before affinity; B2/B3 fresh allocations; observed-only share has no apply action; reverse rollback/dirty-host verified | M1, M5 |
| 7 | Off-stand | Traffic, sequence, clock, and correctness core | Workload/packet/clock schemas | Generator/receiver/oracle modules, exact sequence manifest, wrap/duplicate/reorder/corruption handling | Deterministic packet fixtures; initial/terminal loss detected; clock wraps extended; corrupt/duplicate cases rejected | M1 |
| 8 | Off-stand | Ring, pool, worker, and frontend abstractions | Frontend/pipeline schemas | Component contracts and mock implementations for lifecycle/progress/error testing | Lapping/overwrite, stall, capacity, ownership, and cleanup tests; identical logic across policy modes | M1, M7 |
| 9 | Fixture | Telemetry and result ingestion | Counter fixtures and run schemas | Counter normalization, wrap/multiplexing quality, immutable raw/derived data pipeline | Counter scope preserved; wraps/resets tested; no packet-as-repetition error; provenance round trip | M1–M2 |
| 10 | Analysis | Statistical analysis, attrition audit, and report generation | Frozen synthetic **test fixtures labeled non-measurement**, schemas, and attempt/pair state fixtures | Sole-primary conditional accepted-pair mean log-ratio estimate, one-sided paired t-test and aligned confidence bound, t diagnostics, policy/pair acceptance and categorized attrition/operational-feasibility tables, separately labeled sharp-null and any prospectively frozen attrition/bootstrap/sign sensitivities, Holm key-secondary family, within-run moving-block uncertainty, figures/tables | Conditional and unconditional interpretations cannot be confused; weak-mean-null and sharp-null outputs distinct; both page-record arrival orders, policy-specific failures, incomplete pairs, campaign-wide calibration failure, and denominator reconciliation tested; no rerun/substitution/imputation; fixed schedule enforced; every output traces to scheduled attempt IDs; synthetic values never appear as results | M1, M9 |
| 11 | Physical stand | Stand qualification and environment capture | TG/SUT access, privilege plan, schemas | Environment manifests, topology snapshot, counter/timestamp capability audit, link/isolation proof | SUT meets multi-socket/local-remote requirements; timestamp error bounded; all mandatory controls/read-backs feasible | M3–M4, physical stand |
| 12 | Physical stand | Frontend integration and baseline application | Qualified stand, primary capability/profile, finite catalog, reference mapping, CPU-access profile, planner/applicator/initializer | Working B0–B3 setup with desired/requested/applied/observed logical/physical/page/share records | B0/B1 same initializer; per-attempt immutable observations and post-mate object-wise dTV join work in both randomized orders without delay/rerun; B0--B2 preserve reference catalog index; B2 preserves B1 CPU placement on fresh bound pages; B3 controllable catalog mapping explicit; ownership shares, RTC/staged occupancy, affinity, pages, queues, owners, and workers validate; rollback restores prior state | M5–M8, M11 |
| 13 | Physical stand | Calibration and independent pilot | Integrated stack, resolved workload/rank/admission rules, counter catalogue | Accepted-run calibration dataset; exact n_tr ridge objective; condition/placement-relation coverage map; candidate/admissible folds and findings; nonnegative-ridge grid/fold losses; rank/merge/disable ledger; effective/factorized weights; seen-condition loss/residuals; unseen-condition rank/top-choice/regret; saturation/knee/service/RSS; timestamp; tau_mem; warm-up/duration/N; `l*`; power; fixed schedule; admitted frozen model | Every validation condition has training coverage and each CV condition has at least two independent relations or Condition-Coverage-Insufficient; unseen transfer uses no fitted/validation-derived intercept or absolute MSE; estimator replay and coefficient identity pass; model meets pre-frozen admission/domain gates; pilot/calibration IDs excluded; all artifacts digested before unblinding | M9, M11–M12 |
| 14 | Physical stand | Confirmatory execution | Frozen campaign and exact randomized attempt schedule | Complete planned/attempt/run index, A_bj and pair states/indicators, accepted raw data, policy-specific categorized validation/exclusion records | Fixed schedule completed without outcome-dependent expansion/rerun/substitution; pair-pending resolution does not alter order; p99.9 and acceptance gates applied; policy/pair attrition denominators reconcile; reduced power reported if valid n not reached; checksums complete | M13 |
| 15 | Physical stand | Ablation and robustness execution | Accepted core campaign and predeclared secondary matrix | Term ablations, burst/skew/scale/topology/frontend replication data | Separate families; re-planning performed for term removals; all gates applied | M14 |
| 16 | Analysis | Final statistical analysis and artifact audit | Immutable M14–M15 package and frozen `AnalysisPlan` | Tables, figures, sole primary conditional accepted-pair paired-t hypothesis decision, policy-specific attrition and operational-feasibility report, secondary sharp-null/ownership/cost/predeclared-attrition/exploratory results, limitations, reproducibility archive | Independent rerun reproduces every artifact; conditional estimand/test cannot be substituted or generalized; all scheduled/attempted/accepted/pair/failure counts reconcile; no failed latency imputation; assumptions and sensitivity labels verified; RQ1/RQ2 Holm family and uncertainty verified; checksum audit passes | M10, M14–M15 |
| 17 | Analysis/manuscript | Populate results and conclusion | Audited analysis outputs | Evidence-backed Results, Discussion, revised Abstract, and Conclusion | Every new factual claim added to `CLAIM_EVIDENCE_MATRIX.md`; no unsupported extrapolation; LaTeX builds without warnings | M16 |

### 13.1 Stand-independent stopping point

Milestones 1–10 can be implemented and unit-tested without the final stand. Milestones 2–4 and 9 benefit from captured hwloc/sysfs/counter fixtures from any representative machines. Milestones 11–15 require the physical multi-socket stand. Milestones 16–17 require immutable real data from that stand. If stand qualification fails—especially if no distinguishable local/remote PCIe/NUMA path or no valid external timestamp exists—the experiment must stop and revise the scientific design rather than simulate measurements.

### 13.2 Handoff rule

The future implementation session starts at Milestone 1 with this file and imports `PRE_IMPLEMENTATION_DECISIONS.md` as its staged gate ledger. It must preserve every `FROZEN` row, leave testbed-blocked values unresolved until their freeze stage, reconcile `U01`–`U06`, and preserve the four-baseline causal structure, finite ownership catalogs, B0/B1 page-equivalence requirement, nearest-rank estimator, nonnegative-ridge estimator, and exact-reference status semantics. It must not infer missing stand values, alter the packet path between baselines, or create synthetic data presented as measurements.
