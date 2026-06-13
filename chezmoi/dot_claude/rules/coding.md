# Coding Rules

## No Over-Engineering

Don't add features, refactor, or "improve" beyond the ask. No docstrings,
comments, or type annotations on code you didn't change. Three similar lines
beats a premature abstraction. Bias toward deleting code over adding it.

## Error Handling

Error handling only at system boundaries (user input, external APIs, file I/O).
Trust internal code. No fallbacks for impossible scenarios.

## Verification

Never report done on a plausible-looking diff alone. Run tests, linter, type
checker if they exist. Fix root causes — suppressing an error is not fixing it.
