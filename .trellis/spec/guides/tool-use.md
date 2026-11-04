# Tool Use

## Edit through the available file tools

Use harness-provided file tools to read and change files.
Do not use scripts to modify files.
Read-only shell inspection is permitted when no suitable reader is available.
Send deleted files to the system Trash.
Do not use permanent deletion as a cleanup shortcut.

## Use JetBrains refactoring for structural changes

This section applies to JetBrains IDEs, including IDEA, PyCharm, and CLion, when a corresponding MCP operation is available.
Use the IDE refactoring operation for semantic symbol renames and package, module, class, or file moves.
Do not replace an available semantic refactoring with text edits.
Analyze callers before you move a method to another owner.
After refactoring, check the old references.
Verify the available IDE operations before you depend on them.

Use native filesystem, Git, and build tools for their respective facts.
Check IDE-specific behavior in the actual IDE.

## Inspect applied upstream patches

Review the source after patch application.
Patch text alone does not establish correctness.
Keep upstream changes only when they serve the current feature or compilation.
Baseline warnings do not authorize adjacent cleanup.
Diff context does not grant ownership of those lines.
Do not add helpers, constants, or wrappers only to remove a warning.
