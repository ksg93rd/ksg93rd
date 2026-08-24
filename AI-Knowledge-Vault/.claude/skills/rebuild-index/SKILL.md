---
name: rebuild-index
description: Rebuild the SQLite search index and the graph export from canonical Markdown. Use when search misses records or after bulk edits or a restore.
---

# Skill: rebuild-index

**OBJECTIVE**
Regenerate every derived artifact from the authoritative Markdown files.

**REQUIRED INPUTS**
None.

**PROCESS**
1. `python3 scripts/vault.py rebuild-index`
2. `python3 scripts/vault.py graph-export`
3. `python3 scripts/vault.py status`
4. `python3 scripts/vault.py validate`

**VALIDATION**
Record count matches the number of Markdown records; the stale-index warning
clears; graph node count matches the record count.

**FAILURE BEHAVIOUR**
- Unreadable files are reported, never skipped silently — fix or restore them.
- FTS5 unavailable → search falls back to substring matching; say so.
- The index is disposable: deleting `indexes/vault.db` is always safe.

**STOP CONDITION**
Both indexes rebuild cleanly and validation is no worse than before.

**EXPECTED OUTPUT**
Record and edge counts, FTS5 availability, and any unreadable files.
