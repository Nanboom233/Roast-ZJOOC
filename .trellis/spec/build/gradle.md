# Gradle for JVM Projects

## Keep build logic local and ordered

Inline a helper with one caller, even when the helper is long.
Extract helpers only for actual reuse.
Inline an expression or provider that has one read.
Keep repeated reads local to their task when possible.
Use file-level values only for shared identity or construction.
Preserve lazy provider evaluation.

Use this declaration order:

1. Imports, `buildscript`, and plugins.
2. Project identity and build directories.
3. Language and toolchain configuration.
4. Configurations and dependencies.
5. Shared compile, test, and run configuration.
6. Reused helpers.
7. Task declarations.

## Use Gradle execution contracts

Prefer native task dependencies, included builds, and `JavaExec` to raw process execution.
Preserve arguments, toolchain selection, exit status, and the original failure cause when a process boundary is necessary.
Use explicit Gradle Kotlin DSL tasks or JVM task classes for project-owned build automation.
Do not add or retain project-owned `.js` or `.mjs` build scripts.
Do not make JavaScript or Node.js a prerequisite for project builds or maintenance.

## Keep generated files under their owner

Use the owner's default `layout.buildDirectory` for generated build, test, debug, and temporary output.
Do not add parallel output roots.
Gradle wrapper source files and caches are exceptions.
Apply [Runtime Artifacts](runtime-artifacts.md) when active processes use generated artifacts.

## Separate production tasks from verification

Production artifact tasks and server run tasks must not compile or execute test sources.
They must not depend on `Test`, `check`, `patchCheck`, or other verification tasks.
The standard `build` lifecycle may still depend on `check` or tests.
Put runtime smoke checks in ordinary tests or explicit verification tasks.
