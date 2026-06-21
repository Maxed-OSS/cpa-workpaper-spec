# Conformance suite

This directory holds a **conformance corpus** for the CPA Workpaper Spec: a set
of synthetic documents, each paired with the schema it targets and whether a
conformant validator must **accept** (`valid`) or **reject** (`invalid`) it.

The point of the suite is to give "conformant" a single, runnable meaning. Both
reference validators in this repo (Python and JavaScript) run the same manifest,
which proves they agree. Any third-party implementation can run the same corpus
to demonstrate conformance.

## Layout

```
manifest.json        The list of cases: { file, schema, expect, note }.
suite/valid/         Documents that MUST validate.
suite/invalid/       Documents that MUST be rejected.
run.py               Runner using the reference Python validator.
```

Each manifest case looks like:

```json
{ "file": "suite/valid/engagement-minimal.json", "schema": "engagement", "expect": "valid", "note": "Only the six required fields." }
```

## Running it

With the reference Python validator (uses `validator/validate.py`):

```bash
python3 conformance/run.py        # summary only
python3 conformance/run.py -v     # print every case
```

The same manifest is also executed by both test suites:

```bash
python3 -m pytest -q                       # Python: tests/test_schemas.py
cd validator-js && npm install && npm test # JavaScript: node --test
```

Exit code is `0` only when every fixture behaves exactly as the manifest
requires.

## Targeting it from your own implementation

If you build a validator (in any language) you can prove conformance by:

1. Loading the schemas from `schema/v0.1/`.
2. For each case in `manifest.json`, validating the named `file` against the
   named `schema`.
3. Asserting that your validator **accepts** every `expect: "valid"` case and
   **rejects** every `expect: "invalid"` case.

All fixture data is synthetic. Contributions that add coverage are welcome; see
[`docs/VERSIONING.md`](../docs/VERSIONING.md) for the change process (every new
fixture must be listed in `manifest.json`).
