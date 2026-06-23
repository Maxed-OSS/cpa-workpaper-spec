#!/usr/bin/env python3
"""CPA Workpaper Spec validator.

Validates JSON documents against the CPA Workpaper Spec JSON Schemas (v0.1).

The spec's schemas reference each other by their published ``$id`` (an https URL)
and by relative filename. To make validation work fully offline, this validator
builds a local registry that maps every schema ``$id`` *and* its bare filename to
the on-disk schema, so ``$ref``s resolve without any network access.

Usage:
    validate.py <document.json> --schema <schema-name>
    validate.py <document.json> --schema engagement
    validate.py --all                 # validate every bundled example
    validate.py --list-schemas

Schema names are the schema filenames without the ``.schema.json`` suffix, e.g.
``engagement``, ``close-checklist``, ``tax-prep``, ``engagement-letter``,
``request-list-item``.

Exit code is 0 when every requested validation passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError:  # pragma: no cover - guidance path
    sys.stderr.write(
        "error: the 'jsonschema' (>=4.18) package is required.\n"
        "       install it with:  pip install -r requirements.txt\n"
    )
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schema" / "v0.1"
EXAMPLE_DIR = REPO_ROOT / "examples" / "v0.1"
SCHEMA_SUFFIX = ".schema.json"

# Examples are paired with the schema they should validate against.
EXAMPLE_TO_SCHEMA = {
    "engagement.example.json": "engagement",
    "close-checklist.example.json": "close-checklist",
    "tax-prep.example.json": "tax-prep",
    "engagement-letter.example.json": "engagement-letter",
    "request-list-item.example.json": "request-list-item",
    "workpaper.example.json": "workpaper",
}


def load_schemas() -> dict[str, dict]:
    """Load every schema file in the schema dir, keyed by schema name."""
    schemas: dict[str, dict] = {}
    for path in sorted(SCHEMA_DIR.glob(f"*{SCHEMA_SUFFIX}")):
        name = path.name[: -len(SCHEMA_SUFFIX)]
        with path.open(encoding="utf-8") as fh:
            schemas[name] = json.load(fh)
    return schemas


def build_store(schemas: dict[str, dict]) -> "Registry":
    """Build a ``referencing`` Registry that can resolve every cross-schema $ref.

    Each schema is registered under both its published ``$id`` (an https URL) and
    its bare filename, so relative ``$ref``s such as
    ``common.schema.json#/$defs/id`` resolve fully offline.
    """
    resources: list[tuple[str, "Resource"]] = []
    for name, schema in schemas.items():
        filename = f"{name}{SCHEMA_SUFFIX}"
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        if "$id" in schema:
            resources.append((schema["$id"], resource))
        resources.append((filename, resource))
    return Registry().with_resources(resources)


def list_schema_names(schemas: dict[str, dict]) -> list[str]:
    return sorted(schemas)


def validate_document(
    document: dict,
    schema_name: str,
    schemas: dict[str, dict],
    store: "Registry",
) -> list[str]:
    """Return a list of human-readable validation error strings (empty == valid)."""
    if schema_name not in schemas:
        return [
            f"unknown schema '{schema_name}'. "
            f"known schemas: {', '.join(list_schema_names(schemas))}"
        ]
    schema = schemas[schema_name]
    validator = Draft202012Validator(schema, registry=store)
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    out: list[str] = []
    for err in errors:
        location = "/".join(str(p) for p in err.path) or "<root>"
        out.append(f"  at {location}: {err.message}")
    return out


def _print_result(label: str, errors: list[str]) -> None:
    if errors:
        print(f"FAIL  {label}")
        for line in errors:
            print(line)
    else:
        print(f"OK    {label}")


def validate_one(args: argparse.Namespace, schemas: dict[str, dict], store: "Registry") -> int:
    doc_path = Path(args.document)
    if not doc_path.exists():
        sys.stderr.write(f"error: document not found: {doc_path}\n")
        return 1
    with doc_path.open(encoding="utf-8") as fh:
        document = json.load(fh)
    errors = validate_document(document, args.schema, schemas, store)
    _print_result(f"{doc_path.name} against '{args.schema}'", errors)
    return 1 if errors else 0


def validate_all(schemas: dict[str, dict], store: "Registry") -> int:
    rc = 0
    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        path = EXAMPLE_DIR / example_name
        if not path.exists():
            print(f"FAIL  {example_name} (missing example file)")
            rc = 1
            continue
        with path.open(encoding="utf-8") as fh:
            document = json.load(fh)
        errors = validate_document(document, schema_name, schemas, store)
        _print_result(f"{example_name} against '{schema_name}'", errors)
        if errors:
            rc = 1
    return rc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate documents against the CPA Workpaper Spec.")
    parser.add_argument("document", nargs="?", help="Path to a JSON document to validate.")
    parser.add_argument("--schema", help="Schema name to validate against (e.g. 'engagement').")
    parser.add_argument("--all", action="store_true", help="Validate every bundled example.")
    parser.add_argument("--list-schemas", action="store_true", help="List known schema names and exit.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    schemas = load_schemas()
    store = build_store(schemas)

    if args.list_schemas:
        for name in list_schema_names(schemas):
            print(name)
        return 0

    if args.all:
        return validate_all(schemas, store)

    if not args.document or not args.schema:
        parser.error("provide a document and --schema, or use --all / --list-schemas")

    return validate_one(args, schemas, store)


if __name__ == "__main__":
    raise SystemExit(main())
