# Changelog

All notable changes to the AI Knowledge Vault are recorded here.
Format follows Keep a Changelog; versions follow semantic versioning.

## [1.0.0] — 2026-08-24

First working version. Every capability listed here was exercised end-to-end by
the acceptance test recorded as a RUN in `70-runs/`, and by 55 automated tests.

### Added

**Storage and structure**
- Vault layout: `00-inbox` … `90-archive`, plus `indexes/`, `schemas/`,
  `templates/`, `scripts/`, `config/`, `docs/`, `tests/`, `.claude/`.
- Vault-root resolution: `--vault` → `$VAULT_ROOT` → pointer file → macOS
  iCloud auto-detection → explicit refusal. Never invents an iCloud path.
- `scripts/install-icloud.sh`, which refuses to run off macOS and never
  overwrites an existing file.

**Records and schemas**
- Eight record types: source, claim, entity, decision, artifact, project, run,
  review, with stable ids independent of filenames.
- Schemas declared in `scripts/vaultlib/schema.py` and exported to
  `schemas/*.schema.json` + `schemas/enums.json` for human inspection.
- `yamlite`, a dependency-free YAML-subset reader/writer, so the vault runs on
  stock macOS Python with no `pip install`.
- Atomic record writes (temp file + `os.replace`), which matter in synced storage.

**Ingestion**
- Full pipeline: identify → hash → duplicate check → trust classification →
  security screen → normalize → source record → claim candidates → related
  search → relationship proposals → validation → review → commit.
- SHA-256 content hashing with deterministic normalization; identical content
  is never ingested twice.
- Source revisions via `--revises`: version N+1, prior version marked
  `superseded`, earlier evidence preserved.
- Parsers for `.md`, `.txt`, `.json`, `.csv`. Other formats are hashed and
  stored with `extraction_status: unsupported` — extraction success is never
  claimed falsely.

**Search and graph**
- SQLite FTS5 index at `indexes/vault.db`, fully rebuildable, with a substring
  fallback when FTS5 is unavailable and a hard fallback on malformed queries.
- `indexes/graph.json` with nodes, edges, `generated_at`, and `schema_version`;
  ten relationship types; dangling-edge, self-edge, and cycle detection.
- Deterministic index-staleness detection by fingerprinting the canonical file
  set rather than comparing timestamps.

**Security**
- Trust levels `trusted` / `internal` / `untrusted` / `quarantined`, configured
  in `config/trust-policy.yaml` with ordered origin rules.
- Ten prompt-injection heuristics, twelve secret patterns, and executable /
  malformed-content detection. Secrets are redacted in findings and scrubbed
  from run logs.
- Quarantine that isolates content, blocks claim extraction, fails validation
  when cited, and blocks the review gate.
- Protected paths that ingested content can never cause a write to, including
  refusal of any path resolving outside the vault root.

**Validation and review**
- Validation engine returning PASS/WARN/FAIL, every issue carrying a record, a
  reason, and a remediation. Covers frontmatter syntax, required fields, id
  uniqueness, enums, duplicate hashes, broken references, orphans, invalid
  edges, self-contradictions, supersession cycles, unreviewed-verified claims,
  stale indexes, malformed timestamps, and quarantine policy.
- Review gate: schema → source → critic → relationship → independence, then
  approve / reject / dispute / needs-more-evidence. Blocks self-approval of
  high-risk records and approval over an undeclared contradiction. `--force`
  overrides are recorded permanently.
- Contradiction engine proposing SUPPORTS / CONTRADICTS / SUPERSEDES /
  DUPLICATES / RELATED_TO / NO_RELATION. Newer is never assumed correct and
  nothing is deleted to simplify the graph.

**Provenance, observability, recovery**
- Git provenance with the git directory kept outside synchronized storage; no
  `.git` inside iCloud at all.
- RUN records written at start (`status: running`) so in-flight and interrupted
  runs both leave evidence.
- `STATUS.md` + `indexes/status.json`; a 13-point `health-check`.
- Backups of canonical files with a per-file hash manifest, immediate
  verification, tamper detection, and a restore that refuses to overwrite a
  populated vault.

**Claude Code integration**
- `CLAUDE.md` with durable rules only.
- Ten Skills: ingest-source, create-record, review-claim, verify-source,
  link-knowledge, check-contradictions, rebuild-index, vault-health-check,
  backup-vault, daily-triage.
- Nine subagents: researcher, source-verifier, critic, linker,
  security-reviewer, summarizer, schema-validator, contradiction-reviewer,
  project-librarian — each with purpose, inputs, outputs, allowed tools, write
  scope, forbidden actions, stop conditions, and escalation conditions.
- Five rules files: trust boundary, evidence and uncertainty, write safety,
  human gate, secret safety.

**Testing and documentation**
- 55 tests over temporary directories, covering all twelve required scenarios.
- Ten documents, README first in plain language.
- `scripts/seed-demo.py` producing clearly-marked synthetic demo data through
  the real pipeline.

### Known limitations

- **Prompt-injection screening is heuristic.** It reduces risk; it does not
  guarantee detection. The trust boundary is the real control.
- **Contradiction detection is lexical**, not semantic. It finds opposing
  wording, negation asymmetry, and conflicting figures on a shared subject. It
  will miss a contradiction expressed in entirely different words, and it will
  propose false positives. Every proposal requires review.
- **Claim extraction is a heuristic** over declarative sentences. It does not
  understand documents; output is always a candidate.
- **Semantic search is not implemented.** Deferred by design; keyword and
  metadata search need no API key and no network.
- **Only `.md`, `.txt`, `.json`, `.csv` are parsed.** PDFs and images are
  stored and hashed but not read, and the record says so.
- **Each Mac keeps its own git history** unless a shared remote is configured.
- **No automation is enabled.** Scheduled jobs are specified in
  `docs/AUTOMATION.md` and require explicit human authorization.
