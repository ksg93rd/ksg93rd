---
name: backup-vault
description: Create and verify a backup of canonical vault files, and prove it can be restored. Use before migrations, bulk edits, or risky operations.
---

# Skill: backup-vault

**OBJECTIVE**
Produce a backup that is proven restorable — not merely produced.

**REQUIRED INPUTS**
None; optionally `--label <reason>` and `--dest <dir>`.

**PROCESS**
1. `python3 scripts/vault.py backup --label before-<operation>`
2. The command hashes every file into `BACKUP-MANIFEST.json`, writes a
   `.sha256` for the archive, and immediately verifies the archive.
3. Prove recovery without touching production:
   `python3 scripts/vault.py restore <archive> /tmp/restore-test --yes`
   then `python3 scripts/vault.py rebuild-index --vault /tmp/restore-test`
   and `python3 scripts/vault.py validate --vault /tmp/restore-test`.

**VALIDATION**
`restore-verified: True`, every manifest hash matches, and the restored copy
validates independently.

**FAILURE BEHAVIOUR**
- Verification fails → the backup is not a backup. Investigate before relying
  on it; do not delete the previous archive.
- Restore refuses a non-empty destination by design. Restore somewhere new,
  inspect, then move it into place.

**STOP CONDITION**
A verified archive exists and a test restore validated.

**EXPECTED OUTPUT**
Archive path, file count, SHA-256, and the verification result.
