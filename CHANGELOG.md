# Changelog

All notable changes to the CPA Workpaper Spec are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the spec
follows [Semantic Versioning](https://semver.org/); the schema version is
carried in every document as `specVersion`. See [`docs/VERSIONING.md`](docs/VERSIONING.md)
for how versions and changes are managed.

## [Unreleased]

This release adds the `workpaper` entity (the spec's namesake working file) and
expands the tooling and proof-of-conformance around the vocabulary. The change
is additive: every document that validated against the v0.1 schemas before still
validates.

### Added
- **Normative spec document** (`SPEC.md`): the conformance rules for documents,
  producers, consumers, and validators, stated with RFC 2119 keywords. It names
  the JSON Schema files as its machine-readable form and the conformance suite as
  its runnable definition, and is cross-linked from the README. A test
  (`tests/test_spec_doc.py`) keeps the spec's required-field table in lockstep
  with the schemas.
- **`workpaper` schema** (`schema/v0.1/workpaper.schema.json`): a documented
  working file (lead schedule, reconciliation, supporting schedule, memo,
  calculation, confirmation, checklist) with a sign-off lifecycle, preparer /
  reviewer references, source documents, links to the request-list items it
  depends on, and an optional recorded tie-out. A worked example ships in
  `examples/v0.1/`, and both reference validators recognize the schema.
- **JavaScript / Ajv validator** (`validator-js/`) so JS and Node teams can
  target the exact same schemas as the Python validator, with a matching CLI
  (`cpa-workpaper-validate`) and `node --test` suite.
- **Conformance suite** (`conformance/`): a manifest-driven corpus of 27
  valid/invalid fixtures (including workpaper cases) plus a runner
  (`conformance/run.py`). Both the Python and JavaScript validators run the same
  manifest, proving the two implementations agree. Third parties can run the
  suite to demonstrate their own implementation conforms.
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
