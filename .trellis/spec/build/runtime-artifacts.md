# Runtime Artifacts

## Keep runtime ownership stable

Give each runtime directory a fixed owner.
Protect files and diagnostics that an active process still uses.
Do not let a failed publication replace the previous consistent artifact set with a partial set.

A long-running process must not execute a mutable artifact that another build task can replace or delete.
Before startup, copy the current artifact to a path that the runtime owner controls.
Build, test, and publication tasks continue to use build-owned outputs.

## Retain useful local evidence

For repeatable local tests, keep the latest diagnostics instead of creating timestamped archives for every run.
Acquire ownership before you replace prior diagnostic files.
Do not present stale files as evidence for the current run.
Business audit history is exempt from this local-test retention rule.

Capture complete raw success and failure output only when the test contract requires it.
Mark partial captures as partial.
This rule does not authorize sensitive or production data dumps.
