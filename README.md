# cpa-workpaper-spec

An open, versioned **vocabulary** for the common units of CPA work - expressed as
JSON Schema (draft 2020-12) plus a small OpenAPI description.

It defines firm-agnostic shapes for:

- **Engagement** - a bounded body of client work over a period.
- **Monthly-close checklist** - close tasks plus the *open-items loop*.
- **Tax-prep stage model** - an ordered return-preparation workflow.
- **Engagement-letter config** - structured scope / fee / responsibility terms.
- **Request-list item** - a single "prepared by client" (PBC) request.

This is an **interoperability spec, not an engine.** It standardizes how to
*describe* these things so two systems can exchange them. It does not compute
taxes, reconcile ledgers, or run any workflow.

## Why

Every practice-management tool, accounting platform, and home-grown spreadsheet
re-invents the same nouns - engagements, close checklists, request lists,
engagement-letter terms - with subtly different shapes. There is no shared,
public vocabulary, so integrating any two systems means a bespoke mapping every
time.

`cpa-workpaper-spec` is that shared vocabulary: a small set of schemas anyone can
target, version against, and validate documents with. If your close tool and
your tax tool both speak it, they interoperate for free.

## What's in here

```
schema/v0.1/            JSON Schema (draft 2020-12) - the normative spec
  common.schema.json        shared $defs (money, dates, person refs, …)
  engagement.schema.json
  close-checklist.schema.json
  tax-prep.schema.json
  engagement-letter.schema.json
  request-list-item.schema.json
openapi/                Small OpenAPI 3.1 surface over the vocabulary
examples/v0.1/          One worked, synthetic example per schema
validator/validate.py   Offline validator CLI
tests/                  pytest suite (schemas, examples, negative cases)
docs/MODEL.md           Long-form explanation of the model
```

See [`docs/MODEL.md`](docs/MODEL.md) for the full data model and how the
entities relate.

## Install

Requires Python 3.9+.

```bash
python3 -m pip install -r requirements.txt
# or:  make install
```

The only runtime dependency is [`jsonschema`](https://pypi.org/project/jsonschema/);
`pytest` is used for the test suite.

## Usage

Validate all bundled examples:

```bash
python3 validator/validate.py --all
# or:  make validate
```

Validate your own document against a named schema:

```bash
python3 validator/validate.py path/to/my-engagement.json --schema engagement
```

List the known schema names:

```bash
python3 validator/validate.py --list-schemas
# engagement, close-checklist, tax-prep, engagement-letter, request-list-item, common
```

The validator resolves all cross-schema `$ref`s **offline** - no network access
is needed.

### Example document

A minimal valid `request-list-item` (see [`examples/v0.1/`](examples/v0.1) for
the full set):

```json
{
  "specVersion": "0.1",
  "id": "rli_pyreturn",
  "engagementId": "eng_brightside_2025",
  "label": "Prior-year tax return (2024)",
  "itemType": "document",
  "category": "prior-year",
  "status": "received",
  "required": true
}
```

### Using the schemas in your own validator

The schemas are plain JSON Schema draft 2020-12 and work with any compliant
validator (Ajv, `python-jsonschema`, `jsonschema-rs`, etc.). Each schema has a
stable `$id` under `https://cpa-workpaper-spec.org/schema/v0.1/`. Cross-file
`$ref`s use bare filenames (e.g. `common.schema.json#/$defs/money`), so loading
the `schema/v0.1/` directory into a ref store resolves everything.

## Versioning

Documents carry `specVersion` (currently `"0.1"`). The spec follows
[SemVer](https://semver.org/); a breaking change adds a new `schema/<version>/`
directory so existing documents keep validating. See [`CHANGELOG.md`](CHANGELOG.md).

## Scope and non-goals

In scope: the *shapes* of CPA-work artifacts and a reference HTTP surface.

Out of scope (intentionally): identity/auth, any calculation or automation,
storage/transport, and jurisdiction-specific tax logic. All example data is
synthetic.

## Contributing

Issues and pull requests are welcome. Please:

1. Keep changes firm-agnostic and free of any real client data.
2. Add or update an example for any schema change.
3. Run `make validate && make test` before opening a PR.

## License

[Apache-2.0](LICENSE). See [`NOTICE`](NOTICE).
