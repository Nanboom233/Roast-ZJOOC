# CLI design and normalization boundary

## Application structure

`cli.py` owns the terminal workflow and shared operations.
`__init__.py` retains the package version. `__main__.py` retains the module entrypoint.
Remove `models.py`, `api.py`, and `runner.py` after their logic moves into `cli.py`.
Use native containers for resource and result data. Use `httpx.Client` directly.
Remove record classes, the client wrapper, report properties, and presentation callbacks between former layers.
Define no application classes. Use built-in exceptions for failures.
Use `PermissionError` for authentication failures, which stop the run before another chapter request.
Do not replace removed classes with equivalent wrapper classes or new module layers.

## Data flow

The CLI reads the URL and cookies from a file or header string, then opens an HTTP session.
It reads the chapter tree, skips complete resources, and processes each remaining resource.
The workflow updates Rich progress directly.
A final chapter request checks completion, missing resources, and newly added incomplete resources.

## Service contracts

All business requests use signed GET requests through `https://www.zjooc.cn/ajax`.
Preserve the existing query names, header signatures, cookie scope, and redirect behavior.
Use this browser User-Agent, as requested by the user:

```text
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
```

| Operation | Service |
| --- | --- |
| Course details | `/jxxt/api/course/courseInfo` |
| Chapter tree | `/jxxt/api/course/courseStudent/v2/getStudentCourseChapters` |
| Video submission | `/learningmonitor/api/learning/monitor/videoPlaying` |
| Video verification | `/jxxt/api/course/courseStudent/videoProgress` |
| Non-video initialization | `/jxxt/api/course/courseStudentScore/toLearnVideo` |
| Non-video completion | `/learningmonitor/api/learning/monitor/finishTextChapter` |

Videos submit the ceiling of the actual duration and 100 percent progress.
Video verification requires 100 percent and a playback position at least as long as the submitted duration.
Audio, PDF, and text chapters send initialization before completion.
Each non-video chapter then requires `learnStatus=2` in a fresh chapter tree.
Chapter types 1–4 differ from the material library's `FILE=5` classification.
Reject unsupported resource types and duplicate chapter IDs.
Do not follow authentication redirects or automatically replay completion requests.

## Input and terminal contracts

Expose only `--url`, `--cookies`, and `--verbose` with alias `-v`.
Disable implicit option abbreviation and additional automatic help options.
Prompt for the URL and for a Cookies file path or Cookie header string when their options are absent.
Do not collect multiline raw JSON from the terminal.
When the Cookies value names an existing file, read its content and detect JSON or Cookie header syntax.
When it does not name a file, parse it as a Cookie header string.
Accept an optional `Cookie:` prefix and semicolon-separated `name=value` pairs.
Split each pair at its first equals sign. Preserve later equals signs in its value.
Ignore empty separator segments and trim whitespace from cookie names.
For a header file, accept one `Cookie:` line among other header lines. Ignore the other headers.
Reject malformed JSON files without a fallback to header parsing.
Use a fixed 30-second request timeout. Remove the read-only execution mode.
JSON files accept a cookie array, an object with a `cookies` array, or a name/value object.
Filter unrelated cookie domains without rejecting a mixed export. Never widen their scope to ZJOOC.
Preserve accepted cookie path, persistent expiry, secure, and host-only properties.
Do not block on browser-only `httpOnly` metadata. Resolve session cookies before parsing unused expiry values.
Require a usable cookie after filtering.
Hide pasted cookie input in a terminal. Do not log cookie values.
Rich owns inventory, progress, item failures, and final results.
Preserve complete exception chains with local values hidden.
Use Rich `Text` for external names.
Keep exit codes 0 for verified success, 1 for failure, and 130 for interruption.

## Correction boundary

Normalize the existing modules without changing their behavior or adding extension points.
Keep Pyright strict. Validate application fields at their input boundaries.
Keep internal state explicit and retain existing observable results.
Document public contracts with Google-style docstrings.

Represent decoded values with one recursive JSON wire type at the native JSON decoder boundary.
The default decoder guarantees string object keys. Validate application fields after decoding.
Do not copy dictionaries or add guards for states the decoder cannot produce.

`main` owns argument parsing, input, execution, presentation, and top-level exception handling.
Inline ordinary single-caller helpers, including the former `run` workflow.
Retain helpers only for actual shared behavior, recursion, or required entrypoints.
Tests must use actual file or terminal input and preserve values passed to the client constructor.
Remove production parameters used only for test clocks, nonces, and HTTP transports.
Tests replace those native dependencies at their actual boundaries.
The final result view must show each count once.

Use `Optional` and `Union` as the original Python spec requires.
The user approved only Ruff `UP007` and `UP045` exclusions on November 3, 2026.

## Compatibility

Keep `uv run roast-zjooc`, `python -m roast_zjooc`, and all three JSON file formats.
The three-option interface replaces earlier option names, read-only mode, and help/version flags.
Use Python 3.14 for the runtime pin, minimum package version, Pyright target, and Ruff target.
Update the uv lockfile and development environment through uv.
Retain `vedioTimeLength` and `vedioDuration`, including the platform's field spelling.
Keep complete Rich exception chains. Internal module imports and callbacks are not supported package entrypoints.
Do not introduce a mandatory browser, token, or configuration file.

## Input normalization

Extract the observed 32-character hexadecimal course identifier from its recognizable course path.
Discard input scheme, host, credentials, and port. Always construct the existing fixed HTTPS origin and Referer.
Fail if the course identifier cannot be extracted.
Keep validation that affects outgoing values or credential scope.
The accepted changes follow `research/input-validation-review.md`. No new parser layer or helper is required.

## Validation and test simplification

Use a valid course name or alternate name for display. Otherwise, use the course ID.
Use the chapter ID when its display name is not a usable string.
Keep raw fallback duration data until an incomplete video needs that field.
Validate it in that fallback branch. Unused duration metadata must not block other chapters or final inventory reads.
Let native numeric conversion errors reach the existing item handler without extra exception layers.
Keep sensitive Cookie-expiry conversion errors sanitized.
Check usable cookies once after domain filtering. Retain container type checks at decoding.
Give protocol assertions one dedicated test owner. Keep the offline transport fixture focused on routing and saved state.
Reduce repeated parameter cases as specified in `research/validation-test-audit.md`.
Retain distinct authentication, resource processing, saved-state verification, and privacy regressions.
The audit's case count is evidence about duplication, not a required final count.

## Ownership and recovery

The main session owns Trellis task artifacts and integration.
Spec changes require explicit user approval.
The implement agent owns application, test, dependency, and README corrections.
The check agent verifies the candidate independently and repairs local mechanical defects.
Neither agent may commit or access live credentials.
Use file patches for authored edits. Use uv for dependency and build artifacts.
The initial repository has no commit baseline, so recovery must preserve unrelated local files.
Review changes by path and do not use destructive Git cleanup.

## README and license

Lightly edit the current README without restoring removed explanations or sections.
Compress the user's preview and embed it through a Base64 data URI.
Preserve the source image. Check readability after compression.
Data URI images work in compatible local readers. GitHub filters these images from README output.
Add the standard MIT text in `LICENSE` with `Copyright (c) 2026 Minami`.
Declare the MIT license in package metadata and verify the built license files.
Application behavior and specs remain outside this documentation change.

## Review history

The imported CLI lacked strict type checks and used unchecked JSON values.
Its tests matched interface prose. The bootstrap task referenced a nonexistent backend spec.
An unauthorized spec edit was restored before these corrections.
Earlier reviews accepted helper names as public contracts and treated passing checks as spec compliance.
The current review checks actual callers, data contracts, and rendered output against each applicable clause.
Existing specs already cover these failures. This task requires no spec change.
The user then rejected the remaining module layers and classes.
This instruction replaces the earlier decision to preserve those internal boundaries.
The user's Python 3.14 instruction replaces the earlier Python 3.12 minimum and Python 3.13 environment pin.
