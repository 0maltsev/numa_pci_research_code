#!/usr/bin/env python3
"""Dependency-free validator for the deliberate JSON-Schema subset in v1."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


class SchemaStore:
    def __init__(self, root: Path):
        self.root = root
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, name: str) -> dict[str, Any]:
        if name not in self._cache:
            self._cache[name] = json.loads((self.root / name).read_text(encoding="utf-8"))
        return self._cache[name]

    def resolve(self, reference: str, current_file: str) -> tuple[dict[str, Any], str]:
        file_name, _, fragment = reference.partition("#")
        target_name = file_name or current_file
        target: Any = self.load(target_name)
        if fragment:
            if not fragment.startswith("/"):
                raise ValueError(f"unsupported JSON pointer: {reference}")
            for part in fragment[1:].split("/"):
                part = part.replace("~1", "/").replace("~0", "~")
                target = target[part]
        return target, target_name


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    return False


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    store: SchemaStore,
    current_file: str,
    path: str = "$",
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if "$ref" in schema:
        target, target_file = store.resolve(schema["$ref"], current_file)
        return validate_instance(instance, target, store, target_file, path)

    for subschema in schema.get("allOf", []):
        issues.extend(validate_instance(instance, subschema, store, current_file, path))

    if "oneOf" in schema:
        alternatives = [
            validate_instance(instance, choice, store, current_file, path)
            for choice in schema["oneOf"]
        ]
        passing = [candidate for candidate in alternatives if not candidate]
        if len(passing) != 1:
            issues.append(ValidationIssue(path, f"expected exactly one oneOf branch, got {len(passing)}"))
        return issues

    if "const" in schema and instance != schema["const"]:
        issues.append(ValidationIssue(path, f"expected constant {schema['const']!r}"))
    if "enum" in schema and instance not in schema["enum"]:
        issues.append(ValidationIssue(path, f"value is not in enum {schema['enum']!r}"))

    expected_type = schema.get("type")
    if expected_type and not _json_type_matches(instance, expected_type):
        issues.append(ValidationIssue(path, f"expected {expected_type}"))
        return issues

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            issues.append(ValidationIssue(path, "string is shorter than minLength"))
        if "pattern" in schema and not re.fullmatch(schema["pattern"], instance):
            issues.append(ValidationIssue(path, f"string does not match {schema['pattern']}"))
        if schema.get("format") == "date-time":
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", instance):
                issues.append(ValidationIssue(path, "expected an RFC3339 UTC date-time"))

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            issues.append(ValidationIssue(path, "array is shorter than minItems"))
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in instance]
            if len(encoded) != len(set(encoded)):
                issues.append(ValidationIssue(path, "array items are not unique"))
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                issues.extend(
                    validate_instance(item, item_schema, store, current_file, f"{path}[{index}]")
                )

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in instance:
                issues.append(ValidationIssue(path, f"missing required property {name!r}"))
        properties = schema.get("properties", {})
        for name, value in instance.items():
            if name in properties:
                issues.extend(
                    validate_instance(value, properties[name], store, current_file, f"{path}.{name}")
                )
            elif schema.get("additionalProperties") is False:
                issues.append(ValidationIssue(path, f"unexpected property {name!r}"))

    return issues


def assert_valid(instance: Any, schema_file: str, schema_root: Path) -> None:
    store = SchemaStore(schema_root)
    issues = validate_instance(instance, store.load(schema_file), store, schema_file)
    if issues:
        rendered = "\n".join(f"{issue.path}: {issue.message}" for issue in issues)
        raise AssertionError(rendered)


def validate_record_semantics(document: dict[str, Any]) -> list[ValidationIssue]:
    """Validate cross-field record rules that JSON Schema alone does not express."""

    from tools.canonical_json import CanonicalizationError, canonical_bytes, verify_document_digest

    issues: list[ValidationIssue] = []
    try:
        canonical_bytes(document)
    except CanonicalizationError as exc:
        issues.append(ValidationIssue("$", str(exc)))
        return issues
    if not verify_document_digest(document):
        issues.append(ValidationIssue("$.meta.canonical_digest", "digest replay mismatch"))

    meta = document.get("meta", {})
    provenance = meta.get("provenance", {})
    if meta.get("artifact_class") == "Derived":
        if not provenance.get("source_record_ids"):
            issues.append(ValidationIssue("$.meta.provenance.source_record_ids", "derived record needs source IDs"))
        if not provenance.get("source_digests"):
            issues.append(ValidationIssue("$.meta.provenance.source_digests", "derived record needs source digests"))
        if not provenance.get("raw_records_immutable"):
            issues.append(ValidationIssue("$.meta.provenance.raw_records_immutable", "derived sources must be immutable"))
        if not set(provenance.get("source_digests", [])) <= set(meta.get("input_digests", [])):
            issues.append(ValidationIssue("$.meta.input_digests", "derived source digests must be input digests"))

    if meta.get("data_classification") == "NON_MEASUREMENT_TEST_FIXTURE":
        if meta.get("artifact_class") != "TestFixture":
            issues.append(ValidationIssue("$.meta.artifact_class", "fixture classification requires TestFixture"))
        if meta.get("scientific_disposition") != "NotMeasurement":
            issues.append(ValidationIssue("$.meta.scientific_disposition", "fixture must be NotMeasurement"))

    status_kind = meta.get("status", {}).get("kind")
    if status_kind in {"Failure", "Excluded"} and not meta.get("errors"):
        issues.append(ValidationIssue("$.meta.errors", "failure/excluded record requires a structured error"))
    return issues
