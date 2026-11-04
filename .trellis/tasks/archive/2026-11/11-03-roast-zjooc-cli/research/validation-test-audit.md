# Input validation and test audit

## Decision

The current code still rejects unused fields and repeats some checks through large test matrices.
Remove checks on display-only fields. Check video duration text only when the workflow needs that text.
Keep checks that protect credential scope, outgoing requests, authentication handling, and completion evidence.

This audit changes only this report. Application code, tests, configuration, and specs remain unchanged.

## Scope and evidence

The audit covers all 533 application lines and all 843 test lines.
The reviewer read the task documents and all ten files in `check.jsonl`.
Applicable rules require distinct observable contracts and actual external-data checks.
They prohibit exhaustive test matrices, duplicate assertions, and unnecessary exception conversion.

Pytest collection found **38 test functions and 116 parametrized cases** on Python 3.14.8.
Collection ran with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`.
Synthetic probes used `httpx.MockTransport` and a direct synthetic Cookie header.
No probe read a cookie file or sent a network request.

Previous lint, type-check, build, and test results belong to the existing candidate.
This assessment did not repeat those checks or claim a new suite pass.

## Findings that affect usable execution

### P1: Unused duration text can block the whole course

Location: `src/roast_zjooc/cli.py:122` through line 130.

`_chapters` requires `vedioDuration` to be a string for every resource.
The workflow needs this field only for an incomplete video without `vedioTimeLength`.
The global check also runs during each completion check and the final inventory.

An already complete PDF with `vedioDuration=[]` fails before processing.
An already complete video with valid numeric seconds and `vedioDuration=[]` also fails.
Both synthetic probes returned exit 1 after the chapter request.
The same complete inventory without this unused field returned exit 0.

Remove the global duration-text guard.
Keep the raw field as `JsonValue` in the resource tuple.
Narrow it to a string only in the actual video fallback branch at line 416.
Keep numeric conversion, positive finite duration, and fallback time validation at that branch.
Do not add a helper, class, type suppression, or conversion default.

Test impact: remove the rejection case for `vedioDuration=[]` at `tests/test_roast_zjooc.py:393`.
Replace that policy assertion with a focused acceptance check for an unused duration field.

### P1: Display names can block valid course operations

Locations: `src/roast_zjooc/cli.py:119` and lines 349 through 363.

Course names and chapter names identify terminal rows. Requests use course and chapter IDs.
The course loop checks both `name` and `courseName`, even when the second field is unused.
The display then calls `str`, which already handles non-string JSON values.

With `name="Course"` and `courseName={}`, the probe returned exit 1 after only `courseInfo`.
The valid primary name made the rejected alternate name unnecessary.
A complete chapter with `name={}` also blocked the course before updates.

Remove the course-name rejection loop.
Use the first usable string name, then the course ID, for display.
For chapter names, use the chapter ID when the external name is not a usable string.
This local normalization keeps slicing and Rich `Text` type-safe.
Do not coerce malformed IDs, resource types, learning states, or completion values into successful defaults.

Test impact: remove invalid-name rejection rows at test lines 391, 459, and 460.
Test successful use of IDs or an alternate usable name through actual terminal and request boundaries.
Keep publication-state checks because they control whether updates can occur.

### P2: Numeric conversion adds an unnecessary exception layer

Locations: `src/roast_zjooc/cli.py:410` through line 415 and lines 461 through 466.

The duration branch wraps `float` failures in another `ValueError`.
The progress branch wraps them in `RuntimeError`.
Both exceptions already reach the same item-failure handler, which reports the chapter name and preserves Rich evidence.
Neither replacement type changes continuation, exit status, or authentication handling.

Keep the type guards required before conversion. Keep the finite and completion checks after conversion.
Let native conversion failures reach the existing item handler directly.
Do not apply this removal to cookie-expiry errors that suppress sensitive input values.

Test impact: remove `test_numeric_error_cause_survives_rich` at test line 832.
It requires two nested `ValueError` records from this redundant wrapper.
The invalid-duration tests already cover failed conversion and continuation.
Merge the native `ValueError` trace assertion into the existing `"invalid"` duration case.
The JSON-cause tests independently cover full Rich cause capture and hidden locals.

### P3: Empty-cookie checks have two owners

Locations: `src/roast_zjooc/cli.py:263` and line 327.

The first guard checks both list type and nonempty content.
The final guard rejects a jar with no accepted cookies after domain filtering.
An empty list can safely pass through the loop and reach the final guard.

Keep the first list type guard. Remove only its `or not decoded_cookies` condition.
Keep the final empty-jar guard as the single owner for absent usable cookies.
This removes a duplicate branch without accepting an empty credential set.

## Findings that affect test maintenance

### P2: The global transport fixture repeats protocol assertions

Location: `tests/test_roast_zjooc.py:94` through line 124.

Every request checks the fixed destination, signature formula, timestamp, nonce, headers, User-Agent, and Referer.
The same assertions run for unrelated malformed-input and completion scenarios.
This gives the protocol contract many repeated executions without a distinct behavior owner.

Move protocol assertions into `test_clock_and_nonce_reach_native_request` or one dedicated protocol test.
Use the already fixed clock and nonce to check the actual first request.
Keep fixture routing, synthetic response state, and rejection of unknown services.
Keep initialization order and final verification observations in the relevant workflow tests.
Do not replace the stateful offline fixture with separate fake clients or production test hooks.

The fixture is not wholly redundant. Its state changes distinguish request success from saved progress.

### P2: Parameter matrices repeat the same observable failure

The following changes remove 19 existing case executions before corrective acceptance tests.
This count describes specific duplicate cases. It is not a coverage quota or a final target.
These changes alone leave 37 functions and 97 cases. Updated acceptance tests can change that total.

| Current test and line | Current cases | Retain | Reason |
| --- | ---: | ---: | --- |
| `test_invalid_video_progress_fails_verification`, 368 | 10 | 5 | Keep representative corrupt responses and insufficient playback. The unsaved-progress test already owns incomplete percentage. |
| `test_session_cookie_discards_expiry`, 520 | 3 | 1 | Keep `"unused"`, which proves the expiry converter does not run. |
| `test_browser_only_metadata_does_not_change_http_cookies`, 573 | 2 | 1 | Keep the truthy string `"false"`, which catches accidental truth conversion. |
| `test_hidden_single_line_cookie_input`, 684 | 2 | 1 | One hidden header-input case covers the terminal boundary. File formats have separate owners. |
| `test_header_file_reaches_native_request`, 721 | 3 | 2 | Keep a bare Cookie line and a header block. The block also covers the prefixed-line parser. |
| `test_argument_errors_use_rich`, 667 | 3 | 2 | Keep unknown arguments and one missing-value option. Both value options use the same argparse action. |
| `test_invalid_url_fails_before_requests`, 630 | 4 | 2 | Keep a missing course path and a valid ID with an extra character. |
| `test_course_path_uses_fixed_destination_and_referer`, 647 | 4 | 2 | Keep a missing scheme and a malformed discarded authority. Scheme and port permutations add no parser branch. |
| `test_invalid_or_empty_chapter_inventory_fails`, 409 | 5 | 4 | Keep one non-list payload, a malformed node, duplicate IDs, and an empty inventory. |
| `test_invalid_response_envelope_fails`, 439 | 6 | 5 | Remove either the null or string `success` case. Both exercise the same type rule. |
| `test_invalid_direct_cookie_input_does_not_echo_credentials`, 741 | 6 | 5 | Remove the bare opaque value. The malformed segment case already proves a missing equals sign fails. |
| `test_numeric_error_cause_survives_rich`, 832 | 1 | 0 | Merge its useful evidence into the invalid-duration test and remove the redundant wrapper requirement. |

For progress, retain these five explicit `(field, value)` cases:

- `("playTime", True)` keeps a boolean from becoming recorded playback time.
- `("percent", {})` represents a structurally corrupt progress value.
- `("playTime", "invalid")` preserves numeric-conversion failure evidence.
- `("playTime", "inf")` prevents non-finite playback from satisfying completion.
- `("playTime", 0)` requires sufficient playback despite a complete percentage.

Do not retain an additional `("percent", 0)` case.
`test_success_without_saved_progress_fails[1]` already owns that observable failure through the complete workflow.
The ignored video writes no playback state at fixture line 143.
The progress response then supplies zero percentage and playback at fixture line 159.
The percentage check fails first, so an extra explicit zero-percentage case repeats the same result.

Inspect the native conversion exception in the existing `"invalid"` progress case if that wrapper also changes.
This retains numeric-failure evidence without a separate case or a fixed wrapper stack shape.

The existing unsaved-progress tests still cover the video and non-video verification paths separately.
The three item-failure stages have distinct ordering effects. Keep all three.
Keep all three JSON file formats because they enter distinct normalization branches.
Keep missing and newly added final chapters as separate completion failures.
Keep redirect handling and authentication status handling as separate external responses.
Keep both safe JSON-cause cases because file parsing and HTTP parsing own different conversions.

### P3: Some assertions constrain presentation structure rather than user results

Locations: `tests/test_roast_zjooc.py:231`, lines 333 through 334, and lines 826 through 828.

The exact number of Rich tables does not establish that the final counts and outstanding IDs are correct.
The `max_frames` attribute does not itself establish that a long traceback remains complete.

Where the test needs final results, assert the relevant counts, resource IDs, state, and exit status.
Keep rendered secret-exclusion checks and actual cause/frame checks in the dedicated diagnostic tests.
Avoid new snapshots of every Rich object or assertions against interface prose.

## Checks that still serve the contract

- Extract the required course ID and construct the fixed HTTPS destination.
- Reject malformed nonempty Cookie pairs and credential line breaks.
- Keep one-line hidden terminal input and reject raw JSON terminal input.
- Preserve accepted cookie domain, path, secure flag, host scope, and persistent expiry.
- Filter unrelated cookie domains without widening their scope.
- Keep native JSON container narrowing and required request-field checks.
- Reject duplicate chapter IDs and unsupported resource types.
- Keep learning-state checks so corrupt data cannot appear complete.
- Stop on authentication failure. Continue after other item failures without replay.
- Verify saved progress and final inventory before reporting success.
- Preserve safe exception evidence and suppress credential values.

Native library acceptance alone does not establish server acceptance for unusual Cookie values.
This audit does not recommend a general removal of Cookie syntax or scope checks.

## Completion condition for a correction

The implementation owner can apply the local removals and update the existing tests.
The owner must retain strict Pyright and the current Ruff rules.
Run the affected offline tests, then the required project quality checks for the changed candidate.
No spec edit, live service test, browser operation, or new application layer is necessary.
