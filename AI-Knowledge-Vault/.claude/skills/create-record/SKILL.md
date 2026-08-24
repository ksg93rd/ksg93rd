---
name: create-record
description: Create a well-formed claim, entity, decision, project, or artifact record with correct metadata and honest uncertainty. Use when capturing new knowledge by hand.
---

# Skill: create-record

**OBJECTIVE**
Add a canonical record that is schema-valid, sourced, and honest about its
verification state.

**REQUIRED INPUTS**
- Record type: claim | entity | decision | project | artifact
- A one-sentence title. For a claim, the title *is* the proposition.
- For claims: at least one existing source id.

**PROCESS**
1. Search first — `vault.py search "<topic>"` — a record may already exist.
2. Create it:
   `python3 scripts/vault.py new claim "<proposition>" --source <source-id>`
3. Fill the body: **Proposition**, **Evidence** (what in the source supports
   it, quoted), **Uncertainty** (what would falsify it, what is unknown).
4. Set `source_quality` and `evidence_strength` from the actual source, not
   from how confident the wording sounds.
5. Ask `linker` for relationship proposals; add only justified edges.

**VALIDATION**
- `vault.py validate` returns no new FAIL.
- New claims must be `status: candidate`, `verification_status: unverified`,
  `review_status: pending`.

**FAILURE BEHAVIOUR**
- No source available → do not create a claim; create an entity or a note, or
  record the question instead.
- Duplicate found → link to it rather than restating it.

**STOP CONDITION**
The record validates and is linked to at least one source or entity.

**EXPECTED OUTPUT**
The new record id and path, plus any relationship proposals raised.
