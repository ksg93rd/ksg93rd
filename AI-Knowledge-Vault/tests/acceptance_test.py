#!/usr/bin/env python3
"""End-to-end acceptance test — the 20-step synthetic workflow.

This is not a unit test. It drives the real CLI against a real vault and
asserts on real output, then records itself as a RUN record inside that vault
so the acceptance run is part of the vault's own audit trail.

  python3 tests/acceptance_test.py --vault <root>          # against a vault
  python3 tests/acceptance_test.py                         # temporary vault
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))

from vaultlib import backup, graph, ids, index, records, runs, validate

STEPS = []
FAILURES = []


def step(number, title, ok, detail=""):
    STEPS.append({"step": number, "title": title, "ok": bool(ok), "detail": detail})
    marker = "PASS" if ok else "FAIL"
    print("[%s] %2d. %s%s" % (marker, number, title, ("  — " + detail) if detail else ""))
    if not ok:
        FAILURES.append("%d. %s: %s" % (number, title, detail))
    return ok


def run_cli(vault, *args):
    cmd = [sys.executable, os.path.join(vault, "scripts", "vault.py"),
           "--vault", vault] + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def run_json(vault, *args):
    code, out = run_cli(vault, "--json", *args)
    try:
        return code, json.loads(out)
    except ValueError:
        return code, {"_raw": out}


SOURCE_TEXT = """# ACCEPTANCE - Synthetic Operations Note

SYNTHETIC TEST DATA. Describes no real organization.

Median API response latency decreased from 420 ms to 180 ms after the June 2026
caching rollout.

Support ticket volume decreased by 31 percent in Q2 2026 compared with Q1 2026.
"""

CONTRA_TEXT = """# ACCEPTANCE - Conflicting Synthetic Note

SYNTHETIC TEST DATA.

Median API response latency increased from 180 ms to 420 ms after the June 2026
caching rollout.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", help="vault to test against (default: a temp copy)")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()

    workdir = tempfile.mkdtemp(prefix="vault-acceptance-")
    if args.vault:
        vault = args.vault
        owned = False
    else:
        vault = os.path.join(workdir, "AI-Knowledge-Vault")
        shutil.copytree(REPO, vault, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", "vault.db", ".git"))
        owned = True
        os.environ["VAULT_GIT_DIR"] = os.path.join(workdir, "git", "vault.git")
        os.environ["VAULT_BACKUP_DIR"] = os.path.join(workdir, "backups")
        code, out = run_cli(vault, "init")
        if code != 0:
            print(out)
            return 2

    inputs = os.path.join(workdir, "inputs")
    os.makedirs(inputs)
    src_path = os.path.join(inputs, "acceptance-note.md")
    with open(src_path, "w", encoding="utf-8") as fh:
        fh.write(SOURCE_TEXT)
    contra_path = os.path.join(inputs, "acceptance-contra.md")
    with open(contra_path, "w", encoding="utf-8") as fh:
        fh.write(CONTRA_TEXT)

    print("Acceptance test — vault: %s\n" % vault)
    run = runs.Run(vault, "end-to-end acceptance test (20-step synthetic workflow)",
                   trigger="tests/acceptance_test.py", agent="vault-cli",
                   skill="daily-triage", inputs=[src_path, contra_path], demo=True)

    # 1-3. ingest a synthetic source, create its record, hash it -------------
    code, data = run_json(vault, "ingest", src_path, "--demo", "--extract-claims",
                          "--origin", "file://acceptance/note.md")
    first = (data.get("results") or [{}])[0]
    source_id = first.get("source_id")
    step(1, "Ingest a synthetic source", code == 0 and first.get("status") == "ingested",
         "status=%s" % first.get("status"))
    record = records.find(vault, source_id) if source_id else None
    step(2, "Source record created", record is not None and record.type == "source",
         source_id or "none")
    chash = record.get("content_hash") if record else None
    step(3, "Content hashed (sha256)", bool(chash) and chash.startswith("sha256:")
         and len(chash) == 71, chash or "missing")
    if source_id:
        run.created(source_id)

    # 4-5. duplicate ingestion is detected -----------------------------------
    code, dup = run_json(vault, "ingest", src_path, "--demo")
    dup_first = (dup.get("results") or [{}])[0]
    step(4, "Attempt duplicate ingestion", code == 0, "re-ingested the same bytes")
    step(5, "Duplicate detected, not duplicated",
         dup_first.get("status") == "duplicate" and dup_first.get("duplicate_of") == source_id,
         "status=%s reused=%s" % (dup_first.get("status"), dup_first.get("duplicate_of")))

    # 6. candidate claims ----------------------------------------------------
    claims = [r for r in records.load_all(vault)[0]
              if r.type == "claim" and source_id in r.reflist("sources")]
    step(6, "Candidate claims extracted", len(claims) >= 2,
         "%d claim(s), all candidate/unverified: %s" % (
             len(claims), all(c.get("status") == "candidate" and
                              c.get("verification_status") == "unverified" for c in claims)))
    for claim in claims:
        run.created(claim.id)

    # 7. retrieve related knowledge -----------------------------------------
    code, related = run_json(vault, "related", source_id)
    step(7, "Retrieve related knowledge", code == 0 and len(related.get("edges", [])) >= 2,
         "%d edge(s) from the source" % len(related.get("edges", [])))

    # 8. detect a contradiction ---------------------------------------------
    run_json(vault, "ingest", contra_path, "--demo", "--extract-claims",
             "--origin", "file://acceptance/contra.md")
    code, found = run_json(vault, "contradictions")
    conflict = [f for f in found if f.get("relationship") == "CONTRADICTS"] \
        if isinstance(found, list) else []
    step(8, "Contradiction detected", bool(conflict),
         "%d contradiction candidate(s)" % len(conflict))

    latency_claims = [r for r in records.load_all(vault)[0]
                      if r.type == "claim" and "latency" in (r.title or "").lower()]
    decreased = next((c for c in latency_claims if "decreased" in c.title.lower()), None)
    increased = next((c for c in latency_claims if "increased" in c.title.lower()), None)
    supported = next((c for c in claims if "ticket" in (c.title or "").lower()), None)

    # 9-10. independent review, approve a supported claim ---------------------
    approved_ok = False
    if supported is not None:
        code, gate = run_json(vault, "review", supported.id, "approved",
                              "--reviewer", "acceptance-reviewer",
                              "--author", "vault-cli",
                              "--rationale", "figure appears verbatim in the cited source")
        independent = any(c["check"] == "independence" and c["outcome"] == "PASS"
                          for c in gate.get("checks", []))
        step(9, "Independent review performed",
             bool(gate.get("checks")) and independent,
             "%d gate checks, independence=%s" % (len(gate.get("checks", [])), independent))
        updated = records.find(vault, supported.id)
        approved_ok = (updated.get("status") == "verified" and
                       updated.get("review_status") == "approved" and
                       updated.get("verification_status") == "verified")
        step(10, "Supported claim approved -> verified", approved_ok,
             "status=%s review=%s" % (updated.get("status"), updated.get("review_status")))
        run.modified(supported.id)
        if gate.get("review_id"):
            run.created(gate["review_id"])
    else:
        step(9, "Independent review performed", False, "no supported claim found")
        step(10, "Supported claim approved -> verified", False, "skipped")

    # 11. dispute the unsupported/conflicting claim --------------------------
    disputed_ok = False
    if increased is not None:
        code, blocked = run_json(vault, "review", increased.id, "approved",
                                 "--reviewer", "acceptance-reviewer", "--author", "vault-cli")
        gate_blocked = blocked.get("decision") == "blocked"
        code, gate2 = run_json(vault, "review", increased.id, "disputed",
                               "--reviewer", "acceptance-reviewer", "--author", "vault-cli",
                               "--rationale", "contradicts the decrease claim; both retained")
        updated = records.find(vault, increased.id)
        disputed_ok = updated.get("status") == "disputed" and gate_blocked
        step(11, "Conflicting claim disputed (approval blocked first)", disputed_ok,
             "approval blocked=%s, final status=%s" % (gate_blocked, updated.get("status")))
        run.modified(increased.id)
        if gate2.get("review_id"):
            run.created(gate2["review_id"])
    else:
        step(11, "Conflicting claim disputed", False, "no conflicting claim found")

    # 12. commit canonical changes ------------------------------------------
    code, commit = run_json(vault, "commit", "-m", "acceptance: canonical commit")
    code2, log = run_json(vault, "log", "--limit", "5")
    step(12, "Canonical changes committed to git", code2 == 0 and len(log) >= 1,
         "%d commit(s) in history" % len(log))

    # 13-14. rebuild derived artifacts ---------------------------------------
    os.path.isfile(index.db_path(vault)) and os.unlink(index.db_path(vault))
    code, rebuilt = run_json(vault, "rebuild-index")
    step(13, "SQLite index rebuilt from canonical files",
         code == 0 and rebuilt.get("records", 0) > 0,
         "%s records, %s edges, fts5=%s" % (rebuilt.get("records"),
                                            rebuilt.get("edges"), rebuilt.get("fts5")))
    gpath = graph.graph_path(vault)
    os.path.isfile(gpath) and os.unlink(gpath)
    code, exported = run_json(vault, "graph-export")
    counts = exported.get("counts", {})
    step(14, "Graph rebuilt from canonical files",
         code == 0 and counts.get("nodes", 0) > 0 and counts.get("dangling_edges") == 0,
         "%s nodes, %s edges, %s dangling" % (counts.get("nodes"), counts.get("edges"),
                                              counts.get("dangling_edges")))

    # 15. validator ----------------------------------------------------------
    code, report = run_json(vault, "validate")
    level = report.get("level")
    fails = [i for i in report.get("issues", []) if i["level"] == "FAIL"]
    step(15, "Validator run", level in ("PASS", "WARN"),
         "%s (%d FAIL, %d WARN)" % (level, len(fails),
                                    len(report.get("issues", [])) - len(fails)))
    for issue in fails:
        print("        FAIL %s: %s" % (issue.get("record"), issue.get("reason")))
    run.validation_result = level

    # 16. status -------------------------------------------------------------
    code, status_data = run_json(vault, "status")
    step(16, "STATUS generated", code == 0 and os.path.isfile(os.path.join(vault, "STATUS.md"))
         and os.path.isfile(os.path.join(vault, "indexes", "status.json")),
         "%s records tracked" % status_data.get("totals", {}).get("records"))

    # 17. provenance ---------------------------------------------------------
    target = supported.id if supported else (source_id or "")
    code, prov = run_json(vault, "provenance", target)
    has_evidence = bool(prov.get("record", {}).get("sources") or
                        prov.get("record", {}).get("content_hash"))
    step(17, "Provenance verified", code == 0 and has_evidence and bool(prov.get("git")),
         "%d commit(s), evidence chain present" % len(prov.get("git", [])))

    # 18. search retrieval ---------------------------------------------------
    code, hits = run_json(vault, "search", "latency")
    step(18, "Search retrieval demonstrated", code == 0 and len(hits) >= 2,
         "%d hit(s) for 'latency'" % len(hits))

    # 19. backup -------------------------------------------------------------
    code, made = run_json(vault, "backup", "--label", "acceptance")
    archive = made.get("archive")
    step(19, "Backup created and verified", code == 0 and made.get("verified") is True,
         "%s files, verified=%s" % (made.get("files"), made.get("verified")))

    # 20. recovery -----------------------------------------------------------
    restore_dir = os.path.join(workdir, "restore-check")
    recovered = False
    detail = "no archive"
    if archive:
        try:
            backup.restore(archive, restore_dir)
            rebuilt = index.rebuild(restore_dir)
            rlevel, rissues = validate.validate(restore_dir)
            restored_claim = records.find(restore_dir, target)
            recovered = (restored_claim is not None and rlevel != "FAIL"
                         and rebuilt["records"] > 0)
            detail = "%d records restored, validation=%s" % (rebuilt["records"], rlevel)
        except Exception as exc:            # noqa: BLE001 - report, never mask
            detail = "restore failed: %s" % exc
    step(20, "Recovery procedure validated", recovered, detail)

    # ---- record the acceptance test as a RUN -------------------------------
    for entry in STEPS:
        run.note("step %d %s: %s%s" % (entry["step"], "PASS" if entry["ok"] else "FAIL",
                                       entry["title"],
                                       (" — " + entry["detail"]) if entry["detail"] else ""))
    for failure in FAILURES:
        run.error(failure)
    run.review_result = "approved" if approved_ok else "not-run"
    run_id = run.finish("success" if not FAILURES else "failed")
    run_cli(vault, "rebuild-index")
    run_cli(vault, "status")

    passed = sum(1 for s in STEPS if s["ok"])
    print("\nACCEPTANCE: %d/%d steps passed" % (passed, len(STEPS)))
    print("recorded as RUN %s in %s" % (run_id, os.path.join(vault, "70-runs")))
    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print("  " + failure)
    if owned and not args.keep:
        print("\n(temporary vault at %s — pass --keep to retain it)" % vault)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
