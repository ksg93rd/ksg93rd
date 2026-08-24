# Adding a subagent

Subagents are for work that benefits from a *different perspective* or a
*narrower privilege* — not for splitting up work that one pass handles fine.

## Layout

```
.claude/agents/<agent-name>.md
```

```yaml
---
name: source-verifier
description: Inspects evidence and challenges citations. Produces review results, not knowledge.
tools: Read, Grep, Glob, Bash(python3 scripts/vault.py show:*)
---
```

## Required sections

| Section | Answers |
|---|---|
| **PURPOSE** | the one job |
| **INPUTS** | what it is given |
| **OUTPUTS** | what it returns |
| **ALLOWED TOOLS** | least privilege — the narrowest set that works |
| **WRITE SCOPE** | exactly which paths and fields it may write |
| **FORBIDDEN ACTIONS** | what it must never do, stated concretely |
| **STOP CONDITIONS** | when it is finished, including unsuccessfully |
| **ESCALATION CONDITIONS** | when it must hand off to another agent or a human |

## Authority model

| Agent | May write | Never |
|---|---|---|
| `researcher` | candidate claims | approve, verify, or commit trusted knowledge |
| `source-verifier` | review results | approve a claim it authored |
| `critic` | nothing directly | approve anything |
| `linker` | relationship fields on candidates | invent an unjustified edge |
| `security-reviewer` | quarantine + security fields | raise the trust of quarantined content |
| `summarizer` | candidate artifacts | present a candidate as verified |
| `schema-validator` | failing metadata fields | delete a record to make validation pass |
| `contradiction-reviewer` | contradiction/supersession fields | delete a contradictory record |
| `project-librarian` | project/entity links | approve or verify |

**A high-risk claim must not be created and solely approved by the same agent.**
The gate enforces this: `review.run_gate` blocks approval when reviewer equals
author on a high-risk record.

## Least privilege

Give the narrowest `tools:` list that lets the agent finish. Read-only agents
get `Read, Grep, Glob` plus specific read-only `vault.py` subcommands. Only an
agent that genuinely commits knowledge needs write tools. If you are unsure,
start read-only — widening later is easy and safe; narrowing after a bad write
is not.

## When NOT to add one

- The task is a lookup, a metadata edit, or a single validated write.
- The new agent would have the same purpose and privileges as an existing one.
- You want parallelism for its own sake.

Measure the value before adding the complexity. A small system that reliably
remembers, verifies, retrieves, and explains beats a sophisticated one that
cannot prove what it did.

## Checklist

- [ ] all eight sections present
- [ ] `tools:` is the minimum that works
- [ ] write scope is specific paths/fields, not "the vault"
- [ ] forbidden actions are concrete, not "be careful"
- [ ] cannot both author and approve the same high-risk record
- [ ] escalation path named
- [ ] does not duplicate an existing agent
