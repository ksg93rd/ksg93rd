# Rule: safe writes and reversibility

1. Canonical records may be corrected or superseded; historical evidence in
   `70-runs/`, `80-reviews/`, `20-sources/`, and `90-archive/` stays
   reconstructable.
2. Prefer supersession over deletion. Prefer additive changes over rewrites.
3. Write records only through `scripts/vault.py` or the documented templates,
   so ids, hashes, timestamps, and run linkage stay consistent.
4. Never hand-edit derived artifacts: `indexes/vault.db`, `indexes/graph.json`,
   `indexes/status.json`, `STATUS.md`. Regenerate them.
5. Validate after writing. A run that leaves validation worse than it found it
   is not finished.
6. Every meaningful operation writes a RUN record. Never log a secret.
7. Retry limit: 3 equivalent failures. Then stop, classify the failure
   (TRANSIENT / VALIDATION / SECURITY / PERMISSION / DATA CONFLICT / SYSTEMIC)
   and report the root cause instead of looping.
