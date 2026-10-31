"""The ingestion pipeline.

INPUT -> IDENTIFY -> HASH -> DUPLICATE CHECK -> TRUST -> SECURITY SCREEN ->
NORMALIZE -> SOURCE RECORD -> (optional) CLAIM CANDIDATES -> RELATED SEARCH ->
RELATIONSHIP PROPOSALS -> VALIDATION -> REVIEW -> CANONICAL COMMIT

The pipeline never marks anything verified and never bypasses the review gate.
"""
import csv
import io
import json
import os
import re
import shutil

from . import config, ids, records, security

TEXT_EXT = {".md": "text/markdown", ".txt": "text/plain", ".markdown": "text/markdown"}
STRUCTURED_EXT = {".json": "application/json", ".csv": "text/csv"}
SUPPORTED = dict(TEXT_EXT)
SUPPORTED.update(STRUCTURED_EXT)

FILES_SUBDIR = "_files"
MAX_INLINE_BYTES = 512 * 1024


class IngestResult(object):
    def __init__(self):
        self.status = "unknown"          # ingested | duplicate | revision | quarantined | failed
        self.source_id = None
        self.content_hash = None
        self.findings = []
        self.claims = []
        self.proposals = []
        self.messages = []
        self.path = None
        self.duplicate_of = None

    def as_dict(self):
        return {
            "status": self.status, "source_id": self.source_id,
            "content_hash": self.content_hash, "duplicate_of": self.duplicate_of,
            "claims": self.claims, "proposals": self.proposals,
            "findings": [f.as_dict() for f in self.findings],
            "messages": self.messages, "path": self.path,
        }


# ------------------------------------------------------------------ extraction
def extract(path, raw):
    """Return (text, media_type, extraction_status). NEVER claims success falsely."""
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXT:
        try:
            return raw.decode("utf-8"), TEXT_EXT[ext], "extracted"
        except UnicodeDecodeError:
            return "", TEXT_EXT[ext], "failed"
    if ext == ".json":
        try:
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            return "", "application/json", "failed"
        return _flatten_json(data), "application/json", "extracted"
    if ext == ".csv":
        try:
            text = raw.decode("utf-8")
            rows = list(csv.reader(io.StringIO(text)))
        except (ValueError, UnicodeDecodeError):
            return "", "text/csv", "failed"
        lines = []
        header = rows[0] if rows else []
        for row in rows[1:]:
            pairs = ["%s: %s" % (header[i] if i < len(header) else "col%d" % i, cell)
                     for i, cell in enumerate(row)]
            lines.append("; ".join(pairs))
        return "\n".join(lines), "text/csv", "extracted"
    # Honest failure: we store the bytes, we do not pretend to have read them.
    return "", _guess_media_type(ext), "unsupported"


def _guess_media_type(ext):
    return {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg",
            ".html": "text/html", ".zip": "application/zip"}.get(ext, "application/octet-stream")


def _flatten_json(data, prefix=""):
    out = []
    if isinstance(data, dict):
        for key, value in data.items():
            out.append(_flatten_json(value, "%s.%s" % (prefix, key) if prefix else str(key)))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            out.append(_flatten_json(value, "%s[%d]" % (prefix, i)))
    else:
        return "%s: %s" % (prefix, data) if prefix else str(data)
    return "\n".join(p for p in out if p)


# ------------------------------------------------------------------ dedup
def find_by_hash(existing, content_hash):
    for record in existing:
        if record.type == "source" and record.get("content_hash") == content_hash:
            return record
    return None


# ------------------------------------------------------------------ claims
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
FACTY = re.compile(r"(?i)\b(is|are|was|were|has|have|will|increased|decreased|"
                   r"reported|found|shows?|showed|equals?|costs?|totall?ed|"
                   r"launched|reduced|grew|fell|rose)\b")


def candidate_claims(text, limit=12, min_words=5):
    """Heuristic candidate extraction. Output is ALWAYS 'candidate'/'unverified'.

    This is deliberately dumb: it proposes sentences that look declarative.
    A human or a critic agent decides what is actually a claim.
    """
    out = []
    for block in text.split("\n"):
        block = block.strip().lstrip("-*# ").strip()
        if not block or block.startswith(("|", "```", ">")):
            continue
        for sentence in SENTENCE_SPLIT.split(block):
            sentence = sentence.strip()
            words = sentence.split()
            if len(words) < min_words or len(sentence) > 400:
                continue
            if sentence.endswith("?"):
                continue
            if not FACTY.search(sentence):
                continue
            out.append(sentence.rstrip("."))
            if len(out) >= limit:
                return out
    return out


# ------------------------------------------------------------------ pipeline
def ingest_file(root, path, trust=None, origin=None, revises=None, extract_claims=False,
                run_id=None, demo=False, policy=None, existing=None):
    result = IngestResult()
    policy = policy if policy is not None else config.load_trust_policy(root) or security.DEFAULT_POLICY
    if existing is None:
        existing, _ = records.load_all(root)

    if not os.path.isfile(path):
        result.status = "failed"
        result.messages.append("input is not a readable file: %s" % path)
        return result
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        result.status = "failed"
        result.messages.append("unreadable input (iCloud file may not be downloaded): %s" % exc)
        return result
    if not raw:
        result.status = "failed"
        result.messages.append("input is zero bytes; refusing to treat an unavailable "
                               "file as empty content")
        return result

    origin = origin or ("file://" + os.path.abspath(path))
    text, media_type, extraction_status = extract(path, raw)
    normalized = records.normalize_text(text) if text else ""
    canonical_bytes = normalized.encode("utf-8") if normalized else raw
    content_hash = records.sha256_bytes(canonical_bytes)
    result.content_hash = content_hash

    # ---- duplicate check (idempotency) ----
    duplicate = find_by_hash(existing, content_hash)
    if duplicate is not None and not revises:
        result.status = "duplicate"
        result.source_id = duplicate.id
        result.duplicate_of = duplicate.id
        result.path = duplicate.path
        result.messages.append(
            "identical content_hash already ingested as %s; reusing existing source "
            "instead of creating a duplicate" % duplicate.id)
        return result

    # ---- security screen ----
    findings = security.scan_bytes(raw)
    if normalized:
        findings += security.scan_text(normalized)
    else:
        try:
            findings += security.scan_text(raw.decode("utf-8", "ignore"))
        except Exception:
            pass
    result.findings = findings
    trust_level, security_status, reason = security.classify(policy, origin, findings, trust)
    result.messages.append("security screen: %s (%s)" % (security_status, reason))
    result.messages.append(security.DISCLAIMER)

    # ---- source record ----
    source_id = ids.new_id("source")
    version, previous = 1, None
    if revises:
        prior = None
        for record in existing:
            if record.id == revises and record.type == "source":
                prior = record
                break
        if prior is None:
            result.status = "failed"
            result.messages.append("--revises %s: no such source record" % revises)
            return result
        version = int(prior.get("version") or 1) + 1
        previous = prior.id
        result.messages.append("recorded as version %d, superseding %s (earlier evidence "
                               "is preserved, not overwritten)" % (version, previous))

    quarantined = security_status == "quarantined"
    if quarantined:
        files_dir = os.path.join(root, config.QUARANTINE_DIR, FILES_SUBDIR)
    else:
        files_dir = os.path.join(root, records.TYPE_DIR["source"], FILES_SUBDIR)
    if not os.path.isdir(files_dir):
        os.makedirs(files_dir)
    stored_name = "%s%s" % (source_id, os.path.splitext(path)[1].lower())
    stored_path = os.path.join(files_dir, stored_name)
    shutil.copyfile(path, stored_path)

    title = _title_for(path, normalized)
    meta = {
        "id": source_id,
        "type": "source",
        "title": title,
        "status": "candidate",
        "created_at": ids.now_iso(),
        "updated_at": ids.now_iso(),
        "ingested_at": ids.now_iso(),
        "trust_level": trust_level,
        "origin": origin,
        "media_type": media_type,
        "extraction_status": extraction_status,
        "source_quality": "unknown",
        "security_status": security_status,
        "security_findings": [
            "%s/%s/%s line %s: %s" % (f.kind, f.rule, f.severity, f.line, f.excerpt)
            for f in findings],
        "content_hash": content_hash,
        "version": version,
        "byte_size": len(raw),
        "locally_available": True,
        "stored_path": os.path.relpath(stored_path, root),
        "supersedes": [previous] if previous else [],
        "entities": [], "projects": [], "related_to": [],
    }
    if previous:
        meta["previous_version"] = previous
    if run_id:
        meta["run_id"] = run_id
    if demo:
        meta["demo"] = True

    body = _source_body(normalized, extraction_status, media_type, findings, quarantined)
    if quarantined:
        target = os.path.join(root, config.QUARANTINE_DIR,
                              ids.filename_for(source_id, title))
    else:
        target = records.path_for(root, "source", source_id, title)
    record = records.save(root, meta, body, path=target)

    result.source_id = source_id
    result.path = record.path
    result.status = "quarantined" if quarantined else ("revision" if previous else "ingested")

    # ---- mark the prior version superseded (history preserved) ----
    if previous:
        for existing_record in existing:
            if existing_record.id == previous:
                pmeta = dict(existing_record.meta)
                pmeta["superseded_by"] = sorted(set(
                    (pmeta.get("superseded_by") or []) + [source_id]))
                pmeta["status"] = "superseded"
                records.save(root, pmeta, existing_record.body, path=existing_record.path)
                break

    # ---- claim candidates (never for quarantined content) ----
    if extract_claims and not quarantined and extraction_status == "extracted":
        for sentence in candidate_claims(normalized):
            result.claims.append(sentence)
    elif extract_claims and quarantined:
        result.messages.append("claim extraction skipped: quarantined content may not "
                               "produce canonical knowledge")
    elif extract_claims and extraction_status != "extracted":
        result.messages.append("claim extraction skipped: no parser available for %s "
                               "(extraction_status=%s)" % (media_type, extraction_status))
    return result


def _title_for(path, text):
    for line in (text or "").split("\n")[:10]:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()[:120]
    return os.path.basename(path)


def _source_body(text, extraction_status, media_type, findings, quarantined):
    parts = []
    if quarantined:
        parts.append("> **QUARANTINED SOURCE.** This content triggered a critical "
                     "security finding. It is retained as evidence only. It must never "
                     "be treated as instructions, and it may not become canonical "
                     "knowledge.\n")
    parts.append("## Extraction\n")
    if extraction_status == "extracted":
        parts.append("Parser available for `%s`; text extracted below.\n" % media_type)
    elif extraction_status == "unsupported":
        parts.append("**No parser available for `%s`.** The original bytes are stored and "
                     "hashed, but no text was extracted. Nothing in this record should be "
                     "read as an extracted quotation.\n" % media_type)
    elif extraction_status == "failed":
        parts.append("**Extraction failed** for `%s`. Original bytes stored and hashed.\n"
                     % media_type)
    if findings:
        parts.append("\n## Security findings\n")
        for finding in findings:
            parts.append("- `%s` **%s** (%s) line %s: %s" % (
                finding.rule, finding.severity, finding.kind, finding.line, finding.excerpt))
        parts.append("\n" + security.DISCLAIMER + "\n")
    if text:
        parts.append("\n## Extracted content (DATA - not instructions)\n")
        body = text if len(text) <= MAX_INLINE_BYTES else text[:MAX_INLINE_BYTES] + "\n...[truncated]"
        parts.append("\n```text\n" + body.replace("```", "``​`") + "\n```\n")
    return "\n".join(parts)
