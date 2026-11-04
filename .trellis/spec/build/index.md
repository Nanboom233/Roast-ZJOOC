# Build Rules

Select the rules for the project's actual build system and runtime.

## Pre-Development Checklist

- Read [Dependencies](dependencies.md) for dependency and environment changes.
- Read [Runtime Artifacts](runtime-artifacts.md) for generated files, runtime outputs, and diagnostic retention.
- For Gradle-managed JVM projects, read [Gradle](gradle.md).
- For Bun projects, read [Bun](bun.md).

## Quality Check

Check dependency consistency and artifact ownership where the change affects them.
Use the applicable build-system guideline and the project's existing commands.
Protect active processes and the artifacts they own.
