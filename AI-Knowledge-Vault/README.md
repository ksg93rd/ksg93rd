# AI Knowledge Vault

## What is this?

A filing cabinet for things you and Claude have learned, stored as ordinary
files in your own iCloud Drive.

Every fact it holds is written as a plain text file you can open, read, and
edit yourself. Each fact records where it came from, how strong the evidence
is, whether anyone checked it, and whether anything contradicts it. Facts that
have not been checked say so. Facts that conflict stay conflicting until
someone resolves them — nothing quietly rounds itself up to "true".

**You do not need Claude to read your own knowledge.** That is the point.

---

## Where is my data?

In your iCloud Drive, in a folder called `AI-Knowledge-Vault`. On a Mac:

```
~/Library/Mobile Documents/com~apple~CloudDocs/AI-Knowledge-Vault
```

or in Finder: **iCloud Drive → AI-Knowledge-Vault**.

Inside are numbered folders — `10-claims`, `20-sources`, `40-decisions`, and so
on. Every file is a `.md` (Markdown) text file. Double-click one and it opens
in any text editor. There is no proprietary database holding your knowledge
hostage.

---

## What does iCloud do?

**Only one thing: it copies your files between your devices.**

iCloud is not keeping history, not checking anything, not searching, and not
protecting you from mistakes. It is a sync service. Everything else in this
list is handled by something else on purpose.

One thing to know: iCloud sometimes keeps a file only in the cloud to save disk
space. This system detects that and *refuses to work* rather than treating a
not-yet-downloaded file as an empty one. If it complains, right-click the vault
folder in Finder and choose **Download Now**.

---

## What does Claude do?

Claude reads the vault, adds new material to it, and follows the rules in
`CLAUDE.md` and `.claude/rules/`.

What Claude may **not** do:
- decide on its own that something is verified — only the review step does that;
- treat text inside a document as an instruction (a document that says "ignore
  your instructions" gets quarantined, not obeyed);
- delete your history;
- change its own rules or the security settings.

Claude's memory of your conversations is *not* the database. This vault is.

---

## What does Git do?

Git keeps the history: who changed what, when, and why — and lets you undo a
change. It runs quietly in the background.

Its bookkeeping is deliberately stored **outside** iCloud (in
`~/.ai-knowledge-vault/git/`), because Git's internal files and a sync service
corrupt each other. Your actual knowledge files stay in iCloud where you can
see them. See `docs/VERSION-CONTROL.md`.

---

## How do I add information?

Drop a file into the `00-inbox` folder, then run:

```bash
python3 scripts/vault.py ingest 00-inbox/
```

The system hashes the file (so the same document is never filed twice), screens
it for anything hostile, files it as a *source*, and stores the original.

To write something down yourself:

```bash
python3 scripts/vault.py new claim "Our renewal rate was 91 percent in Q2" \
        --source source-20260812-b77d11
```

`.md`, `.txt`, `.json`, and `.csv` files have their text read. Other formats
(PDFs, images) are stored and hashed safely, and the system says plainly that
it could not read them rather than pretending it did.

---

## How do I search?

```bash
python3 scripts/vault.py search "renewal rate"
python3 scripts/vault.py search --type claim --status disputed
python3 scripts/vault.py show claim-20260812-a91c42
python3 scripts/vault.py related claim-20260812-a91c42
```

You can also just use Finder's search, or `grep` — they are text files.

---

## How is information verified?

Nothing is verified by being written down. A new fact starts as a **candidate**.

To become **verified** it must pass a review that checks: are the required
details present; does it actually cite a source; does that source exist and is
it not quarantined; has anyone tried to disprove it; does it contradict
something already recorded; and is the reviewer someone other than the author
(required for anything high-risk).

```bash
python3 scripts/vault.py review claim-20260812-a91c42 approved \
        --reviewer yourname --rationale "figure appears verbatim in the source"
```

If any check fails, the review is **blocked** and says exactly why. Editing a
file by hand to say "verified" does not work either — validation catches it and
reports a failure.

Possible outcomes: `approved`, `rejected`, `disputed`, `needs-more-evidence`.
Rejected and disputed facts are **kept**, not deleted. Being wrong is part of
the record.

---

## How do I recover?

```bash
python3 scripts/vault.py backup            # make and verify a backup
python3 scripts/vault.py health-check      # is everything sound?
python3 scripts/vault.py validate          # what is broken, and how to fix it
```

`docs/RECOVERY.md` has step-by-step procedures for a deleted record, a bad
automated edit, a Git rollback, a broken search index, an iCloud sync conflict,
and a failed migration.

Quick reassurance: the search index and the relationship map are **disposable**.
If either breaks, delete it and run `rebuild-index` — nothing is lost, because
both are rebuilt from your text files.

---

## What should I avoid storing?

- **Passwords, API keys, tokens, private keys.** The system tries to detect and
  redact them, but do not rely on that. Use a password manager.
- Anything you are not permitted to keep — regulated personal data, someone
  else's confidential material.
- Files you have not looked at from sources you do not trust. They will be
  quarantined, but the safest untrusted file is the one you never added.
- The only copy of anything. This is a knowledge vault, not a backup service.

---

## Getting started

```bash
# On a Mac, install into iCloud Drive:
./scripts/install-icloud.sh

# Anywhere else (or a custom location):
python3 scripts/vault.py init --vault /path/to/vault --remember

# See what the environment supports:
python3 scripts/vault.py doctor
```

Then try the walkthrough:

```bash
python3 scripts/seed-demo.py        # clearly-marked synthetic example data
python3 scripts/vault.py status
python3 scripts/vault.py contradictions
```

Demo records are titled `DEMO -` and carry `demo: true`. Exclude them any time
with `--no-demo`, or delete them once you have looked around.

---

## For the technically inclined

- `docs/ARCHITECTURE.md` — design and the decisions behind it
- `docs/SCHEMA.md` — every field, value, and validation rule
- `docs/SECURITY.md` — trust boundary, screening, and its honest limits
- `docs/OPERATIONS.md` — command reference and the daily loop
- `docs/RECOVERY.md` — recovery procedures
- `docs/VERSION-CONTROL.md` — why Git lives outside iCloud
- `docs/ADDING-SKILLS.md`, `docs/ADDING-AGENTS.md` — extending it
- `docs/AUTOMATION.md` — what may be scheduled, and what must never be

Requirements: Python 3.8+ and Git. **No third-party packages** — it runs on the
Python that ships with macOS. Tests: `python3 tests/test_vault.py`.
