---
name: link-knowledge
description: Propose and record justified relationships between vault records. Use after adding records or when the graph looks sparse.
---

# Skill: link-knowledge

**OBJECTIVE**
Connect records with edges that are justified by text, not by intuition.

**REQUIRED INPUTS**
A record id, or a set of newly created records.

**PROCESS**
1. `vault.py related <id>` — see what already exists.
2. `vault.py search "<key terms from the record>"` — find neighbours.
3. For each candidate pair choose exactly one of: SUPPORTS, CONTRADICTS,
   SUPERSEDES, DERIVED_FROM, MENTIONS, RELATED_TO, PART_OF, DUPLICATES —
   and write down the sentence that justifies it.
4. Add the ids to the matching frontmatter field.
5. `vault.py graph-export && vault.py validate`.

**VALIDATION**
No dangling edges, no self-edges, no pair with both SUPPORTS and CONTRADICTS,
no supersession cycles.

**FAILURE BEHAVIOUR**
- No justification → do not create the edge.
- Target missing → create the target first, or drop the edge.
- Cycle detected → stop and report; do not "fix" it by deleting evidence.

**STOP CONDITION**
Every proposed edge is either recorded with a justification or dropped.

**EXPECTED OUTPUT**
The edges added, each with its justification, and the updated graph counts.
