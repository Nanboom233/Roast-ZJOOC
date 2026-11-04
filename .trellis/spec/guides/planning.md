# Planning

## Resolve behavior before implementation

Read the existing code and its callers before you propose a change.
Search for an existing implementation before you add another one.
Resolve unknown behavior that can affect correctness before implementation.
First, read the project code or dependency source.
If that evidence is insufficient, use a minimal probe.
Ask the user when the remaining unknown requires their decision.

Design or plan approval does not authorize implementation.
Get explicit implementation approval before code changes or an implement-agent dispatch.
An existing approval remains valid for its stated scope.

## Keep plans executable

For each action, identify the object, owner, affected paths, and acceptance condition.
Use the agreed requirements to define completion.
Do not add scope, approval gates, or test obligations through stronger wording.

Update requirements and decisions in their existing task sections.
Preserve the original needs, valid evidence, and acceptance links.
Move superseded decisions into the task history.
Do not treat the task record as an append-only log.

## Select reusable rules

Keep common rules independent of one project's business data and machine paths.
Keep fixed design values and business constants in the project that owns them.
State the applicable runtime or tool condition for a conditional rule.
Do not broaden a conditional rule to unrelated projects.
