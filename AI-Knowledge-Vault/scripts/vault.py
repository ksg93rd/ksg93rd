#!/usr/bin/env python3
"""AI Knowledge Vault - command line interface.

Python standard library only. Works on macOS system Python and on Linux.

  vault.py init | ingest | validate | search | show | related | rebuild-index |
           graph-export | status | health-check | backup | restore | verify-backup |
           review | contradictions | new | provenance | commit | log | doctor
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vaultlib import (SCHEMA_VERSION, backup, config, contradiction, gitprov,
                      graph, ids, index, ingest, records, review, runs,
                      scaffold, schema, security, status, validate)

EXIT_OK, EXIT_WARN, EXIT_FAIL, EXIT_ERROR = 0, 0, 1, 2


# ------------------------------------------------------------------ helpers
def out(text=""):
    sys.stdout.write(str(text) + "\n")


def emit(args, data, human):
    if getattr(args, "json", False):
        out(json.dumps(data, indent=2, default=str))
    else:
        human()


def get_root(args, must_exist=True):
    try:
        return config.resolve_root(getattr(args, "vault", None), must_exist=must_exist)
    except config.VaultRootError as exc:
        out("ERROR: %s" % exc)
        raise SystemExit(EXIT_ERROR)


def autocommit(root, message, enabled=True):
    cfg = config.load_config(root)
    if not enabled or not (cfg.get("features") or {}).get("auto_commit", True):
        return None
    if not gitprov.available():
        return None
    try:
        return gitprov.commit(root, message)
    except gitprov.GitError as exc:
        out("WARNING: git commit failed: %s" % exc)
        return None


# ------------------------------------------------------------------ init
def cmd_init(args):
    root = get_root(args, must_exist=False)
    preexisting = os.path.isdir(root) and bool(
        [n for n in os.listdir(root) if not n.startswith(".")])
    if preexisting:
        out("Existing directory found; inspecting before touching anything.")
        existing, errors = records.load_all(root)
        out("  existing records: %d, unreadable files: %d" % (len(existing), len(errors)))
        out("  init is additive: no existing file will be overwritten.")
    if not os.path.isdir(root):
        os.makedirs(root)
    created = scaffold.ensure_dirs(root)
    schemas = scaffold.write_schemas(root)
    cfg = scaffold.write_config(root)
    templates = scaffold.write_templates(root)

    if config.is_macos():
        container = config.icloud_container()
        location = ("iCloud Drive (%s)" % container) if container and root.startswith(container) \
            else "local filesystem (NOT iCloud)"
    else:
        location = "local filesystem on %s (iCloud Drive is macOS-only)" % sys.platform

    git_info = None
    if gitprov.available() and not args.no_git:
        git_info = gitprov.init(root)
        gitprov.commit(root, "vault: initialize structure, schemas, templates, config")

    pointer = config.POINTER_FILE
    if args.remember:
        directory = os.path.dirname(pointer)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        with open(pointer, "w", encoding="utf-8") as fh:
            fh.write(root + "\n")

    index.rebuild(root)
    graph.export(root)
    status.write(root)

    data = {"root": root, "location": location, "dirs_created": created,
            "schemas": len(schemas), "config": cfg, "templates": templates,
            "git": git_info, "remembered": args.remember}

    def human():
        out("Vault initialized.")
        out("  root      : %s" % root)
        out("  storage   : %s" % location)
        out("  dirs      : %d created" % len(created))
        out("  schemas   : %d exported to schemas/" % len(schemas))
        out("  templates : %d" % len(templates))
        if git_info:
            out("  git dir   : %s  (outside synchronized storage)" % git_info["git_dir"])
        else:
            out("  git       : not initialized")
        if args.remember:
            out("  remembered in %s" % pointer)
    emit(args, data, human)
    return EXIT_OK


# ------------------------------------------------------------------ ingest
def cmd_ingest(args):
    root = get_root(args)
    run = runs.Run(root, "ingest %s" % args.path, trigger=args.trigger,
                   skill="ingest-source", inputs=[args.path], demo=args.demo)
    existing, load_errors = records.load_all(root)
    for error in load_errors:
        run.warn("unreadable file skipped: %s (%s)" % (error.path, error.reason))

    targets = []
    if os.path.isdir(args.path):
        for name in sorted(os.listdir(args.path)):
            full = os.path.join(args.path, name)
            if os.path.isfile(full) and not name.startswith("."):
                targets.append(full)
    else:
        targets.append(args.path)

    results = []
    for target in targets:
        result = ingest.ingest_file(
            root, target, trust=args.trust, origin=args.origin, revises=args.revises,
            extract_claims=args.extract_claims, run_id=run.id, demo=args.demo,
            existing=existing)
        results.append(result)
        if result.status in ("ingested", "revision", "quarantined"):
            run.created(result.source_id)
            existing, _ = records.load_all(root)
        elif result.status == "duplicate":
            run.read(result.source_id)
            run.note("duplicate detected: %s" % result.messages[0])
        elif result.status == "failed":
            run.error("; ".join(result.messages))
        for message in result.messages:
            run.note(message)
        for finding in result.findings:
            run.warn("%s/%s (%s) line %s" % (finding.kind, finding.rule,
                                             finding.severity, finding.line))

        # claim candidates -> draft claim records (candidate/unverified/pending)
        for text in result.claims:
            claim_id = ids.new_id("claim")
            proposals = contradiction.compare_claim(root, text, all_records=existing)
            meta = {
                "id": claim_id, "type": "claim", "title": text[:120],
                "status": "candidate",
                "created_at": ids.now_iso(), "updated_at": ids.now_iso(),
                "trust_level": "untrusted",
                "sources": [result.source_id],
                "source_quality": "unknown", "evidence_strength": "weak",
                "verification_status": "unverified", "review_status": "pending",
                "supports": [], "contradicts": [], "supersedes": [],
                "superseded_by": [], "entities": [], "projects": [],
                "related_to": [], "run_id": run.id,
            }
            for proposal in proposals[:5]:
                if proposal["relationship"] == "CONTRADICTS":
                    meta["contradicts"] = sorted(set(meta["contradicts"] + [proposal["target"]]))
                elif proposal["relationship"] == "SUPPORTS":
                    meta["supports"] = sorted(set(meta["supports"] + [proposal["target"]]))
                elif proposal["relationship"] in ("RELATED_TO", "DUPLICATES"):
                    meta["related_to"] = sorted(set(meta["related_to"] + [proposal["target"]]))
            if args.demo:
                meta["demo"] = True
            body = ("## Proposition\n\n%s\n\n## Evidence\n\nExtracted from source `%s`. "
                    "Heuristic extraction: this is a CANDIDATE, not a verified fact.\n\n"
                    "## Relationship proposals\n\n%s\n\n## Uncertainty\n\n"
                    "Unreviewed. Not verified. Requires the review gate before it may be "
                    "treated as knowledge.\n") % (
                text, result.source_id,
                "\n".join("- **%s** %s (similarity %.2f) - %s" % (
                    p["relationship"], p["target"], p["similarity"], p["rationale"])
                    for p in proposals[:5]) or "- none")
            records.save(root, meta, body)
            run.created(claim_id)
            result.proposals.extend(proposals[:5])
            existing, _ = records.load_all(root)

    level, _ = validate.validate(root, check_indexes=False)
    run.validation_result = level
    run_id = run.finish("success" if all(r.status != "failed" for r in results) else "partial")
    # Rebuild last, so the derived artifacts include this run's own record.
    index.rebuild(root)
    graph.export(root)
    autocommit(root, "vault: ingest %s (run %s)" % (os.path.basename(args.path), run_id),
               not args.no_commit)

    data = {"run_id": run_id, "results": [r.as_dict() for r in results],
            "validation": level}

    def human():
        for result in results:
            out("[%s] %s" % (result.status.upper(), result.source_id or args.path))
            for message in result.messages:
                out("    %s" % message)
            if result.claims:
                out("    %d candidate claim(s) drafted (status=candidate, "
                    "review_status=pending)" % len(result.claims))
            for proposal in result.proposals:
                out("    proposal: %s -> %s (%.2f) %s" % (
                    proposal["relationship"], proposal["target"],
                    proposal["similarity"], proposal["rationale"]))
        out("run: %s   validation: %s" % (run_id, level))
    emit(args, data, human)
    return EXIT_OK if all(r.status != "failed" for r in results) else EXIT_FAIL


# ------------------------------------------------------------------ validate
def cmd_validate(args):
    root = get_root(args)
    level, issues = validate.validate(root, strict=args.strict)
    data = {"level": level, "issues": [i.as_dict() for i in issues]}

    def human():
        for issue in issues:
            out(str(issue))
        fails = sum(1 for i in issues if i.level == validate.FAIL)
        warns = sum(1 for i in issues if i.level == validate.WARN)
        out("")
        out("VALIDATION: %s  (%d FAIL, %d WARN)" % (level, fails, warns))
    emit(args, data, human)
    return EXIT_FAIL if level == validate.FAIL else EXIT_OK


# ------------------------------------------------------------------ search
def cmd_search(args):
    root = get_root(args)
    if args.rebuild:
        index.rebuild(root)
    try:
        rows = index.search(root, args.query, rtype=args.type, status=args.status,
                            trust=args.trust, review=args.review, limit=args.limit,
                            include_demo=not args.no_demo)
    except RuntimeError as exc:
        out("ERROR: %s" % exc)
        return EXIT_ERROR

    def human():
        if not rows:
            out("no matches")
            return
        for row in rows:
            out("%-34s %-9s %s" % (row["id"], row["type"], row["title"]))
            out("    status=%s trust=%s  %s" % (row["status"], row["trust_level"], row["path"]))
            if row.get("snip"):
                out("    %s" % " ".join(str(row["snip"]).split())[:160])
        out("")
        out("%d result(s)" % len(rows))
    emit(args, rows, human)
    return EXIT_OK


def cmd_show(args):
    root = get_root(args)
    record = records.find(root, args.id)
    if record is None:
        out("no record with id %s" % args.id)
        return EXIT_FAIL
    data = {"meta": record.meta, "body": record.body, "path": record.rel_path()}

    def human():
        out("path: %s" % record.rel_path())
        out("-" * 70)
        for key, value in record.meta.items():
            out("%-20s %s" % (key + ":", value))
        out("-" * 70)
        out(record.body)
    emit(args, data, human)
    return EXIT_OK


def cmd_related(args):
    root = get_root(args)
    try:
        data = index.related(root, args.id, depth=args.depth)
    except RuntimeError as exc:
        out("ERROR: %s" % exc)
        return EXIT_ERROR

    def human():
        out("Relationships for %s (depth %d)" % (args.id, args.depth))
        if not data["edges"]:
            out("  none")
        for edge in sorted(data["edges"], key=lambda e: e["relationship"]):
            other = edge["target"] if edge["source"] == args.id else edge["source"]
            arrow = "->" if edge["source"] == args.id else "<-"
            node = data["nodes"].get(other, {})
            out("  %s %-14s %-34s %s" % (arrow, edge["relationship"], other,
                                         node.get("title", "")))
    emit(args, data, human)
    return EXIT_OK


# ------------------------------------------------------------------ indexes
def cmd_rebuild_index(args):
    root = get_root(args)
    result = index.rebuild(root)

    def human():
        out("index rebuilt: %s" % result["db"])
        out("  records: %d  edges: %d  fts5: %s" % (
            result["records"], result["edges"], result["fts5"]))
        for path, reason in result["errors"]:
            out("  WARN unreadable: %s (%s)" % (path, reason))
    emit(args, result, human)
    return EXIT_OK


def cmd_graph_export(args):
    root = get_root(args)
    data, path = graph.export(root)

    def human():
        out("graph exported: %s" % path)
        out("  nodes: %d  edges: %d  dangling: %d" % (
            data["counts"]["nodes"], data["counts"]["edges"],
            data["counts"]["dangling_edges"]))
    emit(args, {"path": path, "counts": data["counts"]}, human)
    return EXIT_OK


def cmd_status(args):
    root = get_root(args)
    data, status_path, json_path = status.write(root)

    def human():
        totals = data["totals"]
        out("AI Knowledge Vault - %s" % root)
        out("  records %d | sources %d | claims %d | entities %d | decisions %d | "
            "runs %d | reviews %d" % (
                totals["records"], totals["sources"], totals["claims"],
                totals["entities"], totals["decisions"], totals["runs"],
                totals["reviews"]))
        claims = data["claims"]
        out("  claims: verified %d, candidate %d, disputed %d, rejected %d, pending review %d"
            % (claims["verified"], claims["candidate"], claims["disputed"],
               claims["rejected"], claims["pending_review"]))
        sec = data["security"]
        out("  security: quarantined %d, flagged %d, warnings %d" % (
            sec["quarantined_sources"], sec["flagged_sources"], sec["security_warnings"]))
        integrity = data["integrity"]
        out("  integrity: %s (%d FAIL / %d WARN), broken refs %d, dup hashes %d" % (
            integrity["validation_level"], integrity["fail_count"],
            integrity["warn_count"], integrity["broken_references"],
            len(integrity["duplicate_hashes"])))
        out("  wrote %s and %s" % (os.path.relpath(status_path, root),
                                   os.path.relpath(json_path, root)))
    emit(args, data, human)
    return EXIT_OK


# ------------------------------------------------------------------ health
def cmd_health_check(args):
    root = get_root(args)
    checks = []

    def add(name, ok, detail, remediation=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail,
                       "remediation": remediation})

    add("vault-root-readable", os.access(root, os.R_OK), root)
    add("vault-root-writable", os.access(root, os.W_OK), root,
        "fix directory permissions before ingesting")
    for directory in config.ALL_DIRS:
        if not os.path.isdir(os.path.join(root, directory)):
            add("dir-%s" % directory, False, "missing", "run vault.py init")
    add("structure-complete", all(os.path.isdir(os.path.join(root, d))
                                  for d in config.ALL_DIRS), "all required directories")
    add("fts5", index.fts5_available(), "SQLite FTS5",
        "search falls back to LIKE matching if unavailable")
    stale, why = index.index_is_stale(root)
    add("index-current", not stale, why, "run vault.py rebuild-index")
    add("graph-present", os.path.isfile(graph.graph_path(root)), graph.graph_path(root),
        "run vault.py graph-export")
    add("trust-policy-present", os.path.isfile(
        os.path.join(root, "config", "trust-policy.yaml")), "config/trust-policy.yaml",
        "run vault.py init")
    add("claude-md-present", os.path.isfile(os.path.join(root, "CLAUDE.md")), "CLAUDE.md")
    placeholders = records.icloud_placeholder_scan(root)
    add("files-locally-available", not placeholders,
        "%d unavailable/zero-byte file(s)" % len(placeholders),
        "open them in Finder to download, or run `brctl download <path>`; "
        "autonomous processing needs the vault to be locally available")
    git_status = gitprov.status(root)
    add("git-initialized", git_status["initialized"],
        git_status.get("git_dir"), "run vault.py commit or vault.py init")
    add("git-metadata-outside-sync", not os.path.exists(os.path.join(root, ".git")),
        "no .git inside the synchronized folder",
        "git metadata must not live in iCloud; see docs/VERSION-CONTROL.md")
    backups = backup.list_backups(root=root)
    add("backup-exists", bool(backups),
        "%d backup(s) in %s" % (len(backups), config.backup_dir(root)),
        "run vault.py backup")
    level, issues = validate.validate(root)
    add("validation", level != validate.FAIL, "validation=%s" % level,
        "run vault.py validate for per-record remediation")

    failed = [c for c in checks if not c["ok"]]
    data = {"root": root, "checks": checks, "failed": len(failed),
            "validation_level": level}

    def human():
        for check in checks:
            out("[%s] %-28s %s" % ("PASS" if check["ok"] else "FAIL",
                                   check["check"], check["detail"]))
            if not check["ok"] and check["remediation"]:
                out("       fix: %s" % check["remediation"])
        out("")
        out("HEALTH: %s (%d/%d checks passed)" % (
            "OK" if not failed else "ATTENTION NEEDED",
            len(checks) - len(failed), len(checks)))
    emit(args, data, human)
    return EXIT_OK if not failed else EXIT_FAIL


# ------------------------------------------------------------------ backup
def cmd_backup(args):
    root = get_root(args)
    result = backup.create(root, dest_dir=args.dest, label=args.label)
    verification = backup.verify(result["archive"])
    result["verified"] = verification["ok"]
    result["verification"] = verification

    def human():
        out("backup created: %s" % result["archive"])
        out("  files: %d  size: %d bytes" % (result["files"], result["bytes"]))
        out("  sha256: %s" % result["sha256"])
        out("  restore-verified: %s (%d files checked)" % (
            verification["ok"], verification["files"]))
        if not verification["ok"]:
            out("  PROBLEMS: %s" % verification)
    emit(args, result, human)
    return EXIT_OK if verification["ok"] else EXIT_FAIL


def cmd_verify_backup(args):
    result = backup.verify(args.archive)

    def human():
        out("archive : %s" % args.archive)
        out("verified: %s (%d files)" % (result["ok"], result["files"]))
        for name in result["mismatched"]:
            out("  MISMATCH %s" % name)
        for name in result["missing"]:
            out("  MISSING  %s" % name)
        for error in result["errors"]:
            out("  ERROR    %s" % error)
    emit(args, result, human)
    return EXIT_OK if result["ok"] else EXIT_FAIL


def cmd_restore(args):
    if not args.yes:
        out("Restore is a high-impact operation and needs explicit confirmation.")
        out("  archive     : %s" % args.archive)
        out("  destination : %s" % args.dest)
        out("Re-run with --yes to proceed. Restore into a NEW empty directory, "
            "inspect it, then move it into place (docs/RECOVERY.md).")
        return EXIT_FAIL
    try:
        dest = backup.restore(args.archive, args.dest, force=args.force)
    except RuntimeError as exc:
        out("ERROR: %s" % exc)
        return EXIT_ERROR
    out("restored to %s" % dest)
    out("next: python3 %s/scripts/vault.py rebuild-index --vault %s" % (dest, dest))
    return EXIT_OK


# ------------------------------------------------------------------ review
def cmd_review(args):
    root = get_root(args)
    run = runs.Run(root, "review %s -> %s" % (args.id, args.decision),
                   trigger="cli", skill="review-claim", inputs=[args.id])
    result, review_id = review.run_gate(
        root, args.id, args.decision, reviewer=args.reviewer,
        reviewer_role=args.role, rationale=args.rationale or "",
        author=args.author, run_id=run.id, force=args.force)
    run.read(args.id)
    if review_id:
        run.created(review_id)
        run.modified(args.id)
    run.review_result = result.decision if result.decision in schema.REVIEW_RESULT else "not-run"
    for check in result.checks:
        run.note("%s: %s - %s" % (check["check"], check["outcome"], check["detail"]))
    for blocker in result.blocking:
        run.warn(blocker)
    level, _ = validate.validate(root, check_indexes=False)
    run.validation_result = level
    run_id = run.finish("success" if result.decision != "blocked" else "partial")
    index.rebuild(root)
    graph.export(root)
    if result.decision != "blocked":
        autocommit(root, "vault: review %s -> %s (run %s)" % (args.id, args.decision, run_id),
                   not args.no_commit)
    data = result.as_dict()
    data["run_id"] = run_id

    def human():
        out("Review gate for %s" % args.id)
        for check in result.checks:
            out("  [%-4s] %-20s %s" % (check["outcome"], check["check"], check["detail"]))
        out("")
        if result.decision == "blocked":
            out("DECISION: BLOCKED - the gate refused this decision.")
            for blocker in result.blocking:
                out("  blocker: %s" % blocker)
            out("  Resolve the blockers, or use --force with an explicit rationale "
                "(recorded in the review).")
        else:
            out("DECISION: %s   review record: %s" % (result.decision.upper(), review_id))
        out("run: %s" % run_id)
    emit(args, data, human)
    return EXIT_OK if result.decision != "blocked" else EXIT_FAIL


def cmd_contradictions(args):
    root = get_root(args)
    found = contradiction.scan_vault(root, threshold=args.threshold)

    def human():
        if not found:
            out("no contradiction or duplicate candidates found")
            return
        for pair in found:
            out("%s  %s  %s   (similarity %.2f)%s" % (
                pair["a"], pair["relationship"], pair["b"], pair["similarity"],
                "" if pair["declared"] else "   [UNDECLARED]"))
            out("    a: %s" % pair["a_title"])
            out("    b: %s" % pair["b_title"])
            out("    why: %s" % pair["rationale"])
        out("")
        out("%d candidate(s). These are PROPOSALS. Newer is never assumed correct; "
            "nothing is deleted to simplify the graph." % len(found))
    emit(args, found, human)
    return EXIT_OK


# ------------------------------------------------------------------ new record
def cmd_new(args):
    root = get_root(args)
    if args.type not in schema.SCHEMAS:
        out("unknown type %r; choose from %s" % (args.type, ", ".join(sorted(schema.SCHEMAS))))
        return EXIT_ERROR
    record_id = ids.new_id(args.type)
    now = ids.now_iso()
    meta = {"id": record_id, "type": args.type, "title": args.title,
            "created_at": now, "updated_at": now,
            "trust_level": args.trust or "internal"}
    if args.type == "claim":
        meta.update({"status": "candidate", "sources": args.source or [],
                     "source_quality": args.source_quality or "unknown",
                     "evidence_strength": "weak", "verification_status": "unverified",
                     "review_status": "pending", "supports": [], "contradicts": [],
                     "supersedes": [], "superseded_by": [], "entities": [],
                     "projects": [], "related_to": []})
    elif args.type == "entity":
        meta.update({"status": "candidate", "entity_type": args.entity_type or "concept",
                     "aliases": [], "sources": args.source or [], "related_to": []})
    elif args.type == "decision":
        meta.update({"status": "proposed", "review_status": "pending",
                     "claims": [], "sources": args.source or [], "related_to": []})
    elif args.type == "project":
        meta.update({"status": "active", "related_to": []})
    elif args.type == "artifact":
        meta.update({"status": "candidate", "artifact_type": "document",
                     "review_status": "pending", "related_to": []})
    else:
        out("use the dedicated command for %s records" % args.type)
        return EXIT_ERROR
    if args.demo:
        meta["demo"] = True
    body = args.body or "## Proposition\n\n%s\n\n## Evidence\n\n(to be supplied)\n\n" \
                        "## Uncertainty\n\nUnreviewed candidate.\n" % args.title
    record = records.save(root, meta, body)
    index.rebuild(root)
    graph.export(root)
    autocommit(root, "vault: create %s" % record_id, not args.no_commit)

    def human():
        out("created %s" % record_id)
        out("  %s" % record.rel_path())
    emit(args, {"id": record_id, "path": record.rel_path()}, human)
    return EXIT_OK


# ------------------------------------------------------------------ git
def cmd_provenance(args):
    root = get_root(args)
    record = records.find(root, args.id)
    if record is None:
        out("no record with id %s" % args.id)
        return EXIT_FAIL
    history = gitprov.provenance(root, record.rel_path())
    run_ids = [record.get("run_id")] if record.get("run_id") else []

    def human():
        out("Provenance for %s" % args.id)
        out("  file      : %s" % record.rel_path())
        out("  hash      : %s" % record.get("content_hash"))
        out("  created   : %s" % record.get("created_at"))
        out("  updated   : %s" % record.get("updated_at"))
        out("  run       : %s" % (", ".join(run_ids) or "none"))
        out("  sources   : %s" % (", ".join(record.reflist("sources")) or "none"))
        out("  reviewers : %s" % (", ".join(record.reflist("reviewed_by")) or "none"))
        out("  git history:")
        if not history:
            out("    (no commits recorded for this path)")
        for entry in history:
            out("    %s  %s  %s" % (entry["sha"][:10], entry["date"], entry["subject"]))
    emit(args, {"record": record.meta, "git": history}, human)
    return EXIT_OK


def cmd_commit(args):
    root = get_root(args)
    if not gitprov.available():
        out("git is not available")
        return EXIT_ERROR
    result = gitprov.commit(root, args.message)

    def human():
        if result["committed"]:
            out("committed %s" % result["sha"][:10])
        else:
            out("nothing to commit (%s)" % result["reason"])
    emit(args, result, human)
    return EXIT_OK


def cmd_log(args):
    root = get_root(args)
    entries = gitprov.log(root, limit=args.limit)

    def human():
        for entry in entries:
            out("%s  %s  %s" % (entry["sha"][:10], entry["date"], entry["subject"]))
        if not entries:
            out("no commits")
    emit(args, entries, human)
    return EXIT_OK


# ------------------------------------------------------------------ doctor
def cmd_doctor(args):
    """Environment preflight. Runs even when no vault exists yet."""
    import platform
    info = {
        "platform": platform.platform(),
        "system": platform.system(),
        "is_macos": config.is_macos(),
        "python": sys.version.split()[0],
        "sqlite_fts5": index.fts5_available(),
        "git": gitprov.available(),
        "icloud_container": config.icloud_container(),
        "detected_default_root": config.detect_default_root(),
        "pointer_file": config.POINTER_FILE,
        "pointer_value": None,
        "env_vault_root": os.environ.get("VAULT_ROOT"),
        "schema_version": SCHEMA_VERSION,
    }
    if os.path.isfile(config.POINTER_FILE):
        with open(config.POINTER_FILE, encoding="utf-8") as fh:
            info["pointer_value"] = fh.read().strip()
    try:
        info["resolved_root"] = config.resolve_root(getattr(args, "vault", None))
        info["resolved"] = True
    except config.VaultRootError as exc:
        info["resolved_root"] = None
        info["resolved"] = False
        info["resolution_error"] = str(exc)

    def human():
        out("Environment preflight")
        out("  platform          : %s" % info["platform"])
        out("  macOS             : %s" % info["is_macos"])
        out("  python            : %s" % info["python"])
        out("  sqlite FTS5       : %s" % info["sqlite_fts5"])
        out("  git               : %s" % info["git"])
        out("  iCloud container  : %s" % (info["icloud_container"] or
                                          "NOT FOUND (macOS only)"))
        out("  default vault root: %s" % (info["detected_default_root"] or "undetermined"))
        out("  $VAULT_ROOT       : %s" % (info["env_vault_root"] or "unset"))
        out("  pointer file      : %s = %s" % (info["pointer_file"],
                                               info["pointer_value"] or "unset"))
        out("")
        if info["resolved"]:
            out("  RESOLVED VAULT    : %s" % info["resolved_root"])
        else:
            out("  NO VAULT RESOLVED. %s" % info["resolution_error"].split("\n")[0])
            out("  " + "\n  ".join(info.get("resolution_error", "").split("\n")[1:]))
    emit(args, info, human)
    return EXIT_OK


# ------------------------------------------------------------------ parser
def build_parser():
    parser = argparse.ArgumentParser(
        prog="vault.py",
        description="AI Knowledge Vault - local-first, evidence-first knowledge store.",
        epilog="The Markdown records are authoritative. Indexes are rebuildable. "
               "Nothing becomes verified without passing the review gate.")
    parser.add_argument("--vault", help="vault root (else $VAULT_ROOT, else the "
                                        "pointer file, else macOS iCloud auto-detect)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")

    # Accept --vault/--json on either side of the subcommand. SUPPRESS keeps an
    # omitted subcommand flag from clobbering the value given before it.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--vault", default=argparse.SUPPRESS,
                        help="vault root (same as the global --vault)")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="machine-readable output")

    sub = parser.add_subparsers(dest="command", parser_class=argparse.ArgumentParser)
    _add = sub.add_parser

    def add_parser(name, **kwargs):
        kwargs.setdefault("parents", [common])
        return _add(name, **kwargs)
    sub.add_parser = add_parser

    p = sub.add_parser("init", help="create or complete the vault structure (never overwrites)")
    p.add_argument("--no-git", action="store_true")
    p.add_argument("--remember", action="store_true",
                   help="record this root in ~/.config/ai-knowledge-vault/vault-root")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("ingest", help="ingest a file or directory through the full pipeline")
    p.add_argument("path")
    p.add_argument("--trust", choices=schema.TRUST, help="override the policy trust level")
    p.add_argument("--origin", help="logical origin (URL, mailbox, ticket)")
    p.add_argument("--revises", help="source id this supersedes (creates version N+1)")
    p.add_argument("--extract-claims", action="store_true",
                   help="draft candidate claims (never verified)")
    p.add_argument("--trigger", default="cli")
    p.add_argument("--demo", action="store_true", help="mark as synthetic demo data")
    p.add_argument("--no-commit", action="store_true")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("validate", help="validate every record; PASS / WARN / FAIL")
    p.add_argument("--strict", action="store_true", help="treat WARN as FAIL")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("search", help="full-text and metadata search")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--type", choices=sorted(schema.SCHEMAS))
    p.add_argument("--status")
    p.add_argument("--trust", choices=schema.TRUST)
    p.add_argument("--review", choices=schema.REVIEW)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--rebuild", action="store_true", help="rebuild the index first")
    p.add_argument("--no-demo", action="store_true", help="exclude synthetic demo records")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("show", help="print one record by id")
    p.add_argument("id")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("related", help="traverse relationships from a record")
    p.add_argument("id")
    p.add_argument("--depth", type=int, default=1)
    p.set_defaults(func=cmd_related)

    p = sub.add_parser("rebuild-index", help="rebuild indexes/vault.db from Markdown")
    p.set_defaults(func=cmd_rebuild_index)

    p = sub.add_parser("graph-export", help="rebuild indexes/graph.json from Markdown")
    p.set_defaults(func=cmd_graph_export)

    p = sub.add_parser("status", help="write STATUS.md and indexes/status.json")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("health-check", help="structural and operational health checks")
    p.set_defaults(func=cmd_health_check)

    p = sub.add_parser("backup", help="create and verify a canonical-files backup")
    p.add_argument("--dest")
    p.add_argument("--label")
    p.set_defaults(func=cmd_backup)

    p = sub.add_parser("verify-backup", help="prove an archive is restorable")
    p.add_argument("archive")
    p.set_defaults(func=cmd_verify_backup)

    p = sub.add_parser("restore", help="restore an archive into an empty directory")
    p.add_argument("archive")
    p.add_argument("dest")
    p.add_argument("--yes", action="store_true", help="required: explicit confirmation")
    p.add_argument("--force", action="store_true", help="allow a non-empty destination")
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("review", help="run the review gate on a record")
    p.add_argument("id")
    p.add_argument("decision", choices=schema.REVIEW_RESULT)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--role", default="reviewer")
    p.add_argument("--author", help="who authored the record (independence check)")
    p.add_argument("--rationale")
    p.add_argument("--force", action="store_true",
                   help="override blocking checks; the override is recorded")
    p.add_argument("--no-commit", action="store_true")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("contradictions", help="scan claims for contradiction candidates")
    p.add_argument("--threshold", type=float, default=0.30)
    p.set_defaults(func=cmd_contradictions)

    p = sub.add_parser("new", help="create a record from a template")
    p.add_argument("type", choices=["claim", "entity", "decision", "project", "artifact"])
    p.add_argument("title")
    p.add_argument("--body")
    p.add_argument("--source", action="append", help="source id (repeatable)")
    p.add_argument("--source-quality", choices=schema.SOURCE_QUALITY)
    p.add_argument("--entity-type")
    p.add_argument("--trust", choices=schema.TRUST)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--no-commit", action="store_true")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("provenance", help="show evidence and git history for a record")
    p.add_argument("id")
    p.set_defaults(func=cmd_provenance)

    p = sub.add_parser("commit", help="commit the working tree to the vault git history")
    p.add_argument("-m", "--message", default="vault: manual commit")
    p.set_defaults(func=cmd_commit)

    p = sub.add_parser("log", help="show vault git history")
    p.add_argument("--limit", type=int, default=15)
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("doctor", help="environment preflight (works without a vault)")
    p.set_defaults(func=cmd_doctor)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return EXIT_OK
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
