"""STATUS.md + indexes/status.json - the vault's observability surface."""
import json
import os

from . import SCHEMA_VERSION, config, graph, ids, index, records, validate


def collect(root):
    all_records, load_errors = records.load_all(root)
    by_type = {}
    for record in all_records:
        by_type.setdefault(record.type, []).append(record)
    claims = by_type.get("claim", [])
    sources = by_type.get("source", [])
    runs = by_type.get("run", [])

    hashes = {}
    duplicate_hashes = []
    for source in sources:
        chash = source.get("content_hash")
        if not chash:
            continue
        if chash in hashes:
            duplicate_hashes.append([hashes[chash], source.id])
        else:
            hashes[chash] = source.id

    level, issues = validate.validate(root)
    graph_data = graph.load(root) or {"counts": {}, "generated_at": None}
    stale, stale_why = index.index_is_stale(root)

    def count(seq, field, value):
        return sum(1 for r in seq if r.get(field) == value)

    data = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": ids.now_iso(),
        "vault_root": root,
        "totals": {
            "records": len(all_records),
            "sources": len(sources),
            "claims": len(claims),
            "entities": len(by_type.get("entity", [])),
            "decisions": len(by_type.get("decision", [])),
            "artifacts": len(by_type.get("artifact", [])),
            "projects": len(by_type.get("project", [])),
            "runs": len(runs),
            "reviews": len(by_type.get("review", [])),
        },
        "claims": {
            "verified": count(claims, "status", "verified"),
            "candidate": count(claims, "status", "candidate"),
            "disputed": count(claims, "status", "disputed"),
            "rejected": count(claims, "status", "rejected"),
            "superseded": count(claims, "status", "superseded"),
            "unknown": count(claims, "status", "unknown"),
            "pending_review": count(claims, "review_status", "pending"),
        },
        "security": {
            "quarantined_sources": count(sources, "trust_level", "quarantined"),
            "flagged_sources": count(sources, "security_status", "flagged"),
            "security_warnings": sum(len(s.reflist("security_findings")) for s in sources),
        },
        "integrity": {
            "validation_level": level,
            "fail_count": sum(1 for i in issues if i.level == validate.FAIL),
            "warn_count": sum(1 for i in issues if i.level == validate.WARN),
            "broken_references": sum(1 for i in issues if i.rule == "broken-reference"),
            "duplicate_hashes": duplicate_hashes,
            "orphans": sum(1 for i in issues if i.rule == "orphan"),
            "load_errors": [(os.path.relpath(e.path, root), e.reason) for e in load_errors],
            "icloud_unavailable": sum(1 for i in issues if i.rule == "icloud-unavailable"),
        },
        "indexes": {
            "db_present": os.path.isfile(index.db_path(root)),
            "db_stale": stale,
            "db_stale_reason": stale_why,
            "fts5": index.fts5_available(),
            "graph_generated_at": graph_data.get("generated_at"),
            "graph_nodes": graph_data.get("counts", {}).get("nodes"),
            "graph_edges": graph_data.get("counts", {}).get("edges"),
        },
        "runs": {
            "total": len(runs),
            "recent_success": [r.id for r in sorted(
                runs, key=lambda r: r.get("started_at") or "", reverse=True)
                if r.get("status") == "success"][:5],
            "recent_failed": [r.id for r in sorted(
                runs, key=lambda r: r.get("started_at") or "", reverse=True)
                if r.get("status") in ("failed", "partial")][:5],
            "last_run_at": max([r.get("completed_at") or r.get("started_at") or ""
                                for r in runs] or [None]) or None,
        },
        "demo_records": sum(1 for r in all_records if r.get("demo")),
    }
    return data, issues


def write(root):
    data, issues = collect(root)
    json_path = os.path.join(root, "indexes", "status.json")
    if not os.path.isdir(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")

    totals, claims, sec = data["totals"], data["claims"], data["security"]
    integrity, idx, runs_info = data["integrity"], data["indexes"], data["runs"]
    lines = [
        "# Vault Status",
        "",
        "_Generated %s by `vault.py status`. Derived file - do not edit by hand._" %
        data["generated_at"],
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Total records | %d |" % totals["records"],
        "| Sources | %d |" % totals["sources"],
        "| Claims | %d |" % totals["claims"],
        "| &nbsp;&nbsp;verified | %d |" % claims["verified"],
        "| &nbsp;&nbsp;candidate | %d |" % claims["candidate"],
        "| &nbsp;&nbsp;disputed | %d |" % claims["disputed"],
        "| &nbsp;&nbsp;rejected | %d |" % claims["rejected"],
        "| &nbsp;&nbsp;superseded | %d |" % claims["superseded"],
        "| Pending reviews | %d |" % claims["pending_review"],
        "| Entities | %d |" % totals["entities"],
        "| Decisions | %d |" % totals["decisions"],
        "| Projects | %d |" % totals["projects"],
        "| Runs | %d |" % totals["runs"],
        "| Reviews | %d |" % totals["reviews"],
        "",
        "## Security",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Quarantined sources | %d |" % sec["quarantined_sources"],
        "| Flagged sources | %d |" % sec["flagged_sources"],
        "| Security warnings recorded | %d |" % sec["security_warnings"],
        "",
        "## Integrity",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Validation | **%s** (%d FAIL, %d WARN) |" % (
            integrity["validation_level"], integrity["fail_count"], integrity["warn_count"]),
        "| Broken references | %d |" % integrity["broken_references"],
        "| Duplicate content hashes | %d |" % len(integrity["duplicate_hashes"]),
        "| Orphan records | %d |" % integrity["orphans"],
        "| Unreadable / unavailable files | %d |" % (
            len(integrity["load_errors"]) + integrity["icloud_unavailable"]),
        "",
        "## Indexes (all rebuildable)",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| SQLite index present | %s |" % idx["db_present"],
        "| SQLite index stale | %s (%s) |" % (idx["db_stale"], idx["db_stale_reason"]),
        "| FTS5 available | %s |" % idx["fts5"],
        "| Graph nodes / edges | %s / %s |" % (idx["graph_nodes"], idx["graph_edges"]),
        "| Graph generated at | %s |" % idx["graph_generated_at"],
        "",
        "## Runs",
        "",
        "- Last run: %s" % (runs_info["last_run_at"] or "never"),
        "- Recent successful: %s" % (", ".join(runs_info["recent_success"]) or "none"),
        "- Recent failed/partial: %s" % (", ".join(runs_info["recent_failed"]) or "none"),
        "",
        "## Demo data",
        "",
        "%d record(s) carry `demo: true`. Synthetic demo content is never real "
        "user knowledge." % data["demo_records"],
        "",
    ]
    if issues:
        lines += ["## Open validation issues", ""]
        for issue in issues[:40]:
            lines.append("- **%s** `%s` - %s  \n  _fix:_ %s" % (
                issue.level, issue.record or issue.path or "-", issue.reason,
                issue.remediation))
        if len(issues) > 40:
            lines.append("- ... and %d more (run `vault.py validate`)" % (len(issues) - 40))
        lines.append("")
    status_path = os.path.join(root, "STATUS.md")
    with open(status_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return data, status_path, json_path
