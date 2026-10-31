# Architecture

## The lifecycle

```
CAPTURE → SECURITY SCREEN → NORMALIZE → CLASSIFY → HASH → DEDUPLICATE →
RETRIEVE CONTEXT → ROUTE → ANALYZE → DRAFT → VERIFY → REVIEW → COMMIT →
INDEX → LEARN → REPEAT
```

Each stage maps to code in `scripts/vaultlib/`:

| Stage | Module |
|---|---|
| capture, normalize, hash, deduplicate, extract | `ingest.py` |
| security screen, trust classification | `security.py` |
| retrieve context, search | `index.py` |
| analyze, relationship proposals | `contradiction.py` |
| verify, review gate | `review.py` |
| validation | `validate.py` |
| commit, provenance | `gitprov.py` |
| index / graph rebuild | `index.py`, `graph.py` |
| run logging | `runs.py` |
| observability | `status.py` |
| backup / recovery | `backup.py` |

## Layering

```
        Markdown + YAML frontmatter          ← AUTHORITATIVE
                    │
        ┌───────────┴───────────┐
        │                       │
  indexes/vault.db        indexes/graph.json   ← DERIVED, disposable
  (SQLite FTS5)           (nodes + edges)
        │                       │
        └───────────┬───────────┘
                    │
        STATUS.md, indexes/status.json         ← DERIVED, disposable
```

Deleting every derived file loses nothing. `rebuild-index` and `graph-export`
regenerate them from the Markdown. The reverse is never true: nothing is ever
written back from the database into a record.

## Storage responsibilities

| Concern | Provided by | Explicitly NOT provided by |
|---|---|---|
| Synchronization between devices | iCloud Drive | — |
| Version history, provenance | Git (metadata outside iCloud) | iCloud |
| Search | SQLite FTS5 (rebuildable) | iCloud |
| Relationships | `graph.json` (rebuildable) | iCloud |
| Authorization | The review gate + human gate rules | iCloud |
| Audit log | `70-runs/`, `80-reviews/`, git history | iCloud |
| Conflict resolution | Git + human review | iCloud's "keep both" dialog |

iCloud is a synchronization layer. It is not version control, not a
transactional database, not a search engine, and not an audit log.

## Canonical state vs. history

**Canonical (may be corrected or superseded)** — `10-claims/`, `30-entities/`,
`40-decisions/`, `50-artifacts/`, `60-projects/`.

**Append-oriented history (kept reconstructable)** — `20-sources/` (original
bytes in `20-sources/_files/`), `70-runs/`, `80-reviews/`,
`90-archive/`, `90-archive/quarantine/`, and git history.

Correction never destroys evidence. A revised source becomes version N+1 and
the prior version is marked `superseded` with `superseded_by` pointing forward.
Both remain on disk.

## Architecture decisions

**ADR-1 — Markdown + YAML frontmatter as the canonical format.**
Human-readable without any tooling, diffable in git, greppable, and portable.
A person can open a claim in TextEdit and understand it. Rejected: a database
as the primary store (opaque, not diffable, corruptible in a synced folder).

**ADR-2 — No third-party Python dependencies.**
macOS system Python has no PyYAML, and a vault that needs `pip install` to be
readable is not local-first. `vaultlib/yamlite.py` implements exactly the YAML
subset the vault writes, and the writer only emits that subset. Rejected:
PyYAML (install friction), JSON frontmatter (unreadable for humans).

**ADR-3 — Git metadata outside the synchronized folder.**
See `VERSION-CONTROL.md`. A `.git` directory inside iCloud invites index and
loose-object corruption when two Macs sync mid-write.

**ADR-4 — The index is disposable.**
SQLite in a synced folder risks corrupted journals. Since `vault.db` can be
rebuilt in seconds and is gitignored, corruption is an inconvenience, never a
loss. `journal_mode=DELETE` avoids stray `-wal` files.

**ADR-5 — Vault root is resolved, never hard-coded.**
`--vault` → `$VAULT_ROOT` → pointer file → macOS iCloud auto-detection → hard
refusal. The system never invents an iCloud path on a machine that has none.

**ADR-6 — Screening cannot be the security control.**
Heuristic prompt-injection detection catches known shapes and will miss novel
phrasing. The actual control is the trust boundary: source content is data and
is never executed as policy. Screening only decides where content is stored and
how loudly it is flagged.

**ADR-7 — Semantic search is deferred.**
Version 1 needs no embeddings, no API key, and no network. Keyword + metadata
search over FTS5 is sufficient and fully local. If embeddings are added they go
behind a feature flag with the keyword path retained as the fallback, and the
vector store never holds the only copy of anything.

## Execution escalation

`DIRECT ACTION → SKILL → ONE SPECIALIST AGENT → INDEPENDENT REVIEW →
MULTIAGENT WORKFLOW`

Escalate on risk, ambiguity, complexity, conflicting evidence, or irreversible
impact. A lookup is a direct action. Approving a security claim is an
independent review. Do not spend a multiagent workflow on a metadata edit.
