# Java

## Use clear imports and value contracts

Use explicit imports and simple type names.
Use a qualified name when a genuine name collision requires it.
For two or three return values, prefer an existing `Pair` or `Triple`.
Do not add a dependency only for that container.
Do not add a wrapper hierarchy for simple values.
Use `Optional` to represent return-value absence.

Use nullable direct parameters and fields when absence is valid.
An `Optional` caller passes `orElse(null)` to such a parameter.
An empty collection or zero remains a value, not an absence marker.

## Keep method boundaries justified

Inline an ordinary private method with one caller.
A retained multi-call private method needs actual reuse and at least seven body lines.
Real API, override, and default-overload boundaries are exceptions.
Validation, error, conversion, thread, and resource boundaries are also exceptions.
Do not evade the rule through visibility changes, wrappers, or padding.

Add an interface only for an actual shared contract with multiple callers.
Framework and public-contract requirements are exceptions.
Keep literals in the smallest applicable scope.
Use class constants or objects when shared identity, contract, cost, or lifecycle requires them.

## Handle nullability at real boundaries

Do not use `Objects.requireNonNull`, Java `assert`, or Guava `checkNotNull`, `checkArgument`, and `checkState` in production code.
These tools remain permitted in tests.
Use explicit guards at real validation boundaries.
Use `requireNonNullElse` or `requireNonNullElseGet` only for a genuine default value.

Annotations must describe guarantees that the code owns.
Check the actual upstream version and its nullability defaults.
Preserve override contracts and upstream nullability requirements.

## Use established Java conventions

Use Lombok in all Java projects for pure getters and setters.
Preserve accessors with meaningful logic, override contracts, or fluent API behavior.
Use a warning suppression only for a verified false positive.
Keep its scope minimal and add an English reason or ownership comment.
Individual Java suppressions do not require user approval.

Keep boolean polarity and branch order consistent within a class.
Do not copy another project's business ordering as a general rule.
Use `_` only for an unused lambda parameter when the project's JDK supports it.
Do not enable preview features or upgrade the JDK only for this spelling.

## Preserve failure ownership

The asynchronous, EventLoop, or lifecycle owner handles failures before they cross its boundary.
Preserve the original `Throwable`.
Add exception fields only when actual behavior uses them.
Do not duplicate diagnostic metadata in exception fields.

## Localize user-facing text

Use internationalization for all Java user-facing text.
Update every supported locale.
Diagnostic-only text is exempt.

## Apply Mixin constraints when relevant

Prefer a suitable public API over a Mixin.
Preserve foreign contracts and required names.
Use `@Final` only when the target is final.
When available, prefer an `@Local` name over an ordinal.
