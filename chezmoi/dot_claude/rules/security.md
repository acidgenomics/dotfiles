# Security Rules

> MANDATORY — ALL interactions, ALL projects, ALL code.

## Secrets & Credentials

NEVER put secrets (API keys, passwords, tokens, certs, connection strings) in
code, comments, prompts, commits, or plan files — use env vars or vaults. Flag
secret-pattern files (`.env`, `credentials.json`, `*_key.*`, `*.pem`, `*token*`).

## Code Security

NEVER introduce `eval()`, `exec()`, dynamic SQL, or shell injection without
explicit approval. Sanitize inputs at boundaries; use parameterized queries. Flag
auth, crypto, network, DB, file-system, or permission changes.

## Data Privacy

NEVER include PII in code, logs, comments, AI prompts, or plan files. Flag code
transmitting user data without consent.
