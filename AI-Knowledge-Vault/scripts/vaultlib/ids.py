"""Stable, filesystem-safe, human-inspectable record identifiers."""
import datetime
import os
import re
import unicodedata

ID_RE = re.compile(r"^(claim|source|entity|decision|artifact|project|run|review)-"
                   r"\d{8}(-\d{6})?-[0-9a-f]{4,8}$")

PREFIXES = ("claim", "source", "entity", "decision", "artifact", "project", "run", "review")


def _rand(n):
    return os.urandom(8).hex()[:n]


def now_iso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


# Ids issued by this process. Entropy alone is not a guarantee: a run id is
# bucketed to the second, so a burst of ids can collide by birthday. The set
# makes collisions impossible within a process and the 32-bit suffix makes them
# negligible across processes.
_ISSUED = set()
_SUFFIX_BITS = 8  # hex characters


def new_id(kind, when=None):
    if kind not in PREFIXES:
        raise ValueError("unknown record kind: %s" % kind)
    when = when or datetime.datetime.now()
    for _attempt in range(100):
        if kind == "run":
            candidate = "run-%s-%s-%s" % (when.strftime("%Y%m%d"),
                                          when.strftime("%H%M%S"), _rand(_SUFFIX_BITS))
        else:
            candidate = "%s-%s-%s" % (kind, when.strftime("%Y%m%d"), _rand(_SUFFIX_BITS))
        if candidate not in _ISSUED:
            _ISSUED.add(candidate)
            return candidate
    raise RuntimeError("could not generate a unique id for %s" % kind)


def is_valid(record_id):
    return bool(record_id) and bool(ID_RE.match(str(record_id)))


def kind_of(record_id):
    if not record_id:
        return None
    head = str(record_id).split("-", 1)[0]
    return head if head in PREFIXES else None


def slugify(text, maxlen=60):
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return (text[:maxlen].rstrip("-") or "untitled")


def filename_for(record_id, title):
    return "%s--%s.md" % (record_id, slugify(title))
