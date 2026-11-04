# Testing

## Verify changed behavior

Use the project's existing lint, type-check, build, and test entrypoints as applicable.
Select checks for the affected behavior and concrete defects.
Check existing evidence before you add a test.
Add tests only for actual verification gaps.
Give each behavior one test owner.
Do not duplicate the same assertion across suites without a distinct contract.

Do not invent coverage quotas, exhaustive combination matrices, or per-function test checklists.
Apply an existing explicit project requirement within its stated scope.
Reuse valid verification when the candidate, inputs, and environment remain unchanged.
Repeat a check when a changed premise or failure makes its prior result inapplicable.
Remove tests that enforce an obsolete design.
Do not add absence-only checks for a retired API.

## Assert observable contracts

Assert behavior, state, exception types, and calls at real boundaries.
Do not read or search production source from tests.
Do not use regular expressions or AST scans of production source as test assertions.
Do not match log, prompt, banner, step-label, or error prose.
Do not test object shape or signatures through `hasattr`, `vars`, or similar introspection.
Do not add test-only parameters, hooks, or branches to production code.

Derive expected results from an independent contract or facts known before the operation.
Do not derive an expected result from the tested parser or the current result.
End-to-end client observations must come from the actual client boundary.
Do not fabricate them through server queries or construction of the tested object.

## Isolate test resources

Use explicit temporary paths and synthetic data.
Do not rely on real default paths, accounts, or credential stores.
Substitute at the actual constructor, clock, or write boundary when isolation requires it.
Restore substituted boundaries after the test.
Reuse the task's test environment under its owner's coordination.

## Approve live tests

Get explicit approval for each concrete live test involving real services, accounts, messages, credentials, or persistent data.
State the actions and necessary dependencies in the approval request.
Do not request approval again for actions covered by an approved concrete action list.
A new action, retry, or run requires approval unless that approval already covers it.
Offline tests do not require this live-test approval.
