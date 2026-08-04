# Coding Rules

## Error Handling

Error handling only at system boundaries (user input, external APIs, file I/O).
Trust internal code. No fallbacks for impossible scenarios.

## Verification

Never report done on a plausible-looking diff alone. Run tests, linter, type
checker if they exist. Fix root causes — suppressing an error is not fixing it.
