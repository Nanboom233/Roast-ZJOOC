# Spec review

## Result

The final candidate passes review after the source distribution repair below.
The reviewer read the complete implementation, tests, task contracts, accepted audits, and applicable spec clauses.
The application needs no further correction.

## Findings resolved

The default source distribution included agent tools, Trellis task files, and local session records.
The implementation owner added an explicit source distribution file list in `pyproject.toml`.
The new archive contains 11 files. It excludes `.agents`, `.codex`, `.trellis`, credentials, and caches.
The reviewer inspected the applied configuration and complete archive inventory.
The wheel contains eight files, including the three application modules and MIT license.

Display names now use a usable primary name, alternate name, or identifier without rejecting unused display fields.
Chapter records retain raw fallback duration data. Only an incomplete video that needs fallback text checks its format.
Complete chapters, non-video resources, and videos with numeric durations accept unused malformed duration metadata.

Native numeric conversion errors reach the existing item handler without redundant exception wrappers.
Sensitive Cookie-expiry conversion errors remain sanitized.
The decoded list has one type check. The final filtered jar owns the empty-cookie failure.

The protocol contract has one dedicated test owner with a fixed clock and nonce.
Its expected service, signatures, query, headers, and User-Agent come from independent contract values.
The offline transport fixture retains routing, initialization order, saved state, and unknown-service failure.

The tests retain distinct authentication, continuation, resource processing, saved-progress, final-inventory, and privacy observations.
They replace exact table counts and Rich configuration properties with actual counts, resource identities, frames, and hidden local values.
The accepted duplicate cases and obsolete rejection policies are gone. No source scans, prose assertions, or production test hooks replace them.

## Preserved contracts

R18 normalization remains intact: fixed HTTPS requests, accepted course paths, mixed-domain filtering, harmless Cookie separators, and session expiry handling.
Cookie scope, required identifiers, persistent expiry, saved completion, and authentication failures retain their checks.
The three options, hidden one-line input, raw JSON terminal rejection, single implementation module, and native state containers remain unchanged.
No new class, helper layer, type suppression, or spec edit was required.

## Verification

The reviewer ran the final application checks on Python 3.14.8.
The packaging owner rebuilt both artifacts after the file-list repair. The reviewer checked the resulting contents independently.
The application and tests did not change during the packaging repair. Their final check results remain valid.

| Check | Result |
| --- | --- |
| `uv run --no-sync pytest -p no:cacheprovider` | Pass, 97 cases in 38 test functions |
| `uv run --no-sync pyright` | Pass, strict mode, zero errors or warnings |
| `uv run --no-sync ruff check --no-cache .` | Pass |
| `uv run --no-sync ruff format --check --no-cache .` | Pass, six files |
| `uv lock --check --offline` | Pass, including after the packaging repair |
| `uv build --offline` | Pass, corrected source distribution and wheel |
| Package inspection | Source and license match current files. Python requirement and MIT metadata are correct. |
| Command and module entrypoints | Both capture invalid URL input with Rich and return exit code 1 without network access. |
| Actual 80-column terminal output | Four resource types complete offline. Progress and final state show 4/4. Literal brackets remain visible. |

Earlier application case counts do not describe this candidate.
The unchanged hidden-input interaction retains valid 80-column PTY evidence.
README, Base64 preview, MIT text, and license metadata remain unchanged from R17.
Their valid image-render and direct package-content evidence remains applicable to those unchanged inputs.
The README commands and options match the current CLI and development configuration.
Compatible local readers display the Base64 preview. GitHub filters data URI images.

Python checks use `PYTHONDONTWRITEBYTECODE=1`. Pytest and Ruff checks disable their caches.
No live account request, credential access, spec edit, or commit occurred during review.
Task context validation passed with 12 implementation entries and 11 check entries. The final cache inventory was empty.
The user approved the four-commit plan after this review.
Signed ordinary work commits are `4fac4d7` for infrastructure and `9f12bff` for the CLI.
