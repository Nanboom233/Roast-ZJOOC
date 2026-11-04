# Research: ZJOOCHelper Comparison

- Query: Compare the public `amdoi7/ZJOOCHelper` implementation with the local `roast-zjooc` CLI.
- Scope: mixed
- Date: 2026-11-04

## Findings

Keep `roast-zjooc` as the focused, cookie-based chapter CLI. Do not adopt the other repository's login, quiz-answer, or chapter-completion path. Its latest public commit is from 2024. Its code disables TLS checks, uses fixed request headers, and reports work without checking saved chapter state. The local CLI uses the inspected current web client's `appid` and timestamp-plus-nonce signature inputs. It also checks server progress and final chapter status. This evidence supports the local design, not a claim that every current platform endpoint will remain stable.

| Area | `ZJOOCHelper` at the inspected commit | Local `roast-zjooc` | Assessment |
| --- | --- | --- | --- |
| Purpose and input | A Python class logs in with a username, password, and OCR captcha. Its REPL handles course reports, videos, quizzes, exams, and homework. [README](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/README.md#L5) [source](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L33) | A terminal command takes a course URL and exported cookie file or header. It exposes only `--url`, `--cookies`, and `--verbose`/`-v`. `pyproject.toml:18` defines the installed command. | These tools have different goals. The older code does not provide evidence that local URL or cookie checks should be removed. |
| Authentication and transport | The class creates a `requests.Session`, then sets `verify = False`. It also submits the user's account password to the login service. [source](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L33) [login](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L42) | The CLI accepts exported cookies and does not implement account login. Interactive cookie input is hidden in a TTY. It sends requests over HTTPS and does not disable HTTPX TLS verification. `cli.py:213`, `cli.py:331` | The local credential model avoids collecting the account password. Keep cookie values out of argv when possible. The direct `--cookies` form can expose a header in shell history or process arguments. |
| Request signing | The shared headers use fixed `SignCheck` and `TimeDate` values from 2023. The file does not set `appid`, `timestamp`, `nonce`, or `clientsign`. [source](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L9) | Each request creates a current millisecond timestamp and a 32-character nonce. It sends `appid=D1R0m75G`, computes `clientsign`, and calls `GET /ajax`. `cli.py:41`, `cli.py:42`, `cli.py:43`, `cli.py:50`, `cli.py:61` | The inspected current first-party web bundle also uses `D1R0m75G` as its default and signs it with the timestamp and nonce. See `research/platform-appid.md:9` and `research/platform-appid.md:15`. The older fixed headers do not establish the current request contract. |
| Chapter inventory | It calls the older `getStudentCourseChapters` endpoint with `urlNeed=0`. It extracts resources through exactly three nested list levels and selects `learnStatus == 0`. [source](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L225) | It calls the `v2/getStudentCourseChapters` endpoint with `urlNeed=1`. It walks child lists recursively, validates resource types 1 through 4, and skips status 2. `cli.py:86`, `cli.py:91`, `cli.py:98`, `cli.py:111`, `cli.py:133`, `cli.py:399` | The local implementation covers nested video, audio, PDF, and text resources. The older tree shape and endpoint may reflect a different service contract. Do not infer that either endpoint is interchangeable. |
| Submission and verification | A truthy duration selects `videoPlaying`; a false duration selects `finishTextChapter`. It does not use `resourceType` to choose the path. The text request keys include trailing `=` characters. It prints `all done!` after request calls but does not read saved progress. [source](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L266) [text request](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L283) [completion message](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L293) | Video time is validated and rounded up. The CLI reads `videoProgress` after submission. Other resource types use `toLearnVideo`, then `finishTextChapter`, then a fresh chapter read. A final inventory controls the exit code. `cli.py:403`, `cli.py:432`, `cli.py:443`, `cli.py:477`, `cli.py:492`, `cli.py:510`, `cli.py:528` | The trailing `=` characters create different query parameter names from `params[courseId]` and `params[chapterId]`. Backend tolerance is unknown. The local success result requires recorded server state. |
| Failure handling and tests | Response parsing calls `.json()` directly in most flows. A parser-level catch prints an error, but video work has no per-resource recovery or final state check. The `get_an` send path decodes the POST body to a string, then reads `res.raise_for_status`. A string has no such attribute, so a normal decoded response raises `AttributeError`. [source](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L329) [send path](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/zjooc.py#L390) | The request wrapper validates response envelopes and stops on known auth failures. Item failures continue, while auth failures stop the run. Tests use an HTTPX mock transport and check requests, server state, auth, and final inventory. `cli.py:62`, `cli.py:69`, `cli.py:74`, `cli.py:501`, `tests/test_roast_zjooc.py:77`, `tests/test_roast_zjooc.py:287`, `tests/test_roast_zjooc.py:323` | Keep the local verification and failure model. The local tests establish offline behavior only. They do not prove live server compatibility. |
| Packaging | The full tree has no test files, project metadata, lockfile, or CI workflow. `requirements.txt` pins `ddddocr==1.5.3`, `html2text==2020.1.16`, and `requests==2.28.2`. [requirements](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/requirements.txt#L1) | The project uses `uv`, Python 3.14, HTTPX, Rich, and an installed `roast-zjooc` entry point. `pyproject.toml:12`, `pyproject.toml:13`, `pyproject.toml:18` | Keep the local package and test setup. No dependency or build pattern from the older repository is needed for this CLI. |

The repositories use MIT licenses. The remote notice names `amdoi7` and 2023. The local notice names Minami and 2026. Any copied substantial code must retain the upstream notice. This comparison requires no code reuse. [remote license](https://github.com/amdoi7/ZJOOCHelper/blob/910b85122cbd51c9c396360f2d3bb81ed8ec67e4/LICENSE#L1) `LICENSE:3`

## Files Found

- Remote `README.md`: describes the Python import and command REPL.
- Remote `zjooc.py`: contains the login, course, chapter, and assessment implementation.
- Remote `requirements.txt`: pins three runtime dependencies.
- Remote `LICENSE`: declares the MIT license and 2023 copyright.
- Remote `.gitignore`: the only other file in the complete repository tree.
- Local `src/roast_zjooc/cli.py`: contains the single CLI workflow and API calls.
- Local `tests/test_roast_zjooc.py`: contains offline request and behavior tests.
- Local `pyproject.toml` and `uv.lock`: define the package, runtime, dependencies, and tool setup.
- Local `README.md` and `LICENSE`: describe the CLI and declare the local MIT notice.
- Local `research/platform-appid.md`: records current first-party bundle evidence for the app ID and signature inputs.

The public default branch was `master` at commit `910b85122cbd51c9c396360f2d3bb81ed8ec67e4`. The commit date is 2024-05-31. The complete tree contains five files and no tests or build metadata.

## External References

- Public repository snapshot: [commit `910b851`](https://github.com/amdoi7/ZJOOCHelper/commit/910b85122cbd51c9c396360f2d3bb81ed8ec67e).
- Public branch metadata: [GitHub API](https://api.github.com/repos/amdoi7/ZJOOCHelper/branches/master). It identified `master` at the commit above.
- Remote dependency versions: `ddddocr==1.5.3`, `html2text==2020.1.16`, and `requests==2.28.2`, from the pinned `requirements.txt`.
- Current app ID evidence: the first-party bundle and its limits are recorded in `research/platform-appid.md`. That source supports the inspected web client only.

## Related Specs

- `.trellis/spec/guides/writing.md`: use current contracts and preserve attribution.
- `.trellis/spec/guides/tool-use.md`: inspect source and use available file tools for edits.
- `.trellis/spec/guides/planning.md`: read code before proposing implementation changes.
- `.trellis/spec/guides/git-workflow.md`: preserve MIT attribution and approval rules for GitHub operations.
- `.trellis/spec/languages/python.md`: local Python typing, package, and testing conventions.

## Caveats / Not Found

No remote code was run. No live ZJOOC request was made for this comparison. The source proves what this commit sends and prints. It does not prove how the current server handles old endpoints, malformed parameter names, or fixed signatures. The author's README claims are not independent evidence of successful completion. The local mock tests prove local request construction and state checks, not current backend behavior.
