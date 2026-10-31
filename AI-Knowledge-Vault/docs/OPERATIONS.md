# Operations

## Daily loop

```bash
python3 scripts/vault.py health-check     # is the vault trustworthy right now?
python3 scripts/vault.py ingest 00-inbox  # process everything waiting
python3 scripts/vault.py contradictions   # adjudicate conflicts
python3 scripts/vault.py validate         # fix what it reports
python3 scripts/vault.py status           # regenerate STATUS.md
```

The `daily-triage` Skill walks the same loop with decision guidance.

## Command reference

| Command | Purpose |
|---|---|
| `doctor` | environment preflight; works with no vault at all |
| `init` | create or complete the structure; never overwrites |
| `ingest PATH` | full pipeline: hash → dedupe → screen → normalize → source record |
| `new TYPE TITLE` | create a claim/entity/decision/project/artifact by hand |
| `validate` | PASS/WARN/FAIL with per-issue remediation |
| `search QUERY` | full-text + metadata search |
| `show ID` | print one record |
| `related ID` | traverse relationships |
| `contradictions` | scan for conflicting or duplicate claims |
| `review ID DECISION` | run the review gate |
| `rebuild-index` | rebuild `indexes/vault.db` |
| `graph-export` | rebuild `indexes/graph.json` |
| `status` | write `STATUS.md` + `indexes/status.json` |
| `health-check` | 13 structural and operational checks |
| `backup` | create and immediately verify a backup |
| `verify-backup ARCHIVE` | prove an archive is restorable |
| `restore ARCHIVE DEST --yes` | restore into an empty directory |
| `provenance ID` | evidence chain + git history |
| `commit -m` / `log` | git history |

Global flags: `--vault PATH` and `--json`, accepted before or after the
subcommand. Exit codes: `0` ok, `1` failed check, `2` error.

## Useful queries

```bash
vault.py search --type claim --review pending      # the review queue
vault.py search --type claim --status disputed     # open conflicts
vault.py search --trust quarantined                # security attention
vault.py search "latency" --type claim             # topic search
vault.py search --no-demo                          # exclude synthetic demo data
vault.py related <id> --depth 2                    # neighbourhood
```

## Ingesting

```bash
vault.py ingest report.md --origin "https://example.com/report" --extract-claims
vault.py ingest updated.md --revises source-20260812-b77d11
vault.py ingest 00-inbox/                          # a whole directory
```

`--extract-claims` uses a deliberately dumb heuristic: it proposes declarative
sentences as **candidates**. It does not understand the document. Everything it
produces is `candidate` / `unverified` / `pending` and must go through review.

Parsed formats: `.md`, `.txt`, `.json`, `.csv`. Anything else is hashed and
stored with `extraction_status: unsupported` — no text is read and none is
claimed.

## Reviewing

```bash
vault.py review <claim-id> approved  --reviewer alice --author bob \
        --rationale "figure appears verbatim in the cited source"
vault.py review <claim-id> disputed  --reviewer alice --rationale "conflicts with X"
vault.py review <claim-id> rejected  --reviewer alice --rationale "source does not say this"
vault.py review <claim-id> needs-more-evidence --reviewer alice
```

The gate blocks approval when: a required field is missing, the claim has no
source, a cited source is missing or quarantined, an undeclared contradiction
exists, or a high-risk record's author and reviewer are the same actor.

`--force` overrides blockers. The override is written into the review record
and stays visible forever. Use it deliberately, never to "get past" a gate.

## Failure handling

| Class | Response |
|---|---|
| TRANSIENT | retry safely, at most 3 equivalent attempts |
| VALIDATION | correct the candidate and re-run `validate` |
| SECURITY | quarantine, stop propagation, do not extract claims |
| PERMISSION | stop and request authorization |
| DATA CONFLICT | preserve both states, mark `disputed`, escalate |
| SYSTEMIC | stop retrying, identify the root cause, report |

Default retry limit is 3 equivalent failures. Do not loop.

## iCloud availability

A cloud-only file is *unavailable*, not empty. The vault refuses to interpret a
zero-byte or unreadable file as empty content: ingestion fails with a clear
message, `load_all` returns it as an error, and `health-check` reports
`files-locally-available`.

Before any autonomous processing, make the vault locally available:

```bash
brctl download "$HOME/Library/Mobile Documents/com~apple~CloudDocs/AI-Knowledge-Vault"
```

or in Finder: right-click the folder → **Download Now**. Turning off
"Optimize Mac Storage" for this folder is the durable fix. **Dependable
autonomous processing requires the active vault to remain locally available on
the Mac.**

## Housekeeping

- Rebuild indexes after any bulk edit or restore.
- Back up before migrations, bulk edits, or anything risky.
- Keep `STATUS.md` current; it is the fastest way to see drift.
- Never hand-edit `indexes/*` or `STATUS.md`.
