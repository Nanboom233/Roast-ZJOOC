# Errors and Logging

## Preserve the observed failure

Report the observed facts, relevant context, and original cause chain.
Do not replace evidence with a list of guessed causes.
Do not use a broad catch to flatten different failures into one result.
Convert exceptions at a boundary only when its contract requires that conversion.

Include safe diagnostic context and counts when they help explain the failure.
Do not include credential values in logs, errors, or reports.

## Give logging one owner

The application entrypoint owns logging setup.
Do not create log files or configure global handlers during module import.
Avoid duplicate handlers and duplicate output.
Record a failure once at the layer that owns its handling.

## Retry under the operation contract

The operation owner controls retries.
Check the operation's replay contract before a retry.
Do not replay successful steps or operations that permit only one execution.
Preserve the failure state when retry is not permitted.
