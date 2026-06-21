# Changelog

All notable changes to the CPA Workpaper Spec are documented here. The spec
follows [Semantic Versioning](https://semver.org/); the schema version is
carried in every document as `specVersion`.

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
