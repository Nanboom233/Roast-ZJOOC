# ZJOOC course completion CLI

## Goal

Provide a terminal-only tool that completes supported ZJOOC chapters and verifies recorded server state.
Maintain the existing implementation with complete Trellis records and executable quality checks.

## Background

The user requested this CLI before Trellis was installed.
The existing implementation dates from November 2, 2026.
On November 3, the user requested its registration as the first task and correction of guideline violations.
This task replaces the generated bootstrap placeholder.
It records completed work retrospectively and distinguishes that work from current corrections.

## Requirements

| ID | Requirement |
| --- | --- |
| R1 | Accept a course URL and a cookie file path or Cookie header string through interactive input or `--url` and `--cookies`. |
| R2 | Keep the CLI terminal-only, with Rich progress, inventory, results, and complete exception chains. |
| R3 | Use uv for the Python environment, declared dependencies, lockfile, tests, and package builds. |
| R4 | Preserve video, audio, PDF, and text chapter handling and the existing signed request contract. |
| R5 | Skip complete chapters and verify recorded state before reporting completion. |
| R6 | Stop on authentication failure. Report other item failures and continue with the next chapter. |
| R7 | Keep cookie values out of logs, task records, commits, and tracebacks. Preserve existing local cookie files. |
| R8 | Supply requirements, design, execution records, context manifests, project behavior notes, and verification evidence. |
| R9 | Correct type, external-data, documentation, and test violations within the existing modules and their direct callers. |
| R10 | Preserve the installed command, module entrypoint, input formats, and exit codes. |
| R11 | Send the standard Chrome browser User-Agent supplied by the user. |
| R12 | Keep one application implementation module with no custom classes. Use native containers, the HTTP client, and built-in exceptions. |
| R13 | Remove generated Python and tool caches after verification. Send removed files to Trash. |
| R14 | Use Python 3.14 for the uv environment, package requirement, and tool targets. |
| R15 | Expose only `--url`, `--cookies`, and `--verbose` with its `-v` alias. Remove other options and their unused branches. |
| R16 | Do not accept raw JSON through interactive input. Accept a cookie file path or a Cookie header string. Auto-detect JSON or header content in a file. |
| R17 | Lightly edit the user's current English README. Compress its preview image and embed it as Base64. Add the MIT license with copyright held by Minami. |
| R18 | Remove input restrictions that do not affect execution: discarded URL origin details, unrelated cookie domains, browser-only metadata, harmless header separators, and unused session expiry. |
| R19 | Remove unused display-field restrictions, premature fallback-duration checks, redundant exception wrappers, and repeated validation tests. Give each observable contract one test owner. |

## Acceptance criteria

| ID | Observable result | Requirements |
| --- | --- | --- |
| AC1 | The task has valid metadata, all three planning documents, and context manifests with existing spec paths. | R8 |
| AC2 | Offline tests cover supported resource processing, initialization order, state verification, and failures. | R4–R6 |
| AC3 | CLI tests verify results and Rich behavior through actual boundaries without matching interface prose. | R1, R2, R10 |
| AC4 | Strict Pyright, Ruff lint, Ruff format checks, pytest, lock validation, and uv package builds pass. | R3, R9 |
| AC5 | Invalid external data produces a controlled error. Tests use synthetic cookies and isolated HTTP transport. | R7, R9 |
| AC6 | README and task notes describe actual modules, commands, API contracts, verification, and limits. | R1–R10 |
| AC7 | The installed command and module entrypoint use the three-option interface and preserve interactive input and exit codes. | R1, R10, R15 |
| AC8 | HTTP requests contain the exact browser User-Agent recorded in the design. | R11 |
| AC9 | One module owns the CLI workflow and shared operations. The application defines no custom classes. | R12 |
| AC10 | No Python or tool cache directories remain after final verification. | R13 |
| AC11 | The locked development environment and CLI checks pass with Python 3.14. | R3, R14 |
| AC12 | Interactive Cookies input accepts only a file path or header string. A file with JSON or header content parses without raw JSON terminal input. | R7, R16 |
| AC13 | README retains its short structure and accurate usage. The compressed preview has no local path dependency. MIT text and package metadata identify the license. | R17 |
| AC14 | Usable course paths and cookie inputs pass after normalization. Requests retain their fixed HTTPS destination and cookie scope. Invalid required values still fail. | R7, R18 |
| AC15 | Unused names and duration fields do not block execution. Tests retain distinct request, failure, privacy, and completion checks without duplicate matrices or global protocol assertions. | R2, R4–R7, R19 |

## Scope limits

This task does not add a GUI, browser dependency, quiz handling, or additional resource kinds.
Course material downloads remain separate from chapter completion.
No live account request forms part of this normalization pass.
Changes under `.trellis/spec/` require explicit user approval.
Local commits require approval under the Git workflow. Remote publication is outside this task.

## Validation limits

Earlier chat records report live video processing and authenticated reads before this task existed.
Those records do not establish current live compatibility.
File initialization and completion currently have static-source evidence and offline regression tests.
The verification record must state the checks run against the corrected project.
