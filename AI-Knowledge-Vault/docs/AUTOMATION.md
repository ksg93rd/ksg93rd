# Automation readiness

## The rule

**Do not automate an unreliable manual workflow.** Automation multiplies
whatever the workflow already does, including its mistakes — and an automated
mistake arrives at 3 a.m. with nobody reading the output.

Before scheduling anything, prove by hand, repeatedly:

- [x] ingest — hashing, deduplication, revisions
- [x] validate — PASS/WARN/FAIL with remediation
- [x] review — the gate blocks what it should block
- [x] commit — provenance recorded
- [x] search — records are retrievable
- [x] recover — a backup was restored and validated

All six are demonstrated by the acceptance-test run in `70-runs/` and by
`tests/test_vault.py` (55 tests).

## Status: prepared, not enabled

No recurring schedule is installed. **Recurring automation requires explicit
human authorization** (`.claude/rules/human-gate.md`). The candidates below are
specified and ready; each still needs someone to turn it on.

| Job | Purpose | Suggested cadence | Trigger |
|---|---|---|---|
| inbox triage | ingest and screen everything in `00-inbox/` | hourly on weekdays | files present in `00-inbox/` |
| vault health check | catch drift, staleness, unavailable files | daily | schedule |
| stale source review | flag sources older than the freshness window whose claims are relied upon | weekly | schedule |
| unresolved claims | report `pending` reviews and `disputed` claims | weekly | schedule |
| index rebuild | keep search current after bulk changes | daily, or on staleness | `index_is_stale()` |
| backup validation | create a backup and verify it restores | daily | schedule |

## Required specification for any scheduled job

Every job must declare all eight before it is enabled:

1. **purpose** — the one outcome it exists for
2. **scope** — exactly which paths and record types it may touch
3. **trigger** — schedule or condition
4. **permissions** — least privilege; read-only wherever possible
5. **retry limit** — default 3 equivalent failures
6. **logging** — a RUN record every time, with secrets scrubbed
7. **stop condition** — including how it stops unsuccessfully
8. **failure handling** — the class of failure and the response

## Hard limits for unattended runs

- **Never auto-approve.** `features.auto_approve` must stay `false`. An
  unattended process may draft, screen, validate, link, and report — it may not
  decide that something is true.
- **Never auto-resolve a contradiction.** Mark `disputed` and escalate.
- **Never ingest from an unavailable vault.** Check availability first and
  abort if placeholders exist; a partial source set produces confidently wrong
  answers.
- **Never modify security configuration** — `config/trust-policy.yaml`,
  `.claude/**`, `CLAUDE.md`, `scripts/**`.
- **Never delete.** Supersede and archive.
- **Stop on repeated failure.** Three equivalent failures ends the job and
  reports a root cause; it does not retry forever.

## Sketch: nightly health check

```bash
#!/bin/bash
set -euo pipefail
VAULT="$HOME/Library/Mobile Documents/com~apple~CloudDocs/AI-Knowledge-Vault"
cd "$VAULT"
brctl download "$VAULT" || true          # availability first
python3 scripts/vault.py health-check --json > "indexes/last-health.json" || true
python3 scripts/vault.py rebuild-index
python3 scripts/vault.py graph-export
python3 scripts/vault.py validate || true   # report, never auto-fix
python3 scripts/vault.py status
python3 scripts/vault.py backup --label nightly
```

Install with `launchd` (a `LaunchAgent` plist), not `cron` — launchd handles a
sleeping Mac correctly. Log to a file, read the log, and only then consider
increasing the cadence.

## Before enabling anything

- [ ] the manual workflow has run cleanly for a week
- [ ] a human authorized this specific job
- [ ] the job writes a RUN record every execution
- [ ] failure output reaches a human who will actually read it
- [ ] the job cannot approve, delete, or modify security configuration
- [ ] a restore drill has been completed in the last month
