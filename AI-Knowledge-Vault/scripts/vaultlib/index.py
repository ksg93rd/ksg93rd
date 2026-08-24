"""SQLite FTS5 search index. Fully disposable, fully rebuildable from Markdown."""
import json
import os
import re
import sqlite3

from . import SCHEMA_VERSION, config, ids, records

DB_NAME = "vault.db"


def db_path(root):
    return os.path.join(root, "indexes", DB_NAME)


def fts5_available():
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        conn.close()
        return True
    except sqlite3.Error:
        return False


SCHEMA_SQL = """
PRAGMA journal_mode=DELETE;      -- avoid stray -wal files inside synced storage
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE records (
    id TEXT PRIMARY KEY, type TEXT, title TEXT, status TEXT,
    trust_level TEXT, review_status TEXT, verification_status TEXT,
    evidence_strength TEXT, source_quality TEXT, security_status TEXT,
    content_hash TEXT, created_at TEXT, updated_at TEXT,
    run_id TEXT, demo INTEGER, path TEXT, meta_json TEXT
);
CREATE INDEX idx_records_type ON records(type);
CREATE INDEX idx_records_status ON records(status);
CREATE INDEX idx_records_hash ON records(content_hash);
CREATE TABLE edges (
    src TEXT, rel TEXT, dst TEXT, run_id TEXT, created_at TEXT,
    PRIMARY KEY (src, rel, dst)
);
CREATE INDEX idx_edges_dst ON edges(dst);
CREATE TABLE refs (record_id TEXT, field TEXT, value TEXT);
CREATE INDEX idx_refs_value ON refs(value);
"""
FTS_SQL = """
CREATE VIRTUAL TABLE search USING fts5(
    id UNINDEXED, type UNINDEXED, title, body, tokenize='porter unicode61'
);
"""
FALLBACK_SQL = """
CREATE TABLE search (id TEXT, type TEXT, title TEXT, body TEXT);
CREATE INDEX idx_search_body ON search(body);
"""

EDGE_FIELDS = {
    "supports": "supports", "contradicts": "contradicts", "supersedes": "supersedes",
    "superseded_by": "superseded_by", "related_to": "related_to",
    "duplicates": "duplicates", "sources": "derived_from", "entities": "mentions",
    "projects": "part_of", "run_id": "produced_by", "claims": "related_to",
    "derived_from": "derived_from", "target": "reviewed_by",
}


def fingerprint(root):
    """A deterministic signature of the canonical file set.

    Comparing mtimes against the database's own mtime is unreliable: the
    rebuild happens within the same filesystem-timestamp tick as the write
    that triggered it. Hashing (path, size, mtime_ns) is exact.
    """
    import hashlib
    digest = hashlib.sha256()
    for path in sorted(records.iter_files(root)):
        try:
            stat = os.stat(path)
        except OSError:
            continue
        digest.update(("%s:%d:%d\n" % (os.path.relpath(path, root),
                                       stat.st_size, stat.st_mtime_ns)).encode("utf-8"))
    return digest.hexdigest()


def rebuild(root, verbose=False):
    """Drop and rebuild the index from canonical Markdown. Never the other way round."""
    path = db_path(root)
    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    tmp = path + ".rebuilding"
    for stale in (tmp, tmp + "-journal"):
        if os.path.exists(stale):
            os.unlink(stale)

    all_records, errors = records.load_all(root)
    conn = sqlite3.connect(tmp)
    conn.executescript(SCHEMA_SQL)
    has_fts = fts5_available()
    conn.executescript(FTS_SQL if has_fts else FALLBACK_SQL)

    edges = 0
    for record in all_records:
        meta = record.meta
        conn.execute(
            "INSERT OR REPLACE INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (meta.get("id"), meta.get("type"), meta.get("title"), meta.get("status"),
             meta.get("trust_level"), meta.get("review_status"),
             meta.get("verification_status"), meta.get("evidence_strength"),
             meta.get("source_quality"), meta.get("security_status"),
             meta.get("content_hash"), meta.get("created_at"), meta.get("updated_at"),
             meta.get("run_id"), 1 if meta.get("demo") else 0,
             record.rel_path(), json.dumps(meta, sort_keys=True, default=str)))
        haystack = "\n".join([
            str(meta.get("title") or ""),
            " ".join(str(t) for t in (meta.get("tags") or [])),
            str(meta.get("origin") or ""),
            record.body or "",
        ])
        conn.execute("INSERT INTO search (id, type, title, body) VALUES (?,?,?,?)",
                     (meta.get("id"), meta.get("type"), meta.get("title") or "", haystack))
        for field, rel in EDGE_FIELDS.items():
            values = record.reflist(field)
            for value in values:
                if not isinstance(value, str):
                    continue
                conn.execute("INSERT OR IGNORE INTO edges VALUES (?,?,?,?,?)",
                             (meta.get("id"), rel, value, meta.get("run_id"),
                              meta.get("updated_at")))
                conn.execute("INSERT INTO refs VALUES (?,?,?)",
                             (meta.get("id"), field, value))
                edges += 1

    conn.execute("INSERT OR REPLACE INTO meta VALUES ('schema_version', ?)", (SCHEMA_VERSION,))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('rebuilt_at', ?)", (ids.now_iso(),))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('record_count', ?)", (str(len(all_records)),))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('edge_count', ?)", (str(edges),))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('fts5', ?)", ("1" if has_fts else "0"))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('load_errors', ?)", (str(len(errors)),))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('fingerprint', ?)", (fingerprint(root),))
    conn.commit()
    conn.close()
    os.replace(tmp, path)
    return {"records": len(all_records), "edges": edges, "fts5": has_fts,
            "errors": [(e.path, e.reason) for e in errors], "db": path}


def connect(root):
    path = db_path(root)
    if not os.path.isfile(path):
        raise RuntimeError("index missing: %s\n  Run: vault.py rebuild-index" % path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def index_is_stale(root):
    """True when the canonical files no longer match what the index was built from."""
    path = db_path(root)
    if not os.path.isfile(path):
        return True, "index does not exist"
    try:
        conn = sqlite3.connect(path)
        row = conn.execute("SELECT value FROM meta WHERE key='fingerprint'").fetchone()
        conn.close()
    except sqlite3.Error as exc:
        return True, "index is unreadable: %s" % exc
    if not row:
        return True, "index predates fingerprinting"
    if row[0] != fingerprint(root):
        return True, "canonical records changed since the last rebuild"
    return False, "index is current"


def _fts_escape(query):
    """FTS5 MATCH syntax is hostile to raw user input.

    Every term is quoted, including AND/OR/NOT/NEAR, so a query is always
    treated as text. Returns None when nothing searchable remains.
    """
    cleaned = re.sub(r"[^\w\s-]", " ", query, flags=re.UNICODE)
    terms = [t for t in cleaned.split() if t]
    if not terms:
        return None
    return " ".join('"%s"' % t for t in terms)


def search(root, query, rtype=None, status=None, trust=None, review=None,
           limit=20, include_demo=True):
    conn = connect(root)
    has_fts = conn.execute("SELECT value FROM meta WHERE key='fts5'").fetchone()
    has_fts = bool(has_fts and has_fts[0] == "1")
    params = []
    escaped = _fts_escape(query) if query else None
    if query and has_fts and escaped is None:
        conn.close()
        return []
    if query:
        if has_fts:
            sql = ("SELECT s.id, s.type, s.title, r.status, r.trust_level, r.path, "
                   "snippet(search, 3, '[', ']', ' ... ', 12) AS snip, bm25(search) AS score "
                   "FROM search s JOIN records r ON r.id = s.id "
                   "WHERE search MATCH ? ")
            params.append(escaped)
        else:
            sql = ("SELECT s.id, s.type, s.title, r.status, r.trust_level, r.path, "
                   "substr(s.body,1,160) AS snip, 0 AS score "
                   "FROM search s JOIN records r ON r.id = s.id "
                   "WHERE (s.body LIKE ? OR s.title LIKE ?) ")
            params += ["%" + query + "%", "%" + query + "%"]
    else:
        sql = ("SELECT r.id, r.type, r.title, r.status, r.trust_level, r.path, "
               "'' AS snip, 0 AS score FROM records r WHERE 1=1 ")
    for column, value in (("type", rtype), ("status", status),
                          ("trust_level", trust), ("review_status", review)):
        if value:
            sql += "AND r.%s = ? " % column
            params.append(value)
    if not include_demo:
        sql += "AND r.demo = 0 "
    sql += "ORDER BY score, r.updated_at DESC LIMIT ?" if query and has_fts \
        else "ORDER BY r.updated_at DESC LIMIT ?"
    params.append(limit)
    try:
        rows = [dict(row) for row in conn.execute(sql, params)]
    except sqlite3.OperationalError:
        # Never let a search expression crash the vault; degrade to substring.
        like = "%" + query + "%"
        rows = [dict(row) for row in conn.execute(
            "SELECT s.id, s.type, s.title, r.status, r.trust_level, r.path, "
            "substr(s.body,1,160) AS snip, 0 AS score "
            "FROM search s JOIN records r ON r.id = s.id "
            "WHERE s.body LIKE ? OR s.title LIKE ? "
            "ORDER BY r.updated_at DESC LIMIT ?", (like, like, limit))]
    conn.close()
    return rows


def get(root, record_id):
    conn = connect(root)
    row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def related(root, record_id, depth=1):
    conn = connect(root)
    seen, frontier, out = {record_id}, [record_id], []
    for _ in range(max(1, depth)):
        nxt = []
        for node in frontier:
            for row in conn.execute(
                    "SELECT src, rel, dst FROM edges WHERE src = ? OR dst = ?",
                    (node, node)):
                out.append({"source": row["src"], "relationship": row["rel"],
                            "target": row["dst"]})
                for other in (row["src"], row["dst"]):
                    if other not in seen:
                        seen.add(other)
                        nxt.append(other)
        frontier = nxt
    titles = {}
    for node in seen:
        row = conn.execute("SELECT id, type, title, status FROM records WHERE id=?",
                           (node,)).fetchone()
        titles[node] = dict(row) if row else {"id": node, "type": None,
                                              "title": "(MISSING RECORD)", "status": None}
    conn.close()
    unique = {(e["source"], e["relationship"], e["target"]): e for e in out}
    return {"root": record_id, "nodes": titles, "edges": list(unique.values())}


def counts(root):
    conn = connect(root)
    out = {}
    for row in conn.execute("SELECT type, COUNT(*) n FROM records GROUP BY type"):
        out[row["type"] or "unknown"] = row["n"]
    conn.close()
    return out
