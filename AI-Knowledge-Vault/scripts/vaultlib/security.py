"""Trust boundary, prompt-injection screening, and secret detection.

HONEST LIMITATION (repeated in docs/SECURITY.md and in every report we print):
heuristic prompt-injection detection is RISK REDUCTION, NOT GUARANTEED DETECTION.
A determined attacker can phrase an instruction in a way these patterns miss.
The real control is the trust boundary: source content is DATA and is never
executed as agent policy, regardless of what the screen returns.
"""
import os
import re

from . import config

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

# --- prompt-injection heuristics -------------------------------------------
INJECTION_PATTERNS = [
    ("instruction-override", "high",
     r"(?i)\b(ignore|disregard|forget|override|bypass)\b[^.\n]{0,40}\b"
     r"(previous|prior|above|earlier|all|any|system|initial)\b[^.\n]{0,20}"
     r"\b(instruction|prompt|rule|direction|guardrail|constraint)s?\b"),
    ("role-hijack", "high",
     r"(?i)\b(you are now|from now on you|act as|pretend to be|new persona|"
     r"your new (role|instructions?|system prompt))\b"),
    ("config-tamper", "critical",
     r"(?i)\b(modify|edit|update|rewrite|append to|delete|replace)\b[^.\n]{0,40}"
     r"(CLAUDE\.md|\.claude/|trust-policy|settings\.json|permissions?|hooks?|"
     r"subagents?|skills?|rules?)\b"),
    ("config-tamper-direct", "critical",
     r"(?i)(CLAUDE\.md|trust-policy\.ya?ml|\.claude/(agents|skills|rules))"),
    ("exfiltration", "critical",
     r"(?i)\b(send|post|upload|exfiltrate|email|curl|wget|fetch)\b[^.\n]{0,40}"
     r"\b(secret|credential|token|api[_ -]?key|password|ssh key|\.env|vault)\b"),
    ("execution-request", "high",
     r"(?i)\b(run|execute|eval|source|invoke)\b[^.\n]{0,25}\b"
     r"(this (script|command|code)|the following (command|script|code)|"
     r"rm -rf|sudo |bash -c|sh -c|os\.system|subprocess|powershell|Invoke-Expression)"),
    ("tool-directive", "medium",
     r"(?i)\b(as an ai|as the assistant|assistant:|system:)\b[^.\n]{0,30}"
     r"\b(you must|you should always|never refuse|do not tell)\b"),
    ("hidden-directive-markup", "medium",
     r"(?i)<!--[^>]{0,200}\b(ignore|instruction|system|prompt|you must)\b[^>]{0,200}-->"),
    ("elevated-trust-claim", "medium",
     r"(?i)\b(this (document|message|file) is (trusted|authorized|verified)|"
     r"treat (this|the following) as (trusted|system|policy|instructions))\b"),
    ("data-destruction", "critical",
     r"(?i)\b(delete|drop|wipe|purge|truncate)\b[^.\n]{0,30}\b"
     r"(all|entire|every|the whole)\b[^.\n]{0,25}\b"
     r"(record|claim|vault|database|history|table|repo)"),
]

# --- secret heuristics ------------------------------------------------------
SECRET_PATTERNS = [
    ("aws-access-key-id", "critical", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("github-token", "critical", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ("slack-token", "critical", r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b"),
    ("google-api-key", "critical", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    ("anthropic-key", "critical", r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b"),
    ("openai-key", "critical", r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b"),
    ("stripe-key", "critical", r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}\b"),
    ("private-key-block", "critical",
     r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ("jwt", "high", r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
    ("bearer-token", "high", r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9._\-]{16,}"),
    ("password-assignment", "medium",
     r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*"
     r"[\"']?[^\s\"']{8,}"),
    ("connection-string", "high",
     r"(?i)\b(postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s:@/]+:[^\s@/]+@"),
]

BINARY_MARKERS = [
    ("elf-binary", b"\x7fELF"), ("mach-o", b"\xcf\xfa\xed\xfe"),
    ("pe-executable", b"MZ"), ("java-class", b"\xca\xfe\xba\xbe"),
    ("zip-or-office", b"PK\x03\x04"),
]

DEFAULT_POLICY = {
    "default_trust": "untrusted",
    "quarantine_on": ["critical"],
    "flag_on": ["high", "medium"],
    "trust_levels": {
        "trusted": {
            "description": "Authored or explicitly ratified inside the vault by the owner.",
            "may_become_canonical": True, "requires_review": True,
        },
        "internal": {
            "description": "Owner's own systems and files. Believed benign, still data.",
            "may_become_canonical": True, "requires_review": True,
        },
        "untrusted": {
            "description": "Anything from outside: web, email, chat, AI output, tickets.",
            "may_become_canonical": True, "requires_review": True,
        },
        "quarantined": {
            "description": "Screened content that tried to act as policy or leaked secrets.",
            "may_become_canonical": False, "requires_review": True,
        },
    },
    "origin_rules": [],
}


class Finding(object):
    def __init__(self, kind, rule, severity, excerpt, line=None):
        self.kind, self.rule, self.severity = kind, rule, severity
        self.excerpt, self.line = excerpt, line

    def as_dict(self):
        return {"kind": self.kind, "rule": self.rule, "severity": self.severity,
                "line": self.line, "excerpt": self.excerpt}

    def __repr__(self):
        return "<%s %s/%s line %s>" % (self.kind, self.rule, self.severity, self.line)


def _redact(text):
    """Findings are stored in the vault, so never store the secret itself."""
    text = text.strip().replace("\n", " ")
    if len(text) <= 24:
        return text[:4] + "***REDACTED***"
    return text[:12] + "***REDACTED***" + text[-4:]


def scan_text(text, redact_secrets=True):
    findings = []
    lines = text.split("\n")
    for rule, severity, pattern in INJECTION_PATTERNS:
        for match in re.finditer(pattern, text):
            line_no = text.count("\n", 0, match.start()) + 1
            excerpt = lines[line_no - 1].strip()[:160] if line_no <= len(lines) else ""
            findings.append(Finding("prompt-injection", rule, severity, excerpt, line_no))
    for rule, severity, pattern in SECRET_PATTERNS:
        for match in re.finditer(pattern, text):
            line_no = text.count("\n", 0, match.start()) + 1
            raw = match.group(0)
            findings.append(Finding("secret", rule, severity,
                                    _redact(raw) if redact_secrets else raw, line_no))
    return findings


def scan_bytes(data):
    findings = []
    head = data[:8]
    for rule, marker in BINARY_MARKERS:
        if head.startswith(marker):
            findings.append(Finding("executable-content", rule, "high",
                                    "binary signature %r" % marker, 1))
    if b"\x00" in data[:4096]:
        findings.append(Finding("malformed-input", "null-bytes", "medium",
                                "NUL bytes in first 4KB; not plain text", 1))
    return findings


def worst_severity(findings):
    if not findings:
        return None
    return max((f.severity for f in findings), key=lambda s: SEVERITY_ORDER.get(s, 0))


def classify(policy, origin, findings, requested_trust=None):
    """Return (trust_level, security_status, reason)."""
    policy = policy or DEFAULT_POLICY
    trust = requested_trust or policy.get("default_trust", "untrusted")
    for rule in policy.get("origin_rules") or []:
        pattern = rule.get("match")
        if pattern and re.search(pattern, origin or ""):
            trust = rule.get("trust", trust)
            break
    quarantine_on = policy.get("quarantine_on") or ["critical"]
    flag_on = policy.get("flag_on") or ["high", "medium"]
    severity = worst_severity(findings)
    if severity in quarantine_on:
        return "quarantined", "quarantined", (
            "screen found a %s finding; content isolated and may not become "
            "operational instruction" % severity)
    if severity in flag_on:
        return trust, "flagged", "screen found a %s finding; review required" % severity
    return trust, "clean", "no screening finding above threshold"


def may_become_canonical(policy, trust_level):
    levels = (policy or DEFAULT_POLICY).get("trust_levels") or {}
    spec = levels.get(trust_level)
    if isinstance(spec, dict) and "may_become_canonical" in spec:
        return bool(spec["may_become_canonical"])
    return trust_level != "quarantined"


PROTECTED_PATHS = ("CLAUDE.md", ".claude", "config/trust-policy.yaml",
                   "config/vault.config.yaml", "scripts")


def is_protected(root, path):
    """True if `path` is security/policy configuration that ingested content
    must never be able to write to."""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    if rel.startswith(".."):
        return True  # outside the vault entirely: always refuse
    parts = rel.replace("\\", "/").split("/")
    for protected in PROTECTED_PATHS:
        pparts = protected.split("/")
        if parts[:len(pparts)] == pparts:
            return True
    return False


DISCLAIMER = ("Heuristic screening reduces risk; it does not guarantee detection. "
              "Source content is DATA and is never treated as agent policy.")
