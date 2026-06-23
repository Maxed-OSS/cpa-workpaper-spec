# CPA Workpaper Spec, v0.1 (normative)

This is the normative specification for the CPA Workpaper Spec. The JSON Schema
files under [`schema/v0.1/`](schema/v0.1) are the machine-readable form of the
rules stated here; where prose and schema appear to differ, the schema is
authoritative for structural validation and this document is authoritative for
the conformance requirements that schema cannot express.

For an explanatory walkthrough of the model (with diagrams) see
[`docs/MODEL.md`](docs/MODEL.md). For the versioning and change process see
[`docs/VERSIONING.md`](docs/VERSIONING.md).

## 1. Terminology

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as
described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals.

- **Document**: a single JSON object that claims to be an instance of one of the
  entity schemas in this spec.
- **Entity**: one of the seven named shapes: `engagement`, `workpaper`,
  `close-checklist`, `tax-prep`, `engagement-letter`, `request-list-item`, and
  the shared `common` definitions.
- **Producer**: software that emits documents.
- **Consumer**: software that reads documents.
- **Validator**: software that decides whether a document conforms to a named
  entity schema.

## 2. Scope

This spec defines the *shapes* of, and the interoperability rules for, the common
artifacts of CPA work. It is a vocabulary for describing and exchanging those
artifacts, not an engine for producing or computing them.

The following are explicitly out of scope and a conformant implementation MUST
NOT read any such meaning into the spec:

- Identity, authentication, and authorization.
- Calculation, derivation, or automation of any figure or state.
- Storage, transport, and persistence.
- Jurisdiction-specific tax rules. Form numbers and the like are carried as
  opaque labels only.

All example and fixture data in this repository is synthetic.

## 3. Document conformance

A document is a **conformant `<entity>` document** if and only if it validates
against `schema/v0.1/<entity>.schema.json` under a JSON Schema draft 2020-12
validator with the cross-file `$ref`s in [`schema/v0.1/`](schema/v0.1) resolved,
and it additionally satisfies the rules in this section.

1. Every document MUST carry a `specVersion` field whose value is the version of
   this spec it targets. For this spec that value is exactly `"0.1"`.
2. Every document MUST carry a stable `id`.
3. Every entity schema sets `additionalProperties: false`. A conformant document
   MUST NOT carry properties beyond those the schema defines. Producers that need
   to attach private data MUST do so out of band, not by adding fields to a
   document they label as conforming.
4. The REQUIRED fields per entity are:

   | Entity              | Required fields                                                       |
   | ------------------- | -------------------------------------------------------------------- |
   | `engagement`        | `specVersion`, `id`, `clientId`, `track`, `title`, `status`          |
   | `workpaper`         | `specVersion`, `id`, `engagementId`, `title`, `kind`, `status`       |
   | `close-checklist`   | `specVersion`, `id`, `engagementId`, `period`, `status`, `tasks`     |
   | `tax-prep`          | `specVersion`, `id`, `engagementId`, `taxYear`, `returnType`, `currentStage` |
   | `engagement-letter` | `specVersion`, `id`, `clientId`, `track`, `scope`, `fee`, `status`   |
   | `request-list-item` | `specVersion`, `id`, `label`, `itemType`, `status`                   |

## 4. Enumerated values

Several fields are closed enumerations (for example a workpaper `status`, a
tax-prep `currentStage`, a request-list `itemType`). These enumerations are
normative.

- A producer MUST NOT emit a value outside the schema enumeration for a closed
  field. Where the vocabulary cannot express a real-world value, the schema
  provides an `other` member (for example `workpaper.kind`); producers SHOULD use
  `other` together with a human-readable label rather than inventing a new
  enumeration value.
- A consumer MUST reject, or treat as invalid, a document carrying an
  out-of-enumeration value for a closed field.
- Lifecycle enumerations (the `status` and `currentStage` fields) define a
  canonical order. A workflow MAY skip forward over states, but a producer MUST
  NOT rename or reorder the states. Consumers SHOULD treat an unknown ordering as
  an error rather than guessing.

## 5. Recorded, not derived

Every figure and flag in a document is a **recorded assertion** by the producer,
not a value the spec computes or verifies. The clearest example is a workpaper
`tieOut`: the `balance`, `supportingTotal`, and `agrees` flag are what the
preparer or reviewer asserts.

- A consumer MUST NOT assume any figure has been validated by the spec or by the
  producer's having emitted it.
- A consumer MUST NOT treat `agrees: true` (or any similar flag) as proof that
  two figures are equal; it is an assertion to be trusted or independently
  re-checked by the consumer, not by this spec.

## 6. Linking between documents

Documents reference one another by id, not by embedding:

- `engagementId`, `clientId`, `engagementLetterId`, `requestItemIds`,
  `openItemIds`, and similar fields hold the `id` of another document or party.
- The spec does NOT require referential integrity across a document set: a
  reference MAY point at an id the consumer has not seen. Consumers SHOULD treat a
  dangling reference as a data condition to surface, not as a validation failure
  of the referencing document.

## 7. Producer and consumer conformance

- A **conformant producer** MUST emit only documents that satisfy Section 3 for
  the entity it claims to emit, MUST set `specVersion` to a version it actually
  targets, and MUST honor the enumeration rules of Section 4.
- A **conformant consumer** MUST validate a document against the named entity
  schema before relying on it, MUST honor Sections 4, 5, and 6, and MUST NOT
  silently discard a document solely because it carries OPTIONAL fields the
  consumer does not understand.
- A **conformant validator** MUST accept every `valid` case and reject every
  `invalid` case in the conformance corpus (Section 8). An implementation that
  does so MAY describe itself as conforming to CPA Workpaper Spec v0.1.

## 8. Conformance corpus

[`conformance/`](conformance) is the runnable definition of conformance: a
manifest of synthetic documents, each tagged with the entity schema it targets
and whether a conformant validator MUST accept or reject it. Both reference
validators in this repository run the same manifest, which proves they agree.

To demonstrate conformance, an independent implementation MUST run the manifest
in [`conformance/manifest.json`](conformance/manifest.json) and reproduce its
accept/reject outcome for every case. See
[`conformance/README.md`](conformance/README.md) for the procedure.

## 9. Versioning and extensions

- `specVersion` identifies the schema version a document targets. A consumer MUST
  NOT validate a document against a `schema/<version>/` directory other than the
  one its `specVersion` names.
- Breaking changes introduce a new `schema/<version>/` directory; existing
  documents continue to validate against the version they were authored for. The
  full policy is in [`docs/VERSIONING.md`](docs/VERSIONING.md).
- There is no in-band extension mechanism in v0.1. Because every entity sets
  `additionalProperties: false`, private extensions MUST be carried out of band
  (Section 3, rule 3).
