---
name: check-contradictions
description: Find and adjudicate conflicting or duplicate claims without deleting either side. Use periodically and before approving a claim.
---

# Skill: check-contradictions

**OBJECTIVE**
Surface conflicts and classify them, preserving all evidence.

**REQUIRED INPUTS**
None (whole vault), or a claim id.

**PROCESS**
1. `python3 scripts/vault.py contradictions`
2. For each pair marked `[UNDECLARED]`, read both claims and their sources.
3. Classify: genuine contradiction | different scope | different time period |
   different definition | measurement difference | duplicate.
4. Record the outcome:
   - genuine → add each other to `contradicts:` and set both `status: disputed`
   - superseded → set `supersedes` / `superseded_by`, keep both records
   - duplicate → set `duplicates:`, keep the better-sourced record canonical
5. Re-run the scan and `vault.py validate`.

**VALIDATION**
No undeclared CONTRADICTS pairs remain, and no record contradicts itself.

**FAILURE BEHAVIOUR**
- Cannot tell which is right → mark both `disputed` and escalate. Ambiguity is
  a valid, recordable state.
- **Never** assume the newer claim is correct.
- **Never** delete a contradictory record to simplify the graph.

**STOP CONDITION**
Every flagged pair is declared or explicitly dismissed with a reason.

**EXPECTED OUTPUT**
Pairs, classifications, actions taken, and what remains for a human.
