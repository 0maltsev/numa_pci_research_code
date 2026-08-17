# Project Progress

Last updated: 2026-08-17  
Stage status: final pre-implementation contract revision complete; off-stand implementation handoff ready; physical evaluation pending

## Completion summary

The final scientific and documentary revision is complete through experimental methodology. Ownership is a finite frontend-qualified catalog rather than a continuous share simplex; direct, validated-indirect, and observed-only control semantics are distinct, and the primary profile is single-owner. Calibration now has one exact complete-run nonnegative-ridge objective, condition-stratified placement-relation-blocked folds with an auditable coverage gate, and separate seen-condition absolute versus unseen-condition ranking-only validation. B0 and B1 use fresh allocations and one topology-blind pre-affinity initializer; each attempt receives an immutable page record, while a later order-independent pair record controls only RQ1 admission. The sole primary B3/B2 latency estimand is explicitly conditional on accepted complete pairs and is accompanied by mandatory policy/pair attrition and operational-feasibility reporting. A 23-row staged decision register and 24 field-level component contracts make the off-stand handoff explicit without guessing testbed values. The manuscript contains no measured result, hypothesis decision, results-dependent discussion, or empirical conclusion.

## Stage status

| Stage | Status | Completion evidence |
|---|---|---|
| 1. Repository inspection | Complete | `AGENTS.md` was read; the document structure, bibliography, build, PDFs, catalogue anomalies, and unavailable records were inspected. |
| 2. Literature map | Complete | `LITERATURE_MATRIX.md` classifies all 50 catalogue records, all 42 available full texts, and one separate non-paper implementation proposal. |
| 3. Research gap | Complete | `RESEARCH_GAP.md` separates CPU affinity, memory policy, PCIe/NIC locality, queue ownership, DMA memory, synchronization, worker placement, and tail metrics using bounded novelty wording. |
| 4. Claim--evidence matrix | Complete | `CLAIM_EVIDENCE_MATRIX.md` records 72 admitted claims (35 supported and 37 derived) and six unresolved testbed inputs. |
| 5. Scientific outline | Complete | `SCIENTIFIC_OUTLINE.md` preserves the hardware-nonuniformity-to-controlled-evaluation argument chain and the revised formal objects. |
| 6. Manuscript | Complete through methodology | Eleven section files contain the pre-results abstract, motivation, related work, formal model, graph, cost, algorithm, system design, methodology, and one explicit results/discussion/conclusion placeholder. |
| 7. Experimental specification | Complete | `EXPERIMENT_SPEC.md` contains all required sections, a registry of 24 producer/consumer contracts with fields, units, invariants, digests, errors, and verification procedures, four exact baselines, fixed statistical rules, acceptance gates, artifacts, and 17 ordered milestones. `PRE_IMPLEMENTATION_DECISIONS.md` supplies the staged freeze gate. |
| 8. Document validation | Complete | A forced clean TeX Live 2026 `latexmk -gg` build produces a 33-page PDF. The final LaTeX and BibTeX logs contain no warnings, undefined citations/references, missing glyphs, or overfull/underfull boxes. All 33 pages were rendered at 144 dpi and visually inspected; all 300 per-page font-usage records are embedded Type 1 fonts with ToUnicode maps. `paper/BUILD.md` records the commands and retained-artifact policy. |

## Revision decisions completed

1. The placement tuple now includes direction-specific RX/TX queue pairs, descriptor and payload memory, typed material/null event-ring and application-state objects, logical worker/I/O roles, owner sets and shares, a role-to-physical-context map, and a context-to-processing-unit map.
2. Eligibility, role/context/PU service, byte, slot, ring-rate, physical-context/PU multiplicity, SMT, exclusivity, isolation, ownership, and shared-resource constraints are hard feasibility conditions. Run-to-completion is an explicit one-context/one-slot equality case with summed demand; staged roles use distinct contexts and slots.
3. Notation distinguishes offered rates, event rate, service demand, capacities, locations, and mappings. Units, normalization, zero-load behavior, unknown values, and measurable versus calibrated quantities are stated.
4. The request/response cost covers RX/TX payload and descriptor DMA, I/O-context memory access, worker payload access, event synchronization, state access, MMIO/control, and cache/DDIO effects. Component weights are normalized within explicit topology/load groups, group coefficients determine relative scale, and a term-ownership ledger plus unloaded-response subtraction prevents base/congestion double counting; calibration follows seven frozen phases.
5. The unsupported restricted-case hardness theorem was removed. The paper makes no complexity-class claim for the full typed formulation and labels the planner a deterministic heuristic without an optimality guarantee.
6. Algorithm 1 defines complete candidate construction, a resource-identical safety certificate for dominance, cap expansion and regeneration, bounded backtracking, five exact local neighborhoods, tie-breaking, full time/memory bounds, incomplete-data handling, and exact-small-instance/locality-only quality checks. The heuristic reports `Search-Limited`, `Cap-Limited`, or `Data-Incomplete` without claiming infeasibility; only a separate complete checker may supply `Proven-Infeasible` with a certificate.
7. Logical roles map to physical execution contexts and then PUs. RTC poller/worker roles occupy one context and slot with summed service; staged roles occupy distinct contexts and slots. Absent ring/state stages use typed zero-capacity, zero-cost null objects.
8. B0--B2 preserve one topology-agnostic reference queue-to-worker mapping and frozen finite ownership-catalog indices. The primary profile has one owner and share one; qualified shared-owner catalogs are secondary, while observed-only shares are frozen workload observations and never applicator claims. B3 may choose only controllable catalog entries within invariant inventories/cardinalities; fixed-reference and ownership-only variants expose that treatment component.
9. Confirmatory measurement requires two physical hosts and a qualified single-clock external turnaround path. Exact expected-sequence accounting distinguishes missing, corrupt, duplicate, ambiguous, reordered, and out-of-range responses.
10. The sole primary estimand is the conditional mean paired log p99.9 ratio among accepted B3/B2 pairs at one frozen reference condition. Its primary inference is a one-sided paired t-test for the weak conditional mean null with an aligned confidence bound; label randomization is a separately labeled sharp-null sensitivity. Planned, attempted, accepted-policy, and adjacent-pair counts plus categorized policy failures are mandatory operational-feasibility outputs. A performance-blind pilot fixes sample size and the complete attempt schedule; there is no outcome-dependent extension, rerun, substitution, or failed-latency imputation.
11. The DPDK prior-art entry now cites Vipin Varghese's exact 5 November 2024 `[PATCH v4 0/4]` primary archive message; the March 2025 item is labeled as follow-up review.
12. The motivation, typed-topology, and system-information-flow figures were revised as LaTeX-native vector diagrams; DMA and control arrows were routed clear of node boxes and labels. The document has keywords, non-final author placeholders, and PDF metadata; `JOURNAL_SUBMISSION_CHECKLIST.md` records venue-dependent submission work.
13. B0/B1 first-touch confounding is controlled by one separate topology-blind initialization context, fresh per-attempt processes and allocations, default memory policy, and complete pre-affinity faulting. Each attempt independently validates and freezes its page observation; a pair remains `Pair-Pending` until both immutable records exist, after which an order-independent `Pair-Equivalent`, `Page-Equivalence-Failed`, or `Page-Equivalence-Unsupported` record controls only RQ1 without delaying measurement or triggering a rerun.
14. Every latency percentile uses the one-indexed nearest-rank estimator with explicit zero/one boundaries, no interpolation, stable handling of ties, exact response filtering, one-time tick conversion, and bounded-histogram interval semantics. p99.9 remains primary and p99.99 exploratory.
15. Calibration uses complete accepted runs, log nearest-rank p99.9, `n_tr=|C_tr|`, the exact averaged squared-error plus ridge objective, unpenalized fit/evaluation-only condition intercepts, no global intercept, and a finite positive regularization grid. Cross-validation is condition-stratified and placement-relation blocked, requires at least two independent relation groups per participating condition and training coverage for every validation condition, and stores the coverage/fold audit. Seen conditions receive training-intercept absolute validation; unseen transfer receives rank/top-choice/regret only. Coverage or admission failure terminates as `Calibration-Failed`.
16. The independent exact-small procedure enumerates the entire uncapped finite Cartesian catalog, checks every hard constraint and the full objective, and certifies feasibility or infeasibility only after exhaustion. Predeclared pipeline/Cartesian/time/memory budgets instead yield `Exact-Budget-Exceeded` and never a false infeasibility claim.
17. `PRE_IMPLEMENTATION_DECISIONS.md` records 23 decisions with allowed options, defaults, evidence, freeze points, affected components, and reopen rules for off-stand, integration, calibration, and confirmation stages. D23 freezes the conditional estimand and attrition policy.
18. The results placeholder now names the calibration coverage/fold audit, seen/unseen validation split, immutable page states, all policy/pair denominators, categorized attrition, conditional latency analysis, nearest-rank estimates, and exact-reference statuses that real measurements must later populate; no result or superiority claim was added.
19. `paper/BUILD.md` freezes the qualified TeX toolchain, commands, warning/font/page/visual checks, missing-package failure policy, and decision not to retain generated `main.bbl`; `resources/RESOURCE_AUDIT.md` records the independent file-level archive audit.

## Source review

- Catalogue: **50** records. Available full texts: **42 papers**, **633 PDF pages** (**27 core / 430 pages**, **15 methods / 203 pages**), independently counted with Ghostscript 10.07.0.
- Full-text categories: **11** direct NUMA/PCIe/NIC/I/O-locality; **14** packet-processing/network-I/O architecture; **8** CPU/memory/runtime placement; **6** topology mapping/scheduling; **3** tail-latency/experimental methodology.
- Updating search: eleven new records screened, five full papers admitted (RxBisect, Phoenix, State--Compute Replication, ShRing, and X-Lane), one DPDK development proposal retained as non-peer-reviewed implementation prior art, and five records excluded. Queries and selection limits are recorded in `LITERATURE_SEARCH_PROTOCOL.md`.
- Unavailable and excluded from evidence: catalogue IDs **3, 4, 5, 7, 8, 11, 16, and 34**; reasons are in `resources/unavailable_papers.tsv`. ID 11 remains a slide-only lead.
- Integrity: all 42 admitted PDFs have distinct recorded SHA-256 digests and pass checksum verification from the repository root; a fresh hash grouping found zero duplicates. IOctopus and nanoPU retain known parser-anomaly notes, but valid PDF signatures, matching checksums, complete Ghostscript structural traversal, exact page counts, and meaningful extracted text through their references make the anomalies non-blocking. The current environment lacks `pdfinfo` and `pdftotext`; no resource file was modified.
- The ID 21 archive file is the inspected 2024 COREC arXiv preprint, not the different 2025 catalogue title. The bibliography cites only verified preprint metadata.
- The manuscript bibliography contains **35 inspected sources**. AF_XDP authorship, venue, pages, and DOI were corrected; no unavailable source is cited.

## Files created or materially modified

- Evidence and search: `LITERATURE_MATRIX.md`, `LITERATURE_SEARCH_PROTOCOL.md`, `RESEARCH_GAP.md`, and `CLAIM_EVIDENCE_MATRIX.md`.
- Planning and handoff: `SCIENTIFIC_OUTLINE.md`, `EXPERIMENT_SPEC.md`, `PRE_IMPLEMENTATION_DECISIONS.md`, and `JOURNAL_SUBMISSION_CHECKLIST.md`.
- Resource records: `resources/manifest.tsv`, `resources/README_RU.md`, the new `resources/RESOURCE_AUDIT.md`, and five added inspected PDFs.
- Manuscript: `paper/main.tex`, `paper/references.bib`, and `paper/sections/01_abstract.tex` through `paper/sections/11_results_placeholder.tex`. This final cycle materially revised sections 01, 02, 07, 10, and 11; sections 03--06, 08, and 09 and the bibliography required no new scientific change.
- Build record and validated artifact: `paper/BUILD.md` and retained `paper/main.pdf`; generated auxiliary, log, and `.bbl` files are removed after validation under the documented policy.
- Status record: `PROGRESS.md`.

## Unresolved citation or metadata issues

- The eight unavailable catalogue papers cannot support claims until their full research texts are obtained and inspected.
- No uncertain entry is admitted to `paper/references.bib`. The COREC catalogue mismatch and the non-peer-reviewed DPDK proposal are labeled in the matrices.
- The target venue, venue template, final author list, affiliations, ORCIDs, corresponding-author data, funding, acknowledgments, conflict statement, data/code availability wording, and venue-specific bibliography style remain unsupplied. The current `article` wrapper is deliberately reversible.

## Open scientific decisions

Rows `U01`--`U06` in `CLAIM_EVIDENCE_MATRIX.md` remain unresolved:

1. final CPU/NUMA/cache/PCIe/NIC topology;
2. NIC firmware, driver, queue limits, timestamp capabilities, and counters;
3. DPDK or AF_XDP as the primary confirmatory frontend;
4. calibrated cost coefficients and path penalties;
5. absolute offered rates, sustained duration, and queue/worker maxima; and
6. valid uncore, cache, PCIe, and interconnect events.

The 23-row decision register turns these broad inputs into staged gates. `D15` (smallest scientifically relevant effect) remains an investigator decision. `D01`, `D02`, `D09`, `D13`, `D18`, `D20`, and `D22` have protocol defaults but still require qualification. D23 is frozen and does not supply a stand value. No unresolved row is silently assigned a numerical parameter.

## Work blocked on the physical testbed

- `D04` timestamp tier, `D05` direct/switched path, `D06` page-location mechanism, `D07` NIC port/BDF, `D08` huge-page configuration, and `D10` hardware counters.
- `D14` reference workload, `D16` warm-up/cooldown gates, `D17` page-equivalence tolerance, and `D19` cost-model validity domain.
- Stand qualification and complete environment/topology capture; frontend privileges, independent read-back, rollback, and four-baseline validation.
- Saturation, service-demand, queue-drain, RSS, page-repeatability, timestamp-error, and seven-phase cost calibration.
- Fixed confirmatory campaign, ablations, robustness runs, replication, and statistical analysis.
- Evidence-backed results, hypothesis decisions, revised abstract, discussion, and conclusion.

## Scope confirmation and future entry point

No experimental implementation, source code, launcher, orchestration script, synthetic measurement dataset, fabricated log, plot, table, or performance result was generated. Results and the conclusion remain an explicit placeholder.

The exact entry point for a separate future implementation repository and Codex session is **`EXPERIMENT_SPEC.md`, Milestone 1**. Its first action is to import `PRE_IMPLEMENTATION_DECISIONS.md`, preserve all `FROZEN` rows, implement unresolved states as explicit gates, and resolve `U01`--`U06` before confirmatory execution.
