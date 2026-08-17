#!/usr/bin/env python3
"""Generate the immutable Milestone 1 decision ledger and campaign template."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from tools.canonical_json import digest_document
except ModuleNotFoundError:  # Direct execution adds tools/, not the repository root.
    from canonical_json import digest_document


ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-08-17T13:40:05Z"
ZERO_DIGEST = "sha256:" + "0" * 64
CONTRACT_DIGESTS = [
    "sha256:9b685e095d175df898080c15b9929642c0ab5c860fdbab463d102fa0558fc409",
    "sha256:802a2053ab8c3c0f6f8bd803668ddaa24455cc1ae3721bc0d83f8594c113205e",
    "sha256:67ecff1220cb949abafb50f89daf0d0f7e050bd5cb7a579360dee81c83d8f4fd",
    "sha256:c5877e26e2f28271473681ee3ce51961469149cd5c6ee0404ce5673031c9f565",
    "sha256:720414761fa65e7a616e59f64621857faf8d38d757964e8b82442be1765139bb",
    "sha256:d38c3284590f4e7f8fd8f56abf166115919786e983f2c8b73dd437ef9e81b8ac",
    "sha256:782c3ca3912ab346db99e9ad0e5024e270d551ddc64b805a4cd414cd1516a553",
    "sha256:31e3ae3dd23369593e61aadb1b887cd53a190968b0854977364128736dede94b",
    "sha256:25e69d112f669bdfb4015fa9ddda0caee293cea6888b7a01a90eb7ca47784b32",
]


def known(value: str | bool | list[str]) -> dict[str, Any]:
    return {"state": "Known", "value": value}


def unknown(reason: str) -> dict[str, str]:
    return {"state": "Unknown", "reason": reason}


def quantity_unknown(unit: str, reason: str) -> dict[str, str]:
    return {"state": "Unknown", "unit": unit, "reason": reason}


def metadata(
    *, record_id: str, input_digests: list[str], status_kind: str, status_code: str,
    artifact_class: str, transformation: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "record_id": record_id,
        "producer": {"identity": "tool:milestone1-protocol-freezer", "version": "1.0.0"},
        "created_at": {"value": CREATED_AT, "clock_domain": "UTC"},
        "campaign_or_stage_id": "stage:milestone-1",
        "input_digests": input_digests,
        "canonical_digest": ZERO_DIGEST,
        "status": {"kind": status_kind, "code": status_code, "detail": "Milestone 1 protocol definition; not measurement data"},
        "errors": [],
        "artifact_class": artifact_class,
        "data_classification": "ProtocolDefinition",
        "scientific_disposition": "NotMeasurement",
        "validity_domain": {
            "state": "Known",
            "definition": "Scientific protocol and schema version 1.0.0 only",
            "evidence_digests": input_digests,
        },
        "provenance": {
            "source_record_ids": [],
            "source_digests": input_digests,
            "transformation": transformation,
            "raw_records_immutable": True,
        },
    }


DECISIONS: list[dict[str, Any]] = [
    {
        "decision_id": "D01", "decision": "Primary packet-I/O frontend", "state": "PendingQualification",
        "allowed_options": ["DPDK", "AF_XDP"],
        "recommended_default": known("First profile passing every control, read-back, timestamp-volume, and invariant-path gate"),
        "selection_evidence": "Off-stand capability audit and stand qualification without latency comparison",
        "freeze_point": "Before stand integration plan acceptance",
        "affected_components": ["capability-profile", "frontend", "pools", "queues", "applicator", "validator", "planner"],
        "reopen_conditions": "Mandatory capability failure or driver/kernel/profile revision",
    },
    {
        "decision_id": "D02", "decision": "Primary pipeline", "state": "PendingQualification",
        "allowed_options": ["RunToCompletion", "Staged"],
        "recommended_default": known("RTC only when the frozen service requires no material handoff"),
        "selection_evidence": "Functional semantics, slot accounting, service operation, and invariant-path evidence",
        "freeze_point": "Before frontend integration",
        "affected_components": ["pipeline-manifest", "role-context-model", "ring", "worker", "planner"],
        "reopen_conditions": "Service semantics or correctness/capacity gates require a handoff",
    },
    {
        "decision_id": "D03", "decision": "Primary ownership mode", "state": "Frozen",
        "allowed_options": ["SingleOwner", "QualifiedFiniteSharedOwnerSecondaryOnly"],
        "recommended_default": known("SingleOwner"),
        "resolved_value": known(["mode=SingleOwner", "owner_cardinality=1", "share=1", "scope=every-controllable-non-null-direction"]),
        "selection_evidence": "Frozen scientific contract D03",
        "freeze_point": "Before off-stand schemas and planner tests",
        "affected_components": ["ownership-catalog", "planner", "applicator", "validator", "baselines"],
        "reopen_conditions": "Prospective versioned secondary or replication protocol after D20; never confirmatory outcomes",
    },
    {
        "decision_id": "D04", "decision": "Timestamping tier", "state": "BlockedOnTestbed",
        "allowed_options": ["ExternalSingleClockInstrument", "SameTgNicHardwareTxRx", "BoundedTgSoftwareDiagnostic", "Unsupported"],
        "recommended_default": known("Highest qualified tier in the declared decision-tree order"),
        "selection_evidence": "Clock identity, boundary, capacity, loss, resolution, bias, drift, and overhead qualification",
        "freeze_point": "Before calibration timing data",
        "affected_components": ["traffic-generator", "timestamp-backend", "oracle", "analysis"],
        "reopen_conditions": "Clock, NIC, firmware, or rate validity domain changes",
    },
    {
        "decision_id": "D05", "decision": "Direct-link or switched topology", "state": "BlockedOnTestbed",
        "allowed_options": ["DirectIsolatedLink", "InvariantQualifiedSwitchPath"],
        "recommended_default": known("DirectIsolatedLink"),
        "selection_evidence": "Physical availability, isolation, QoS visibility, and reproducible-path evidence",
        "freeze_point": "Before stand campaign definition",
        "affected_components": ["environment", "traffic-generator", "timestamp-path", "validity-domain"],
        "reopen_conditions": "Cabling or path change",
    },
    {
        "decision_id": "D06", "decision": "Page-location verification mechanism", "state": "BlockedOnTestbed",
        "allowed_options": ["CompletePageInventory", "ValidatedBoundedCoverage", "Unsupported"],
        "recommended_default": known("CompletePageInventory when privilege and page type permit"),
        "selection_evidence": "Coverage, classification accuracy, perturbation, resolution, and repeatability",
        "freeze_point": "Before baseline integration",
        "affected_components": ["page-initializer", "pool-manager", "observed-validator", "b0-b1-gate"],
        "reopen_conditions": "Kernel, page type, privilege, or coverage changes",
    },
    {
        "decision_id": "D07", "decision": "Primary NIC port and PCI BDF", "state": "BlockedOnTestbed",
        "allowed_options": ["AnyQualifiedUniquelyResolvedPortBdf"],
        "recommended_default": known("Port with complete ancestry and required control/read-back"),
        "selection_evidence": "Topology, driver join, link, queue, counter, and timestamp qualification",
        "freeze_point": "Before topology and frontend freeze",
        "affected_components": ["inspector", "graph", "frontend", "planner", "environment"],
        "reopen_conditions": "Port, function, driver, firmware, link, or boot identity changes",
    },
    {
        "decision_id": "D08", "decision": "Huge-page sizes and allocation source", "state": "BlockedOnTestbed",
        "allowed_options": ["QualifiedFrontendPageSize", "QualifiedUmemOrdinaryPages", "Unsupported"],
        "recommended_default": known("One qualified size/source common to all baselines"),
        "selection_evidence": "Inventory, allocation, placement observability, capacity, and frontend compatibility",
        "freeze_point": "Before pool-manager integration",
        "affected_components": ["pools", "descriptors", "page-initializer", "environment"],
        "reopen_conditions": "Capacity, frontend, or page-verification change",
    },
    {
        "decision_id": "D09", "decision": "Interrupt or polling mode", "state": "PendingQualification",
        "allowed_options": ["UserspaceBusyPolling", "QualifiedInterrupt", "FrontendSpecificHybridSeparateProfile"],
        "recommended_default": known("Busy polling for DPDK; one qualified invariant mode for AF_XDP"),
        "selection_evidence": "Frontend semantics, owner visibility, wakeup, CPU cost, and invariant-path proof",
        "freeze_point": "Before frontend profile freeze",
        "affected_components": ["frontend", "ownership", "affinity", "telemetry"],
        "reopen_conditions": "Frontend cannot preserve mode or a replication profile is declared",
    },
    {
        "decision_id": "D10", "decision": "Hardware-counter availability", "state": "BlockedOnTestbed",
        "allowed_options": ["ValidatedMandatorySet", "OptionalExplanatorySet", "Unavailable"],
        "recommended_default": known("Optional unless a frozen RQ5 contrast requires the event"),
        "selection_evidence": "Event audit, scope, sign/scaling, multiplexing, and attribution probes",
        "freeze_point": "Before calibration design freeze",
        "affected_components": ["telemetry", "calibrator", "rq5", "validity-domain"],
        "reopen_conditions": "CPU, NIC, firmware, kernel, or event definition changes",
    },
    {
        "decision_id": "D11", "decision": "Exact quantile representation", "state": "Frozen",
        "allowed_options": ["RawTimestampNearestRank", "BoundedResolutionHistogramInterval"],
        "recommended_default": known("RawTimestampNearestRank"),
        "resolved_value": known(["estimator=NearestRank", "index=max(1,ceil(p*N))", "one-indexed=true", "interpolation=false", "p0=minimum", "p1=maximum", "p99.99=exploratory"]),
        "selection_evidence": "Frozen scientific contract D11",
        "freeze_point": "Before off-stand analysis implementation",
        "affected_components": ["timestamp-backend", "oracle", "aggregator", "statistics"],
        "reopen_conditions": "Prospective versioned protocol revision only",
    },
    {
        "decision_id": "D12", "decision": "Calibration estimator", "state": "Frozen",
        "allowed_options": ["SpecifiedCompleteRunNonnegativeRidgeOnly"],
        "recommended_default": known("SpecifiedCompleteRunNonnegativeRidgeOnly"),
        "resolved_value": known([
            "unit=complete-accepted-run", "response=log-nearest-rank-p99.9", "coefficients=nonnegative",
            "condition-intercepts=unpenalized-fit-only", "global-intercept=none", "lambda-grid=finite-positive",
            "folds=condition-stratified-placement-relation-blocked", "minimum-independent-relations-per-cv-condition=2",
            "validation-condition-must-occur-in-training=true", "lambda-rule=minimum-fold-size-weighted-mse-larger-lambda-exact-tie",
            "confirmatory-data-used=false",
        ]),
        "selection_evidence": "Frozen scientific contract D12",
        "freeze_point": "Before off-stand calibration implementation",
        "affected_components": ["calibration-dataset", "calibration-model", "planner", "statistics"],
        "reopen_conditions": "Prospective scientific revision before confirmatory data with new validation/version",
    },
    {
        "decision_id": "D13", "decision": "Exact-small resource budget", "state": "PendingQualification",
        "allowed_options": ["FinitePipelinesCartesianMemoryAndWallTimeLimits"],
        "recommended_default": known("Largest limits completing reliably under frozen off-stand benchmark rule"),
        "selection_evidence": "Completion time and memory on manual/captured fixtures without heuristic outputs",
        "freeze_point": "Before exact-small campaign freeze",
        "affected_components": ["exact-solver", "planner-quality-analysis", "artifacts"],
        "reopen_conditions": "Implementation platform or candidate schema changes; never infer infeasibility after budget exceedance",
    },
    {
        "decision_id": "D14", "decision": "Primary reference workload l-star", "state": "BlockedOnTestbed",
        "allowed_options": ["CellsPassingFrozenSelectionRule"],
        "recommended_default": known("Lexicographically first qualifying cell"),
        "selection_evidence": "Performance-blind feasibility, fidelity, capacity, and RSS occupancy",
        "freeze_point": "Before confirmatory campaign and unblinding",
        "affected_components": ["traffic-generator", "workload-matrix", "power", "primary-analysis"],
        "reopen_conditions": "Frozen condition infeasible before acquisition; new campaign required",
    },
    {
        "decision_id": "D15", "decision": "Smallest scientifically relevant effect", "state": "UnresolvedScientificDecision",
        "allowed_options": ["PositiveRelativeReductionFromTargetLatencyBudget"],
        "recommended_default": unknown("No numerical default is scientifically admissible"),
        "selection_evidence": "Application/service latency budget and measurement capability, not observed policy effects",
        "freeze_point": "Before pilot power calculation",
        "affected_components": ["power", "timestamp-gate", "attempt-schedule"],
        "reopen_conditions": "Target service contract changes before confirmation",
    },
    {
        "decision_id": "D16", "decision": "Warm-up and cooldown gates", "state": "BlockedOnTestbed",
        "allowed_options": ["FixedDurationsAndFrozenStabilityEnvelopes"],
        "recommended_default": known("Longest performance-blind stabilization bound plus fixed environmental cooldown"),
        "selection_evidence": "Pilot repeatability of throughput, frequency, temperature, and occupancy",
        "freeze_point": "Before confirmatory attempt schedule",
        "affected_components": ["orchestrator", "telemetry", "acceptance"],
        "reopen_conditions": "Hardware, power, or workload-domain changes",
    },
    {
        "decision_id": "D17", "decision": "Accepted page-distribution tolerance tau_mem", "state": "BlockedOnTestbed",
        "allowed_options": ["NonnegativeThresholdSupportedByQualifiedObservationMethod"],
        "recommended_default": known("Smallest threshold consistent with resolution and repeated invariant initialization"),
        "selection_evidence": "Performance-blind repeated B0/B1 initializer observations and coverage",
        "freeze_point": "Before confirmatory B0/B1 pairing",
        "affected_components": ["page-initializer", "observed-validator", "rq1-acceptance"],
        "reopen_conditions": "Page size, allocator, mechanism, kernel, or initialization protocol changes",
    },
    {
        "decision_id": "D18", "decision": "Correctness thresholds", "state": "PendingQualification",
        "allowed_options": ["ZeroLogicalFailuresPlusQualifiedMeasurementTolerances"],
        "recommended_default": known("Zero corruption ambiguity and duplicates; resolution-based measurement tolerances"),
        "selection_evidence": "Protocol semantics, fault injection, and performance-blind resolution pilots",
        "freeze_point": "Before calibration data admission then unchanged for confirmation",
        "affected_components": ["oracle", "orchestrator", "validator", "telemetry", "statistics"],
        "reopen_conditions": "Packet semantics or measurement backend changes before campaign freeze",
    },
    {
        "decision_id": "D19", "decision": "Primary cost-model validity domain", "state": "BlockedOnTestbed",
        "allowed_options": ["QualifiedCoveredSubset"],
        "recommended_default": known("Smallest domain containing l-star and planned primary B3 candidates"),
        "selection_evidence": "Coverage, no-extrapolation checks, and held-out admission metrics",
        "freeze_point": "Before B3 confirmatory planning",
        "affected_components": ["model-artifact", "planner", "rq4", "rq6"],
        "reopen_conditions": "Defining topology, frontend, workload, power, or clock leaves the domain",
    },
    {
        "decision_id": "D20", "decision": "Shared-ownership capability gate", "state": "PendingQualification",
        "allowed_options": ["DirectFiniteEntries", "ValidatedIndirectFiniteEntries", "ObservedOnlyFrozenStrata", "Unsupported"],
        "recommended_default": known("Secondary or replication only"),
        "selection_evidence": "Finite-catalog completeness, stable identities, estimator resolution, repeatability, and coverage",
        "freeze_point": "Before shared-owner calibration or replication",
        "affected_components": ["capability-profile", "ownership-catalog", "applicator", "validator", "ablations"],
        "reopen_conditions": "Capability or workload share behavior changes; never favorable latency",
    },
    {
        "decision_id": "D21", "decision": "B0/B1 initialization CPU rule", "state": "Frozen",
        "allowed_options": ["StableTopologyBlindIdentifierRule"],
        "recommended_default": known("SmallestStableOsCpuIdentifierAfterFunctionalExclusions"),
        "resolved_value": known([
            "rule=smallest-stable-os-cpu-identifier-in-initialization-cpuset-after-functional-exclusions",
            "topology-blind=true", "initializer-is-not-data-plane-role=true", "faulting-before-data-plane-affinity=true",
            "forbidden-inputs=nic-bdf,pcie-ancestry,numa-distance,page-location,cost-model,latency",
        ]),
        "selection_evidence": "Frozen scientific contract D21",
        "freeze_point": "Before off-stand orchestrator/page-initializer implementation",
        "affected_components": ["page-initializer", "b0", "b1", "run-protocol"],
        "reopen_conditions": "Only functional unusability; replacement remains topology blind and starts a new campaign",
    },
    {
        "decision_id": "D22", "decision": "Calibration design and rank admission limits", "state": "PendingQualification",
        "allowed_options": ["FrozenGridFoldsRankAndValidationLimitsFollowingSpecifiedProcedures"],
        "recommended_default": known("Procedures are fixed; numerical limits have no default"),
        "selection_evidence": "Solver precision, timing resolution, replicate noise, margins, coverage, and validity domain",
        "freeze_point": "Before held-out calibration outcomes are revealed",
        "affected_components": ["calibration-dataset", "calibrator", "model-artifact", "b3-admission"],
        "reopen_conditions": "Feature schema, relation definition, coverage, or solver changes before confirmation",
    },
    {
        "decision_id": "D23", "decision": "Conditional estimand and attrition policy", "state": "Frozen",
        "allowed_options": ["ConditionalAcceptedPairPrimaryWithMandatoryAttritionReport"],
        "recommended_default": known("No weighting or bounding unless fully frozen before unblinding"),
        "resolved_value": known([
            "primary-contrast=B3/B2", "estimand=conditional-accepted-pair-mean-log-ratio",
            "test=one-sided-paired-t-weak-conditional-mean-null", "accepted-run-pairs-are-repetitions=true",
            "packets-are-repetitions=false", "rerun=false", "neighbor-substitution=false", "failed-latency-imputation=false",
            "policy-and-pair-denominators=mandatory", "failure-categories=mandatory", "differential-attrition=mandatory-interpretation-limit",
        ]),
        "selection_evidence": "Frozen scientific contract D23",
        "freeze_point": "Before off-stand analysis schemas and fixtures",
        "affected_components": ["acceptance-records", "pair-aggregator", "orchestrator", "statistical-analysis", "planned-tables"],
        "reopen_conditions": "Prospective protocol revision before confirmatory acquisition only",
    },
]


def complete_decisions() -> list[dict[str, Any]]:
    complete: list[dict[str, Any]] = []
    for gate in DECISIONS:
        item = dict(gate)
        if "resolved_value" not in item:
            item["resolved_value"] = unknown(
                f"{item['decision_id']} is unresolved in state {item['state']}; no stand-dependent value is supplied"
            )
        item["evidence_digests"] = []
        complete.append(item)
    return complete


def make_ledger() -> dict[str, Any]:
    document = {
        "meta": metadata(
            record_id="decision:gate-ledger-v1",
            input_digests=CONTRACT_DIGESTS,
            status_kind="Success",
            status_code="Milestone1-Frozen",
            artifact_class="Protocol",
            transformation="faithful typed transcription of PRE_IMPLEMENTATION_DECISIONS.md",
        ),
        "record_type": "DecisionGateLedger",
        "payload": {
            "ledger_version": "1.0.0",
            "allowed_states": [
                "Frozen", "PendingQualification", "BlockedOnTestbed",
                "UnresolvedScientificDecision", "Unsupported", "NotApplicable",
            ],
            "gates": complete_decisions(),
            "frozen_decision_ids": ["D03", "D11", "D12", "D21", "D23"],
            "unresolved_decision_ids": [
                "D01", "D02", "D04", "D05", "D06", "D07", "D08", "D09", "D10",
                "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20", "D22",
            ],
        },
    }
    document["meta"]["canonical_digest"] = digest_document(document)
    return document


def make_campaign(ledger_digest: str) -> dict[str, Any]:
    unknown_testbed = "Unresolved until the declared qualification or physical-testbed freeze point"
    document = {
        "meta": metadata(
            record_id="campaign:template-v1",
            input_digests=CONTRACT_DIGESTS + [ledger_digest],
            status_kind="Pending",
            status_code="Template-NotExecutable",
            artifact_class="Protocol",
            transformation="versioned campaign template derived from the frozen scientific protocol",
        ),
        "record_type": "CampaignDefinition",
        "payload": {
            "campaign_template_version": "1.0.0",
            "campaign_id": unknown("Assigned only when a campaign is instantiated"),
            "stage": "Template",
            "decision_ledger_digest": ledger_digest,
            "analysis_plan": unknown("AnalysisPlan is frozen before confirmatory unblinding"),
            "frontend_profile": unknown("D01 is PendingQualification; neither DPDK nor AF_XDP is selected"),
            "topology_snapshot": unknown(unknown_testbed),
            "primary_nic_port_bdf": unknown("D07 is BlockedOnTestbed; no NIC or PCI BDF is invented"),
            "timestamp_mechanism": unknown("D04 is BlockedOnTestbed"),
            "counter_set": unknown("D10 is BlockedOnTestbed"),
            "huge_page_size": quantity_unknown("byte", "D08 is BlockedOnTestbed"),
            "tau_mem": quantity_unknown("dimensionless", "D17 is BlockedOnTestbed"),
            "cost_coefficients": unknown("U04/D12/D22 require prospective calibration; no coefficients exist"),
            "smallest_relevant_effect": quantity_unknown("ratio", "D15 is an unresolved scientific decision"),
            "warmup_duration": quantity_unknown("second", "D16 is BlockedOnTestbed"),
            "cooldown_duration": quantity_unknown("second", "D16 is BlockedOnTestbed"),
            "measurement_duration": quantity_unknown("second", "Resolved during the excluded feasibility pilot"),
            "offered_rates": [quantity_unknown("packet_per_second", "No stand-dependent offered rate is supplied")],
            "queue_counts": [quantity_unknown("count", "No stand-dependent queue count is supplied")],
            "worker_counts": [quantity_unknown("count", "No stand-dependent worker count is supplied")],
            "reference_condition": unknown("D14 is BlockedOnTestbed"),
            "randomization_seed": unknown("Generated and recorded before blocks when a campaign is instantiated"),
            "fixed_attempt_schedule": unknown("Frozen after pilot power and invalid-attempt planning"),
            "attrition_sensitivity": known("None unless formulas and positivity rules are prospectively frozen before unblinding"),
            "protocol_input_digests": CONTRACT_DIGESTS,
            "confirmatory_execution_permitted": False,
        },
    }
    document["meta"]["canonical_digest"] = digest_document(document)
    return document


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ledger = make_ledger()
    write_json(ROOT / "protocol" / "v1" / "decision-gates.json", ledger)
    campaign = make_campaign(ledger["meta"]["canonical_digest"])
    write_json(ROOT / "campaigns" / "templates" / "v1" / "campaign.json", campaign)


if __name__ == "__main__":
    main()
