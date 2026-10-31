# Recovery procedures

Golden rules: **the Markdown records are the only irreplaceable thing.** Indexes
and the graph are rebuildable. Never "fix" a problem by deleting evidence.

Before any recovery, snapshot the current state so the recovery is itself
reversible:

```bash
python3 scripts/vault.py backup --label before-recovery
```

---

## 1. Accidental deletion of a record

**If git has it (most cases):**
```bash
G=~/.ai-knowledge-vault/git/<hash>.git
git --git-dir=$G --work-tree="$VAULT" log --oneline --diff-filter=D -- '10-claims/*'
git --git-dir=$G --work-tree="$VAULT" checkout <sha>^ -- <path-to-record>
python3 scripts/vault.py rebuild-index && python3 scripts/vault.py validate
```

**If git does not have it:** restore from a backup into a scratch directory,
copy the single file across, rebuild, validate.

Find the right git dir with `python3 -c "import sys; sys.path.insert(0,'scripts');
from vaultlib import config; print(config.git_dir('$VAULT'))"`.

---

## 2. Bad agent write

```bash
python3 scripts/vault.py provenance <record-id>       # see what changed and when
git --git-dir=$G --work-tree="$VAULT" diff HEAD~1 -- <path>
git --git-dir=$G --work-tree="$VAULT" checkout HEAD~1 -- <path>
python3 scripts/vault.py rebuild-index && python3 scripts/vault.py validate
```

If several records were touched in one run, find them from the run record —
`records_created` and `records_modified` list exactly what it wrote:

```bash
python3 scripts/vault.py show <run-id>
```

Revert per file. Do not `git reset --hard` the whole tree unless you have
confirmed no unrelated work would be lost.

---

## 3. Git rollback of a whole commit

```bash
git --git-dir=$G --work-tree="$VAULT" revert --no-edit <sha>   # preferred: additive
```

`revert` creates a new commit undoing the old one, so the history of what
happened stays intact. Prefer it to `reset`, which discards history.

---

## 4. Broken or missing search index

The index is disposable.

```bash
rm -f "$VAULT/indexes/vault.db"
python3 scripts/vault.py rebuild-index
```

If the rebuild reports unreadable files, fix those first (sections 1 and 7) —
the index is telling you the truth about the records.

---

## 5. Corrupted graph export

```bash
rm -f "$VAULT/indexes/graph.json"
python3 scripts/vault.py graph-export
python3 scripts/vault.py validate
```

`dangling_edges > 0` means records reference ids that do not exist. Fix the
records; never hand-edit `graph.json`.

---

## 6. iCloud sync conflict

iCloud may leave files like `claim-… 2.md` or `… (conflicted copy).md`.

1. **Do not delete either copy.**
2. Compare them: `diff "original.md" "original 2.md"`.
3. Keep the correct one under the original filename.
4. If both contain real content, ingest the second as a revision so the
   supersession chain records it:
   `python3 scripts/vault.py ingest "original 2.md" --revises <source-id>`
5. For a claim, create the alternative as its own claim and mark the pair
   `contradicts` — then adjudicate through review.
6. `rebuild-index && validate`.

Never treat iCloud conflict resolution as source control.

---

## 7. Cloud-only / unavailable files

Symptoms: `health-check` fails `files-locally-available`; `validate` reports
`icloud-unavailable`; ingestion refuses a zero-byte file.

```bash
brctl download "$HOME/Library/Mobile Documents/com~apple~CloudDocs/AI-Knowledge-Vault"
```

Then re-run `validate`. Do not process an incomplete source set: an answer
computed from a partially-downloaded vault is wrong in a way nothing will flag.

---

## 8. Failed migration or a bad bulk edit

```bash
python3 scripts/vault.py verify-backup <archive>            # 1. confirm the backup is good
python3 scripts/vault.py restore <archive> /tmp/vault-restore --yes   # 2. restore aside
python3 scripts/vault.py rebuild-index --vault /tmp/vault-restore     # 3. inspect
python3 scripts/vault.py validate --vault /tmp/vault-restore
```

Only after the restored copy validates, move it into place — and keep the
damaged copy until you are certain:

```bash
mv "$VAULT" "$VAULT.damaged-$(date +%Y%m%d%H%M)"
mv /tmp/vault-restore "$VAULT"
python3 scripts/vault.py rebuild-index && python3 scripts/vault.py health-check
```

`restore` refuses a non-empty destination by design; `--force` exists but
overwriting a live vault is a high-risk action that needs a human decision.

---

## 9. Restore drill (run this before you need it)

```bash
python3 scripts/vault.py backup --label drill
python3 scripts/vault.py verify-backup <archive>
python3 scripts/vault.py restore <archive> /tmp/drill --yes
python3 scripts/vault.py rebuild-index --vault /tmp/drill
python3 scripts/vault.py validate --vault /tmp/drill
rm -rf /tmp/drill
```

A backup that has never been restored is not yet a backup. `vault.py backup`
verifies every file hash against the manifest immediately after writing the
archive, but a full restore drill is the only end-to-end proof.

---

## What cannot be recovered

- A secret that reached git history — **rotate it**; deletion is not enough.
- Content that was never ingested. iCloud is not a backup of things outside it.
- A source's original bytes if `20-sources/_files/` was deleted and no backup
  exists. This is why backups include `_files/`.
