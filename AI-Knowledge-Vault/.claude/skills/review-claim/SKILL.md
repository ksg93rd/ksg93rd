---
name: review-claim
description: Run the review gate on a claim or record so it can be approved, rejected, or disputed. Use before anything is treated as verified knowledge.
---

# Skill: review-claim

**OBJECTIVE**
Move a candidate through the gate — or block it — with an auditable record.

**REQUIRED INPUTS**
- Record id.
- A reviewer identity that is **not** the author for high-risk records.
- A decision: `approved` | `rejected` | `disputed` | `needs-more-evidence`.

**PROCESS**
1. Read the record and its sources: `vault.py show <id>`.
2. Verify citations (`source-verifier`): does the source actually say this?
3. Falsify it (`critic`): what is missing, overstated, or explainable otherwise?
4. Check relationships (`linker`, `contradiction-reviewer`): any undeclared
   contradiction must be resolved or recorded before approval.
5. Decide:
   `python3 scripts/vault.py review <id> approved --reviewer <name> --rationale "..."`

The gate runs SCHEMA VALIDATION → SOURCE VALIDATION → CRITIC REVIEW →
RELATIONSHIP CHECK → INDEPENDENCE, then applies the decision and writes a
review record.

**VALIDATION**
On approval the claim becomes `status: verified`, `verification_status:
verified`, `review_status: approved`, and a record appears in `80-reviews/`.

**FAILURE BEHAVIOUR**
- `BLOCKED` — the gate refused. Fix the blockers listed; do not work around them.
- `--force` exists for a deliberate, documented override only; the override is
  recorded in the review record and remains visible forever.
- Weak evidence → choose `needs-more-evidence`, not `approved`.

**STOP CONDITION**
A review record exists and the target's review state reflects the decision.

**EXPECTED OUTPUT**
Per-check results, the decision, the review id, and the run id.
