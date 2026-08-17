# ADR 0003: Canonical serialization and digest rules

- Status: Accepted
- Date: 2026-08-17

## Context

Every record must be content-addressable and reproducible across processes/languages. Ordinary JSON permits insignificant key order, whitespace, number spelling, Unicode normalization differences, and ambiguous `null`.

## Decision

Canonical JSON v1 uses:

1. UTF-8 encoding and NFC normalization for every key/string;
2. object keys sorted lexicographically by normalized Unicode string;
3. array order preserved exactly as declared by each schema (arrays representing sets must be sorted by the producer's recorded stable rule);
4. separators `,` and `:` with no insignificant whitespace;
5. JSON booleans as booleans;
6. no JSON `null` and no raw JSON numbers in records;
7. numeric values encoded as canonical decimal strings inside typed quantity objects with a controlled explicit unit;
8. SHA-256 rendered as lowercase `sha256:<64 hex>`.

The canonical-content digest is SHA-256 over the complete record after removing only top-level `meta.canonical_digest`. All other metadata—including producer, creation clock/time, input digests, status, errors, provenance, validity, and scientific disposition—remains covered. Input artifacts retain their own digests; derived outputs list and cover those digests.

## Consequences

Known zero cannot collide with unavailable states, and floating-point serializer differences cannot alter evidence. Record creation time intentionally affects identity. Schema evolution requires a new schema/canonicalization version; v1 bytes are never silently reinterpreted. `tools/canonical_json.py` is the executable off-stand reference and digest replay test oracle.
