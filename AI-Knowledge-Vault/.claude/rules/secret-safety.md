# Rule: secrets never enter the vault

1. Never write a credential, API key, token, private key, or password into a
   record, a run log, a review, a summary, or a commit message — not even
   "for completeness". Run logs are scrubbed automatically; do not rely on that
   as the only control.
2. When screening finds a secret, record the rule, the line, and a redacted
   excerpt. Never the value.
3. `.gitignore` blocks common credential files. Do not weaken it.
4. Never copy sensitive configuration into the vault "so Claude can see it".
5. If a secret is already committed, tell the human immediately: it must be
   rotated, not merely deleted — deletion does not remove it from git history.
6. Do not modify existing credential storage (keychains, `.env`, CI secrets)
   without an explicit human instruction.
