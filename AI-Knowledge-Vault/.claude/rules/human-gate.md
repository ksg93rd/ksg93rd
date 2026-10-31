# Rule: when a human must authorize

Stop and obtain explicit human authorization before:

1. Destructive filesystem changes — deleting records, directories, or backups;
   restoring over an existing vault; bulk rewrites.
2. Deleting or rewriting meaningful history (`70-runs/`, `80-reviews/`,
   `20-sources/`, git history).
3. Any change to security or policy configuration: `config/trust-policy.yaml`,
   `.claude/**`, `CLAUDE.md`, permissions, hooks.
4. Credential or access modification of any kind.
5. Production cybersecurity remediation.
6. Legal conclusions that will be relied upon outside this vault.
7. Financial recommendations derived from sensitive data.
8. Public factual assertions with significant consequences.
9. Enabling any recurring or scheduled automation.

Approving a high-risk claim requires a reviewer who is not its author.
When in doubt, ask. An unnecessary question is cheaper than an irreversible act.
