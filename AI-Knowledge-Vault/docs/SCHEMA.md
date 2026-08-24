# Schema reference

Machine-readable copies live in `schemas/*.schema.json` and `schemas/enums.json`,
generated from `scripts/vaultlib/schema.py` (the single source of truth) by
`vault.py init`.

## Identifiers

Format: `<type>-YYYYMMDD-<hex>`; runs add a time component.

```
claim-20260812-a91c42        source-20260812-b77d11
run-20260812-113901-f0a2     review-20260812-4e6728
```

The id is stable and independent of the filename. Filenames are
`<id>--<slug>.md` so a record stays findable if its title changes — rename
freely; the id is what everything references.

## Common fields

| Field | Required | Type | Notes |
|---|---|---|---|
| `id` | yes | id | stable, unique, filesystem-safe |
| `type` | yes | enum | source, claim, entity, decision, artifact, project, run, review |
| `title` | yes | string | for a claim, this *is* the proposition |
| `created_at`, `updated_at` | yes | ISO-8601 | with timezone offset |
| `trust_level` | yes | enum | `trusted`, `internal`, `untrusted`, `quarantined` |
| `run_id` | no | ref(run) | the run that produced it |
| `tags` | no | list | free-form |
| `demo` | no | bool | `true` marks synthetic demo data |

## Uncertainty vocabulary

| `status` | Meaning |
|---|---|
| `unknown` | recorded, not yet assessed |
| `candidate` | drafted; not verified; the default for anything new |
| `verified` | passed the review gate with an approval |
| `disputed` | conflicting evidence exists; both sides retained |
| `rejected` | reviewed and found unsupported; kept as history |
| `superseded` | replaced by a newer record that points back to it |

These are never collapsed. A candidate claim is not "probably true".

## Claim

```yaml
id: claim-20260812-a91c42
type: claim
title: Median API latency decreased from 420 ms to 180 ms in June 2026
status: candidate
created_at: 2026-08-12T09:35:00-05:00
updated_at: 2026-08-12T09:35:00-05:00
trust_level: internal
sources:            # REQUIRED - a claim with no source cannot be verified
  - source-20260812-b77d11
source_quality: primary          # primary | secondary | tertiary |
                                 # self-reported | ai-generated | unknown
evidence_strength: high          # none | weak | moderate | high
verification_status: unverified  # unverified | verifying | verified |
                                 # failed | not-applicable
review_status: pending           # not-required | pending | in-review |
                                 # approved | rejected | disputed
reviewed_by: []
supports: []
contradicts: []
supersedes: []
superseded_by: []
entities: []
projects: []
related_to: []
run_id: run-20260812-113901-f0a2
```

Validation rules specific to claims:
- `sources` must be non-empty and every id must exist.
- `status: verified` or `verification_status: verified` requires
  `review_status: approved`. Hand-editing this is a FAIL, not a warning.
- `trust_level: trusted` without an approved review is a WARN.
- `evidence_strength: high` with `source_quality: ai-generated`,
  `self-reported`, or `unknown` is a WARN — the evidence is overstated.
- Citing a quarantined source is a FAIL.

## Source

Adds `content_hash` (`sha256:<64 hex>`), `origin`, `media_type`,
`extraction_status`, `security_status`, `security_findings`, `version`,
`previous_version`, `ingested_at`, `stored_path`, `byte_size`,
`locally_available`.

`extraction_status` is the honesty field:

| Value | Meaning |
|---|---|
| `extracted` | a real parser ran and produced the text shown |
| `stored-only` | bytes kept deliberately without extraction |
| `unsupported` | no parser exists for this format — **no text was read** |
| `failed` | a parser existed and errored |

Never set `extracted` without a parser. `.md`, `.txt`, `.json`, `.csv` are
parsed; everything else is hashed and stored with `unsupported`.

## Review

`target` (the reviewed record), `reviewer`, `reviewer_role`, `independent`,
`checks`, `findings`, `decided_at`, and `status` — one of `approved`,
`rejected`, `disputed`, `needs-more-evidence`. Reviews are append-oriented:
a later review does not erase an earlier one.

## Run

`objective`, `trigger`, `started_at`, `completed_at`, `agent`, `skill`,
`inputs`, `records_read`, `records_created`, `records_modified`,
`validation_result`, `review_result`, `warnings`, `errors`, `retry_count`,
`final_status`, and optionally `tokens_used` / `cost_usd`.

A run record is written as `status: running` *before* the work starts, so
records created during the run can reference it and so an interrupted run
still leaves evidence. Secrets are scrubbed from run logs automatically —
but never write one in the first place.

## Relationships

`SUPPORTS`, `CONTRADICTS`, `SUPERSEDES`, `DERIVED_FROM`, `MENTIONS`,
`RELATED_TO`, `PART_OF`, `PRODUCED_BY`, `REVIEWED_BY`, `DUPLICATES`.

Edges are derived from frontmatter fields, so the Markdown stays the single
source of truth:

| Field | Edge |
|---|---|
| `supports` | SUPPORTS |
| `contradicts` | CONTRADICTS |
| `supersedes` / `superseded_by` | SUPERSEDES |
| `sources`, `derived_from` | DERIVED_FROM |
| `entities` | MENTIONS |
| `projects` | PART_OF |
| `run_id` | PRODUCED_BY |
| `target` (review) | REVIEWED_BY |
| `related_to` | RELATED_TO |
| `duplicates` | DUPLICATES |

Forbidden by validation: dangling targets, self-edges (except RELATED_TO),
a pair with both SUPPORTS and CONTRADICTS, and supersession cycles.

## Adding a field

1. Edit `SCHEMAS` in `scripts/vaultlib/schema.py`.
2. Run `vault.py init` to regenerate `schemas/*.json`.
3. Run `vault.py validate` — unknown fields are reported as WARN, so
   existing records tell you exactly what needs backfilling.
