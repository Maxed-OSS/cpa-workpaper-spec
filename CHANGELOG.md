# Changelog

All notable changes to the CPA Workpaper Spec are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the spec
follows [Semantic Versioning](https://semver.org/); the schema version is
carried in every document as `specVersion`. See [`docs/VERSIONING.md`](docs/VERSIONING.md)
for how versions and changes are managed.

## [Unreleased]

No normative schema changes. The spec surface (the schemas under
`schema/v0.1/`) is unchanged; documents that validated before still validate.
This release expands the tooling and proof-of-conformance around the spec.

### Added
- **JavaScript / Ajv validator** (`validator-js/`) so JS and Node teams can
  target the exact same schemas as the Python validator, with a matching CLI
  (`cpa-workpaper-validate`) and `node --test` suite.
- **Conformance suite** (`conformance/`): a manifest-driven corpus of 23
  valid/invalid fixtures plus a runner (`conformance/run.py`). Both the Python
  and JavaScript validators run the same manifest, proving the two
  implementations agree. Third parties can run the suite to demonstrate their
  own implementation conforms.
- **Versioning and RFC process** doc (`docs/VERSIONING.md`) describing SemVer
  policy, side-by-side schema versions, and the lightweight change process.
- A continuous-integration workflow (`.github/workflows/ci.yml`) that runs the
  Python suite across multiple Python versions, the JavaScript suite across
  multiple Node versions, the conformance runner, and an OpenAPI lint/build.
- Expanded README install/usage instructions for both validators and the
  conformance suite.

## [0.1.0] - 2026-06-21

Initial public release.

### Added
- Five entity schemas (JSON Schema, draft 2020-12):
  - `engagement` - the top-level container for a body of client work.
  - `close-checklist` - monthly-close tasks plus the open-items loop.
  - `tax-prep` - an ordered tax-preparation stage model.
  - `engagement-letter` - structured scope/fee/responsibility terms.
  - `request-list-item` - a single PBC ("prepared by client") request.
- A shared `common` definitions schema (money, dates, person refs, periods,
  attachments, notes, service tracks).
- A small OpenAPI 3.1 description of a read-oriented HTTP surface over the vocabulary.
- One worked example document per entity schema.
- An offline validator (`validator/validate.py`) and a pytest suite.
