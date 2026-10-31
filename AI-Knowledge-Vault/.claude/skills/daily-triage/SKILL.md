---
name: daily-triage
description: Work the inbox, pending reviews, contradictions, and vault health in one pass. Use as the routine operating loop.
---

# Skill: daily-triage

**OBJECTIVE**
Keep the vault current without letting anything become verified by neglect.

**REQUIRED INPUTS**
None.

**PROCESS**
1. **Availability** — `vault.py health-check`. Stop if files are unavailable.
2. **Inbox** — for each file in `00-inbox/`: run `ingest-source`, then move the
   original out of the inbox. Record a reason for anything discarded.
3. **Pending reviews** — `vault.py search --review pending --type claim`.
   Run `review-claim` on each; approve nothing that has not been falsified.
4. **Contradictions** — `vault.py contradictions`; adjudicate undeclared pairs.
5. **Stale sources** — look for sources older than the freshness window whose
   claims are still relied upon; re-verify or mark them stale.
6. **Rebuild and report** — `rebuild-index`, `graph-export`, `status`, `validate`.
7. **Backup** — `backup-vault` if none exists for today.

**VALIDATION**
Inbox empty or fully accounted for; validation not worse than at the start;
STATUS.md regenerated.

**FAILURE BEHAVIOUR**
- Too many pending reviews to complete → do the highest-risk ones and report
  the backlog. Never bulk-approve.
- A quarantined item appears → hand to `security-reviewer` and stop that item.
- Three equivalent failures on one item → skip it, record why, continue.

**STOP CONDITION**
Every inbox item and every pending review has a decision or a recorded reason.

**EXPECTED OUTPUT**
Counts processed, decisions made, items escalated, and the closing status line.
