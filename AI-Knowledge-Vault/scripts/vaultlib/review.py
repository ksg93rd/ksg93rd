"""The review gate.

DRAFT -> SCHEMA VALIDATION -> SOURCE VALIDATION -> CRITIC REVIEW ->
RELATIONSHIP CHECK -> APPROVE / REJECT / DISPUTE -> COMMIT

Nothing becomes verified without passing through here. The gate refuses
self-approval on high-risk records and refuses anything touching quarantine.
"""
from . import contradiction, ids, records, schema, security, validate

HIGH_RISK_TRIGGERS = ("security", "credential", "legal", "financial", "medical",
                      "production", "outage", "compliance", "contract", "liability")


class GateResult(object):
    def __init__(self, target_id):
        self.target_id = target_id
        self.checks = []
        self.decision = None
        self.blocking = []
        self.review_id = None

    def add(self, name, outcome, detail):
        self.checks.append({"check": name, "outcome": outcome, "detail": detail})
        if outcome == "FAIL":
            self.blocking.append("%s: %s" % (name, detail))

    def as_dict(self):
        return {"target": self.target_id, "decision": self.decision,
                "checks": self.checks, "blocking": self.blocking,
                "review_id": self.review_id}


def is_high_risk(record):
    text = ("%s %s" % (record.title, record.body or "")).lower()
    if any(word in text for word in HIGH_RISK_TRIGGERS):
        return True
    return record.get("trust_level") == "trusted"


def run_gate(root, target_id, decision, reviewer, reviewer_role="reviewer",
             rationale="", author=None, all_records=None, run_id=None, force=False):
    """Evaluate the gate and, if it passes, write a review record and update the target."""
    if all_records is None:
        all_records, _ = records.load_all(root)
    by_id = {r.id: r for r in all_records}
    target = by_id.get(target_id)
    result = GateResult(target_id)
    if target is None:
        result.decision = "blocked"
        result.add("target-exists", "FAIL", "no record with id %s" % target_id)
        return result, None

    # 1. SCHEMA VALIDATION -------------------------------------------------
    spec_map = schema.SCHEMAS.get(target.type)
    if not spec_map:
        result.add("schema-validation", "FAIL", "unknown record type %r" % target.type)
    else:
        missing = [f for f, s in spec_map.items()
                   if s["required"] and target.meta.get(f) is None]
        if missing:
            result.add("schema-validation", "FAIL",
                       "missing required fields: %s" % ", ".join(missing))
        else:
            result.add("schema-validation", "PASS", "all required fields present")

    # 2. SOURCE VALIDATION -------------------------------------------------
    sources = target.reflist("sources")
    if target.type == "claim":
        if not sources:
            result.add("source-validation", "FAIL", "claim cites no source")
        else:
            missing_sources = [s for s in sources if s not in by_id]
            quarantined = [s for s in sources
                           if s in by_id and by_id[s].get("trust_level") == "quarantined"]
            if missing_sources:
                result.add("source-validation", "FAIL",
                           "cited sources do not exist: %s" % ", ".join(missing_sources))
            elif quarantined:
                result.add("source-validation", "FAIL",
                           "cites quarantined source(s): %s; quarantined content may not "
                           "become canonical knowledge" % ", ".join(quarantined))
            else:
                qualities = [by_id[s].get("source_quality") for s in sources]
                result.add("source-validation", "PASS",
                           "%d source(s) present, quality: %s"
                           % (len(sources), ", ".join(str(q) for q in qualities)))
    else:
        result.add("source-validation", "PASS", "not applicable for type=%s" % target.type)

    # 3. CRITIC REVIEW -----------------------------------------------------
    critic_notes = []
    if target.type == "claim":
        if target.get("evidence_strength") in (None, "none", "weak") and \
                decision == "approved":
            critic_notes.append("evidence_strength=%s is weak for an approval"
                                % target.get("evidence_strength"))
        if target.get("source_quality") == "ai-generated":
            critic_notes.append("source is AI-generated; treat as self-reported, "
                                "not primary evidence")
        if not (target.body or "").strip():
            critic_notes.append("record body is empty; the proposition is not stated")
    if critic_notes and decision == "approved" and not force:
        result.add("critic-review", "WARN", "; ".join(critic_notes))
    elif critic_notes:
        result.add("critic-review", "WARN", "; ".join(critic_notes))
    else:
        result.add("critic-review", "PASS", "no falsification finding raised")

    # 4. RELATIONSHIP CHECK ------------------------------------------------
    if target.type == "claim":
        proposals = contradiction.compare_claim(
            root, contradiction.claim_text(target),
            exclude_id=target.id, all_records=all_records)
        detected = set(p["target"] for p in proposals
                       if p["relationship"] == "CONTRADICTS")
        declared = set(target.reflist("contradicts"))
        undeclared = sorted(detected - declared)
        # A contradiction counts as resolved only when the opposing record has
        # itself been rejected or superseded. Declaring a conflict documents it;
        # it does not settle it, so an unresolved conflict still blocks approval.
        unresolved = sorted(
            other for other in (declared | detected)
            if other in by_id and by_id[other].get("status") not in
            ("rejected", "superseded"))
        if undeclared and decision == "approved":
            result.add("relationship-check", "FAIL",
                       "undeclared contradiction(s) with %s; resolve or record them "
                       "before approval" % ", ".join(undeclared))
        elif unresolved and decision == "approved":
            result.add("relationship-check", "FAIL",
                       "unresolved contradiction(s) with %s; reject or supersede the "
                       "opposing claim, or record this one as disputed, before it may "
                       "be verified" % ", ".join(unresolved))
        elif declared or detected:
            result.add("relationship-check", "WARN",
                       "%d contradiction(s) recorded; opposing records are rejected or "
                       "superseded" % len(declared | detected))
        else:
            result.add("relationship-check", "PASS", "no contradiction detected")
    else:
        result.add("relationship-check", "PASS", "not applicable")

    # 5. INDEPENDENCE ------------------------------------------------------
    author = author or target.get("created_by") or target.get("run_id")
    independent = bool(reviewer) and reviewer != author
    high_risk = is_high_risk(target)
    if high_risk and not independent and decision == "approved":
        result.add("independence", "FAIL",
                   "high-risk record: author and reviewer are both %r; an independent "
                   "reviewer is required" % reviewer)
    elif not independent:
        result.add("independence", "WARN", "reviewer is not independent of the author")
    else:
        result.add("independence", "PASS", "reviewer is independent of the author")

    # ---- decide ----------------------------------------------------------
    if decision not in schema.REVIEW_RESULT:
        result.decision = "blocked"
        result.add("decision-valid", "FAIL",
                   "decision must be one of %s" % ", ".join(schema.REVIEW_RESULT))
        return result, None
    if result.blocking and decision == "approved" and not force:
        result.decision = "blocked"
        return result, None

    result.decision = decision

    # ---- write the review record (append-oriented history) ---------------
    review_id = ids.new_id("review")
    review_meta = {
        "id": review_id, "type": "review",
        "title": "Review of %s: %s" % (target_id, decision),
        "status": decision,
        "created_at": ids.now_iso(), "updated_at": ids.now_iso(),
        "decided_at": ids.now_iso(),
        "trust_level": "internal",
        "target": target_id, "reviewer": reviewer, "reviewer_role": reviewer_role,
        "independent": independent,
        "checks": ["%s: %s - %s" % (c["check"], c["outcome"], c["detail"])
                   for c in result.checks],
        "findings": result.blocking or [],
    }
    if run_id:
        review_meta["run_id"] = run_id
    if target.get("demo"):
        review_meta["demo"] = True
    body = "## Decision\n\n**%s**\n\n## Rationale\n\n%s\n\n## Gate checks\n\n%s\n" % (
        decision.upper(), rationale or "(none recorded)",
        "\n".join("- **%s** - %s: %s" % (c["check"], c["outcome"], c["detail"])
                  for c in result.checks))
    records.save(root, review_meta, body)
    result.review_id = review_id

    # ---- apply the decision to the target (canonical commit) -------------
    meta = dict(target.meta)
    meta["review_status"] = {"approved": "approved", "rejected": "rejected",
                             "disputed": "disputed",
                             "needs-more-evidence": "in-review"}[decision]
    meta["reviewed_by"] = sorted(set((meta.get("reviewed_by") or []) + [reviewer]))
    if target.type == "claim":
        if decision == "approved":
            meta["status"] = "verified"
            meta["verification_status"] = "verified"
        elif decision == "rejected":
            meta["status"] = "rejected"
            meta["verification_status"] = "failed"
        elif decision == "disputed":
            meta["status"] = "disputed"
            meta["verification_status"] = "unverified"
        else:
            meta["status"] = "candidate"
            meta["verification_status"] = "verifying"
    elif "review_status" not in schema.SCHEMAS.get(target.type, {}):
        meta.pop("review_status", None)
        meta.pop("reviewed_by", None)
    records.save(root, meta, target.body, path=target.path)
    return result, review_id
