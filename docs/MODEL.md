# The CPA Workpaper Spec data model

This document explains the vocabulary the spec defines and how the entities
relate. The goal is a shared, firm-agnostic way to *describe* the common units
of CPA work so that two systems can exchange them without bespoke mapping.

The spec is a **vocabulary**, not an engine. It says nothing about how to
compute a tax liability, reconcile a ledger, or chase a client. It only defines
the shapes of the things those processes operate on.

## Entities at a glance

```
                         ┌──────────────────────┐
                         │      Engagement      │  the container
                         │  (tax | bookkeeping  │
                         │   | accounting | …)  │
                         └─────────┬────────────┘
              engagementId         │         engagementLetterId
        ┌──────────────────────────┼───────────────────────────┐
        │                          │                            │
        ▼                          ▼                            ▼
┌───────────────┐        ┌──────────────────┐         ┌──────────────────┐
│ CloseChecklist│        │     TaxPrep      │         │ RequestListItem  │
│  tasks +      │        │  ordered stage   │         │  one PBC ask     │
│  open-items   │        │  model + review  │         │  (doc/info/…)    │
│  loop         │        │  comments        │         └──────────────────┘
└───────────────┘        └──────────────────┘

      ┌──────────────────────────┐     ┌──────────────────────────┐
      │   EngagementLetter        │     │       Workpaper          │
      │   scope / fee / duties    │     │  lead schedule / recon / │
      │   (referenced by          │     │  memo, sign-off state,   │
      │    Engagement)            │     │  sources, optional       │
      └──────────────────────────┘     │  tie-out                 │
                                        └──────────────────────────┘
```

## Engagement

The **engagement** is the top-level container: a bounded body of professional
work for one client over one period. Its `track` (`tax`, `bookkeeping`,
`accounting`, `advisory`, `audit`, `other`) signals which downstream artifacts
apply - a bookkeeping engagement carries close checklists; a tax engagement
carries a tax-prep workflow. The engagement owns the lifecycle `status` and the
reporting `period`.

Everything else points back at an engagement by `engagementId`.

## Workpaper

A **workpaper** is a single documented working file that supports a position
taken in the engagement: a lead schedule, an account reconciliation, a
supporting schedule, a memo, a calculation, a confirmation, or a checklist
(`kind`). It carries its own sign-off lifecycle
(`not_started -> in_progress -> prepared -> reviewed -> finalized`, with
`reopened` for a finalized paper sent back), the `preparedBy` / `reviewedBy`
people and timestamps, the `sources` it relies on, and the `requestItemIds`
whose receipt it depends on, linking the client-side chase loop to the working
file.

A workpaper may also record a **tie-out**: the `balance` it supports, the
`supportingTotal` of the detail behind it, and an `agrees` flag. As everywhere
in the spec, these figures are *recorded, not derived*: the vocabulary carries
the preparer's and reviewer's assertions, it does not compute or verify them.

## Close checklist (and the open-items loop)

For a bookkeeping/accounting engagement, the books are closed one fiscal period
at a time. A **close checklist** holds:

- **tasks** - the concrete close steps (reconcile bank, post accruals, tie out
  the balance sheet, etc.), each with its own `status`.
- **open items** - the questions raised while doing the work. This is the
  *open-items loop*: an item moves `open -> awaiting_response -> answered ->
  resolved` (or `wont_fix`). A task can list the `openItemIds` that block it, so
  a checklist cannot be honestly "closed" while blocking questions are unresolved.

The open-items loop is the part most ad-hoc systems get wrong; modeling it
explicitly is a core reason this vocabulary exists.

## Tax-prep stage model

A **tax-prep** record advances a return through a canonical, ordered set of
stages:

```
gathering → in_preparation → in_review → awaiting_client_signature
          → ready_to_file → filed → sealed
```

`currentStage` is the single source of truth for where the return is; the
`stages` array carries per-stage timing and ownership. `reviewComments` capture
reviewer feedback that may gate sign-off (`info`, `question`, `must_fix`). A
workflow may skip stages, but it must not invent stage names - that is what
makes the model interoperable.

## Engagement-letter configuration

An **engagement letter** is the contract. This spec models the *terms*, not the
rendered prose: `scope` (services in/out), `fee` (model + amount + cadence), and
`responsibilities` (who does what). Keeping these structured lets a system
generate the prose, surface the fee in a quote, or check that work performed is
in scope - all from the same record.

## Request-list item

A **request-list item** is one thing the firm needs from the client (a.k.a. a
PBC, "prepared by client"). Each item has an `itemType` (`document`,
`information`, `confirmation`, `signature`, `access`) and runs a small chase
loop: `requested -> reminded -> received -> accepted` (or `rejected` / `waived`).
Request items are the upstream feeders for tax-prep `gathering` and for close
`open items`.

## Shared building blocks (`common.schema.json`)

To keep the entity schemas consistent, common types live in one place and are
referenced by `$ref`:

| Definition      | Purpose                                              |
| --------------- | ---------------------------------------------------- |
| `money`         | decimal-string amount + ISO-4217 currency            |
| `isoDate` / `isoDateTime` | RFC-3339 date / timestamp                  |
| `fiscalPeriod`  | a labeled start/end reporting period                 |
| `personRef`     | a stable id + display name (no identity system)      |
| `attachmentRef` | a reference to a document (not the bytes)            |
| `note`          | an authored free-text annotation                     |
| `serviceTrack`  | the engagement-track enumeration                     |

## Versioning

Every document carries `specVersion` (currently `"0.1"`). The spec follows
semantic versioning; breaking changes to a shape will bump the major/minor and a
new `schema/<version>/` directory will be added so old documents keep validating.

## What is intentionally out of scope

- Identity, authentication, and authorization.
- Calculation/automation of any kind (this is a vocabulary, not an engine).
- Storage, transport, and persistence concerns.
- Jurisdiction-specific tax logic (form numbers are carried as opaque labels).
