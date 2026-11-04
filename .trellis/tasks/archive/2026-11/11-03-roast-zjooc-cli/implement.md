# Execution plan

## Existing deliverable

The CLI accepts a course URL and cookies, sends signed requests, and verifies recorded state with Rich output.
It supports video, audio, PDF, and text chapters and failure handling.
The PRD records the complete requirements. The design owns contracts and compatibility decisions.

## Current work

1. [x] Register the existing script as the first task and create its planning artifacts.
2. [x] Restore original specs and record the user's two approved Ruff exceptions.
3. [x] Merge application logic into `cli.py` and remove redundant classes and layer callbacks.
4. [x] Set up Python 3.14 through uv and align the package, tool targets, and README.
5. [x] Reduce options to `--url`, `--cookies`, and `--verbose`/`-v`. Remove unused mode branches and update tests and README.
6. [x] Accept Cookies as a file path or Cookie header string. Detect JSON or header content in files and remove raw JSON terminal input.
7. [x] Lightly edit README, compress and embed its preview, and add the Minami MIT license and package metadata.
8. [x] Apply the five input simplifications from the accepted review and update affected boundary tests.
9. [x] Remove unused-field restrictions and duplicate exception or empty-value checks from the second audit.
10. [x] Consolidate repeated test cases and protocol assertions while retaining distinct behavior evidence.
11. [x] Review the simplified candidate and run affected quality checks.
12. [x] Remove generated caches after the final checks.
13. [x] Complete the final review and restrict the source distribution to project and build inputs.

The main session owns task documents and integration.
The original implement agent owns application, test, and README repairs.
The check agent verifies the corrected candidate. Specs require separate approval before any edit.

## Checks

```sh
uv run pyright
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv lock --check
uv build
python3 .trellis/scripts/task.py validate .trellis/tasks/archive/2026-11/11-03-roast-zjooc-cli
```

Reuse unchanged lock evidence. Repeat entrypoint and package checks after the final CLI edit.
Use offline HTTP transport and synthetic cookies.
Set `PYTHONDONTWRITEBYTECODE=1` for Python checks. Disable pytest and Ruff caches during this pass.
The user approved the four-commit plan. Signed ordinary work commits are complete.
Infrastructure commit: `4fac4d7`. CLI commit: `9f12bff`.
Trellis records the completed task and session in separate bookkeeping commits.
