# cpa-workpaper-spec validator for agents

Machine interface for the offline JSON-Schema validator. Fully offline: it
builds a local registry so cross-schema `$ref`s resolve without network access.

## Command

```
python validator/validate.py <document.json|-> --schema <name> [--json]
python validator/validate.py --all [--json]
python validator/validate.py --list-schemas [--json]
```

- Read the document from stdin with `-`.
- `--schema` names: `engagement`, `workpaper`, `close-checklist`, `tax-prep`,
  `engagement-letter`, `request-list-item` (run `--list-schemas`).
- Requires `pip install -r requirements.txt` (jsonschema, referencing).

## Output with --json

Single document:

```json
{"ok": true, "valid": true, "schema": "engagement", "document": "<stdin>", "errors": []}
```

An invalid document lists human-readable schema errors under `errors` with
`valid: false`. `--all` emits `{"ok": bool, "results": [...]}`;
`--list-schemas --json` emits `{"ok": true, "schemas": [...]}`.

## Exit codes (stable)

| code | meaning |
|---|---|
| 0 | every requested document is valid |
| 1 | a document is invalid |
| 2 | usage or input error (missing file, unreadable JSON, missing dependency) |

## Backs the MCP tool

`validate_workpaper` in [maxed-mcp](https://github.com/maxed-oss/maxed-mcp),
which pipes the document to `validate.py - --schema <name> --json`. Point
maxed-mcp at a checkout with `CPA_WORKPAPER_SPEC_DIR`.
