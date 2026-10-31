---
id: run-20260824-213345-9907cb96
type: run
title: end-to-end acceptance test (20-step synthetic workflow)
status: success
created_at: 2026-08-24T21:33:45+00:00
updated_at: 2026-08-24T21:33:47+00:00
trust_level: internal
objective: end-to-end acceptance test (20-step synthetic workflow)
trigger: tests/acceptance_test.py
started_at: 2026-08-24T21:33:45+00:00
agent: vault-cli
skill: daily-triage
inputs:
  - /tmp/vault-acceptance-qbh2ebv7/inputs/acceptance-note.md
  - /tmp/vault-acceptance-qbh2ebv7/inputs/acceptance-contra.md
records_read: []
records_created:
  - source-20260824-ad94426c
  - claim-20260824-22e64238
  - claim-20260824-553f921e
  - review-20260824-bad2c027
  - review-20260824-76be0b32
records_modified:
  - claim-20260824-553f921e
  - claim-20260824-316fe696
validation_result: PASS
review_result: approved
warnings: []
errors: []
retry_count: 0
completed_at: 2026-08-24T21:33:47+00:00
final_status: success
demo: true
---

## Objective

end-to-end acceptance test (20-step synthetic workflow)

## Notes

- step 1 PASS: Ingest a synthetic source — status=ingested
- step 2 PASS: Source record created — source-20260824-ad94426c
- step 3 PASS: Content hashed (sha256) — sha256:94e21e7e9cf6e2496df51e850c828ca42bbdf4530a3280c86a6ad8a200ad8c0e
- step 4 PASS: Attempt duplicate ingestion — re-ingested the same bytes
- step 5 PASS: Duplicate detected, not duplicated — status=duplicate reused=source-20260824-ad94426c
- step 6 PASS: Candidate claims extracted — 2 claim(s), all candidate/unverified: True
- step 7 PASS: Retrieve related knowledge — 3 edge(s) from the source
- step 8 PASS: Contradiction detected — 4 contradiction candidate(s)
- step 9 PASS: Independent review performed — 5 gate checks, independence=True
- step 10 PASS: Supported claim approved -> verified — status=verified review=approved
- step 11 PASS: Conflicting claim disputed (approval blocked first) — approval blocked=True, final status=disputed
- step 12 PASS: Canonical changes committed to git — 5 commit(s) in history
- step 13 PASS: SQLite index rebuilt from canonical files — 23 records, 42 edges, fts5=True
- step 14 PASS: Graph rebuilt from canonical files — 23 nodes, 42 edges, 0 dangling
- step 15 PASS: Validator run — PASS (0 FAIL, 0 WARN)
- step 16 PASS: STATUS generated — 23 records tracked
- step 17 PASS: Provenance verified — 2 commit(s), evidence chain present
- step 18 PASS: Search retrieval demonstrated — 8 hit(s) for 'latency'
- step 19 PASS: Backup created and verified — 122 files, verified=True
- step 20 PASS: Recovery procedure validated — 23 records restored, validation=WARN
