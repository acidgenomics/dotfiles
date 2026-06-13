# Security Rules

> MANDATORY — ALL interactions, ALL projects, ALL code.

## Secrets & Credentials

- NEVER put API keys, passwords, tokens, certs, or connection strings in code,
  comments, prompts, commits, or plan files. Use env vars or vaults.
- Flag secret-pattern files: `.env`, `credentials.json`, `*_key.*`, `*.pem`,
  `*.p12`, `secrets.*`, `*token*`. Warn before committing; recommend rotation.

## Code Security

- Flag security-sensitive changes: auth, crypto, network, DB queries, file
  system, permission changes.
- NEVER introduce `eval()`, `exec()`, dynamic SQL, or shell injection without
  explicit approval. Sanitize inputs at boundaries. Use parameterized queries.

## Data Privacy

- NEVER include PII in code, logs, comments, AI prompts, or plan files.
- Flag code transmitting user data without consent; warn on info-leaking errors.
