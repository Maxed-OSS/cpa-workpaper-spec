# Versioning and the change process

The CPA Workpaper Spec is meant to be a **living standard**: stable enough to
build on, but able to evolve as practices and tools converge. This document
describes how the spec is versioned and how changes are proposed and accepted.

## Semantic versioning

The spec follows [Semantic Versioning 2.0.0](https://semver.org/). The version
that a document conforms to is carried in its `specVersion` field.

For the spec, the three parts mean:

| Bump | Meaning | Examples |
| --- | --- | --- |
| **MAJOR** (`1.0.0`) | A change that can make a previously valid document invalid, or change the meaning of a field. | Removing a field, making an optional field required, removing an enum value, renaming a property, tightening a pattern. |
| **MINOR** (`0.2.0`) | A backward-compatible addition. Documents valid under the old version stay valid. | Adding an optional field, adding a new entity schema, adding a new enum value to an open-ended list, relaxing a constraint. |
| **PATCH** (`0.1.1`) | A clarification with no schema-behaviour change. | Fixing a typo in a `description`, correcting documentation, adding examples. |

Because the spec is pre-1.0, the surface may still move; we treat any
breaking change as a MAJOR bump even during `0.x` so that `specVersion`
remains a reliable compatibility signal.

## How versions live side by side

Schemas are published under a version directory: `schema/v0.1/`,
`schema/v0.2/`, and so on. A MAJOR (and, during `0.x`, any breaking) release
adds a **new** directory and leaves older ones in place. This means:

- Documents written for an older version keep validating against the schemas
  they were authored against.
- A consumer can support multiple versions by loading multiple schema
  directories and dispatching on the document's `specVersion`.
- The `$id` of every schema embeds its version, so references never collide
  across versions.

`specVersion` in `common.schema.json` is a `const`, so a document explicitly
declares the one version it targets and a validator will reject a mismatched
document early and clearly.

## The change process (lightweight RFC)

Changes are proposed as **RFCs** (Requests for Comments). The process is
deliberately small:

1. **Open an issue** describing the problem the change solves. Real-world
   interop pain ("system A and system B model the same thing differently")
   is the strongest motivation. Synthetic examples only; never include real
   client data.
2. **Draft the change** as a pull request. A complete proposal includes:
   - the schema edit(s),
   - at least one new or updated **example**,
   - at least one **conformance fixture** (valid and/or invalid) under
     `conformance/suite/` plus its `conformance/manifest.json` entry,
   - a **CHANGELOG** entry under an `## [Unreleased]` heading, classified as
     Added / Changed / Deprecated / Removed / Fixed,
   - the intended version bump (MAJOR / MINOR / PATCH) and why.
3. **Review.** Maintainers and interested implementers comment. The bar for
   acceptance is: does this make two independent systems more likely to
   interoperate, and is it firm-agnostic?
4. **Accept and release.** On merge, the change lands under `[Unreleased]`.
   When a version is cut, the `[Unreleased]` section is renamed to the new
   version with a date, and (for a breaking release) a new `schema/<version>/`
   directory is created.

## Compatibility guarantees

- We will not silently change the meaning of an existing field within a
  version. Such a change requires a MAJOR/breaking release and a new schema
  directory.
- Additive, backward-compatible changes (new optional fields, new schemas)
  may appear in MINOR releases within the same schema directory only when
  they cannot invalidate an existing document; otherwise they go to a new
  version directory.
- The reference validators (Python and JavaScript) and the conformance suite
  are released together with the schemas so that "conformant" has a single,
  runnable meaning per version.

## Deprecation

A field or value may be marked deprecated (in its `description`) one MINOR
release before it is removed in a MAJOR release. Deprecated items keep working
until the MAJOR release that removes them.
