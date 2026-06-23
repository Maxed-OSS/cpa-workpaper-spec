"""Keep the normative SPEC.md in lockstep with the schemas.

The spec document (SPEC.md) restates, in prose, facts that also live in the
JSON Schema files: the set of entities, their required fields, and the
specVersion. If those drift, the anchor spec is no longer trustworthy. This test
parses the relevant tables out of SPEC.md and asserts they match the schemas.

Run with:  pytest -q
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DOC = REPO_ROOT / "SPEC.md"
SCHEMA_DIR = REPO_ROOT / "schema" / "v0.1"

# entity name -> schema filename (the seven schemas; common has no required list)
ENTITIES = {
    "engagement": "engagement.schema.json",
    "workpaper": "workpaper.schema.json",
    "close-checklist": "close-checklist.schema.json",
    "tax-prep": "tax-prep.schema.json",
    "engagement-letter": "engagement-letter.schema.json",
    "request-list-item": "request-list-item.schema.json",
}


def _schema(filename: str) -> dict:
    with (SCHEMA_DIR / filename).open(encoding="utf-8") as fh:
        return json.load(fh)


def _spec_required_table() -> dict[str, set[str]]:
    """Parse the 'Required fields per entity' markdown table from SPEC.md.

    Rows look like:
        | `engagement` | `specVersion`, `id`, `clientId`, ... |
    """
    text = SPEC_DOC.read_text(encoding="utf-8")
    out: dict[str, set[str]] = {}
    row = re.compile(r"^\s*\|\s*`([a-z-]+)`\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)
    for entity, fields_cell in row.findall(text):
        if entity not in ENTITIES:
            continue
        fields = set(re.findall(r"`([^`]+)`", fields_cell))
        out[entity] = fields
    return out


def test_spec_doc_exists():
    assert SPEC_DOC.is_file(), "SPEC.md (the normative anchor) is missing"


def test_spec_lists_every_entity():
    parsed = _spec_required_table()
    assert set(parsed) == set(ENTITIES), (
        "SPEC.md required-fields table must cover exactly the entity schemas"
    )


def test_spec_required_fields_match_schemas():
    parsed = _spec_required_table()
    for entity, filename in ENTITIES.items():
        schema_required = set(_schema(filename).get("required", []))
        assert parsed[entity] == schema_required, (
            f"SPEC.md required fields for '{entity}' "
            f"{sorted(parsed[entity])} do not match the schema "
            f"{sorted(schema_required)}"
        )


def test_spec_states_the_specversion():
    const = _schema("common.schema.json")["$defs"]["specVersion"]["const"]
    assert f'`"{const}"`' in SPEC_DOC.read_text(encoding="utf-8"), (
        "SPEC.md must state the current specVersion const value"
    )


def test_every_entity_locks_additional_properties():
    # SPEC.md rule 3 asserts additionalProperties is false everywhere; verify it.
    for filename in ENTITIES.values():
        assert _schema(filename).get("additionalProperties") is False, (
            f"{filename} must set additionalProperties: false per SPEC.md"
        )
