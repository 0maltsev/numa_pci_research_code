#!/usr/bin/env python3
"""Deterministic JSON serialization and SHA-256 replay for contract records."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any


class CanonicalizationError(ValueError):
    """Raised when a document cannot be represented by the frozen rules."""


def _normalize(value: Any) -> Any:
    if value is None:
        raise CanonicalizationError("JSON null is forbidden; use a typed state")
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        raise CanonicalizationError(
            "raw JSON numbers are forbidden; use a quantity with a decimal string and unit"
        )
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError("object keys must be strings")
            normalized[unicodedata.normalize("NFC", key)] = _normalize(item)
        if len(normalized) != len(value):
            raise CanonicalizationError("Unicode normalization produced duplicate keys")
        return normalized
    raise CanonicalizationError(f"unsupported JSON value type: {type(value).__name__}")


def canonical_bytes(document: Any) -> bytes:
    """Return UTF-8 canonical bytes; object keys sort, array order is retained."""

    normalized = _normalize(document)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def digest_document(document: dict[str, Any]) -> str:
    """Digest a record while excluding only meta.canonical_digest."""

    digest_input = copy.deepcopy(document)
    try:
        del digest_input["meta"]["canonical_digest"]
    except (KeyError, TypeError) as exc:
        raise CanonicalizationError("record lacks meta.canonical_digest") from exc
    return "sha256:" + hashlib.sha256(canonical_bytes(digest_input)).hexdigest()


def verify_document_digest(document: dict[str, Any]) -> bool:
    try:
        stored = document["meta"]["canonical_digest"]
    except (KeyError, TypeError):
        return False
    return stored == digest_document(document)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} RECORD.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    document = json.loads(path.read_text(encoding="utf-8"))
    print(digest_document(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
