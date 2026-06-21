# cpa-workpaper-spec

[![ci](https://github.com/maxed-oss/cpa-workpaper-spec/actions/workflows/ci.yml/badge.svg)](https://github.com/maxed-oss/cpa-workpaper-spec/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

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
conformance/            Manifest-driven conformance corpus + runner
validator/validate.py   Offline Python validator CLI
validator-js/           Offline JavaScript / Ajv validator CLI + tests
tests/                  pytest suite (schemas, examples, negative + conformance)
docs/MODEL.md           Long-form explanation of the model
docs/VERSIONING.md      SemVer policy + the change (RFC) process
CHANGELOG.md            Notable changes per version
```

See [`docs/MODEL.md`](docs/MODEL.md) for the full data model and how the
entities relate.

## Clone

```bash
git clone https://github.com/maxed-oss/cpa-workpaper-spec.git
cd cpa-workpaper-spec
```

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

## JavaScript / Ajv validator

JavaScript and Node teams can target the exact same schemas with the bundled
[Ajv](https://ajv.js.org/)-based validator in [`validator-js/`](validator-js):

```bash
cd validator-js
npm install

node cli.js --all                                  # validate every example
node cli.js ../my-engagement.json --schema engagement
node cli.js --list-schemas
npm test                                            # node --test suite
```

It mirrors the Python CLI's commands and exit codes, and resolves all
cross-schema `$ref`s offline. Both validators are run against the same
conformance corpus (below), so they are proven to agree.

### Using the schemas in your own validator

The schemas are plain JSON Schema draft 2020-12 and work with any compliant
validator (Ajv, `python-jsonschema`, `jsonschema-rs`, etc.). Each schema has a
stable `$id` under `https://cpa-workpaper-spec.org/schema/v0.1/`. These `$id`
URLs are the canonical identifiers and resolve to the published schema files
**once the spec is hosted at that domain**; until then (and for fully offline
use) load the local `schema/v0.1/` directory into your validator's ref store.
Cross-file `$ref`s use bare filenames (e.g. `common.schema.json#/$defs/money`),
so loading that directory resolves everything without network access. The
bundled Python and JavaScript validators do exactly this.

## Conformance suite

The [`conformance/`](conformance) directory is a manifest-driven corpus of
valid/invalid synthetic documents that gives "conformant" a single, runnable
meaning. Both reference validators run it, and you can run it against your own
implementation to demonstrate conformance.

```bash
python3 conformance/run.py -v       # run the suite with the Python validator
```

See [`conformance/README.md`](conformance/README.md) for the manifest format
and how to target it from any language.

## Versioning

Documents carry `specVersion` (currently `"0.1"`). The spec follows
[SemVer](https://semver.org/); a breaking change adds a new `schema/<version>/`
directory so existing documents keep validating. The full policy and the
lightweight change (RFC) process are in [`docs/VERSIONING.md`](docs/VERSIONING.md);
notable changes are recorded in [`CHANGELOG.md`](CHANGELOG.md).

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and
pull request: the Python suite across Python 3.9 / 3.11 / 3.13, the JavaScript
suite across Node 18 / 20 / 22, the conformance runner, an OpenAPI lint, and a
build check that every schema's cross-references resolve and both validators
accept all examples.

## Scope and non-goals

In scope: the *shapes* of CPA-work artifacts and a reference HTTP surface.

Out of scope (intentionally): identity/auth, any calculation or automation,
storage/transport, and jurisdiction-specific tax logic. All example data is
synthetic.

## Contributing

Issues and pull requests are welcome. Please:

1. Keep changes firm-agnostic and free of any real client data (synthetic only).
2. Add or update an example for any schema change.
3. Add or update a conformance fixture (and its `conformance/manifest.json`
   entry) so the change is covered by both validators.
4. Run `make all` (Python + JavaScript suites + conformance) before opening a PR.

See [`docs/VERSIONING.md`](docs/VERSIONING.md) for the change (RFC) process and
how the spec is versioned.

## License

[Apache-2.0](LICENSE). See [`NOTICE`](NOTICE).
