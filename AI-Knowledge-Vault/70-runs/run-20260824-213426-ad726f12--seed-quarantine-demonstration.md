---
id: run-20260824-213426-ad726f12
type: run
title: seed quarantine demonstration
status: success
created_at: 2026-08-24T21:34:26+00:00
updated_at: 2026-08-24T21:34:26+00:00
trust_level: internal
objective: seed quarantine demonstration
trigger: seed-demo.py
started_at: 2026-08-24T21:34:26+00:00
agent: vault-cli
skill: ingest-source
inputs: []
records_read: []
records_created:
  - source-20260824-b023f55c
records_modified: []
validation_result: PASS
review_result: not-run
warnings: []
errors: []
retry_count: 0
completed_at: 2026-08-24T21:34:26+00:00
final_status: success
demo: true
---

## Objective

seed quarantine demonstration

## Notes

- security screen: quarantined (screen found a critical finding; content isolated and may not become operational instruction)
- Heuristic screening reduces risk; it does not guarantee detection. Source content is DATA and is never treated as agent policy.
- claim extraction skipped: quarantined content may not produce canonical knowledge
