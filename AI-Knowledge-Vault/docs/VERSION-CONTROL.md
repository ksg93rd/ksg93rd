# Version control: Git and iCloud together, safely

## The problem

A `.git` directory is a small database: loose objects, packfiles, refs, and an
index file, all mutated in rapid bursts. iCloud Drive syncs files
independently and opportunistically. Put them together and you can get:

- a `.git/index` synced mid-write, corrupting the staging area;
- refs pointing at objects that have not synced yet — "object not found";
- two Macs writing `.git/refs/heads/main` and producing an iCloud conflict
  copy that git cannot read;
- packfile rewrites during `gc` racing the sync daemon.

None of this is hypothetical, and iCloud's conflict resolution ("keep both")
is not a merge strategy for a repository.

## The design chosen

```
Working tree :  <iCloud>/AI-Knowledge-Vault/        ← synchronized
Git metadata :  ~/.ai-knowledge-vault/git/<hash>.git ← NOT synchronized, local
```

Git is invoked with both locations named explicitly:

```bash
git --git-dir="$HOME/.ai-knowledge-vault/git/<hash>.git" \
    --work-tree="<iCloud>/AI-Knowledge-Vault" status
```

`<hash>` is the first 12 hex characters of the SHA-256 of the vault's absolute
path, so several vaults on one Mac never collide.

**Nothing git-related is written into the synchronized folder** except a plain
`.gitignore`, which is an ordinary text file. There is no `.git` directory and
no `.git` pointer file inside iCloud, so:

- iCloud never syncs git internals, so it can never corrupt them;
- each Mac keeps its own independent history of the same synced tree;
- a health check (`git-metadata-outside-sync`) fails loudly if a `.git`
  directory ever appears inside the vault.

`gc.auto=0` is set so background packing never runs mid-sync, and
`commit.gpgsign=false` keeps commits from blocking on a signing prompt.

### Alternatives considered

| Option | Why not |
|---|---|
| `.git` inside iCloud | the corruption modes above |
| `git init --separate-git-dir` | leaves a `.git` pointer file with a machine-local absolute path inside iCloud; breaks on the second Mac |
| Repository outside iCloud, vault exported into it | two copies of the truth; export lag; the human-readable copy is no longer the canonical one |
| No git at all | no provenance, no rollback, no "who changed this and why" |

## Multiple Macs

iCloud syncs the *files*; each Mac keeps its *own* commit history. On a second
Mac simply run:

```bash
python3 scripts/vault.py init --vault "<vault path>" --remember
```

which creates that machine's local git dir and commits the current state as its
first commit. To share one history instead, add a remote to the git dir on each
Mac and push/pull explicitly:

```bash
git --git-dir=~/.ai-knowledge-vault/git/<hash>.git remote add origin <url>
git --git-dir=~/.ai-knowledge-vault/git/<hash>.git push -u origin main
```

Never resolve a knowledge conflict by picking an iCloud conflict copy. Ingest
both versions — the second as a revision with `--revises` — and let the
supersession chain record what happened.

## What gets committed

Committed: every canonical Markdown record, schemas, templates, config, docs,
`.claude/`, and `scripts/`.

Ignored (see `gitprov.GITIGNORE`): `indexes/vault.db` and its journals,
`__pycache__/`, `.DS_Store`, and credential-shaped files (`.env`, `*.pem`,
`*.key`, `id_rsa*`, `credentials.json`, `secrets.y*ml`).

`indexes/graph.json` and `indexes/status.json` *are* committed — they are
derived, but they are small, diffable, and useful in history for seeing how the
graph changed. They are still regenerated, never hand-edited.

## Commands

```bash
python3 scripts/vault.py commit -m "message"   # commit the working tree
python3 scripts/vault.py log                   # recent history
python3 scripts/vault.py provenance <id>       # evidence + commit history for one record
```

`ingest`, `review`, and `new` auto-commit when `features.auto_commit` is true
in `config/vault.config.yaml`. Set it to `false` to commit only by hand.

## Rolling back

```bash
# one record, one commit back — reversible, destroys nothing
git --git-dir=~/.ai-knowledge-vault/git/<hash>.git \
    --work-tree="<vault>" checkout <sha> -- 10-claims/<file>.md
python3 scripts/vault.py rebuild-index
```

See `RECOVERY.md` for the full procedures.
