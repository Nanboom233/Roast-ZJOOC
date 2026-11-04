# TypeScript

Use strict TypeScript settings.
Do not use `any` except at a validated untyped SDK boundary.
Keep validation at that boundary.

Separate `import type` from value imports.
Use `export type` for type exports.
Use namespace imports when code uses a module as an aggregate.

Use kebab-case for files and directories, including React files.
Framework-required filenames are exceptions.
Use conventional casing for symbols.

Use named `export function` declarations for components, hooks, and utilities.
Use function declarations for event handlers.
Do not use default exports for ordinary modules.
Framework-required default exports are exceptions.
