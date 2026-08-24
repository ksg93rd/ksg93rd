"""Vault root resolution and configuration.

Resolution order (first hit wins):
  1. explicit --vault PATH
  2. $VAULT_ROOT
  3. ~/.config/ai-knowledge-vault/vault-root  (a file containing one path)
  4. macOS iCloud Drive auto-detection
  5. failure -> the caller must ask the user; we NEVER invent an iCloud path.
"""
import os
import platform
import sys

from . import yamlite

VAULT_DIRNAME = "AI-Knowledge-Vault"
POINTER_FILE = os.path.join(
    os.path.expanduser("~"), ".config", "ai-knowledge-vault", "vault-root"
)

CANONICAL_DIRS = {
    "inbox": "00-inbox",
    "claim": "10-claims",
    "source": "20-sources",
    "entity": "30-entities",
    "decision": "40-decisions",
    "artifact": "50-artifacts",
    "project": "60-projects",
    "run": "70-runs",
    "review": "80-reviews",
    "archive": "90-archive",
}
QUARANTINE_DIR = os.path.join("90-archive", "quarantine")
ALL_DIRS = list(CANONICAL_DIRS.values()) + [
    QUARANTINE_DIR, "indexes", "schemas", "templates", "scripts", "config",
    "docs", "tests", ".claude",
]


class VaultRootError(RuntimeError):
    pass


def is_macos():
    return sys.platform == "darwin" or platform.system() == "Darwin"


def icloud_container():
    """Return the real iCloud Drive directory, or None. Never fabricates."""
    if not is_macos():
        return None
    base = os.path.join(os.path.expanduser("~"), "Library", "Mobile Documents")
    if not os.path.isdir(base):
        return None
    docs = os.path.join(base, "com~apple~CloudDocs")
    return docs if os.path.isdir(docs) else None


def detect_default_root():
    container = icloud_container()
    if container:
        return os.path.join(container, VAULT_DIRNAME)
    return None


def resolve_root(explicit=None, must_exist=True):
    candidates = []
    if explicit:
        candidates.append(("--vault", os.path.abspath(os.path.expanduser(explicit))))
    env = os.environ.get("VAULT_ROOT")
    if env:
        candidates.append(("$VAULT_ROOT", os.path.abspath(os.path.expanduser(env))))
    if os.path.isfile(POINTER_FILE):
        try:
            with open(POINTER_FILE, "r", encoding="utf-8") as fh:
                pointed = fh.read().strip()
            if pointed:
                candidates.append((POINTER_FILE, os.path.abspath(os.path.expanduser(pointed))))
        except OSError:
            pass
    auto = detect_default_root()
    if auto:
        candidates.append(("iCloud Drive auto-detect", auto))

    if not candidates:
        raise VaultRootError(
            "Cannot determine a vault root.\n"
            "  Platform: %s (iCloud Drive is a macOS feature)\n"
            "  Fix: run with --vault PATH, or export VAULT_ROOT=PATH, or write the\n"
            "       path into %s\n"
            "  Refusing to invent an iCloud location." % (platform.system(), POINTER_FILE)
        )
    if not must_exist:
        return candidates[0][1]
    for origin, path in candidates:
        if os.path.isdir(path):
            return path
    origin, path = candidates[0]
    raise VaultRootError(
        "Vault root does not exist: %s (from %s)\n"
        "  Run:  python3 scripts/vault.py init --vault '%s'" % (path, origin, path)
    )


def config_path(root):
    return os.path.join(root, "config", "vault.config.yaml")


def load_config(root):
    path = config_path(root)
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yamlite.loads(fh.read()) or {}


def load_trust_policy(root):
    path = os.path.join(root, "config", "trust-policy.yaml")
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yamlite.loads(fh.read()) or {}


def git_dir(root):
    """Git metadata lives OUTSIDE the synchronized folder. See docs/VERSION-CONTROL.md."""
    override = os.environ.get("VAULT_GIT_DIR")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    import hashlib
    tag = hashlib.sha256(os.path.abspath(root).encode("utf-8")).hexdigest()[:12]
    return os.path.join(os.path.expanduser("~"), ".ai-knowledge-vault", "git", tag + ".git")


def backup_dir(root):
    override = os.environ.get("VAULT_BACKUP_DIR")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    return os.path.join(os.path.expanduser("~"), ".ai-knowledge-vault", "backups")
