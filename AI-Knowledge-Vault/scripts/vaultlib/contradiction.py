"""Contradiction / relationship proposal engine.

It PROPOSES, it never decides. Ambiguous pairs are escalated to review.
Rule: newer is NEVER assumed correct, and a contradictory record is NEVER
deleted to tidy the graph.
"""
import re

from . import records

STOPWORDS = set("""a an the of to in on at for by with and or but is are was were be been
being it its this that these those as from we our you your they their he she i not no
than then there here have has had do does did will would can could should may might""".split())

NEGATORS = {"not", "no", "never", "none", "cannot", "without", "failed", "denied",
            "false", "incorrect", "unable", "n't", "decreased", "fell", "dropped",
            "declined", "shrank", "lost", "down"}
POSITIVES = {"increased", "rose", "grew", "gained", "up", "improved", "expanded"}
ANTONYMS = [({"increased", "rose", "grew", "up", "higher", "gained", "expanded"},
             {"decreased", "fell", "declined", "down", "lower", "lost", "shrank"}),
            ({"passed", "succeeded", "approved", "accepted"},
             {"failed", "rejected", "denied", "blocked"}),
            ({"available", "online", "enabled", "supported"},
             {"unavailable", "offline", "disabled", "unsupported"}),
            ({"secure", "safe", "patched"}, {"vulnerable", "insecure", "exploitable"})]

NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?%?")


def tokens(text):
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def token_set(text):
    return set(tokens(text))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def numbers(text):
    return set(NUMBER_RE.findall(text or ""))


def classify_pair(text_a, text_b, threshold=0.30):
    """Return (relationship, confidence, rationale).

    relationship in SUPPORTS | CONTRADICTS | DUPLICATES | RELATED_TO | NO_RELATION
    'confidence' is a heuristic similarity score. It is NOT evidence and is
    never written into a record as proof.
    """
    set_a, set_b = token_set(text_a), token_set(text_b)
    similarity = jaccard(set_a, set_b)
    if similarity >= 0.92:
        return "DUPLICATES", similarity, "near-identical wording"
    if similarity < threshold:
        return "NO_RELATION", similarity, "insufficient lexical overlap"

    subject = set_a & set_b
    rationale = ["shared subject terms: %s" % ", ".join(sorted(list(subject))[:6])]

    for group_x, group_y in ANTONYMS:
        a_x, a_y = set_a & group_x, set_a & group_y
        b_x, b_y = set_b & group_x, set_b & group_y
        if (a_x and b_y) or (a_y and b_x):
            rationale.append("opposing direction terms")
            return "CONTRADICTS", similarity, "; ".join(rationale)

    neg_a, neg_b = bool(set_a & NEGATORS), bool(set_b & NEGATORS)
    if neg_a != neg_b:
        rationale.append("one statement is negated and the other is not")
        return "CONTRADICTS", similarity, "; ".join(rationale)

    num_a, num_b = numbers(text_a), numbers(text_b)
    if num_a and num_b and not (num_a & num_b) and similarity >= 0.45:
        rationale.append("same subject with different figures (%s vs %s)"
                         % (sorted(num_a)[:3], sorted(num_b)[:3]))
        return "CONTRADICTS", similarity, "; ".join(rationale)

    if similarity >= 0.55:
        return "SUPPORTS", similarity, "; ".join(rationale + ["consistent phrasing"])
    return "RELATED_TO", similarity, "; ".join(rationale)


def compare_claim(root, text, exclude_id=None, all_records=None, threshold=0.30):
    """Compare one proposition against every existing claim. Returns proposals."""
    if all_records is None:
        all_records, _ = records.load_all(root)
    proposals = []
    for record in all_records:
        if record.type != "claim" or record.id == exclude_id:
            continue
        other = "%s %s" % (record.title, _proposition(record))
        rel, score, why = classify_pair(text, other, threshold)
        if rel == "NO_RELATION":
            continue
        proposals.append({
            "target": record.id, "target_title": record.title,
            "relationship": rel, "similarity": round(score, 3), "rationale": why,
            "requires_review": rel in ("CONTRADICTS", "DUPLICATES", "SUPERSEDES")
                               or score < 0.45,
            "decided": False,
        })
    proposals.sort(key=lambda p: -p["similarity"])
    return proposals


def claim_text(record):
    """The comparable text of a claim: its title plus its stated proposition.

    Record bodies carry boilerplate headings that dilute similarity, so every
    comparison path must use this helper - otherwise the review gate and the
    vault scan disagree about what contradicts what.
    """
    return "%s %s" % (record.title, _proposition(record))


def _proposition(record):
    for line in (record.body or "").split("\n"):
        line = line.strip()
        if line and not line.startswith(("#", ">", "-", "*", "|", "`")):
            return line
    return ""


def scan_vault(root, threshold=0.30):
    """Find undeclared contradictions between existing claims."""
    all_records, _ = records.load_all(root)
    claims = [r for r in all_records if r.type == "claim"]
    found = []
    for i, first in enumerate(claims):
        for second in claims[i + 1:]:
            rel, score, why = classify_pair(
                claim_text(first), claim_text(second), threshold)
            if rel not in ("CONTRADICTS", "DUPLICATES"):
                continue
            declared = second.id in first.reflist("contradicts") or \
                first.id in second.reflist("contradicts") or \
                second.id in first.reflist("duplicates") or \
                first.id in second.reflist("duplicates")
            found.append({"a": first.id, "b": second.id, "relationship": rel,
                          "similarity": round(score, 3), "rationale": why,
                          "declared": declared,
                          "a_title": first.title, "b_title": second.title})
    return found
