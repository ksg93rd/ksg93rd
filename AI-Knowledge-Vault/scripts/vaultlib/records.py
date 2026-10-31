"""The canonical record store: Markdown files on disk are the source of truth."""
import hashlib
import io
import os

from . import config, frontmatter, ids

TYPE_DIR = {
    "source": "20-sources", "claim": "10-claims", "entity": "30-entities",
    "decision": "40-decisions", "artifact": "50-artifacts", "project": "60-projects",
    "run": "70-runs", "review": "80-reviews",
}
SCAN_DIRS = list(TYPE_DIR.values()) + ["90-archive"]
RAW_FILES_DIR = "_files"


class Record(object):
    __slots__ = ("meta", "body", "path", "root")

    def __init__(self, meta, body, path, root):
        self.meta, self.body, self.path, self.root = meta, body, path, root

    @property
    def id(self):
        return self.meta.get("id")

    @property
    def type(self):
        return self.meta.get("type")

    @property
    def title(self):
        return self.meta.get("title") or ""

    def rel_path(self):
        return os.path.relpath(self.path, self.root)

    def get(self, key, default=None):
        return self.meta.get(key, default)

    def reflist(self, key):
        value = self.meta.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return [v for v in value if v]
        return [value]

    def __repr__(self):
        return "<Record %s %s>" % (self.type, self.id)


def sha256_bytes(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def normalize_text(text):
    """Deterministic normalization so trivial formatting churn is not a new source."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n" if lines else ""


def dir_for(record_type):
    return TYPE_DIR.get(record_type)


def path_for(root, record_type, record_id, title):
    directory = dir_for(record_type)
    if not directory:
        raise ValueError("unknown record type: %r" % record_type)
    return os.path.join(root, directory, ids.filename_for(record_id, title))


def save(root, meta, body, path=None):
    meta = dict(meta)
    meta.setdefault("created_at", ids.now_iso())
    meta["updated_at"] = ids.now_iso()
    target = path or path_for(root, meta.get("type"), meta.get("id"), meta.get("title"))
    frontmatter.write_atomic(target, meta, body)
    return Record(meta, body, target, root)


def iter_files(root, dirs=None):
    for directory in (dirs or SCAN_DIRS):
        base = os.path.join(root, directory)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            # `_files/` holds the original ingested bytes, not vault records.
            # A stored .md original must never be parsed as a record.
            dirnames[:] = [d for d in dirnames
                           if not d.startswith(".") and d != RAW_FILES_DIR]
            for name in sorted(filenames):
                if name.endswith(".md") and not name.startswith("."):
                    yield os.path.join(dirpath, name)


class LoadError(object):
    def __init__(self, path, reason):
        self.path, self.reason = path, reason


def load_all(root, dirs=None):
    """Return (records, errors). Unreadable files become errors, never silent empties."""
    records, errors = [], []
    for path in iter_files(root, dirs):
        try:
            if os.path.getsize(path) == 0:
                errors.append(LoadError(path, "file is empty (possible iCloud placeholder "
                                              "or interrupted write)"))
                continue
            with io.open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            errors.append(LoadError(path, "unreadable: %s (file may not be downloaded "
                                          "from iCloud)" % exc))
            continue
        except UnicodeDecodeError as exc:
            errors.append(LoadError(path, "not valid UTF-8: %s" % exc))
            continue
        try:
            meta, body = frontmatter.parse(text)
        except frontmatter.FrontmatterError as exc:
            errors.append(LoadError(path, "invalid frontmatter: %s" % exc))
            continue
        if not meta:
            errors.append(LoadError(path, "no YAML frontmatter block"))
            continue
        records.append(Record(meta, body, path, root))
    return records, errors


def index_by_id(records):
    out = {}
    for record in records:
        if record.id:
            out.setdefault(record.id, []).append(record)
    return out


def find(root, record_id):
    records, _ = load_all(root)
    for record in records:
        if record.id == record_id:
            return record
    return None


def icloud_placeholder_scan(root):
    """Detect Apple's dataless-file placeholders (.icloud) and zero-byte stand-ins."""
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for name in filenames:
            full = os.path.join(dirpath, name)
            if name.startswith(".") and name.endswith(".icloud"):
                findings.append((os.path.relpath(full, root), "cloud-only placeholder"))
            else:
                try:
                    if name.endswith(".md") and os.path.getsize(full) == 0:
                        findings.append((os.path.relpath(full, root), "zero-byte record"))
                except OSError:
                    findings.append((os.path.relpath(full, root), "unreadable"))
    return findings
