"""Tests for the CPA Workpaper Spec schemas, examples, and validator.

Run with:  pytest -q
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "validator"))

from validate import (  # noqa: E402
    EXAMPLE_TO_SCHEMA,
    EXAMPLE_DIR,
    SCHEMA_DIR,
    build_store,
    load_schemas,
    validate_document,
)

SCHEMAS = load_schemas()
STORE = build_store(SCHEMAS)


def _load_example(name: str) -> dict:
    with (EXAMPLE_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Schema files are well-formed
# ---------------------------------------------------------------------------

def test_all_schema_files_are_valid_json():
    files = list(SCHEMA_DIR.glob("*.schema.json"))
    assert files, "expected schema files to exist"
    for path in files:
        with path.open(encoding="utf-8") as fh:
            json.load(fh)  # raises on malformed JSON


def test_entity_schemas_declare_draft_2020_12():
    for name, schema in SCHEMAS.items():
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", name


def test_entity_schemas_have_id_and_title():
    for name, schema in SCHEMAS.items():
        assert "$id" in schema, name
        assert "title" in schema, name


# ---------------------------------------------------------------------------
# Every bundled example validates against its schema
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("example_name,schema_name", sorted(EXAMPLE_TO_SCHEMA.items()))
def test_examples_validate(example_name: str, schema_name: str):
    document = _load_example(example_name)
    errors = validate_document(document, schema_name, SCHEMAS, STORE)
    assert errors == [], f"{example_name}:\n" + "\n".join(errors)


def test_every_entity_schema_has_an_example():
    entity_schemas = {n for n in SCHEMAS if n != "common"}
    covered = set(EXAMPLE_TO_SCHEMA.values())
    assert entity_schemas == covered


# ---------------------------------------------------------------------------
# Negative cases: invalid documents are rejected
# ---------------------------------------------------------------------------

def test_missing_required_field_fails():
    doc = _load_example("engagement.example.json")
    del doc["track"]
    errors = validate_document(doc, "engagement", SCHEMAS, STORE)
    assert errors, "expected validation to fail when a required field is removed"


def test_unknown_property_fails_under_additional_properties_false():
    doc = _load_example("engagement.example.json")
    doc["unexpectedField"] = "nope"
    errors = validate_document(doc, "engagement", SCHEMAS, STORE)
    assert errors


def test_bad_enum_value_fails():
    doc = _load_example("tax-prep.example.json")
    doc["currentStage"] = "totally_made_up_stage"
    errors = validate_document(doc, "tax-prep", SCHEMAS, STORE)
    assert errors


def test_wrong_spec_version_fails():
    doc = _load_example("close-checklist.example.json")
    doc["specVersion"] = "9.9"
    errors = validate_document(doc, "close-checklist", SCHEMAS, STORE)
    assert errors


def test_bad_money_format_fails():
    doc = _load_example("engagement-letter.example.json")
    doc["fee"]["amount"]["amount"] = "not-a-number"
    errors = validate_document(doc, "engagement-letter", SCHEMAS, STORE)
    assert errors


def test_money_currency_pattern_enforced():
    doc = _load_example("engagement-letter.example.json")
    doc["fee"]["amount"]["currency"] = "dollars"
    errors = validate_document(doc, "engagement-letter", SCHEMAS, STORE)
    assert errors


def test_unknown_schema_name_reports_error():
    doc = _load_example("engagement.example.json")
    errors = validate_document(doc, "does-not-exist", SCHEMAS, STORE)
    assert errors
    assert "unknown schema" in errors[0]


# ---------------------------------------------------------------------------
# Cross-reference: nested $defs and $ref to common.schema.json resolve
# ---------------------------------------------------------------------------

def test_nested_open_item_validation():
    doc = _load_example("close-checklist.example.json")
    # make a nested open-item invalid (bad enum on a nested object)
    doc["openItems"][0]["status"] = "not_a_real_status"
    errors = validate_document(doc, "close-checklist", SCHEMAS, STORE)
    assert errors


def test_common_ref_personref_required_name():
    doc = _load_example("engagement.example.json")
    # personRef requires 'name'
    doc["team"][0] = {"id": "usr_x"}
    errors = validate_document(doc, "engagement", SCHEMAS, STORE)
    assert errors


def test_valid_document_round_trips_clean():
    # mutate then restore should be clean (guards against shared-state bugs)
    doc = _load_example("request-list-item.example.json")
    snapshot = copy.deepcopy(doc)
    assert validate_document(doc, "request-list-item", SCHEMAS, STORE) == []
    assert doc == snapshot
