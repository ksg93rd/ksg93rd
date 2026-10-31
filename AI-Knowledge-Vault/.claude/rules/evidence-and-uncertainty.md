# Rule: evidence outranks confidence

1. Never present a model confidence score as proof. Confidence is not evidence.
2. Every claim cites at least one real source id. No source, no verification.
3. Track and honour: `source_quality`, `evidence_strength`,
   `verification_status`, `review_status`, `reviewed_by`, freshness, provenance.
4. Preserve uncertainty explicitly. The allowed states are `unknown`,
   `candidate`, `verified`, `disputed`, `rejected`, `superseded`. Never silently
   convert uncertainty into certainty, and never drop a qualifier in a summary.
5. Never claim extraction succeeded when no parser exists for the format. Say
   the bytes were stored and hashed, and that no text was read.
6. A matching `content_hash` proves identity, not correctness.
7. AI-generated material is `source_quality: ai-generated` — never `primary`.
8. Contradictions are preserved, not resolved by deletion. Newer is never
   assumed correct.
