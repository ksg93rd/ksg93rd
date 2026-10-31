"""Declarative record schemas + field-level validation.

Schemas are declared here (single source of truth) and EXPORTED to
schemas/*.json by `vault.py init` so a human can read them without Python.
"""
import re

from . import SCHEMA_VERSION

ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$")
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

# ---------------------------------------------------------------- enums
STATUS = ["unknown", "candidate", "verified", "disputed", "rejected", "superseded"]
TRUST = ["trusted", "internal", "untrusted", "quarantined"]
SOURCE_QUALITY = ["primary", "secondary", "tertiary", "self-reported", "ai-generated", "unknown"]
EVIDENCE_STRENGTH = ["none", "weak", "moderate", "high"]
VERIFICATION = ["unverified", "verifying", "verified", "failed", "not-applicable"]
REVIEW = ["not-required", "pending", "in-review", "approved", "rejected", "disputed"]
REL_TYPES = ["supports", "contradicts", "supersedes", "derived_from", "mentions",
             "related_to", "part_of", "produced_by", "reviewed_by", "duplicates"]
RUN_STATUS = ["running", "success", "partial", "failed", "aborted"]
REVIEW_RESULT = ["approved", "rejected", "disputed", "needs-more-evidence"]
DECISION_STATUS = ["proposed", "accepted", "rejected", "superseded", "deprecated"]

COMMON = {
    "id":         {"required": True,  "type": "id"},
    "type":       {"required": True,  "type": "str"},
    "title":      {"required": True,  "type": "str"},
    "created_at": {"required": True,  "type": "timestamp"},
    "updated_at": {"required": True,  "type": "timestamp"},
    "trust_level": {"required": True, "type": "enum", "values": TRUST},
    "tags":       {"required": False, "type": "list"},
    "run_id":     {"required": False, "type": "ref", "kinds": ["run"]},
    "demo":       {"required": False, "type": "bool",
                   "doc": "true marks clearly-labelled synthetic demo data"},
}

RELATIONAL = {
    "supports":      {"required": False, "type": "reflist"},
    "contradicts":   {"required": False, "type": "reflist"},
    "supersedes":    {"required": False, "type": "reflist"},
    "superseded_by": {"required": False, "type": "reflist"},
    "related_to":    {"required": False, "type": "reflist"},
    "duplicates":    {"required": False, "type": "reflist"},
    "entities":      {"required": False, "type": "reflist", "kinds": ["entity"]},
    "projects":      {"required": False, "type": "reflist", "kinds": ["project"]},
}


def _merge(*parts):
    out = {}
    for part in parts:
        out.update(part)
    return out


SCHEMAS = {
    "source": _merge(COMMON, {
        "status":            {"required": True, "type": "enum", "values": STATUS},
        "content_hash":      {"required": True, "type": "hash"},
        "origin":            {"required": True, "type": "str",
                              "doc": "where it came from: file path, URL, mailbox, ..."},
        "media_type":        {"required": True, "type": "str"},
        "extraction_status": {"required": True, "type": "enum",
                              "values": ["extracted", "stored-only", "unsupported", "failed"],
                              "doc": "NEVER 'extracted' unless a parser actually ran"},
        "source_quality":    {"required": True, "type": "enum", "values": SOURCE_QUALITY},
        "security_status":   {"required": True, "type": "enum",
                              "values": ["clean", "flagged", "quarantined"]},
        "security_findings": {"required": False, "type": "list"},
        "version":           {"required": True, "type": "int"},
        "previous_version":  {"required": False, "type": "ref", "kinds": ["source"]},
        "ingested_at":       {"required": True, "type": "timestamp"},
        "stored_path":       {"required": False, "type": "str"},
        "byte_size":         {"required": False, "type": "int"},
        "locally_available": {"required": False, "type": "bool"},
    }, RELATIONAL),

    "claim": _merge(COMMON, {
        "status":              {"required": True, "type": "enum", "values": STATUS},
        "sources":             {"required": True, "type": "reflist", "kinds": ["source"],
                                "doc": "a claim with no source cannot be verified"},
        "source_quality":      {"required": True, "type": "enum", "values": SOURCE_QUALITY},
        "evidence_strength":   {"required": True, "type": "enum", "values": EVIDENCE_STRENGTH},
        "verification_status": {"required": True, "type": "enum", "values": VERIFICATION},
        "review_status":       {"required": True, "type": "enum", "values": REVIEW},
        "reviewed_by":         {"required": False, "type": "list"},
        "content_hash":        {"required": False, "type": "hash"},
    }, RELATIONAL),

    "entity": _merge(COMMON, {
        "status":        {"required": True, "type": "enum", "values": STATUS},
        "entity_type":   {"required": True, "type": "enum",
                          "values": ["person", "organization", "product", "system",
                                     "place", "concept", "event", "other"]},
        "aliases":       {"required": False, "type": "list"},
        "sources":       {"required": False, "type": "reflist", "kinds": ["source"]},
    }, RELATIONAL),

    "decision": _merge(COMMON, {
        "status":        {"required": True, "type": "enum", "values": DECISION_STATUS},
        "decided_at":    {"required": False, "type": "timestamp"},
        "decided_by":    {"required": False, "type": "list"},
        "context":       {"required": False, "type": "str"},
        "consequences":  {"required": False, "type": "list"},
        "sources":       {"required": False, "type": "reflist", "kinds": ["source"]},
        "claims":        {"required": False, "type": "reflist", "kinds": ["claim"]},
        "review_status": {"required": True, "type": "enum", "values": REVIEW},
    }, RELATIONAL),

    "artifact": _merge(COMMON, {
        "status":         {"required": True, "type": "enum", "values": STATUS},
        "artifact_type":  {"required": True, "type": "str"},
        "content_hash":   {"required": False, "type": "hash"},
        "derived_from":   {"required": False, "type": "reflist"},
        "review_status":  {"required": True, "type": "enum", "values": REVIEW},
    }, RELATIONAL),

    "project": _merge(COMMON, {
        "status":     {"required": True, "type": "enum",
                       "values": ["active", "paused", "completed", "abandoned"]},
        "owner":      {"required": False, "type": "str"},
        "started_at": {"required": False, "type": "timestamp"},
        "ended_at":   {"required": False, "type": "timestamp"},
    }, RELATIONAL),

    "run": _merge(COMMON, {
        "status":            {"required": True, "type": "enum", "values": RUN_STATUS},
        "objective":         {"required": True, "type": "str"},
        "trigger":           {"required": True, "type": "str"},
        "started_at":        {"required": True, "type": "timestamp"},
        "completed_at":      {"required": False, "type": "timestamp"},
        "agent":             {"required": False, "type": "str"},
        "skill":             {"required": False, "type": "str"},
        "inputs":            {"required": False, "type": "list"},
        "records_read":      {"required": False, "type": "list"},
        "records_created":   {"required": False, "type": "list"},
        "records_modified":  {"required": False, "type": "list"},
        "validation_result": {"required": False, "type": "enum",
                              "values": ["PASS", "WARN", "FAIL", "not-run"]},
        "review_result":     {"required": False, "type": "enum",
                              "values": REVIEW_RESULT + ["not-run", "mixed"]},
        "warnings":          {"required": False, "type": "list"},
        "errors":            {"required": False, "type": "list"},
        "retry_count":       {"required": False, "type": "int"},
        "final_status":      {"required": False, "type": "enum", "values": RUN_STATUS},
        "tokens_used":       {"required": False, "type": "int"},
        "cost_usd":          {"required": False, "type": "str"},
    }),

    "review": _merge(COMMON, {
        "status":       {"required": True, "type": "enum", "values": REVIEW_RESULT},
        "target":       {"required": True, "type": "ref"},
        "reviewer":     {"required": True, "type": "str"},
        "reviewer_role": {"required": False, "type": "str"},
        "independent":  {"required": False, "type": "bool",
                         "doc": "false when author and reviewer are the same actor"},
        "checks":       {"required": False, "type": "list"},
        "findings":     {"required": False, "type": "list"},
        "decided_at":   {"required": True, "type": "timestamp"},
    }),
}


def field_doc():
    """Human-readable export of every schema, used by docs/SCHEMA.md + schemas/*.json."""
    out = {}
    for rtype, fields in SCHEMAS.items():
        out[rtype] = {
            "schema_version": SCHEMA_VERSION,
            "record_type": rtype,
            "fields": {
                name: {
                    "required": spec["required"],
                    "type": spec["type"],
                    "allowed_values": spec.get("values"),
                    "ref_kinds": spec.get("kinds"),
                    "notes": spec.get("doc"),
                }
                for name, spec in fields.items()
            },
        }
    return out
