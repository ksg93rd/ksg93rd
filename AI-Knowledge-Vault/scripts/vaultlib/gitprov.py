"""Git provenance with the repository metadata kept OUTSIDE synchronized storage.

Design (see docs/VERSION-CONTROL.md):
  working tree : <vault>                     (inside iCloud Drive)
  git metadata : ~/.ai-knowledge-vault/git/<hash>.git   (NOT synchronized)

Nothing git-related is written into the synced folder except a plain-text
`.gitignore`, so iCloud never syncs loose objects, refs, or index files, and
two Macs can never produce a corrupted shared `.git`.
"""
import os
import subprocess

from . import config

GITIGNORE = """# Derived, rebuildable artifacts - never the only copy of anything.
indexes/vault.db
indexes/vault.db-journal
indexes/vault.db-wal
indexes/vault.db-shm
indexes/*.rebuilding
__pycache__/
*.pyc
.DS_Store
.vault-tmp-*

# Never commit credentials.
*.env
.env
.env.*
*.pem
*.key
id_rsa*
credentials.json
secrets.yaml
secrets.yml
config/*.secret.*
"""


class GitError(RuntimeError):
    pass


def available():
    try:
        subprocess.check_output(["git", "--version"], stderr=subprocess.STDOUT)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _base(root):
    return ["git", "--git-dir=%s" % config.git_dir(root), "--work-tree=%s" % root]


def run(root, args, check=True):
    proc = subprocess.Popen(_base(root) + args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, cwd=root)
    out, _ = proc.communicate()
    text = out.decode("utf-8", "replace")
    if check and proc.returncode != 0:
        raise GitError("git %s failed (%d):\n%s" % (" ".join(args), proc.returncode, text))
    return proc.returncode, text


def is_initialized(root):
    gdir = config.git_dir(root)
    return os.path.isdir(gdir) and os.path.isfile(os.path.join(gdir, "HEAD"))


def init(root):
    """Idempotent. Safe to run on every Mac that syncs the vault."""
    gdir = config.git_dir(root)
    created = False
    if not is_initialized(root):
        parent = os.path.dirname(gdir)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        subprocess.check_call(["git", "init", "--bare", "--quiet", gdir])
        created = True
    run(root, ["config", "core.bare", "false"])
    run(root, ["config", "core.worktree", os.path.abspath(root)])
    run(root, ["config", "commit.gpgsign", "false"])
    run(root, ["config", "gc.auto", "0"])
    _, name = run(root, ["config", "user.name"], check=False)
    if not name.strip():
        run(root, ["config", "user.name", "Vault Owner"])
    _, email = run(root, ["config", "user.email"], check=False)
    if not email.strip():
        run(root, ["config", "user.email", "vault@localhost"])
    gitignore = os.path.join(root, ".gitignore")
    if not os.path.isfile(gitignore):
        with open(gitignore, "w", encoding="utf-8") as fh:
            fh.write(GITIGNORE)
    return {"git_dir": gdir, "created": created, "work_tree": root}


def status(root):
    if not is_initialized(root):
        return {"initialized": False, "dirty": None, "changes": [], "git_dir": config.git_dir(root)}
    _, out = run(root, ["status", "--porcelain"])
    changes = [line for line in out.split("\n") if line.strip()]
    _, head = run(root, ["rev-parse", "--short", "HEAD"], check=False)
    return {"initialized": True, "dirty": bool(changes), "changes": changes,
            "head": head.strip() or None, "git_dir": config.git_dir(root)}


def commit(root, message, paths=None, allow_empty=False):
    if not is_initialized(root):
        init(root)
    if paths:
        run(root, ["add", "--"] + list(paths))
    else:
        run(root, ["add", "-A", "."])
    code, out = run(root, ["diff", "--cached", "--quiet"], check=False)
    if code == 0 and not allow_empty:
        return {"committed": False, "reason": "nothing staged", "sha": None}
    args = ["commit", "-m", message]
    if allow_empty:
        args.append("--allow-empty")
    _, out = run(root, args)
    _, sha = run(root, ["rev-parse", "HEAD"])
    return {"committed": True, "sha": sha.strip(), "output": out.strip()}


def log(root, limit=15, path=None):
    if not is_initialized(root):
        return []
    args = ["log", "--pretty=format:%H|%an|%aI|%s", "-n", str(limit)]
    if path:
        args += ["--", path]
    _, out = run(root, args, check=False)
    entries = []
    for line in out.split("\n"):
        if line.count("|") >= 3:
            sha, author, when, subject = line.split("|", 3)
            entries.append({"sha": sha, "author": author, "date": when, "subject": subject})
    return entries


def provenance(root, rel_path):
    """Full commit history for one record: who changed it, when, and why."""
    return log(root, limit=50, path=rel_path)


def restore_path(root, rel_path, ref="HEAD"):
    """Roll one record back to a previous commit. Reversible; nothing is destroyed."""
    run(root, ["checkout", ref, "--", rel_path])
    return {"restored": rel_path, "from": ref}
