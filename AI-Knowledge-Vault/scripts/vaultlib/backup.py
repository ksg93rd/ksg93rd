"""Backup, restore validation, and recovery helpers.

A backup protects CANONICAL files. Derived indexes are deliberately excluded:
they are rebuildable and including them would make backups large and stale.
"""
import hashlib
import json
import os
import tarfile

from . import SCHEMA_VERSION, config, ids, records

CANONICAL_TOP = ["00-inbox", "10-claims", "20-sources", "30-entities", "40-decisions",
                 "50-artifacts", "60-projects", "70-runs", "80-reviews", "90-archive",
                 "schemas", "templates", "config", "docs", "scripts", "tests",
                 ".claude", "CLAUDE.md", "README.md", "CHANGELOG.md"]
EXCLUDE_NAMES = {"__pycache__", ".DS_Store", "vault.db", "vault.db-journal",
                 "vault.db-wal", "vault.db-shm"}


def _members(root):
    for entry in CANONICAL_TOP:
        full = os.path.join(root, entry)
        if os.path.isfile(full):
            yield full, entry
        elif os.path.isdir(full):
            for dirpath, dirnames, filenames in os.walk(full):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDE_NAMES]
                for name in sorted(filenames):
                    if name in EXCLUDE_NAMES or name.startswith(".vault-tmp-"):
                        continue
                    path = os.path.join(dirpath, name)
                    yield path, os.path.relpath(path, root)


def create(root, dest_dir=None, label=None):
    dest_dir = dest_dir or config.backup_dir(root)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    stamp = ids.now_iso().replace(":", "").replace("-", "")[:15]
    name = "vault-backup-%s%s.tar.gz" % (stamp, ("-" + label) if label else "")
    archive = os.path.join(dest_dir, name)

    manifest = {"schema_version": SCHEMA_VERSION, "created_at": ids.now_iso(),
                "vault_root": root, "files": {}, "note": "Derived indexes are excluded "
                "by design; rebuild them with vault.py rebuild-index && graph-export."}
    count = 0
    with tarfile.open(archive, "w:gz") as tar:
        for path, arcname in _members(root):
            tar.add(path, arcname=os.path.join("vault", arcname))
            manifest["files"][arcname] = records.sha256_file(path)
            count += 1
        manifest_path = archive + ".manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)
        tar.add(manifest_path, arcname="vault/BACKUP-MANIFEST.json")
    archive_hash = records.sha256_file(archive)
    with open(archive + ".sha256", "w", encoding="utf-8") as fh:
        fh.write("%s  %s\n" % (archive_hash.split(":", 1)[1], os.path.basename(archive)))
    return {"archive": archive, "manifest": manifest_path, "files": count,
            "sha256": archive_hash, "bytes": os.path.getsize(archive)}


def verify(archive):
    """Prove a backup is restorable WITHOUT touching the live vault."""
    result = {"archive": archive, "ok": False, "files": 0, "mismatched": [],
              "missing": [], "errors": []}
    if not os.path.isfile(archive):
        result["errors"].append("archive not found")
        return result
    try:
        with tarfile.open(archive, "r:gz") as tar:
            names = tar.getnames()
            manifest_member = "vault/BACKUP-MANIFEST.json"
            if manifest_member not in names:
                result["errors"].append("archive has no BACKUP-MANIFEST.json")
                return result
            manifest = json.loads(tar.extractfile(manifest_member).read().decode("utf-8"))
            for arcname, expected in manifest["files"].items():
                member = "vault/" + arcname
                if member not in names:
                    result["missing"].append(arcname)
                    continue
                data = tar.extractfile(member).read()
                actual = "sha256:" + hashlib.sha256(data).hexdigest()
                if actual != expected:
                    result["mismatched"].append(arcname)
                result["files"] += 1
    except (tarfile.TarError, ValueError, KeyError) as exc:
        result["errors"].append("unreadable archive: %s" % exc)
        return result
    result["ok"] = not (result["mismatched"] or result["missing"] or result["errors"])
    return result


def restore(archive, dest, force=False):
    """Restore into an EMPTY destination. Never overwrites a populated vault."""
    if os.path.isdir(dest) and os.listdir(dest) and not force:
        raise RuntimeError(
            "refusing to restore into a non-empty directory: %s\n"
            "  restore to a new path, inspect it, then move it into place "
            "(see docs/RECOVERY.md)" % dest)
    if not os.path.isdir(dest):
        os.makedirs(dest)
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            name = member.name
            if name.startswith("/") or ".." in name.split("/"):
                raise RuntimeError("unsafe path in archive: %s" % name)
            if not name.startswith("vault/"):
                continue
            member.name = name[len("vault/"):]
            if not member.name:
                continue
            tar.extract(member, dest)
    return dest


def list_backups(dest_dir=None, root=None):
    dest_dir = dest_dir or config.backup_dir(root or "")
    if not os.path.isdir(dest_dir):
        return []
    out = []
    for name in sorted(os.listdir(dest_dir), reverse=True):
        if name.endswith(".tar.gz"):
            path = os.path.join(dest_dir, name)
            out.append({"path": path, "bytes": os.path.getsize(path),
                        "mtime": os.path.getmtime(path)})
    return out
