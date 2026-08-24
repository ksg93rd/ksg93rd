---
name: verify-source
description: Check that a source is intact, available, correctly classified, and actually supports what cites it. Use when auditing evidence or before relying on a source.
---

# Skill: verify-source

**OBJECTIVE**
Establish that a source is what the vault says it is.

**REQUIRED INPUTS**
A source id.

**PROCESS**
1. `vault.py show <source-id>` — read `content_hash`, `origin`,
   `extraction_status`, `security_status`, `version`.
2. Confirm the stored bytes exist at `stored_path` and are locally available.
3. Recompute the hash; a mismatch means the stored file changed after ingestion.
4. Check `extraction_status`. If `unsupported` or `failed`, no text was read —
   any claim quoting it is unfounded.
5. `vault.py related <source-id>` — inspect every claim citing it and confirm
   the source supports each one.

**VALIDATION**
Hash matches, file readable, and every citing claim has a verdict.

**FAILURE BEHAVIOUR**
- Hash mismatch → do not overwrite. Record a new version with `--revises` and
  keep the old evidence.
- File unavailable (iCloud placeholder) → report; never assume contents.
- Source quarantined → every citing claim must be rejected or re-sourced.

**STOP CONDITION**
A verdict exists for the source and for each citation.

**EXPECTED OUTPUT**
Availability, hash status, extraction honesty, and per-citation verdicts.
