---
name: vault-health-check
description: Verify vault structure, index freshness, file availability, git provenance, and backups. Use routinely and after any incident.
---

# Skill: vault-health-check

**OBJECTIVE**
Answer one question honestly: is this vault currently trustworthy?

**REQUIRED INPUTS**
None.

**PROCESS**
1. `python3 scripts/vault.py health-check`
2. `python3 scripts/vault.py validate`
3. `python3 scripts/vault.py status`
4. Read the failures in order: availability → structure → validation →
   provenance → backup.

**VALIDATION**
All health checks PASS and validation is PASS or WARN with known, recorded
warnings.

**FAILURE BEHAVIOUR**
- Files unavailable (iCloud placeholders) → download them before any autonomous
  processing; an incomplete source set produces wrong answers.
- `git-metadata-outside-sync` fails → a `.git` directory has appeared inside
  the synchronized folder; see `docs/VERSION-CONTROL.md` before touching it.
- No backup → run `backup-vault` immediately.
- Validation FAIL → fix records, never delete them.

**STOP CONDITION**
Every check passes, or each failure has a recorded owner and remediation.

**EXPECTED OUTPUT**
Per-check PASS/FAIL with remediation, plus the overall health verdict.
