"""Derived knowledge-graph export. Markdown stays authoritative; this rebuilds."""
import json
import os

from . import SCHEMA_VERSION, ids, records

REL_FIELDS = [
    ("supports", "SUPPORTS"), ("contradicts", "CONTRADICTS"),
    ("supersedes", "SUPERSEDES"), ("superseded_by", "SUPERSEDES_INVERSE"),
    ("sources", "DERIVED_FROM"), ("derived_from", "DERIVED_FROM"),
    ("entities", "MENTIONS"), ("related_to", "RELATED_TO"),
    ("projects", "PART_OF"), ("duplicates", "DUPLICATES"),
    ("run_id", "PRODUCED_BY"), ("claims", "RELATED_TO"), ("target", "REVIEWED_BY"),
]
VALID_RELS = {"SUPPORTS", "CONTRADICTS", "SUPERSEDES", "DERIVED_FROM", "MENTIONS",
              "RELATED_TO", "PART_OF", "PRODUCED_BY", "REVIEWED_BY", "DUPLICATES"}


def graph_path(root):
    return os.path.join(root, "indexes", "graph.json")


def build(root):
    all_records, errors = records.load_all(root)
    known = set(r.id for r in all_records if r.id)
    nodes, edges = [], []
    for record in all_records:
        nodes.append({
            "id": record.id, "type": record.type, "title": record.title,
            "status": record.get("status"), "trust_level": record.get("trust_level"),
            "review_status": record.get("review_status"),
            "verification_status": record.get("verification_status"),
            "demo": bool(record.get("demo")), "path": record.rel_path(),
            "updated_at": record.get("updated_at"),
        })
        for field, rel in REL_FIELDS:
            for target in record.reflist(field):
                if not isinstance(target, str):
                    continue
                if rel == "SUPERSEDES_INVERSE":
                    src, dst, actual = target, record.id, "SUPERSEDES"
                else:
                    src, dst, actual = record.id, target, rel
                edges.append({
                    "source": src, "relationship": actual, "target": dst,
                    "run_id": record.get("run_id"),
                    "created_at": record.get("updated_at"),
                    "evidence": field,
                    "dangling": dst not in known,
                })
    unique = {}
    for edge in edges:
        unique[(edge["source"], edge["relationship"], edge["target"])] = edge
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": ids.now_iso(),
        "generator": "vault.py graph-export",
        "authoritative": False,
        "note": "Derived from Markdown records. Rebuildable. Never edit by hand.",
        "counts": {"nodes": len(nodes), "edges": len(unique),
                   "dangling_edges": sum(1 for e in unique.values() if e["dangling"]),
                   "load_errors": len(errors)},
        "nodes": sorted(nodes, key=lambda n: n["id"] or ""),
        "edges": sorted(unique.values(),
                        key=lambda e: (e["source"] or "", e["relationship"], e["target"] or "")),
    }


def export(root):
    data = build(root)
    path = graph_path(root)
    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=False)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return data, path


def load(root):
    path = graph_path(root)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def supersession_cycles(data):
    """Detect A supersedes B supersedes ... supersedes A."""
    adjacency = {}
    for edge in data["edges"]:
        if edge["relationship"] == "SUPERSEDES":
            adjacency.setdefault(edge["source"], set()).add(edge["target"])
    cycles, state = [], {}

    def visit(node, stack):
        state[node] = 1
        for nxt in adjacency.get(node, ()):
            if state.get(nxt) == 1:
                cycles.append(stack[stack.index(nxt):] + [nxt] if nxt in stack
                              else [node, nxt])
            elif state.get(nxt) is None:
                visit(nxt, stack + [nxt])
        state[node] = 2

    for node in list(adjacency):
        if state.get(node) is None:
            visit(node, [node])
    return cycles


def self_contradictions(data):
    """A record that both supports and contradicts the same target."""
    pairs = {}
    for edge in data["edges"]:
        if edge["relationship"] in ("SUPPORTS", "CONTRADICTS"):
            pairs.setdefault((edge["source"], edge["target"]), set()).add(edge["relationship"])
    return [{"source": s, "target": t} for (s, t), rels in pairs.items() if len(rels) > 1]
