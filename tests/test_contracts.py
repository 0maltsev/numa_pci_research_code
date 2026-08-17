from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

from tools.canonical_json import CanonicalizationError, canonical_bytes, digest_document, verify_document_digest
from tools.schema_validator import SchemaStore, assert_valid, validate_instance, validate_record_semantics


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "v1"
INDEX = json.loads((SCHEMAS / "schema-index.json").read_text(encoding="utf-8"))
ZERO_DIGEST = "sha256:" + "0" * 64


def synthesize(schema: dict[str, Any], store: SchemaStore, current_file: str, seed: str = "fixture") -> Any:
    if "$ref" in schema:
        target, target_file = store.resolve(schema["$ref"], current_file)
        return synthesize(target, store, target_file, seed)
    if "const" in schema:
        return schema["const"]
    if "examples" in schema:
        return copy.deepcopy(schema["examples"][0])
    if "oneOf" in schema:
        return synthesize(schema["oneOf"][0], store, current_file, seed)
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        properties = schema.get("properties", {})
        return {
            name: synthesize(properties[name], store, current_file, f"{seed}-{name}")
            for name in schema.get("required", [])
        }
    if kind == "array":
        count = schema.get("minItems", 0)
        items = schema.get("items", {})
        values = []
        for index in range(count):
            if schema.get("uniqueItems") and "enum" in items and index < len(items["enum"]):
                values.append(items["enum"][index])
            else:
                value = synthesize(items, store, current_file, f"{seed}-{index}")
                if schema.get("uniqueItems") and isinstance(value, str) and index:
                    value = f"fixture:unique-{index}"
                values.append(value)
        return values
    if kind == "string":
        if schema.get("pattern") == r"D(?:0[1-9]|1[0-9]|2[0-3])":
            return "D01"
        return "fixture-value"
    if kind == "boolean":
        return False
    raise AssertionError(f"cannot synthesize schema at {seed}: {schema}")


def fixture_for(entry: dict[str, Any]) -> dict[str, Any]:
    store = SchemaStore(SCHEMAS)
    schema = store.load(entry["schema"])
    document = synthesize(schema, store, entry["schema"], entry["record_type"])
    meta = document["meta"]
    meta["record_id"] = f"fixture:{entry['record_type'].lower()}"
    meta["producer"] = {"identity": "test:contract-validator", "version": "1.0.0"}
    meta["created_at"] = {"value": "2000-01-01T00:00:00Z", "clock_domain": "TEST_MONOTONIC"}
    meta["campaign_or_stage_id"] = "stage:milestone-1-tests"
    meta["input_digests"] = []
    meta["status"] = {"kind": "Success", "code": "Fixture-Valid", "detail": "Synthetic non-measurement schema fixture"}
    meta["errors"] = []
    meta["artifact_class"] = "TestFixture"
    meta["data_classification"] = "NON_MEASUREMENT_TEST_FIXTURE"
    meta["scientific_disposition"] = "NotMeasurement"
    meta["validity_domain"] = {"state": "Known", "definition": "Contract validation only", "evidence_digests": []}
    meta["provenance"] = {
        "source_record_ids": [], "source_digests": [],
        "transformation": "deterministic schema fixture synthesis", "raw_records_immutable": True,
    }
    meta["canonical_digest"] = digest_document(document)
    return document


def replace_first_quantity(value: Any, replacement: dict[str, str]) -> bool:
    if isinstance(value, dict):
        if set(value) == {"state", "value", "unit"} and value.get("state") == "Known":
            value.clear()
            value.update(replacement)
            return True
        return any(replace_first_quantity(child, replacement) for child in value.values())
    if isinstance(value, list):
        return any(replace_first_quantity(child, replacement) for child in value)
    return False


def schema_has_path(schema: dict[str, Any], schema_file: str, path: str) -> bool:
    store = SchemaStore(SCHEMAS)
    parts = path.replace("[*]", "").split(".")[1:]  # discard RecordType
    current = schema
    current_file = schema_file
    for part in parts:
        while "$ref" in current:
            current, current_file = store.resolve(current["$ref"], current_file)
        if current.get("type") == "array":
            current = current["items"]
            while "$ref" in current:
                current, current_file = store.resolve(current["$ref"], current_file)
        properties = current.get("properties", {})
        if part not in properties:
            return False
        current = properties[part]
    return True


class SchemaContractTests(unittest.TestCase):
    def test_all_c01_c24_are_mapped_to_schemas_and_test_classes(self) -> None:
        required_contracts = {f"C{index:02d}" for index in range(1, 25)}
        mapped: set[str] = set()
        expected_classes = {
            "normal-path", "boundary", "malformed-input", "missing-data",
            "deterministic-replay", "digest-provenance", "declared-failure-status",
        }
        for entry in INDEX["records"]:
            mapped.update(entry["contracts"])
            self.assertEqual(expected_classes, set(entry["required_test_classes"]), entry["record_type"])
            self.assertTrue((SCHEMAS / entry["schema"]).is_file())
        self.assertEqual(required_contracts, mapped)

    def test_every_record_schema_has_normal_boundary_missing_and_failure_examples(self) -> None:
        store = SchemaStore(SCHEMAS)
        for entry in INDEX["records"]:
            with self.subTest(record=entry["record_type"], case="normal-zero-boundary"):
                document = fixture_for(entry)
                assert_valid(document, entry["schema"], SCHEMAS)
                self.assertTrue(verify_document_digest(document))
                self.assertFalse(validate_record_semantics(document))

            with self.subTest(record=entry["record_type"], case="typed-missing"):
                missing = fixture_for(entry)
                changed = replace_first_quantity(
                    missing["payload"],
                    {"state": "Missing", "unit": "dimensionless", "reason": "Fixture intentionally omits a numeric observation"},
                )
                if changed:
                    missing["meta"]["canonical_digest"] = digest_document(missing)
                    assert_valid(missing, entry["schema"], SCHEMAS)

            with self.subTest(record=entry["record_type"], case="declared-failure"):
                failed = fixture_for(entry)
                failed["meta"]["status"] = {"kind": "Failure", "code": "Fixture-Declared-Failure", "detail": "Declared failure-state schema test"}
                failed["meta"]["errors"] = [{
                    "error_id": "fixture:error-001", "component": entry["record_type"], "stage": "contract-test",
                    "code": "Fixture-Declared-Failure", "severity": "Error", "affected_facts": [],
                    "message": "Synthetic failure for schema validation", "recovery_status": "NotRequired",
                    "rollback_status": "NotApplicable", "scientific_disposition": "ScientificallyExcluded",
                }]
                failed["meta"]["canonical_digest"] = digest_document(failed)
                assert_valid(failed, entry["schema"], SCHEMAS)

    def test_every_record_rejects_missing_envelope_and_extra_top_level_data(self) -> None:
        store = SchemaStore(SCHEMAS)
        for entry in INDEX["records"]:
            schema = store.load(entry["schema"])
            document = fixture_for(entry)
            without_meta = copy.deepcopy(document)
            del without_meta["meta"]
            self.assertTrue(validate_instance(without_meta, schema, store, entry["schema"]), entry["record_type"])
            malformed = copy.deepcopy(document)
            malformed["ambiguous_extra"] = "forbidden"
            self.assertTrue(validate_instance(malformed, schema, store, entry["schema"]), entry["record_type"])

    def test_every_record_digest_replays_and_detects_tampering(self) -> None:
        for entry in INDEX["records"]:
            document = fixture_for(entry)
            reordered = json.loads(json.dumps(document, sort_keys=False))
            self.assertEqual(canonical_bytes(document), canonical_bytes(reordered))
            self.assertEqual(digest_document(document), digest_document(reordered))
            reordered["meta"]["status"]["detail"] = "tampered"
            self.assertFalse(verify_document_digest(reordered), entry["record_type"])

    def test_quantity_states_forbid_unknown_zero_ambiguity(self) -> None:
        store = SchemaStore(SCHEMAS)
        wrapper = {"$ref": "common.schema.json#/$defs/quantity"}
        valid = [
            {"state": "Known", "value": "0", "unit": "count"},
            {"state": "Unknown", "unit": "count", "reason": "Not yet knowable"},
            {"state": "Missing", "unit": "count", "reason": "Expected source absent"},
            {"state": "Unsupported", "unit": "count", "reason": "Capability absent"},
            {"state": "NotApplicable", "unit": "count", "reason": "Dimension does not apply"},
        ]
        for item in valid:
            self.assertFalse(validate_instance(item, wrapper, store, "common.schema.json"), item)
        invalid = [
            {"state": "Unknown", "value": "0", "unit": "count", "reason": "ambiguous"},
            {"state": "Known", "unit": "count"},
            {"state": "Missing", "unit": "count"},
            {"state": "Known", "value": 0, "unit": "count"},
            {"state": "Known", "value": "0", "unit": "mystery_unit"},
        ]
        for item in invalid:
            self.assertTrue(validate_instance(item, wrapper, store, "common.schema.json"), item)
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"state": "Known", "value": 0, "unit": "count"})
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"state": None})

    def test_derived_records_require_immutable_source_provenance(self) -> None:
        entry = next(item for item in INDEX["records"] if item["record_type"] == "AggregatedDataset")
        document = fixture_for(entry)
        document["meta"]["artifact_class"] = "Derived"
        document["meta"]["data_classification"] = "ProtocolDefinition"
        document["meta"]["provenance"]["source_record_ids"] = ["fixture:raw-001"]
        document["meta"]["provenance"]["source_digests"] = [ZERO_DIGEST]
        document["meta"]["input_digests"] = [ZERO_DIGEST]
        document["meta"]["canonical_digest"] = digest_document(document)
        assert_valid(document, entry["schema"], SCHEMAS)
        self.assertFalse(validate_record_semantics(document))
        invalid = copy.deepcopy(document)
        invalid["meta"]["provenance"]["source_digests"] = []
        invalid["meta"]["canonical_digest"] = digest_document(invalid)
        self.assertTrue(validate_record_semantics(invalid))

    def test_generated_schema_tree_is_deterministic(self) -> None:
        from tools import generate_schemas as generator

        expected_common = json.dumps(generator.COMMON, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        self.assertEqual(expected_common, (SCHEMAS / "common.schema.json").read_text(encoding="utf-8"))
        expected_records = []
        for title, (contracts, description, payload) in sorted(generator.ALL_RECORDS.items()):
            name = generator.file_name(title)
            expected = generator.record_schema(title, description, payload)
            encoded = json.dumps(expected, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            self.assertEqual(encoded, (SCHEMAS / name).read_text(encoding="utf-8"), title)
            expected_records.append({
                "record_type": title,
                "schema": name,
                "contracts": contracts,
                "required_test_classes": [
                    "normal-path", "boundary", "malformed-input", "missing-data",
                    "deterministic-replay", "digest-provenance", "declared-failure-status",
                ],
            })
        self.assertEqual(expected_records, INDEX["records"])

    def test_pending_and_final_page_records_are_order_independent(self) -> None:
        entry = next(item for item in INDEX["records"] if item["record_type"] == "PageEquivalenceRecord")
        digest_b0 = "sha256:" + "1" * 64
        digest_b1 = "sha256:" + "2" * 64

        pending = fixture_for(entry)
        pending["payload"]["state"] = "Pair-Pending"
        pending["payload"]["b0_page_record_digest"] = {"state": "Known", "value": digest_b0}
        pending["payload"]["b1_page_record_digest"] = {"state": "Missing", "reason": "B1 mate has not arrived"}
        pending["payload"]["input_record_digests_sorted"] = [digest_b0]
        pending["meta"]["canonical_digest"] = digest_document(pending)
        assert_valid(pending, entry["schema"], SCHEMAS)

        def finalized(arrival: list[str]) -> dict[str, Any]:
            record = fixture_for(entry)
            record["payload"]["state"] = "Pair-Equivalent"
            record["payload"]["b0_page_record_digest"] = {"state": "Known", "value": digest_b0}
            record["payload"]["b1_page_record_digest"] = {"state": "Known", "value": digest_b1}
            record["payload"]["input_record_digests_sorted"] = sorted(arrival)
            record["payload"]["latency_input_used"] = False
            record["meta"]["canonical_digest"] = digest_document(record)
            return record

        b0_then_b1 = finalized([digest_b0, digest_b1])
        b1_then_b0 = finalized([digest_b1, digest_b0])
        assert_valid(b0_then_b1, entry["schema"], SCHEMAS)
        assert_valid(b1_then_b0, entry["schema"], SCHEMAS)
        self.assertEqual(canonical_bytes(b0_then_b1), canonical_bytes(b1_then_b0))
        self.assertEqual(digest_document(b0_then_b1), digest_document(b1_then_b0))

    def test_planner_and_exact_status_semantics_are_representable(self) -> None:
        by_type = {entry["record_type"]: entry for entry in INDEX["records"]}
        for status in ("Feasible", "Search-Limited", "Cap-Limited", "Data-Incomplete"):
            document = fixture_for(by_type["CandidateSearchAudit"])
            document["payload"]["terminal_status"] = status
            document["meta"]["canonical_digest"] = digest_document(document)
            assert_valid(document, by_type["CandidateSearchAudit"]["schema"], SCHEMAS)
        for status in ("Exact-Feasible", "Proven-Infeasible", "Exact-Budget-Exceeded", "Exact-Execution-Error"):
            document = fixture_for(by_type["ExactReferenceResult"])
            document["payload"]["terminal_status"] = status
            document["payload"]["heuristic_input_used"] = False
            document["meta"]["canonical_digest"] = digest_document(document)
            assert_valid(document, by_type["ExactReferenceResult"]["schema"], SCHEMAS)


class ProtocolLedgerTests(unittest.TestCase):
    def test_decision_ledger_schema_digest_and_all_23_ids(self) -> None:
        ledger = json.loads((ROOT / "protocol/v1/decision-gates.json").read_text(encoding="utf-8"))
        assert_valid(ledger, "decision-gate-ledger.schema.json", SCHEMAS)
        self.assertTrue(verify_document_digest(ledger))
        gates = {item["decision_id"]: item for item in ledger["payload"]["gates"]}
        self.assertEqual({f"D{index:02d}" for index in range(1, 24)}, set(gates))
        frozen = {"D03", "D11", "D12", "D21", "D23"}
        self.assertEqual(frozen, {gate_id for gate_id, gate in gates.items() if gate["state"] == "Frozen"})
        for gate_id, gate in gates.items():
            if gate_id in frozen:
                self.assertEqual("Known", gate["resolved_value"]["state"])
            else:
                self.assertNotEqual("Frozen", gate["state"])
                self.assertEqual("Unknown", gate["resolved_value"]["state"])

    def test_protocol_records_regenerate_byte_identically_and_source_digests_match(self) -> None:
        from tools import generate_protocol_records as generator

        ledger_path = ROOT / "protocol/v1/decision-gates.json"
        campaign_path = ROOT / "campaigns/templates/v1/campaign.json"
        ledger = generator.make_ledger()
        campaign = generator.make_campaign(ledger["meta"]["canonical_digest"])
        expected_ledger = json.dumps(ledger, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        expected_campaign = json.dumps(campaign, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        self.assertEqual(expected_ledger, ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(expected_campaign, campaign_path.read_text(encoding="utf-8"))

        source_paths = [
            "paper_contract/EXPERIMENT_SPEC.md",
            "paper_contract/PRE_IMPLEMENTATION_DECISIONS.md",
            "paper_contract/CLAIM_EVIDENCE_MATRIX.md",
            "paper_contract/manuscript/sections/05_problem_statement.tex",
            "paper_contract/manuscript/sections/06_topology_model.tex",
            "paper_contract/manuscript/sections/07_cost_model.tex",
            "paper_contract/manuscript/sections/08_placement_algorithm.tex",
            "paper_contract/manuscript/sections/09_system_design.tex",
            "paper_contract/manuscript/sections/10_experimental_methodology.tex",
        ]
        actual_digests = ["sha256:" + hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in source_paths]
        self.assertEqual(generator.CONTRACT_DIGESTS, actual_digests)

    def test_frozen_decisions_are_exact_and_not_unresolved_defaults(self) -> None:
        ledger = json.loads((ROOT / "protocol/v1/decision-gates.json").read_text(encoding="utf-8"))
        gates = {item["decision_id"]: item for item in ledger["payload"]["gates"]}
        d03 = set(gates["D03"]["resolved_value"]["value"])
        self.assertTrue({"mode=SingleOwner", "owner_cardinality=1", "share=1"} <= d03)
        d11 = set(gates["D11"]["resolved_value"]["value"])
        self.assertTrue({"estimator=NearestRank", "index=max(1,ceil(p*N))", "interpolation=false"} <= d11)
        d12 = set(gates["D12"]["resolved_value"]["value"])
        self.assertTrue({
            "unit=complete-accepted-run", "coefficients=nonnegative",
            "condition-intercepts=unpenalized-fit-only", "global-intercept=none",
            "folds=condition-stratified-placement-relation-blocked",
            "validation-condition-must-occur-in-training=true", "confirmatory-data-used=false",
        } <= d12)
        d21 = set(gates["D21"]["resolved_value"]["value"])
        self.assertIn("topology-blind=true", d21)
        self.assertIn("forbidden-inputs=nic-bdf,pcie-ancestry,numa-distance,page-location,cost-model,latency", d21)
        d23 = set(gates["D23"]["resolved_value"]["value"])
        self.assertTrue({
            "estimand=conditional-accepted-pair-mean-log-ratio", "rerun=false",
            "failed-latency-imputation=false", "policy-and-pair-denominators=mandatory",
            "failure-categories=mandatory", "packets-are-repetitions=false",
        } <= d23)

    def test_campaign_template_is_valid_non_executable_and_contains_no_stand_values(self) -> None:
        campaign = json.loads((ROOT / "campaigns/templates/v1/campaign.json").read_text(encoding="utf-8"))
        assert_valid(campaign, "campaign-definition.schema.json", SCHEMAS)
        self.assertTrue(verify_document_digest(campaign))
        payload = campaign["payload"]
        self.assertFalse(payload["confirmatory_execution_permitted"])
        for field in ("campaign_id", "frontend_profile", "topology_snapshot", "primary_nic_port_bdf", "timestamp_mechanism", "counter_set", "cost_coefficients", "reference_condition"):
            self.assertEqual("Unknown", payload[field]["state"], field)
        for field in ("huge_page_size", "tau_mem", "smallest_relevant_effect", "warmup_duration", "measurement_duration"):
            self.assertEqual("Unknown", payload[field]["state"], field)

    def test_every_rq_and_output_path_resolves_to_a_schema_field(self) -> None:
        mapping = json.loads((ROOT / "protocol/v1/rq-field-map.json").read_text(encoding="utf-8"))
        self.assertEqual({f"RQ{index}" for index in range(1, 7)}, set(mapping["research_questions"]))
        by_type = {entry["record_type"]: entry for entry in INDEX["records"]}
        for rq, details in mapping["research_questions"].items():
            self.assertTrue(details["fields"], rq)
            for path in details["fields"]:
                record_type = path.split(".", 1)[0]
                self.assertIn(record_type, by_type, path)
                entry = by_type[record_type]
                schema = json.loads((SCHEMAS / entry["schema"]).read_text(encoding="utf-8"))
                self.assertTrue(schema_has_path(schema, entry["schema"], path), path)

    def test_no_measurement_or_result_artifact_was_generated(self) -> None:
        self.assertFalse((ROOT / "results").exists())
        for path in [ROOT / "protocol/v1/decision-gates.json", ROOT / "campaigns/templates/v1/campaign.json"]:
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotEqual("Measurement", document["meta"]["data_classification"])
            self.assertEqual("NotMeasurement", document["meta"]["scientific_disposition"])


if __name__ == "__main__":
    unittest.main()
