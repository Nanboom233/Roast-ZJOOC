# Python

## Keep strict types

Use Pyright or Pylance in strict mode.
Annotate all functions, including private functions.
Give attributes and state precise types.
Do not add errors to the existing type-check baseline.
Use `Optional` and `Union` syntax for optional and union types.

Get explicit approval before type-check suppression, `noqa`, configuration relaxation, or `typing.cast`.
Use the smallest approved scope and record its reason.
Do not use `Any` to hide a type defect.
Guards must check the conditions that their narrowed types claim.
Use `Protocol` for module or instance structural contracts.
Runtime attribute presence does not establish a compatible signature.

## Keep returns and helpers simple

Use tuples or native containers for composite return values.
Do not add a dataclass, `NamedTuple`, or `TypedDict` only to name returned fields.
Real domain types and wire contracts are valid separate types.

Inline a private helper with one caller.
Also inline a private helper with at most three callers and at most seven definition lines, including `def`.
Genuine public API and framework boundaries are exceptions.
Place a retained helper at the owner shared by all its callers.

Keep small custom exception classes in the module that owns them.
Create a separate `errors.py` only for more than ten actual custom exception types that require classification.

## Use explicit state and local values

Keep stable literals inline when they occur fewer than five times.
Configuration, correctness, opaque meaning, and keys vulnerable to silent spelling errors are exceptions.
Use `Enum` for internal state machines.
Keep primitive values at wire and storage boundaries when their contracts require them.
When you extend a `Literal` or `Enum`, update dependent branches.

## Document public contracts

Use Google-style docstrings for public functions.
Describe the contract, side effects, and relevant ordering or cost constraints.
Do not add a `Returns` section for `None`.

## Preserve package boundaries

Use proper packages and relative imports where applicable.
Do not modify `sys.path`, mount a source directory, or use dynamic imports to hide type errors.
Genuine dynamic plugin loading and non-package tool entrypoints retain their existing import contracts.

## Keep diagnostic dumps optional

`coredumpy` is optional.
Configure it at the application entrypoint when needed.
Use safe temporary paths and filter sensitive values.
Do not share sensitive dumps.
Send obsolete dumps to the system Trash.
