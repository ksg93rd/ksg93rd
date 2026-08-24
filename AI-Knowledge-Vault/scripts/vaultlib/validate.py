"""The validation engine. Returns PASS / WARN / FAIL with remediation for every issue."""
import os
import re

from . import config, graph, ids, index, records, schema, security

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
RANK = {PASS: 0, WARN: 1, FAIL: 2}


class Issue(object):
    def __init__(self, level, record, reason, remediation, path=None, rule=None):
        self.level, self.record, self.reason = level, record, reason
        self.remediation, self.path, self.rule = remediation, path, rule

    def as_dict(self):
        return {"level": self.level, "record": self.record, "rule": self.rule,
                "reason": self.reason, "remediation": self.remediation, "path": self.path}

    def __str__(self):
        return "[%s] %s: %s\n         fix: %s" % (
            self.level, self.record or self.path or "-", self.reason, self.remediation)


def _check_value(field, spec, value, known_ids):
    """Return a list of (reason, remediation) for one field."""
    problems = []
    ftype = spec["type"]
    if ftype == "id":
        if not ids.is_valid(value):
            problems.append(("id %r is not a valid vault identifier" % value,
                             "regenerate the id as <type>-YYYYMMDD-<hex>"))
    elif ftype == "timestamp":
        if not (isinstance(value, str) and schema.ISO_RE.match(value)):
            problems.append(("%s=%r is not an ISO-8601 timestamp" % (field, value),
                             "use e.g. 2026-08-24T09:35:00-05:00"))
    elif ftype == "hash":
        if not (isinstance(value, str) and schema.HASH_RE.match(value)):
            problems.append(("%s=%r is not 'sha256:<64 hex>'" % (field, value),
                             "recompute with vault.py rebuild-index after re-ingesting"))
    elif ftype == "enum":
        if value not in spec["values"]:
            problems.append(("%s=%r is not an allowed value" % (field, value),
                             "use one of: %s" % ", ".join(map(str, spec["values"]))))
    elif ftype == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            problems.append(("%s=%r is not an integer" % (field, value),
                             "set %s to a whole number" % field))
    elif ftype == "bool":
        if not isinstance(value, bool):
            problems.append(("%s=%r is not a boolean" % (field, value),
                             "use true or false"))
    elif ftype == "list":
        if not isinstance(value, list):
            problems.append(("%s must be a list" % field, "use a YAML list, or []"))
    elif ftype == "ref":
        if not ids.is_valid(value):
            problems.append(("%s=%r is not a record id" % (field, value),
                             "reference an existing record id"))
        elif value not in known_ids:
            problems.append(("%s points at %s which does not exist" % (field, value),
                             "create the record, fix the id, or clear the field"))
        elif spec.get("kinds") and ids.kind_of(value) not in spec["kinds"]:
            problems.append(("%s=%s must be one of %s" % (field, value, spec["kinds"]),
                             "reference the correct record type"))
    elif ftype == "reflist":
        if not isinstance(value, list):
            problems.append(("%s must be a list of record ids" % field, "use a YAML list, or []"))
        else:
            for item in value:
                if not ids.is_valid(item):
                    problems.append(("%s contains %r which is not a record id" % (field, item),
                                     "remove it or replace with a valid id"))
                elif item not in known_ids:
                    problems.append(("%s references missing record %s" % (field, item),
                                     "create %s, fix the id, or remove the reference" % item))
                elif spec.get("kinds") and ids.kind_of(item) not in spec["kinds"]:
                    problems.append(("%s contains %s but expects %s" % (field, item, spec["kinds"]),
                                     "reference the correct record type"))
    return problems


def validate(root, strict=False, check_indexes=True):
    issues = []
    all_records, load_errors = records.load_all(root)

    for error in load_errors:
        issues.append(Issue(FAIL, None, error.reason,
                            "open the file and repair it, or restore it from a backup "
                            "(vault.py backup / docs/RECOVERY.md)",
                            path=os.path.relpath(error.path, root), rule="unreadable-record"))

    known_ids = set(r.id for r in all_records if r.id)
    by_id = {}
    for record in all_records:
        by_id.setdefault(record.id, []).append(record)

    # --- duplicate ids ---
    for record_id, group in by_id.items():
        if record_id and len(group) > 1:
            issues.append(Issue(FAIL, record_id,
                                "id used by %d files: %s" % (
                                    len(group), ", ".join(r.rel_path() for r in group)),
                                "give each record a unique id (vault.py new generates one)",
                                rule="duplicate-id"))

    hashes = {}
    for record in all_records:
        meta = record.meta
        rtype = meta.get("type")
        rel = record.rel_path()
        if rtype not in schema.SCHEMAS:
            issues.append(Issue(FAIL, meta.get("id"),
                                "unknown record type %r" % rtype,
                                "set type to one of: %s" % ", ".join(sorted(schema.SCHEMAS)),
                                path=rel, rule="unknown-type"))
            continue
        spec_map = schema.SCHEMAS[rtype]
        for field, spec in spec_map.items():
            present = field in meta and meta[field] is not None
            if spec["required"] and not present:
                issues.append(Issue(FAIL, meta.get("id"),
                                    "required field %r is missing" % field,
                                    "add %r (see docs/SCHEMA.md)" % field,
                                    path=rel, rule="missing-required"))
                continue
            if not present:
                continue
            for reason, remediation in _check_value(field, spec, meta[field], known_ids):
                issues.append(Issue(FAIL, meta.get("id"), reason, remediation,
                                    path=rel, rule="field-invalid"))
        for field in meta:
            if field not in spec_map:
                issues.append(Issue(WARN, meta.get("id"),
                                    "field %r is not in the %s schema" % (field, rtype),
                                    "remove it, or add it to scripts/vaultlib/schema.py",
                                    path=rel, rule="unknown-field"))
        if ids.kind_of(meta.get("id")) not in (None, rtype):
            issues.append(Issue(FAIL, meta.get("id"),
                                "id prefix does not match type=%s" % rtype,
                                "reissue the id with the matching prefix",
                                path=rel, rule="id-type-mismatch"))
        # duplicate content hashes across sources
        chash = meta.get("content_hash")
        if chash and rtype == "source":
            if chash in hashes and hashes[chash] != meta.get("id"):
                issues.append(Issue(WARN, meta.get("id"),
                                    "content_hash duplicates source %s" % hashes[chash],
                                    "deduplicate: keep one source and reference it, or "
                                    "record this as a revision with --revises",
                                    path=rel, rule="duplicate-hash"))
            else:
                hashes[chash] = meta.get("id")

        # --- knowledge-integrity rules ---
        if rtype == "claim":
            if not record.reflist("sources"):
                issues.append(Issue(FAIL, meta.get("id"),
                                    "claim has no sources",
                                    "cite at least one source id, or set status: unknown",
                                    path=rel, rule="claim-unsourced"))
            if meta.get("verification_status") == "verified" and \
                    meta.get("review_status") != "approved":
                issues.append(Issue(FAIL, meta.get("id"),
                                    "claim is marked verified but review_status=%r"
                                    % meta.get("review_status"),
                                    "run the review gate (vault.py review) before "
                                    "verifying; verification may not bypass review",
                                    path=rel, rule="unreviewed-verified"))
            if meta.get("status") == "verified" and meta.get("review_status") != "approved":
                issues.append(Issue(FAIL, meta.get("id"),
                                    "status=verified without an approved review",
                                    "approve it through vault.py review, or set "
                                    "status back to candidate",
                                    path=rel, rule="unreviewed-verified"))
            if meta.get("trust_level") == "trusted" and meta.get("review_status") != "approved":
                issues.append(Issue(WARN, meta.get("id"),
                                    "trust_level=trusted without approved review",
                                    "review it, or lower trust_level to internal",
                                    path=rel, rule="unreviewed-trusted"))
            if meta.get("evidence_strength") == "high" and \
                    meta.get("source_quality") in ("ai-generated", "self-reported", "unknown"):
                issues.append(Issue(WARN, meta.get("id"),
                                    "evidence_strength=high but source_quality=%s"
                                    % meta.get("source_quality"),
                                    "downgrade evidence_strength or cite a primary source",
                                    path=rel, rule="evidence-overstated"))
        if rtype == "source":
            if meta.get("security_status") == "quarantined" and \
                    meta.get("trust_level") != "quarantined":
                issues.append(Issue(FAIL, meta.get("id"),
                                    "quarantined source has trust_level=%r"
                                    % meta.get("trust_level"),
                                    "set trust_level: quarantined",
                                    path=rel, rule="quarantine-policy"))
            if meta.get("trust_level") == "quarantined" and \
                    config.QUARANTINE_DIR.replace(os.sep, "/") not in rel.replace(os.sep, "/"):
                issues.append(Issue(FAIL, meta.get("id"),
                                    "quarantined source is stored outside %s"
                                    % config.QUARANTINE_DIR,
                                    "move the file into 90-archive/quarantine/",
                                    path=rel, rule="quarantine-policy"))
            if meta.get("extraction_status") == "unsupported" and record.body and \
                    "## Extracted content" in record.body:
                issues.append(Issue(WARN, meta.get("id"),
                                    "extraction_status=unsupported but the record shows "
                                    "extracted content",
                                    "correct extraction_status, or remove the content block",
                                    path=rel, rule="false-extraction-claim"))
        if rtype == "review":
            if meta.get("independent") is False and meta.get("status") == "approved":
                issues.append(Issue(WARN, meta.get("id"),
                                    "approval by a non-independent reviewer",
                                    "have a different actor review high-risk records",
                                    path=rel, rule="self-approval"))

    # --- claims referenced by quarantined sources ---
    quarantined = set(r.id for r in all_records
                      if r.type == "source" and r.get("trust_level") == "quarantined")
    for record in all_records:
        if record.type == "claim":
            tainted = [s for s in record.reflist("sources") if s in quarantined]
            if tainted:
                issues.append(Issue(FAIL, record.id,
                                    "claim cites quarantined source(s): %s" % ", ".join(tainted),
                                    "quarantined content may not become canonical knowledge; "
                                    "reject the claim or cite a clean source",
                                    path=record.rel_path(), rule="quarantine-propagation"))

    # --- graph-level rules ---
    data = graph.build(root)
    for edge in data["edges"]:
        if edge["dangling"]:
            issues.append(Issue(FAIL, edge["source"],
                                "%s edge points at missing record %s"
                                % (edge["relationship"], edge["target"]),
                                "create the target record or remove the reference",
                                rule="broken-reference"))
        if edge["relationship"] not in graph.VALID_RELS:
            issues.append(Issue(FAIL, edge["source"],
                                "invalid edge type %r" % edge["relationship"],
                                "use one of: %s" % ", ".join(sorted(graph.VALID_RELS)),
                                rule="invalid-edge"))
        if edge["source"] == edge["target"] and edge["relationship"] != "RELATED_TO":
            issues.append(Issue(FAIL, edge["source"],
                                "record %s %s itself" % (edge["source"], edge["relationship"]),
                                "remove the self-referencing edge",
                                rule="self-edge"))
    for pair in graph.self_contradictions(data):
        issues.append(Issue(FAIL, pair["source"],
                            "record both supports and contradicts %s" % pair["target"],
                            "pick one relationship, or split into two claims",
                            rule="self-contradictory"))
    for cycle in graph.supersession_cycles(data):
        issues.append(Issue(FAIL, cycle[0],
                            "supersession cycle: %s" % " -> ".join(cycle),
                            "supersession must be acyclic; break the loop",
                            rule="supersession-cycle"))

    # --- orphans ---
    referenced = set()
    for edge in data["edges"]:
        referenced.add(edge["target"])
        referenced.add(edge["source"])
    for record in all_records:
        if record.type in ("claim", "entity", "decision", "artifact") and \
                record.id not in referenced:
            issues.append(Issue(WARN, record.id,
                                "orphan: no relationships in or out",
                                "link it to a source, entity, or project",
                                path=record.rel_path(), rule="orphan"))

    # --- index freshness ---
    # Callers that rebuild immediately after validating pass check_indexes=False:
    # otherwise every command would report a stale index caused by the very run
    # record it is about to write.
    if check_indexes:
        stale, why = index.index_is_stale(root)
        if stale:
            issues.append(Issue(WARN, None, "search index is stale: %s" % why,
                                "run: vault.py rebuild-index", rule="stale-index"))
        gpath = graph.graph_path(root)
        if not os.path.isfile(gpath):
            issues.append(Issue(WARN, None, "graph export missing",
                                "run: vault.py graph-export", rule="stale-graph"))

    # --- iCloud availability ---
    for rel, why in records.icloud_placeholder_scan(root):
        issues.append(Issue(WARN, None, "%s: %s" % (rel, why),
                            "open the file in Finder to force a download, or run "
                            "`brctl download` on it; do not process an incomplete "
                            "source set", path=rel, rule="icloud-unavailable"))

    level = PASS
    for issue in issues:
        if RANK[issue.level] > RANK[level]:
            level = issue.level
    if strict and level == WARN:
        level = FAIL
    return level, issues
