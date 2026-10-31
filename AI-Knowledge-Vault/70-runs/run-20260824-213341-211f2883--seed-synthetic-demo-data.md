---
id: run-20260824-213341-211f2883
type: run
title: seed synthetic demo data
status: success
created_at: 2026-08-24T21:33:41+00:00
updated_at: 2026-08-24T21:33:41+00:00
trust_level: internal
objective: seed synthetic demo data
trigger: seed-demo.py
started_at: 2026-08-24T21:33:41+00:00
agent: vault-cli
skill: create-record
inputs: []
records_read: []
records_created:
  - source-20260824-b694bc79
  - entity-20260824-059aed03
  - claim-20260824-d7d3ce9b
  - claim-20260824-80956143
  - claim-20260824-316fe696
  - review-20260824-196e6a7f
  - review-20260824-dfe1baca
  - decision-20260824-d3c31e1c
records_modified:
  - source-20260824-b694bc79
  - claim-20260824-d7d3ce9b
validation_result: PASS
review_result: approved
warnings: []
errors: []
retry_count: 0
completed_at: 2026-08-24T21:33:41+00:00
final_status: success
demo: true
---

## Objective

seed synthetic demo data

## Notes

- synthetic demo data seeded; every record carries demo: true
