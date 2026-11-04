# Data Contracts

## Validate external data at its boundary

Validate external container types and field types before use.
Use one shared decoder for a shared untyped payload contract.
Keep persisted domain data shapes consistent across execution modes.
Use the actual data contract in each caller and view.

Preserve the difference between missing, unknown, corrupt, unsupported, and failed states.
Do not convert these states into an empty result or a successful default.
Show an empty state only when the data contract establishes that the result is empty.

## Keep test records outside business storage

Business storage contains business facts and necessary runtime state.
Do not add test-only snapshots, fixtures, or acceptance tables to it.
Do not hide case identifiers, expected results, or test pass/fail state in business rows, JSON, or configuration.
Keep that information in the test runner or task evidence.
History and snapshots required by the business remain valid business data.
