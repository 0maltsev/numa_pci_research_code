#!/usr/bin/env python3
"""Generate the frozen Milestone 1 JSON-Schema set from a compact catalogue."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "v1"
SCHEMA_URI = "https://numa-pcie-research.invalid/schemas/v1/"
DRAFT = "https://json-schema.org/draft/2020-12/schema"


def ref(name: str) -> dict[str, str]:
    return {"$ref": f"common.schema.json#/$defs/{name}"}


S = ref("nonemptyString")
ID = ref("stableId")
DIGEST = ref("digest")
TS = ref("timestamp")
Q = ref("quantity")
SV = ref("statefulValue")
STATUS = ref("status")
VALIDITY = ref("validityDomain")
FINDING = ref("finding")


def array(items: dict[str, Any], *, minimum: int = 0, unique: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "array", "items": items, "minItems": minimum}
    if unique:
        result["uniqueItems"] = True
    return result


def obj(
    properties: dict[str, Any],
    required: list[str] | None = None,
    *,
    additional: bool = False,
) -> dict[str, Any]:
    return {
        "type": "object",
        "required": required if required is not None else list(properties),
        "properties": properties,
        "additionalProperties": additional,
    }


def enum(*values: str) -> dict[str, Any]:
    return {"type": "string", "enum": list(values)}


def strings(*, minimum: int = 0, unique: bool = False) -> dict[str, Any]:
    return array(S, minimum=minimum, unique=unique)


def quantities(*, minimum: int = 0) -> dict[str, Any]:
    return array(Q, minimum=minimum)


def state_vector() -> dict[str, Any]:
    return array(
        obj({"domain_id": ID, "fraction": Q}),
        minimum=1,
    )


def dro() -> dict[str, Any]:
    return obj({"desired": SV, "requested": SV, "applied": SV, "observed": SV})


COMMON = {
    "$schema": DRAFT,
    "$id": SCHEMA_URI + "common.schema.json",
    "title": "NUMA/PCIe benchmark common record definitions",
    "$defs": {
        "nonemptyString": {"type": "string", "minLength": 1, "examples": ["fixture-value"]},
        "stableId": {
            "type": "string",
            "pattern": r"[A-Za-z][A-Za-z0-9_.:/-]{2,127}",
            "examples": ["fixture:record-001"],
        },
        "digest": {
            "type": "string",
            "pattern": r"sha256:[0-9a-f]{64}",
            "examples": ["sha256:" + "0" * 64],
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "examples": ["2000-01-01T00:00:00Z"],
        },
        "unit": {
            "type": "string",
            "enum": [
                "dimensionless",
                "count",
                "byte",
                "bit",
                "page",
                "slot",
                "packet",
                "event",
                "transaction",
                "packet_per_second",
                "bit_per_second",
                "byte_per_second",
                "second",
                "millisecond",
                "microsecond",
                "nanosecond",
                "tick",
                "cycle",
                "hertz",
                "degree_celsius",
                "ratio",
                "percent",
                "pu_second_per_second",
                "index",
            ],
        },
        "decimalString": {
            "type": "string",
            "pattern": r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?",
            "examples": ["0"],
        },
        "quantityKnown": obj(
            {
                "state": {"const": "Known"},
                "value": {"$ref": "#/$defs/decimalString"},
                "unit": {"$ref": "#/$defs/unit"},
            }
        ),
        "quantityUnavailable": obj(
            {
                "state": enum("Unknown", "Missing", "Unsupported", "NotApplicable"),
                "unit": {"$ref": "#/$defs/unit"},
                "reason": {"$ref": "#/$defs/nonemptyString"},
            }
        ),
        "quantity": {
            "oneOf": [
                {"$ref": "#/$defs/quantityKnown"},
                {"$ref": "#/$defs/quantityUnavailable"},
            ]
        },
        "statefulKnown": obj(
            {
                "state": {"const": "Known"},
                "value": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "boolean"},
                        {"type": "array", "items": {"type": "string"}},
                    ]
                },
            }
        ),
        "statefulUnavailable": obj(
            {
                "state": enum("Unknown", "Missing", "Unsupported", "NotApplicable"),
                "reason": {"$ref": "#/$defs/nonemptyString"},
            }
        ),
        "statefulValue": {
            "oneOf": [
                {"$ref": "#/$defs/statefulKnown"},
                {"$ref": "#/$defs/statefulUnavailable"},
            ]
        },
        "producer": obj(
            {"identity": {"$ref": "#/$defs/stableId"}, "version": {"$ref": "#/$defs/nonemptyString"}}
        ),
        "creationTime": obj(
            {"value": {"$ref": "#/$defs/timestamp"}, "clock_domain": {"$ref": "#/$defs/nonemptyString"}}
        ),
        "status": obj(
            {
                "kind": enum("Success", "Pending", "Failure", "Blocked", "Excluded"),
                "code": {"$ref": "#/$defs/nonemptyString"},
                "detail": {"$ref": "#/$defs/nonemptyString"},
            }
        ),
        "errorRecord": obj(
            {
                "error_id": {"$ref": "#/$defs/stableId"},
                "component": {"$ref": "#/$defs/nonemptyString"},
                "stage": {"$ref": "#/$defs/nonemptyString"},
                "code": {"$ref": "#/$defs/nonemptyString"},
                "severity": enum("Info", "Warning", "Error", "Fatal"),
                "affected_facts": array({"$ref": "#/$defs/stableId"}),
                "message": {"$ref": "#/$defs/nonemptyString"},
                "recovery_status": enum("NotRequired", "Pending", "Succeeded", "Failed", "Impossible"),
                "rollback_status": enum("NotApplicable", "NotStarted", "Succeeded", "Failed"),
                "scientific_disposition": enum("Eligible", "ScientificallyExcluded", "DiagnosticOnly"),
            }
        ),
        "validityDomain": obj(
            {
                "state": enum("Known", "Unknown", "Missing", "Unsupported", "NotApplicable"),
                "definition": {"$ref": "#/$defs/nonemptyString"},
                "evidence_digests": array({"$ref": "#/$defs/digest"}),
            }
        ),
        "provenance": obj(
            {
                "source_record_ids": array({"$ref": "#/$defs/stableId"}, unique=True),
                "source_digests": array({"$ref": "#/$defs/digest"}, unique=True),
                "transformation": {"$ref": "#/$defs/nonemptyString"},
                "raw_records_immutable": {"type": "boolean"},
            }
        ),
        "recordMetadata": obj(
            {
                "schema_version": {"const": "1.0.0"},
                "record_id": {"$ref": "#/$defs/stableId"},
                "producer": {"$ref": "#/$defs/producer"},
                "created_at": {"$ref": "#/$defs/creationTime"},
                "campaign_or_stage_id": {"$ref": "#/$defs/stableId"},
                "input_digests": array({"$ref": "#/$defs/digest"}, unique=True),
                "canonical_digest": {"$ref": "#/$defs/digest"},
                "status": {"$ref": "#/$defs/status"},
                "errors": array({"$ref": "#/$defs/errorRecord"}),
                "artifact_class": enum("Raw", "Derived", "Configuration", "Protocol", "TestFixture"),
                "data_classification": enum(
                    "Measurement",
                    "NON_MEASUREMENT_TEST_FIXTURE",
                    "ProtocolDefinition",
                    "ConfigurationEvidence",
                ),
                "scientific_disposition": enum("Eligible", "ScientificallyExcluded", "DiagnosticOnly", "NotMeasurement"),
                "validity_domain": {"$ref": "#/$defs/validityDomain"},
                "provenance": {"$ref": "#/$defs/provenance"},
            }
        ),
        "finding": obj(
            {
                "finding_id": {"$ref": "#/$defs/stableId"},
                "code": {"$ref": "#/$defs/nonemptyString"},
                "severity": enum("Info", "Warning", "Error", "Fatal"),
                "subject_ids": array({"$ref": "#/$defs/stableId"}),
                "detail": {"$ref": "#/$defs/nonemptyString"},
            }
        ),
        "quantityVectorEntry": obj(
            {"domain_id": {"$ref": "#/$defs/stableId"}, "quantity": {"$ref": "#/$defs/quantity"}}
        ),
    },
}


def record_schema(title: str, description: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "$schema": DRAFT,
        "$id": SCHEMA_URI + file_name(title),
        "title": title,
        "description": description,
        "type": "object",
        "required": ["meta", "record_type", "payload"],
        "properties": {
            "meta": ref("recordMetadata"),
            "record_type": {"const": title},
            "payload": payload,
        },
        "additionalProperties": False,
    }


attribute = obj(
    {
        "attribute_id": ID,
        "name": S,
        "value": SV,
        "quantity": Q,
        "provenance_class": enum("Discovered", "Derived", "Calibrated", "Unknown"),
        "source_digest": DIGEST,
        "observed_at": TS,
        "confidence": Q,
    },
    required=["attribute_id", "name", "value", "quantity", "provenance_class", "source_digest", "observed_at", "confidence"],
)

vertex = obj(
    {
        "vertex_id": ID,
        "vertex_type": S,
        "attributes": array(attribute),
    }
)

edge = obj(
    {
        "edge_id": ID,
        "edge_type": S,
        "from_vertex_id": ID,
        "to_vertex_id": ID,
        "directional": {"type": "boolean"},
        "attributes": array(attribute),
    }
)

share = obj({"owner_id": ID, "share": Q})

location_object = obj(
    {
        "object_id": ID,
        "role": enum("rx_payload", "tx_payload", "rx_descriptor", "tx_descriptor", "event_ring", "state"),
        "materiality": enum("Material", "Null"),
        "capacity_bytes": Q,
        "used_bytes": Q,
        "capacity_slots": Q,
        "page_size": Q,
        "backing_source": SV,
        "desired_distribution": state_vector(),
        "requested_policy": SV,
        "allowed_node_ids": strings(),
        "allocation_actor_id": SV,
        "fault_actor_id": SV,
        "accessor_shares": array(share),
        "observed_distribution": state_vector(),
        "observation_coverage": Q,
        "observation_status": S,
    }
)

response_category = obj(
    {
        "expected_sequence_id": ID,
        "candidate_response_ids": strings(),
        "format_results": strings(),
        "payload_results": strings(),
        "binding_results": strings(),
        "timestamp_results": strings(),
        "final_category": enum("valid", "missing", "corrupt", "duplicate", "ambiguous"),
        "out_of_range": {"type": "boolean"},
    }
)

cost_term = obj(
    {
        "term_id": ID,
        "pipeline_id": ID,
        "physical_mechanism": S,
        "owner_group": S,
        "initiator_id": ID,
        "target_id": ID,
        "transaction_class": S,
        "raw_value": Q,
        "base_reference": Q,
        "transform": S,
        "scale": Q,
        "normalized_value": Q,
        "component_weight": Q,
        "group_coefficient": Q,
        "term_class": enum("Base", "Surcharge"),
        "load_attribution": Q,
        "uncertainty": Q,
    }
)


RECORDS: dict[str, tuple[list[str], str, dict[str, Any]]] = {
    "RawTopologyObservation": (["C01"], "Raw, inference-free topology fact capture.", obj({
        "collection_epoch_id": ID, "host_identity": SV, "boot_identity": SV,
        "source_uri": S, "source_class": S, "raw_capture_digest": DIGEST,
        "raw_value": SV, "raw_quantity": Q, "provenance_class": {"const": "Discovered"},
        "collection_start": TS, "collection_end": TS,
        "access_result": enum("Success", "Source-Inaccessible", "Host-Changed", "Device-Disappeared", "Partial-Collection"),
        "warnings": strings(),
    })),
    "TopologySnapshot": (["C02"], "Validated typed topology graph with explicit unknown inventory.", obj({
        "snapshot_id": ID, "host_id": ID, "boot_id": ID,
        "vertices": array(vertex, minimum=1), "edges": array(edge),
        "unknown_inventory": array(obj({"fact_id": ID, "state": enum("Unknown", "Missing", "Unsupported", "NotApplicable"), "reason": S})),
        "validation_findings": array(FINDING), "source_digests": array(DIGEST, minimum=1, unique=True),
    })),
    "FrontendCapabilityProfile": (["C03"], "Qualified frontend control and read-back capability surface.", obj({
        "frontend_identity": SV, "driver_identity": SV, "kernel_identity": SV, "nic_identity": SV,
        "control_surfaces": array(obj({
            "surface_id": ID, "control_class": enum("Direct", "ValidatedIndirect", "ObservedOnly", "Unsupported"),
            "request_method": SV, "readback_method": SV, "coverage": Q,
            "required_privileges": strings(), "qualification_evidence_digests": array(DIGEST),
        }), minimum=1),
        "profile_validity_domain": VALIDITY,
    })),
    "OwnershipCatalog": (["C04"], "Frozen finite ownership entries; no continuous-share domain.", obj({
        "catalog_id": ID, "catalog_version": S, "freeze_time": TS, "pipeline_id": ID,
        "direction": enum("rx", "tx", "not_applicable"), "cardinality": Q,
        "entries": array(obj({
            "entry_index": ID, "owner_role_ids": strings(), "planning_shares": array(share),
            "control_class": enum("Direct", "ValidatedIndirect", "ObservedOnly", "Unsupported"),
            "requested_action": SV, "observed_share_range": quantities(), "observation_coverage_gate": Q,
            "capability_evidence_digest": DIGEST, "primary_eligibility": {"type": "boolean"},
        }), minimum=1),
        "stable_order_rule": S,
    })),
    "SerializedGraph": (["C05"], "Portable deterministic graph serialization artifact.", obj({
        "snapshot_digest": DIGEST, "encoding": {"const": "canonical-json-v1"},
        "canonical_order_declaration": S, "source_digest_list": array(DIGEST, minimum=1),
        "graph_document_digest": DIGEST, "roundtrip_status": enum("Verified", "Roundtrip-Mismatch", "Noncanonical-Order", "Digest-Mismatch"),
    })),
    "CalibrationDataset": (["C06"], "Complete-run calibration rows and fold-admissibility evidence.", obj({
        "rows": array(obj({
            "run_id": ID, "condition_id": ID, "placement_relation_id": ID,
            "response_log_p999": Q, "latency_unit_before_log": enum("nanosecond", "microsecond", "second"),
            "valid_observation_count": Q,
            "features": array(obj({"feature_id": ID, "group": S, "normalized_value": Q, "transform": S}), minimum=1),
            "split": enum("Training", "ExternalValidationSeen", "ExternalValidationUnseen"),
            "fold_id": SV, "acceptance_record_digest": DIGEST,
        }), minimum=1),
        "condition_relation_coverage_map": array(obj({"condition_id": ID, "placement_relation_ids": strings(minimum=1, unique=True), "independent_relation_count": Q}), minimum=1),
        "candidate_folds": array(obj({"fold_id": ID, "validation_run_ids": strings(), "training_run_ids": strings(), "relation_blocks_intact": {"type": "boolean"}, "training_condition_coverage": {"type": "boolean"}, "admissible": {"type": "boolean"}, "findings": strings()}), minimum=1),
        "feature_order": strings(minimum=1, unique=True), "confirmatory_ids_excluded": {"const": True},
    })),
    "CalibrationModelArtifact": (["C07"], "Frozen nonnegative-ridge model and seen/unseen validation audit.", obj({
        "estimator": {"const": "CompleteRunNonnegativeRidge"},
        "objective": {"const": "(1/n_tr)*sum_r(y_r-delta_condition(r)-x_r^T*theta)^2+lambda*||theta||_2^2"},
        "n_tr": Q, "condition_intercepts_unpenalized": {"const": True}, "global_intercept": {"const": False},
        "coefficient_constraint": {"const": "Nonnegative"}, "lambda_grid": quantities(minimum=1),
        "lambda_selection_rule": {"const": "MinimumFoldSizeWeightedAdmissibleCvMseThenLargerLambdaOnExactTie"},
        "selected_lambda": Q, "fold_losses": array(obj({"fold_id": ID, "lambda": Q, "mse_log_latency": Q, "fold_size": Q, "admissible": {"type": "boolean"}}), minimum=1),
        "coverage_audit_digest": DIGEST, "effective_coefficients": array(obj({"feature_id": ID, "coefficient": Q, "status": enum("Enabled", "Merged", "Disabled", "Disabled-Zero-Scale")}), minimum=1),
        "merge_disable_ledger": array(obj({"feature_id": ID, "action": S, "reason": S})),
        "factorization": obj({"s_top": Q, "alpha": array(obj({"group": S, "feature_id": ID, "value": Q})), "beta": array(obj({"group": S, "value": Q})), "beta_top": Q, "identity_verified": {"type": "boolean"}}),
        "seen_condition_validation": array(obj({"condition_id": ID, "log_mse": Q, "residual_summary": quantities(), "spearman_rank": Q, "top_choice_accuracy": Q, "regret": Q})),
        "unseen_condition_validation": array(obj({"condition_id": ID, "absolute_mse_state": {"const": "NotApplicable"}, "spearman_rank": Q, "top_choice_accuracy": Q, "regret": Q, "independent_relation_count": Q})),
        "admission_status": enum("Admitted", "Condition-Coverage-Insufficient", "Calibration-Failed", "Rank-Deficient", "Topology-Scale-Zero", "Validation-Failed", "Out-Of-Domain"),
        "model_validity_domain": VALIDITY,
    })),
    "PlacementPlan": (["C08"], "Declarative feasible placement; it performs no host mutation.", obj({
        "planner_status": {"const": "Feasible"}, "fidelity": enum("Full", "NUMA", "CPU", "Default"),
        "snapshot_digest": DIGEST, "capability_digest": DIGEST, "catalog_digests": array(DIGEST, minimum=1),
        "workload_digest": DIGEST, "model_digest": DIGEST, "reference_mapping_digest": DIGEST,
        "assignments": array(obj({"pipeline_id": ID, "queue_binding_id": ID, "worker_role_id": ID, "rx_catalog_index": ID, "tx_catalog_index": ID, "role_context_ids": strings(), "context_pu_ids": strings(), "memory_object_ids": strings()}), minimum=1),
        "desired_distributions": array(obj({"object_id": ID, "distribution": state_vector()})),
        "constraint_proofs": array(obj({"constraint_id": ID, "pass": {"const": True}, "evidence_digest": DIGEST}), minimum=1),
        "cost_terms": array(cost_term), "total_score": Q, "tie_key": strings(minimum=1),
        "ordered_actions": strings(), "validation_predicates": strings(minimum=1),
    })),
    "CandidateSearchAudit": (["C08"], "Finite-domain exposure and bounded heuristic search audit.", obj({
        "terminal_status": enum("Feasible", "Search-Limited", "Cap-Limited", "Data-Incomplete", "Model-Out-Of-Domain", "Stale-Input"),
        "queue_audits": array(obj({
            "queue_id": ID, "endpoint_identity": ID, "raw_candidate_count": Q, "unpruned_candidate_count": Q,
            "exposed_candidate_count": Q, "domain_exhausted": {"type": "boolean"}, "cap": Q,
            "cap_expansions": quantities(), "dominance_certificate_digests": array(DIGEST),
        }), minimum=1),
        "search_node_budget": Q, "search_nodes_consumed": Q, "depth_budget": Q, "maximum_depth": Q,
        "conflict_witnesses": array(FINDING), "neighborhood_counts": quantities(), "tie_break_trace": strings(),
        "elapsed_time": Q, "peak_memory": Q, "external_exact_reference_digest": SV,
    })),
    "ExactReferenceResult": (["C09"], "Independent full-product exact-small result and exhaustion semantics.", obj({
        "terminal_status": enum("Exact-Feasible", "Proven-Infeasible", "Exact-Budget-Exceeded", "Exact-Execution-Error"),
        "raw_catalog_digests": array(DIGEST, minimum=1), "heuristic_input_used": {"const": False},
        "resource_limits": obj({"maximum_pipelines": Q, "maximum_cartesian_size": Q, "peak_memory_budget": Q, "wall_time_budget": Q}),
        "preflight_estimates": quantities(), "cartesian_size": Q, "visited_count": Q, "feasible_count": Q,
        "rejection_counts": array(obj({"constraint_class": S, "count": Q})),
        "best_placement_digest": SV, "best_value": Q, "tie_trace": strings(),
        "elapsed_time": Q, "peak_memory": Q, "enumerators_exhausted": {"type": "boolean"}, "exhaustion_certificate_digest": SV,
    })),
    "AppliedPlacement": (["C10"], "Requested placement actions with prior-state and rollback evidence.", obj({
        "plan_digest": DIGEST, "authorization": enum("DryRun", "ApplyAuthorized"),
        "placement_state": dro(),
        "actions": array(obj({"action_id": ID, "dependency_ids": strings(), "desired": SV, "requested": SV, "no_action_reason": SV, "status": S, "started_at": TS, "ended_at": TS}), minimum=1),
        "prior_state_journal": array(obj({"journal_entry_id": ID, "target_id": ID, "prior_value": SV, "captured_digest": DIGEST}), minimum=1),
        "rollback_plan": strings(minimum=1), "rollback_result": enum("NotRequired", "Succeeded", "Failed"),
        "post_rollback_readback_digest": SV, "dirty_host": {"type": "boolean"},
    })),
    "PageInitializationRecord": (["C11"], "Immutable per-attempt fresh allocation/fault/page observation.", obj({
        "attempt_id": ID, "policy": enum("B0", "B1", "B2", "B3"), "fresh_process_id": ID,
        "fresh_allocation_id": ID, "initialization_context_id": ID, "initialization_cpu": SV,
        "initializer_rule": S, "topology_blind": {"type": "boolean"}, "data_plane_affinity_applied_after_fault": {"type": "boolean"},
        "objects": array(location_object, minimum=1), "allocation_order": strings(minimum=1), "fault_pattern": S,
        "fault_coverage": Q, "start_time": TS, "end_time": TS, "observation_integrity_status": S,
        "pair_distance_present": {"const": False},
    })),
    "ObservedPlacement": (["C12"], "Independent desired/requested/applied/observed placement validation.", obj({
        "attempt_id": ID, "plan_digest": DIGEST, "applied_placement_digest": DIGEST,
        "role_context_cpu_observations": array(obj({"role_id": ID, "context_id": ID, "thread_id": ID, "requested_cpu_mask": SV, "effective_cpu_mask": SV, "observed_cpu_ids": strings(), "coverage": Q}), minimum=1),
        "page_observations": array(location_object, minimum=1),
        "ownership_observations": array(obj({"queue_id": ID, "catalog_entry_index": ID, "control_class": S, "desired_share": Q, "requested_action": SV, "applied_claim": SV, "observed_shares": array(share), "coverage": Q, "acceptance_range_result": enum("Pass", "Fail", "Unsupported")}), minimum=1),
        "placement_deltas": array(obj({"subject_id": ID, "state": dro(), "match_status": S})),
        "validation_status": enum("Pass", "Placement-Mismatch", "Share-Out-Of-Range", "Observation-Incomplete"),
    })),
    "PageEquivalenceRecord": (["C12", "C23"], "Immutable pending or order-independent final B0/B1 page-equivalence record.", obj({
        "prospective_pair_key": ID, "state": enum("Pair-Pending", "Pair-Equivalent", "Page-Equivalence-Failed", "Page-Equivalence-Unsupported"),
        "b0_page_record_digest": SV, "b1_page_record_digest": SV,
        "input_record_digests_sorted": array(DIGEST, minimum=1, unique=True),
        "mandatory_object_join": array(obj({"object_id": ID, "b0_vector": state_vector(), "b1_vector": state_vector(), "coverage_compatible": {"type": "boolean"}, "d_tv": Q, "status": S})),
        "tau_mem": Q, "tau_mem_pilot_digest": SV, "maximum_d_tv": Q,
        "latency_input_used": {"const": False}, "superseded_pending_record_ids": strings(),
    })),
    "FrontendRunRecord": (["C13"], "Invariant frontend path self-description and queue evidence.", obj({
        "run_id": ID, "profile_digest": DIGEST, "port_identity": SV, "pci_bdf": SV,
        "queue_handles": array(obj({"direction": enum("rx", "tx"), "queue_id": ID, "hardware_index": SV, "owner_ids": strings(), "catalog_entry_index": ID}), minimum=1),
        "mode": SV, "offloads": strings(), "descriptor_count": Q, "packet_events_digest": DIGEST,
        "per_queue_counters": array(obj({"queue_id": ID, "counter_id": ID, "value": Q, "width": Q})),
        "hidden_fallback_detected": {"type": "boolean"}, "self_description_digest": DIGEST,
    })),
    "MemoryObjectRecord": (["C14"], "Typed material or null memory-object lifecycle record.", obj({
        "attempt_id": ID, "object": location_object, "address_span_reference": SV,
        "usable_bytes": Q, "reserved_bytes": Q, "element_size": Q, "element_count": Q,
        "lifecycle": enum("Declared", "Allocated", "Faulted", "InUse", "Destroyed", "Null"),
        "fresh_allocation_proof_digest": SV, "teardown_proof_digest": SV,
    })),
    "RingRecord": (["C15"], "Event-ring progress, lapping, and explicit no-handoff record.", obj({
        "run_id": ID, "ring_id": ID, "null_marker": {"type": "boolean"}, "capacity_slots": Q, "capacity_bytes": Q,
        "producer_ids": strings(), "consumer_ids": strings(), "producer_extended_sequence": Q, "consumer_extended_sequence": Q,
        "occupancy": Q, "high_water": Q, "generation": Q, "handoff_event_digest": SV,
        "lapping_detected": {"type": "boolean"}, "drain_equal": {"type": "boolean"},
    })),
    "WorkerRecord": (["C16"], "Invariant worker service and execution-context evidence.", obj({
        "run_id": ID, "request_sequence_id": ID, "response_sequence_id": ID, "worker_role_id": ID,
        "physical_context_id": ID, "thread_id": ID, "operation_result": S, "progress": Q,
        "cycles": Q, "elapsed_time": Q, "cpu_samples": strings(), "integrity_status": S,
    })),
    "TrafficGenerationRecord": (["C17"], "Committed trace execution and generator-fidelity record.", obj({
        "run_id": ID, "workload_digest": DIGEST, "sequence_manifest_digest": DIGEST, "expected_set_committed_before_send": {"const": True},
        "intended_packet_rate": Q, "actual_packet_rate": Q, "intended_bit_rate": Q, "actual_bit_rate": Q,
        "trace_digest": DIGEST, "flow_digest": DIGEST, "send_events_digest": DIGEST,
        "link_counters": array(obj({"counter_id": ID, "value": Q})), "generator_utilization": Q,
        "latency_adaptive_rate": {"const": False},
    })),
    "TimestampRecord": (["C18"], "Raw timestamp evidence with clock, wrap, and qualification links.", obj({
        "event_id": ID, "run_id": ID, "sequence_id": ID, "raw_ticks": Q, "extended_ticks": Q,
        "clock_id": ID, "epoch_id": ID, "direction": enum("request_tx", "response_rx", "diagnostic"),
        "capture_layer": S, "tick_frequency": Q, "wrap_width": Q, "conversion_rule": S,
        "converted_time": Q, "validity": enum("Valid", "Clock-Step", "Wrap-Ambiguous", "Timestamp-Ambiguous", "Loss-Gate-Failed", "Qualification-Out-Of-Domain"),
        "qualification_digest": DIGEST, "overhead_digest": DIGEST,
    })),
    "SequenceManifest": (["C19"], "Receive-independent exact expected sequence-set commitment.", obj({
        "block_id": ID, "run_id": ID, "encoding": enum("ExplicitSet", "DeterministicRule"),
        "exact_sequence_ids": strings(minimum=1, unique=True), "generator_rule": SV, "expected_count": Q,
        "transmit_order": strings(minimum=1), "request_flow_bindings": array(obj({"sequence_id": ID, "request_id": ID, "flow_id": ID}), minimum=1),
        "packet_schema_digest": DIGEST, "trace_digest": DIGEST, "commitment_time": TS,
        "receive_state_input_used": {"const": False},
    })),
    "OracleReport": (["C20"], "Exhaustive expectation/response correctness classification.", obj({
        "run_id": ID, "sequence_manifest_digest": DIGEST, "response_categories": array(response_category, minimum=1),
        "valid_sequence_ids": strings(), "missing_count": Q, "corrupt_count": Q, "duplicate_count": Q,
        "ambiguous_count": Q, "out_of_range_count": Q, "reordered_count": Q, "raw_receive_count": Q,
        "latency_eligible_count": Q, "drain_status": S, "accounting_reconciled": {"type": "boolean"},
    })),
    "RunRecord": (["C21"], "Scheduled policy-attempt lifecycle and immutable acceptance index.", obj({
        "block_id": ID, "run_id": ID, "attempt_id": ID, "policy": enum("B0", "B1", "B2", "B3"),
        "randomization_seed_digest": DIGEST, "scheduled_order_index": Q, "phase_record_ids": strings(minimum=1),
        "input_record_digests": array(DIGEST, minimum=1), "A_bj": {"type": "boolean"},
        "prospective_pair_keys": strings(), "pair_status": enum("NotApplicable", "Pair-Pending", "Finalized"),
        "acceptance_record_digest": DIGEST, "attempt_status": S, "exclusion_status": S,
        "cleanup_status": enum("Verified", "Rollback-Incomplete", "Host-Dirty"), "dirty_host": {"type": "boolean"},
        "operator_intervention": {"type": "boolean"},
    })),
    "PhaseRecord": (["C21"], "Planned/actual lifecycle boundary and performance-blind gate record.", obj({
        "run_id": ID, "phase_name": enum("Reset", "Allocate", "Fault", "ObservePages", "ApplyPlacement", "ReadBack", "WarmUp", "Measure", "Drain", "PostValidate", "Cooldown", "Teardown", "Rollback"),
        "planned_start": TS, "planned_end": TS, "actual_start": TS, "actual_end": TS,
        "stability_inputs": array(obj({"metric_id": ID, "value": Q})), "gate_result": enum("Pass", "Fail", "NotApplicable"), "reason": S,
        "latency_summary_input_used": {"const": False},
    })),
    "TelemetryRecord": (["C22"], "Scoped raw/extended counter sample and quality evidence.", obj({
        "run_id": ID, "phase_record_id": ID, "event_id": ID, "event_encoding": S, "scope_id": ID,
        "raw_value": Q, "extended_value": Q, "sample_time": Q, "enabled_time": Q, "running_time": Q,
        "counter_width": Q, "wrap_status": S, "reset_status": S, "multiplexing_ratio": Q,
        "quality": enum("Valid", "Event-Unavailable", "Wrap-Ambiguous", "Multiplexing-Gate-Failed", "Attribution-Mismatch", "Interval-Missing"),
    })),
    "AggregatedDataset": (["C23"], "Run-level nearest-rank, pair, and attrition dataset with immutable provenance.", obj({
        "analysis_plan_digest": DIGEST, "scheduled_attempt_ids": strings(minimum=1, unique=True),
        "runs": array(obj({
            "run_id": ID, "block_id": ID, "policy": enum("B0", "B1", "B2", "B3"), "A_bj": {"type": "boolean"},
            "valid_observation_count": Q, "quantiles": obj({"p50": Q, "p90": Q, "p99": Q, "p999": Q, "p9999_exploratory": Q, "maximum": Q}),
            "nearest_rank_indices": obj({"p50": Q, "p90": Q, "p99": Q, "p999": Q, "p9999_exploratory": Q}),
            "correctness_digest": DIGEST, "scientifically_excluded": {"type": "boolean"}, "source_record_digests": array(DIGEST, minimum=1),
        }), minimum=1),
        "page_equivalence_records": array(obj({"pair_key": ID, "record_digest": DIGEST, "E_mem_j": {"type": "boolean"}, "state": S})),
        "adjacent_pair_indicators": array(obj({"block_id": ID, "A_1_0": {"type": "boolean"}, "A_2_1": {"type": "boolean"}, "A_3_2": {"type": "boolean"}, "pair_record_ids": strings()}), minimum=1),
        "attrition": array(obj({"policy_or_pair": S, "planned_count": Q, "attempted_count": Q, "accepted_count": Q, "failure_category": S, "failure_count": Q, "failure_rate": Q, "incomplete_block_policy": SV}), minimum=1),
        "packet_as_repetition": {"const": False}, "quantile_rule": {"const": "NearestRankNoInterpolation"},
    })),
    "StatisticalAnalysisArtifact": (["C24"], "Frozen conditional accepted-pair inference and mandatory attrition report.", obj({
        "analysis_plan_digest": DIGEST, "decision_ledger_digest": DIGEST,
        "primary": obj({
            "estimand_label": {"const": "ConditionalAcceptedPairMeanLogRatio_B3_over_B2"}, "reference_condition_id": ID,
            "accepted_pair_ids": strings(), "D_j": quantities(), "mean_D": Q, "standard_error": Q,
            "t_statistic": Q, "one_sided_p_value": Q, "upper_one_sided_95_bound": Q,
            "two_sided_95_lower": Q, "two_sided_95_upper": Q, "transformed_relative_effect": Q,
            "planned_pair_count": Q, "accepted_pair_count": Q, "decision": S,
        }),
        "key_secondary": obj({
            "rq1_b1_b0": obj({"accepted_pair_ids": strings(), "mean_log_ratio": Q, "absolute_difference": Q, "raw_p_value": Q, "holm_adjusted_p_value": Q}),
            "rq2_b2_b1": obj({"accepted_pair_ids": strings(), "mean_log_ratio": Q, "absolute_difference": Q, "raw_p_value": Q, "holm_adjusted_p_value": Q}),
        }),
        "secondary_analyses": obj({
            "rq4_interactions": array(obj({"factor": enum("packet_size", "offered_load", "burst_shape", "flow_skew", "queue_count", "worker_count"), "incremental_contrast": enum("B1/B0", "B2/B1", "B3/B2"), "estimate": Q, "interval_lower": Q, "interval_upper": Q, "analysis_family": S})),
            "rq5_model_explanation": array(obj({"term_or_group_id": ID, "ablation_plan_digest": DIGEST, "placement_changed": {"type": "boolean"}, "p999_effect": Q, "goodput_effect": Q, "counter_association": Q, "held_out_rank": Q, "family_label": S})),
            "rq6_stability": array(obj({"change_id": ID, "change_class": enum("Workload", "Topology", "FrontendReplication"), "policy_rank_correlation": Q, "candidate_cost_rank_correlation": Q, "top_choice_accuracy": Q, "regret": Q, "validity_domain_result": S})),
        }),
        "operational_feasibility": obj({"planned_blocks": Q, "attempted_blocks": Q, "policy_counts": quantities(minimum=1), "adjacent_pair_counts": quantities(minimum=1), "categorized_attrition_digest": DIGEST}),
        "diagnostics": array(obj({"diagnostic_id": ID, "value": Q, "threshold": Q, "result": S})),
        "assumption_sensitive": {"type": "boolean"}, "sharp_null_sensitivity_labeled_secondary": {"const": True},
        "failed_latency_imputed": {"const": False}, "packets_as_repetitions": {"const": False},
        "table_figure_data_digests": array(DIGEST),
    })),
}


ADDITIONAL: dict[str, tuple[list[str], str, dict[str, Any]]] = {
    "EnvironmentManifest": (["C01", "C02", "C21"], "Machine-readable host/build/environment protocol evidence.", obj({
        "host_role": enum("TG", "SUT", "Diagnostic"), "host_identity": SV, "boot_identity": SV,
        "hardware_inventory": SV, "firmware_inventory": SV, "kernel_identity": SV, "driver_identity": SV,
        "frontend_identity": SV, "build_identity": SV, "power_isolation_settings": SV, "clock_description": SV,
        "topology_snapshot_digest": SV, "raw_source_digests": array(DIGEST), "missing_fields": strings(),
    })),
    "FrontendProfile": (["C03", "C13"], "Frozen frontend/pipeline profile without choosing DPDK or AF_XDP prematurely.", obj({
        "profile_type": enum("PendingQualification", "DPDK", "AF_XDP", "Unsupported"), "profile_version": S,
        "driver_mode": SV, "fixed_queue_pair_ids": strings(), "resource_controls": array(obj({"resource_role": S, "control": SV})),
        "logical_role_ids": strings(), "physical_context_ids": strings(), "pipeline_mode": SV,
        "ownership_catalog_digests": array(DIGEST), "capability_digest": SV, "required_privileges": strings(), "verification_predicates": strings(),
    })),
    "ReferenceMapping": (["C04", "C08", "C13"], "Topology-blind B0-B2 logical mapping and catalog indices.", obj({
        "construction_rule": S, "topology_inputs_used": {"const": False}, "queue_worker_map": array(obj({"queue_id": ID, "worker_role_id": ID}), minimum=1),
        "direction_catalog_indices": array(obj({"queue_id": ID, "direction": enum("rx", "tx"), "entry_index": ID}), minimum=1),
        "inventory_digests": array(DIGEST, minimum=1),
    })),
    "CPUAccessProfile": (["C08", "C11", "C14"], "Frozen per-object actual CPU-access demand shares for B2.", obj({
        "objects": array(obj({"object_role": S, "material": {"type": "boolean"}, "accessors": array(obj({"physical_context_id": ID, "demand_share": Q}), minimum=1), "dominant_accessor_id": ID, "split_access": {"type": "boolean"}, "derivation_digest": DIGEST}), minimum=1),
        "frozen_before_baseline_execution": {"const": True},
    })),
    "WorkloadSpec": (["C06", "C08", "C17", "C19"], "Versioned workload and exact expected-set contract.", obj({
        "packet_bytes": Q, "on_wire_bytes": Q, "flow_keys": strings(), "flow_distribution": SV,
        "offered_rate_rule": S, "resolved_packet_rate": Q, "trace_digest": SV, "burst_model": SV,
        "queue_count": Q, "worker_count": Q, "io_role_count": Q, "physical_context_count": Q,
        "pipeline_mode": SV, "service_operation": S, "sequence_manifest_digest": SV,
        "warmup_duration": Q, "measurement_duration": Q, "expected_request_count": Q, "drain_deadline": Q, "cooldown_duration": Q,
    })),
    "ClockQualification": (["C18"], "Timestamp decision-tree qualification and error bounds.", obj({
        "selected_branch": enum("PendingQualification", "ExternalSingleClock", "SameTgNicHardwareClock", "BoundedTgSoftwareDiagnostic", "Unsupported"),
        "rejected_branches": strings(), "clock_ids": strings(), "capture_boundary": SV, "resolution": Q,
        "wrap_rule": SV, "matching_capacity": Q, "rate_dependent_bias": Q, "timestamp_loss": Q,
        "error_bound": Q, "overhead_bound": Q, "qualification_validity_domain": VALIDITY,
    })),
    "AcceptanceRecord": (["C12", "C20", "C21", "C23"], "Performance-blind immutable attempt acceptance and contrast admission.", obj({
        "block_id": ID, "attempt_id": ID, "policy": enum("B0", "B1", "B2", "B3"),
        "gates": array(obj({"gate_id": ID, "category": S, "result": enum("Pass", "Fail", "Unsupported", "NotApplicable"), "evidence_digest": DIGEST}), minimum=1),
        "A_bj": {"type": "boolean"}, "primary_failure_category": SV, "all_failed_gate_ids": strings(),
        "prospective_pair_keys": strings(), "contrast_admission": array(obj({"contrast": enum("B1/B0", "B2/B1", "B3/B2"), "status": enum("Pair-Pending", "Admitted", "Excluded"), "indicator_record_digest": SV})),
        "decision_before_latency_summary": {"const": True},
    })),
    "AnalysisPlan": (["C23", "C24"], "Frozen confirmatory and secondary analysis protocol.", obj({
        "reference_condition": SV, "reference_condition_selection_rule": S,
        "attempt_indicator_definition": {"const": "A_bj_is_one_only_after_all_applicable_performance_blind_attempt_gates_pass"},
        "pair_indicator_definitions": obj({"A_1_0": {"const": "A_B1j*A_B0j*E_mem_j"}, "A_2_1": {"const": "A_B2j*A_B1j"}, "A_3_2": {"const": "A_B3j*A_B2j"}}),
        "primary_estimand": {"const": "E[log(Y_B3/Y_B2)|A_3_2=1,scheduled_at_l_star]"},
        "primary_test": {"const": "OneSidedPairedTWeakConditionalMeanNullAlpha0.05"},
        "quantile_rule": {"const": "NearestRankNoInterpolation"}, "fixed_attempt_schedule_digest": SV,
        "attrition_reporting": {"const": "MandatoryPolicyAndAdjacentPairDenominatorsAndCategories"},
        "attrition_sensitivity": SV, "failed_latency_imputation": {"const": False}, "outcome_dependent_reruns": {"const": False},
        "key_secondary_family": {"const": "RQ1_RQ2_Holm"}, "exploratory_labels": strings(),
    })),
    "LocationQualifiedObject": (["C11", "C12", "C14"], "Field-level desired/requested/observed location-qualified object.", location_object),
    "QueueBinding": (["C08", "C12", "C13"], "Field-level endpoint/queue/catalog/worker/context binding.", obj({
        "endpoint_bdf": SV, "port_id": ID, "direction": enum("rx", "tx"), "hardware_queue_index": SV,
        "pipeline_id": ID, "paired_queue_id": ID, "descriptor_object_id": ID, "payload_pool_id": ID,
        "reference_mapping_digest": DIGEST, "ownership_catalog_digest": DIGEST, "selected_entry_index": ID,
        "owner_role_ids": strings(), "planning_shares": array(share), "control_class": S, "request_action": SV,
        "observed_shares": array(share), "observed_range_result": S, "observation_coverage": Q,
        "role_context_pu_bindings": array(obj({"role_id": ID, "context_id": ID, "requested_pu": SV, "effective_pu": SV})), "rss_digest": DIGEST,
    })),
    "ExecutionBinding": (["C08", "C12", "C16"], "Field-level logical-role/context/PU occupancy proof.", obj({
        "physical_context_id": ID, "occupancy_group_id": ID, "logical_role_ids": strings(minimum=1),
        "pipeline_mode": enum("RTC", "Staged"), "grouping_predicates": strings(minimum=1),
        "requested_cpu_mask": SV, "effective_cpu_mask": SV, "chosen_pu": SV, "physical_core_group_id": ID,
        "occupied_slot_count": Q, "service_contributions": array(obj({"role_id": ID, "demand": Q})), "service_sum": Q,
        "isolation_class": S, "observed_thread_ids": strings(), "observed_cpu_ids": strings(), "observation_coverage": Q,
    })),
    "CapacityCheck": (["C08", "C15", "C16"], "Reproducible hard-capacity inequality.", obj({
        "resource_id": ID, "resource_type": S, "contributors": array(obj({"contributor_id": ID, "demand": Q}), minimum=1),
        "calibrated_capacity": Q, "safety_guard": Q, "total_demand": Q, "inequality": S,
        "result": enum("Pass", "Fail"), "calibration_digest": DIGEST,
    })),
    "CostTermValue": (["C07", "C08"], "Term-ledger-owned normalized score contribution.", cost_term),
    "TimestampEvidence": (["C18", "C20"], "Field-level paired timestamp validity evidence.", obj({
        "sequence_id": ID, "request_raw_ticks": Q, "response_raw_ticks": Q, "clock_id": ID, "epoch_id": ID,
        "capture_layer": S, "conversion_rule": S, "wrap_extension_state": S, "valid": {"type": "boolean"},
        "validity_reason": S, "qualification_digest": DIGEST,
    })),
    "ResponseCategory": (["C20"], "Field-level exhaustive response classification.", response_category),
    "PrimaryAnalysisRecord": (["C24"], "Field-level primary conditional inference record.", obj({
        "analysis_plan_digest": DIGEST, "reference_condition_id": ID,
        "conditional_estimand_label": {"const": "ConditionalAcceptedPairMeanLogRatio_B3_over_B2"},
        "planned_attempt_count": Q, "attempted_policy_counts": quantities(minimum=1), "accepted_policy_counts": quantities(minimum=1),
        "adjacent_pair_counts": quantities(minimum=1), "failure_counts": quantities(minimum=1),
        "accepted_b3_b2_run_pair_ids": strings(), "D_j": quantities(), "planned_n": Q, "accepted_n": Q,
        "mean_D": Q, "standard_error": Q, "t_statistic": Q, "one_sided_p_value": Q,
        "upper_one_sided_bound": Q, "two_sided_interval": quantities(), "decision": S,
        "operational_feasibility_digest": DIGEST, "assumption_diagnostics_digest": DIGEST,
    })),
    "PacketExpectation": (["C19", "C20"], "One immutable expected packet identity.", obj({
        "run_id": ID, "expected_sequence_id": ID, "transmit_order_index": Q, "request_id": ID,
        "flow_id": ID, "intended_queue_id": ID, "sequence_manifest_digest": DIGEST,
    })),
    "PacketObservation": (["C18", "C20"], "One raw received candidate with no implied validity.", obj({
        "run_id": ID, "candidate_response_id": ID, "parsed_sequence": SV, "observed_queue_id": SV,
        "request_tx_raw_ticks": Q, "response_rx_raw_ticks": Q, "clock_id": ID, "epoch_id": ID,
        "converted_latency": Q, "format_result": S, "payload_result": S, "binding_result": S,
        "duplicate_reorder_category": S, "timestamp_validity": S,
    })),
    "CounterSample": (["C22"], "Field-level raw/extended scoped counter sample.", obj({
        "run_id": ID, "source_id": ID, "event_id": ID, "scope_id": ID, "raw_value": Q,
        "extended_value": Q, "sample_clock_id": ID, "sample_time": Q, "enabled_time": Q,
        "running_time": Q, "counter_width": Q, "wrap_reset_indicator": S, "quality_flag": S,
    })),
    "DecisionGateLedger": ([], "Typed D01-D23 protocol decision state and resolution evidence.", obj({
        "ledger_version": {"const": "1.0.0"},
        "allowed_states": array(enum("Frozen", "PendingQualification", "BlockedOnTestbed", "UnresolvedScientificDecision", "Unsupported", "NotApplicable"), minimum=6, unique=True),
        "gates": array(obj({
            "decision_id": {"type": "string", "pattern": r"D(?:0[1-9]|1[0-9]|2[0-3])"},
            "decision": S,
            "state": enum("Frozen", "PendingQualification", "BlockedOnTestbed", "UnresolvedScientificDecision", "Unsupported", "NotApplicable"),
            "allowed_options": strings(minimum=1),
            "recommended_default": SV,
            "resolved_value": SV,
            "selection_evidence": S,
            "evidence_digests": array(DIGEST),
            "freeze_point": S,
            "affected_components": strings(minimum=1),
            "reopen_conditions": S,
        }), minimum=23),
        "frozen_decision_ids": strings(minimum=5, unique=True),
        "unresolved_decision_ids": strings(minimum=18, unique=True),
    })),
    "CampaignDefinition": (["C06", "C17", "C21", "C23", "C24"], "Versioned campaign template with unresolved stand values retained as typed states.", obj({
        "campaign_template_version": {"const": "1.0.0"}, "campaign_id": SV,
        "stage": enum("Template", "Feasibility", "Calibration", "Confirmatory", "Robustness", "Analysis"),
        "decision_ledger_digest": DIGEST, "analysis_plan": SV,
        "frontend_profile": SV, "topology_snapshot": SV, "primary_nic_port_bdf": SV,
        "timestamp_mechanism": SV, "counter_set": SV, "huge_page_size": Q, "tau_mem": Q,
        "cost_coefficients": SV, "smallest_relevant_effect": Q, "warmup_duration": Q,
        "cooldown_duration": Q, "measurement_duration": Q, "offered_rates": array(Q),
        "queue_counts": array(Q), "worker_counts": array(Q), "reference_condition": SV,
        "randomization_seed": SV, "fixed_attempt_schedule": SV,
        "attrition_sensitivity": SV, "protocol_input_digests": array(DIGEST, minimum=1),
        "confirmatory_execution_permitted": {"const": False},
    })),
}


ALL_RECORDS = RECORDS | ADDITIONAL


def file_name(title: str) -> str:
    import re

    words = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", title)
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", words)
    return words.lower() + ".schema.json"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    write_json(SCHEMA_DIR / "common.schema.json", COMMON)

    index_records: list[dict[str, Any]] = []
    for title, (contracts, description, payload) in sorted(ALL_RECORDS.items()):
        name = file_name(title)
        write_json(SCHEMA_DIR / name, record_schema(title, description, payload))
        index_records.append({
            "record_type": title,
            "schema": name,
            "contracts": contracts,
            "required_test_classes": [
                "normal-path",
                "boundary",
                "malformed-input",
                "missing-data",
                "deterministic-replay",
                "digest-provenance",
                "declared-failure-status",
            ],
        })

    write_json(SCHEMA_DIR / "schema-index.json", {
        "schema_version": "1.0.0",
        "canonical_serialization": "canonical-json-v1",
        "records": index_records,
    })


if __name__ == "__main__":
    main()
