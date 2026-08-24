# Adding a Skill

Skills hold *procedures*. `CLAUDE.md` holds *durable rules*. If you are about
to add a numbered procedure to `CLAUDE.md`, it belongs here instead.

## Layout

```
.claude/skills/<skill-name>/SKILL.md
```

Frontmatter needs a `name` and a `description`. The description is what makes
the Skill get picked up, so write it as *when to use this*, not *what it is*:

```yaml
---
name: verify-source
description: Check that a source is intact, available, correctly classified, and
  actually supports what cites it. Use when auditing evidence or before relying
  on a source.
---
```

## Required sections

Every Skill in this vault defines all eight:

| Section | Answers |
|---|---|
| **OBJECTIVE** | what "done" means, in one sentence |
| **REQUIRED INPUTS** | what the caller must supply |
| **PROCESS** | numbered steps, with the exact commands |
| **VALIDATION** | how to prove the step worked |
| **FAILURE BEHAVIOUR** | what to do when it does not, including the retry limit |
| **STOP CONDITION** | when to stop, including stopping unsuccessfully |
| **EXPECTED OUTPUT** | what the caller receives |

A Skill without a stop condition will loop. A Skill without failure behaviour
will fail silently. Neither is acceptable here.

## Rules for vault Skills

1. Use `scripts/vault.py`, not ad-hoc file edits — it keeps ids, hashes,
   timestamps, and run linkage consistent.
2. Never instruct anything to set `verified` or `approved` outside the gate.
3. State explicitly when a step needs a human (see `.claude/rules/human-gate.md`).
4. Give a retry limit. The vault default is 3 equivalent failures.
5. Say what to do with partial success — this is the case people forget.
6. Prefer one clear command over a clever pipeline.

## Checklist

- [ ] `description` says *when to use it*
- [ ] all eight sections present
- [ ] commands copy-pasteable and tested against a scratch vault
- [ ] failure and partial-success paths described
- [ ] stop condition cannot loop
- [ ] escalation to a human named where required
- [ ] validation step included

## Test it

```bash
cp -r "$VAULT" /tmp/skill-test && export VAULT_GIT_DIR=/tmp/skill-test-git
# run the Skill's commands against /tmp/skill-test, then:
python3 /tmp/skill-test/scripts/vault.py validate --vault /tmp/skill-test
```

Never rehearse a new Skill against the production vault.
