from __future__ import annotations

import hashlib
import io
import json
from functools import partial
from pathlib import Path
from typing import Optional, Union
from unittest.mock import Mock

import httpx
import pytest
from rich.console import Console
from rich.progress import Progress, ProgressColumn
from rich.text import Text
from rich.traceback import Traceback

from roast_zjooc import cli
from roast_zjooc.cli import JsonValue

COURSE_ID = "8a221122a079851f01a089ef43b03a72"
COURSE_URL = f"https://www.zjooc.cn/ucenter/student/course/study/{COURSE_ID}/"
COOKIE_VALUE = "test-session-not-a-real-credential"
COOKIE_JSON = json.dumps({"lano.connect.sid": COOKIE_VALUE})

# These paths come from the platform request contract.
COURSE = "/jxxt/api/course/courseInfo"
CHAPTERS = "/jxxt/api/course/courseStudent/v2/getStudentCourseChapters"
VIDEO = "/learningmonitor/api/learning/monitor/videoPlaying"
PROGRESS = "/jxxt/api/course/courseStudent/videoProgress"
START = "/jxxt/api/course/courseStudentScore/toLearnVideo"
FINISH = "/learningmonitor/api/learning/monitor/finishTextChapter"


def chapter(
    resource_id: str, kind: int = 1, status: int = 0, seconds: JsonValue = "12.2"
) -> dict[str, JsonValue]:
    return {
        "id": resource_id,
        "name": f"Chapter {resource_id}",
        "resourceType": kind,
        "learnStatus": status,
        "vedioTimeLength": seconds,
    }


def reply(data: JsonValue = None) -> httpx.Response:
    return httpx.Response(200, json={"resultCode": 0, "success": True, "data": data})


@pytest.fixture
def nodes() -> list[dict[str, JsonValue]]:
    return [chapter("video")]


@pytest.fixture
def responses() -> dict[tuple[str, str], list[httpx.Response]]:
    return {}


@pytest.fixture
def calls() -> list[httpx.Request]:
    return []


@pytest.fixture
def ignored() -> set[str]:
    return set()


@pytest.fixture
def course() -> dict[str, JsonValue]:
    return {"name": "Offline course", "publishStatus": 1}


@pytest.fixture(autouse=True)
def offline(
    monkeypatch: pytest.MonkeyPatch,
    nodes: list[dict[str, JsonValue]],
    responses: dict[tuple[str, str], list[httpx.Response]],
    calls: list[httpx.Request],
    ignored: set[str],
    course: dict[str, JsonValue],
) -> Mock:
    playback: dict[str, dict[str, JsonValue]] = {}
    started: set[str] = set()

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        query = request.url.params
        service = query["service"]
        resource_id = query.get("params[chapterId]", "")
        queued = responses.get((service, resource_id))
        if queued:
            return queued.pop(0) if len(queued) > 1 else queued[0]
        if service == COURSE:
            return reply(course)
        if service == CHAPTERS:
            return reply(list(nodes))
        if service == START:
            started.add(resource_id)
            return reply()
        if service in {VIDEO, FINISH}:
            if service == VIDEO:
                seconds = int(query["params[playTime]"])
                if resource_id not in ignored:
                    playback[resource_id] = {"percent": 100, "playTime": seconds}
            else:
                assert resource_id in started
            if resource_id not in ignored:
                pending: list[JsonValue] = list(nodes)
                while pending:
                    node = pending.pop()
                    assert isinstance(node, dict)
                    if node.get("id") == resource_id:
                        node["learnStatus"] = 2
                    children = node.get("children")
                    if isinstance(children, list):
                        pending.extend(children)
            return reply()
        if service == PROGRESS:
            return reply(playback.get(resource_id, {"percent": 0, "playTime": 0}))
        raise AssertionError(service)

    constructor = Mock(wraps=partial(httpx.Client, transport=httpx.MockTransport(handle)))
    monkeypatch.setattr(httpx, "Client", constructor)
    return constructor


@pytest.fixture
def argv(tmp_path: Path) -> list[str]:
    path = tmp_path / "cookies.json"
    path.write_text(COOKIE_JSON, encoding="utf-8-sig")
    return ["--url", COURSE_URL, "--cookies", str(path)]


@pytest.fixture(autouse=True)
def terminal(monkeypatch: pytest.MonkeyPatch) -> tuple[Console, io.StringIO, Mock]:
    stream = io.StringIO()
    console = Console(file=stream, width=100, force_terminal=False)
    output = Mock(wraps=console.print)
    monkeypatch.setattr(console, "print", output)
    monkeypatch.setattr(cli, "Console", lambda: console)
    return console, stream, output


def test_all_kinds_use_expected_requests_and_progress(
    monkeypatch: pytest.MonkeyPatch,
    nodes: list[dict[str, JsonValue]],
    calls: list[httpx.Request],
    argv: list[str],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    nodes[:] = [chapter("done", status=2)] + [chapter(str(kind), kind) for kind in range(1, 5)]
    nodes[0].update({"name": {}, "vedioDuration": []})
    nodes[1]["vedioDuration"] = {}
    nodes[3]["vedioDuration"] = []
    instances: list[Progress] = []

    def make_progress(
        *columns: Union[str, ProgressColumn], console: Console, expand: bool
    ) -> Progress:
        progress = Progress(*columns, console=console, expand=expand)
        instances.append(progress)
        return progress

    monkeypatch.setattr(cli, "Progress", make_progress)
    assert cli.main(argv) == 0
    assert [(r.url.params["service"], r.url.params.get("params[chapterId]")) for r in calls] == [
        (COURSE, None),
        (CHAPTERS, None),
        (VIDEO, "1"),
        (PROGRESS, "1"),
        (START, "2"),
        (FINISH, "2"),
        (CHAPTERS, None),
        (START, "3"),
        (FINISH, "3"),
        (CHAPTERS, None),
        (START, "4"),
        (FINISH, "4"),
        (CHAPTERS, None),
        (CHAPTERS, None),
    ]
    assert calls[2].url.params["params[playTime]"] == "13"
    assert calls[2].url.params["params[percent]"] == "100"
    assert calls[1].url.params["params[pageNo]"] == "1"
    assert calls[1].url.params["params[urlNeed]"] == "1"
    assert calls[4].url.params["params[resourceType]"] == "2"
    assert calls[7].url.params["params[resourceType]"] == "3"
    assert calls[10].url.params["params[resourceType]"] == "4"
    assert all(
        r.extensions["timeout"] == dict.fromkeys(("connect", "read", "write", "pool"), 30)
        for r in calls
    )
    assert all(node["learnStatus"] == 2 for node in nodes)
    assert len(instances) == 1
    assert instances[0].tasks[0].completed == instances[0].tasks[0].total == 5
    assert "5/5" in terminal[1].getvalue()
    assert COOKIE_VALUE not in terminal[1].getvalue()


def test_clock_and_nonce_reach_native_request(
    monkeypatch: pytest.MonkeyPatch, argv: list[str], calls: list[httpx.Request]
) -> None:
    monkeypatch.setattr(cli.time, "time_ns", lambda: 1_730_000_000_123_000_000)
    monkeypatch.setattr(cli.secrets, "choice", Mock(return_value="A"))
    assert cli.main(argv) == 0
    request = calls[0]
    timestamp, nonce = "1730000000123", "A" * 32
    assert request.method == "GET"
    assert request.url.scheme == "https" and request.url.host == "www.zjooc.cn"
    assert request.url.path == "/ajax"
    assert request.url.params == httpx.QueryParams(
        {
            "time": nonce + timestamp,
            "service": COURSE,
            "params[courseId]": COURSE_ID,
            "checkTimeout": "true",
        }
    )
    assert request.headers["timestamp"] == request.headers["TimeDate"] == timestamp
    assert request.headers["nonce"] == nonce
    assert request.headers["appid"] == "D1R0m75G"
    assert (
        request.headers["SignCheck"]
        == hashlib.md5(f"{timestamp}gxpt_lanao".encode(), usedforsecurity=False).hexdigest()
    )
    assert (
        request.headers["clientsign"]
        == hashlib.md5(
            f"appid=D1R0m75G&timestamp={timestamp}&nonce={nonce}".encode(), usedforsecurity=False
        ).hexdigest()
    )
    assert request.headers["Accept"] == "application/json"
    assert request.headers["X-Requested-With"] == "XMLHttpRequest"
    assert request.headers["Referer"] == COURSE_URL
    assert request.headers["User-Agent"] == (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
    )
    assert "authorization" not in request.headers
    assert request.headers["Cookie"] == f"lano.connect.sid={COOKIE_VALUE}"


@pytest.mark.parametrize("option", ["--verbose", "-v"])
def test_verbose_options_show_each_resource_result(
    option: str,
    nodes: list[dict[str, JsonValue]],
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    nodes[:] = [chapter("done", status=2), chapter("pending")]
    assert cli.main([*argv, option]) == 0
    assert [r.url.params["service"] for r in calls] == [COURSE, CHAPTERS, VIDEO, PROGRESS, CHAPTERS]
    text = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Text)]
    assert sum("Chapter done" in item.plain for item in text) == 1
    assert sum("Chapter pending" in item.plain for item in text) == 1


def test_complete_resources_are_skipped(
    nodes: list[dict[str, JsonValue]], argv: list[str], calls: list[httpx.Request]
) -> None:
    nodes[0]["learnStatus"] = 2
    assert cli.main(argv) == 0
    assert [r.url.params["service"] for r in calls] == [COURSE, CHAPTERS, CHAPTERS]


@pytest.mark.parametrize("kind", [1, 3])
def test_success_without_saved_progress_fails(
    kind: int,
    nodes: list[dict[str, JsonValue]],
    ignored: set[str],
    argv: list[str],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    nodes[:] = [chapter("unsaved", kind)]
    ignored.add("unsaved")
    assert cli.main(argv) == 1
    traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
    assert len(traces) == 1
    assert traces[0].trace.stacks[0].exc_type == "RuntimeError"
    assert nodes[0]["learnStatus"] == 0


@pytest.mark.parametrize("service", [START, FINISH, VIDEO])
def test_item_failure_continues_without_replaying_steps(
    service: str,
    nodes: list[dict[str, JsonValue]],
    responses: dict[tuple[str, str], list[httpx.Response]],
    calls: list[httpx.Request],
    argv: list[str],
) -> None:
    nodes[:] = [chapter("bad", 1 if service == VIDEO else 3), chapter("good")]
    responses[(service, "bad")] = [httpx.Response(200, json={"resultCode": 9})]
    assert cli.main(argv) == 1
    services = [(r.url.params["service"], r.url.params.get("params[chapterId]")) for r in calls]
    assert services.count((service, "bad")) == 1
    if service == START:
        assert (FINISH, "bad") not in services
    assert (VIDEO, "good") in services
    assert nodes[0]["learnStatus"] == 0
    assert nodes[1]["learnStatus"] == 2


def test_auth_failure_stops_later_items(
    nodes: list[dict[str, JsonValue]],
    responses: dict[tuple[str, str], list[httpx.Response]],
    calls: list[httpx.Request],
    argv: list[str],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    nodes[:] = [chapter("bad"), chapter("later")]
    responses[(VIDEO, "bad")] = [httpx.Response(200, json={"resultCode": 409})]
    assert cli.main(argv) == 1
    assert [r.url.params["service"] for r in calls] == [COURSE, CHAPTERS, VIDEO]
    traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
    assert len(traces) == 1
    assert traces[0].trace.stacks[0].exc_type == "PermissionError"


@pytest.mark.parametrize("final", [[], [chapter("done", status=2), chapter("added")]])
def test_final_inventory_detects_missing_and_added_chapters(
    final: JsonValue,
    responses: dict[tuple[str, str], list[httpx.Response]],
    argv: list[str],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    responses[(CHAPTERS, "")] = [reply([chapter("done", status=2)]), reply(final)]
    assert cli.main(argv) == 1
    assert (
        "Chapter added" in terminal[1].getvalue()
        if final
        else "Chapter done" in terminal[1].getvalue()
    )
    assert "1/2" in terminal[1].getvalue() if final else "0/0" in terminal[1].getvalue()


@pytest.mark.parametrize("seconds", [None, "NaN", 0, "invalid", True, {}])
def test_invalid_duration_does_not_invent_time(
    seconds: JsonValue,
    nodes: list[dict[str, JsonValue]],
    calls: list[httpx.Request],
    argv: list[str],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    nodes[:] = [chapter("bad", seconds=seconds), chapter("good")]
    assert cli.main(argv) == 1
    assert [
        r.url.params["params[chapterId]"] for r in calls if r.url.params["service"] == VIDEO
    ] == ["good"]
    if seconds == "invalid":
        traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
        assert [stack.exc_type for stack in traces[0].trace.stacks] == ["ValueError"]


@pytest.mark.parametrize(
    ("duration", "expected"), [("01:02:03", "3723"), ("00:01:60", None), ([], None)]
)
def test_duration_text_fallback(
    duration: JsonValue,
    expected: Optional[str],
    nodes: list[dict[str, JsonValue]],
    calls: list[httpx.Request],
    argv: list[str],
) -> None:
    nodes[0]["vedioTimeLength"] = None
    nodes[0]["vedioDuration"] = duration
    assert cli.main(argv) == (0 if expected else 1)
    submissions = [r for r in calls if r.url.params["service"] == VIDEO]
    assert [r.url.params["params[playTime]"] for r in submissions] == (
        [expected] if expected else []
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("playTime", True),
        ("percent", {}),
        ("playTime", "invalid"),
        ("playTime", "inf"),
        ("playTime", 0),
    ],
)
def test_invalid_video_progress_fails_verification(
    field: str,
    value: JsonValue,
    responses: dict[tuple[str, str], list[httpx.Response]],
    argv: list[str],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    data: dict[str, JsonValue] = {"percent": 100, "playTime": 13}
    data[field] = value
    responses[(PROGRESS, "video")] = [reply(data)]
    assert cli.main(argv) == 1
    if value == "invalid":
        traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
        assert [stack.exc_type for stack in traces[0].trace.stacks] == ["ValueError"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("resourceType", True),
        ("resourceType", 1.0),
        ("resourceType", 5),
        ("learnStatus", True),
        ("learnStatus", 2.0),
        ("learnStatus", -1),
        ("id", ""),
        ("children", {}),
    ],
)
def test_invalid_chapter_fields_fail_before_updates(
    field: str,
    value: JsonValue,
    nodes: list[dict[str, JsonValue]],
    argv: list[str],
    calls: list[httpx.Request],
) -> None:
    nodes[0][field] = value
    assert cli.main(argv) == 1
    assert [r.url.params["service"] for r in calls] == [COURSE, CHAPTERS]


@pytest.mark.parametrize("data", [None, [False], [chapter("dup"), chapter("dup")], []])
def test_invalid_or_empty_chapter_inventory_fails(
    data: JsonValue, responses: dict[tuple[str, str], list[httpx.Response]], argv: list[str]
) -> None:
    responses[(CHAPTERS, "")] = [reply(data)]
    assert cli.main(argv) == 1


def test_nested_chapters_are_processed(nodes: list[dict[str, JsonValue]], argv: list[str]) -> None:
    nodes[:] = [{"resourceType": 0, "children": [{"children": [chapter("nested", 3)]}]}]
    assert cli.main(argv) == 0


@pytest.mark.parametrize("status", [302, 401, 403])
def test_http_auth_failure_does_not_follow_redirect(
    status: int,
    responses: dict[tuple[str, str], list[httpx.Response]],
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    responses[(COURSE, "")] = [
        httpx.Response(status, headers={"Location": "https://example.com/login"})
    ]
    assert cli.main(argv) == 1
    assert len(calls) == 1
    traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
    assert traces[0].trace.stacks[0].exc_type == "PermissionError"


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"resultCode": False},
        {"resultCode": []},
        {"resultCode": 0, "success": "false"},
        {"resultCode": 0, "success": False},
    ],
)
def test_invalid_response_envelope_fails(
    payload: JsonValue, responses: dict[tuple[str, str], list[httpx.Response]], argv: list[str]
) -> None:
    responses[(COURSE, "")] = [httpx.Response(200, json=payload)]
    assert cli.main(argv) == 1


@pytest.mark.parametrize(
    "data",
    [None, {"publishStatus": "4"}, {"publishStatus": False}],
)
def test_invalid_course_metadata_fails(
    data: JsonValue, responses: dict[tuple[str, str], list[httpx.Response]], argv: list[str]
) -> None:
    responses[(COURSE, "")] = [reply(data)]
    assert cli.main(argv) == 1


@pytest.mark.parametrize(
    ("primary", "alternate", "expected"),
    [("Course", {}, "Course"), ({}, "Alternate", "Alternate"), ([], {}, COURSE_ID)],
)
def test_display_names_use_a_string_or_identifier(
    primary: JsonValue,
    alternate: JsonValue,
    expected: str,
    course: dict[str, JsonValue],
    nodes: list[dict[str, JsonValue]],
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    course.update({"name": primary, "courseName": alternate})
    nodes[:] = [chapter("fallback-chapter", status=2)]
    nodes[0].update({"name": {}, "vedioDuration": []})
    assert cli.main([*argv, "-v"]) == 0
    text = [i.plain for c in terminal[2].call_args_list for i in c.args if isinstance(i, Text)]
    assert expected in text
    assert any("fallback-chapter" in item for item in text)
    assert [request.url.params["service"] for request in calls] == [COURSE, CHAPTERS, CHAPTERS]


def test_closed_course_blocks_updates(
    course: dict[str, JsonValue], calls: list[httpx.Request], argv: list[str]
) -> None:
    course["publishStatus"] = 4
    assert cli.main(argv) == 1
    assert all(r.url.params["service"] in {COURSE, CHAPTERS} for r in calls)


@pytest.mark.parametrize(
    "source",
    [
        {"lano.connect.sid": COOKIE_VALUE},
        [{"name": "lano.connect.sid", "value": COOKIE_VALUE}],
        {"cookies": [{"name": "lano.connect.sid", "value": COOKIE_VALUE}]},
    ],
)
def test_cookie_formats_reach_native_client(
    source: JsonValue, argv: list[str], calls: list[httpx.Request]
) -> None:
    Path(argv[3]).write_text(json.dumps(source), encoding="utf-8-sig")
    assert cli.main(argv) == 0
    assert calls[0].headers["Cookie"] == f"lano.connect.sid={COOKIE_VALUE}"


def test_cookie_properties_survive_input(argv: list[str], offline: Mock) -> None:
    Path(argv[3]).write_text(
        json.dumps(
            [
                {
                    "name": "sid",
                    "value": COOKIE_VALUE,
                    "domain": "www.zjooc.cn",
                    "path": "/ajax",
                    "hostOnly": True,
                    "httpOnly": True,
                    "secure": False,
                    "expirationDate": 2_100_000_000,
                }
            ]
        ),
        encoding="utf-8",
    )
    assert cli.main(argv) == 0
    cookies = offline.call_args.kwargs["cookies"]
    assert isinstance(cookies, httpx.Cookies)
    cookie = next(iter(cookies.jar))
    assert cookie.domain == "www.zjooc.cn" and not cookie.domain_specified
    assert cookie.path == "/ajax" and cookie.path_specified
    assert cookie.expires == 2_100_000_000 and not cookie.discard
    assert not cookie.secure and cookie.has_nonstandard_attr("HttpOnly")


def test_session_cookie_discards_expiry(argv: list[str], offline: Mock) -> None:
    Path(argv[3]).write_text(
        json.dumps(
            [
                {
                    "name": "sid",
                    "value": COOKIE_VALUE,
                    "expires": "unused",
                    "session": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    assert cli.main(argv) == 0
    cookies = offline.call_args.kwargs["cookies"]
    assert isinstance(cookies, httpx.Cookies)
    cookie = next(iter(cookies.jar))
    assert cookie.expires is None and cookie.discard


def test_mixed_export_filters_foreign_cookies_before_irrelevant_validation(
    argv: list[str],
    calls: list[httpx.Request],
    offline: Mock,
) -> None:
    Path(argv[3]).write_text(
        json.dumps(
            [
                {"domain": ".example.org", "name": False, "value": {}, "path": 1, "expires": "bad"},
                {
                    "name": "sid",
                    "value": COOKIE_VALUE,
                    "domain": "www.zjooc.cn",
                    "path": "/ajax",
                    "hostOnly": True,
                },
            ]
        ),
        encoding="utf-8",
    )
    assert cli.main(argv) == 0
    assert calls[0].headers["Cookie"] == f"sid={COOKIE_VALUE}"
    cookies = offline.call_args.kwargs["cookies"]
    assert isinstance(cookies, httpx.Cookies)
    assert [(cookie.domain, cookie.path, cookie.domain_specified) for cookie in cookies.jar] == [
        ("www.zjooc.cn", "/ajax", False)
    ]


def test_browser_only_metadata_does_not_change_http_cookies(
    argv: list[str],
    calls: list[httpx.Request],
    offline: Mock,
) -> None:
    Path(argv[3]).write_text(
        json.dumps(
            [
                {
                    "name": "sid",
                    "value": COOKIE_VALUE,
                    "httpOnly": "false",
                    "secure": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    assert cli.main(argv) == 0
    assert calls[0].headers["Cookie"] == f"sid={COOKIE_VALUE}"
    cookies = offline.call_args.kwargs["cookies"]
    assert isinstance(cookies, httpx.Cookies)
    cookie = next(iter(cookies.jar))
    assert cookie.secure and not cookie.has_nonstandard_attr("HttpOnly")


@pytest.mark.parametrize(
    "source",
    [
        [],
        None,
        [False],
        {"sid": 1},
        [{"name": "sid", "value": COOKIE_VALUE, "domain": "evil.cn"}],
        [{"name": "sid", "value": COOKIE_VALUE, "secure": "false"}],
        [{"name": "sid", "value": COOKIE_VALUE, "hostOnly": 1}],
        [{"name": "sid", "value": COOKIE_VALUE, "domain": 0}],
        [{"name": "sid", "value": COOKIE_VALUE, "path": False}],
        [{"name": "sid", "value": COOKIE_VALUE, "expires": True}],
        [{"name": "sid\n", "value": COOKIE_VALUE}],
        [{"name": "sid", "value": COOKIE_VALUE, "expires": COOKIE_VALUE}],
    ],
)
def test_invalid_cookies_fail_without_exposure(
    source: JsonValue,
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    Path(argv[3]).write_text(json.dumps(source), encoding="utf-8")
    assert cli.main(argv) == 1
    assert not calls
    assert COOKIE_VALUE not in terminal[1].getvalue()


@pytest.mark.parametrize(
    "url",
    [
        "https://www.zjooc.cn/",
        COURSE_URL.replace(COURSE_ID, COURSE_ID + "a"),
    ],
)
def test_invalid_url_fails_before_requests(
    url: str, argv: list[str], calls: list[httpx.Request]
) -> None:
    argv[1] = url
    assert cli.main(argv) == 1
    assert not calls


@pytest.mark.parametrize(
    "url",
    [
        COURSE_URL.removeprefix("https://"),
        COURSE_URL.replace("www.zjooc.cn", "[discarded-invalid-origin"),
    ],
)
def test_course_path_uses_fixed_destination_and_referer(
    url: str, argv: list[str], calls: list[httpx.Request]
) -> None:
    argv[1] = url
    assert cli.main(argv) == 0
    assert all(
        request.url.host == "www.zjooc.cn" and request.url.scheme == "https" for request in calls
    )
    assert all(request.headers["Referer"] == COURSE_URL for request in calls)


@pytest.mark.parametrize("option", [["--unknown-option"], ["--url"]])
def test_argument_errors_use_rich(
    option: list[str], terminal: tuple[Console, io.StringIO, Mock]
) -> None:
    assert cli.main(option) == 1
    assert any(isinstance(i, Traceback) for c in terminal[2].call_args_list for i in c.args)


def test_unquoted_header_argument_does_not_echo_credentials(
    argv: list[str], calls: list[httpx.Request], terminal: tuple[Console, io.StringIO, Mock]
) -> None:
    argv[3] = "Cookie:"
    assert cli.main([*argv, f"sid={COOKIE_VALUE}"]) == 1
    assert not calls
    assert COOKIE_VALUE not in terminal[1].getvalue()


def test_hidden_single_line_cookie_input(
    monkeypatch: pytest.MonkeyPatch,
    terminal: tuple[Console, io.StringIO, Mock],
    calls: list[httpx.Request],
) -> None:
    terminal_input = Mock(return_value=f"Cookie: lano.connect.sid={COOKIE_VALUE}")
    monkeypatch.setattr(cli.Prompt, "ask", Mock(return_value=COURSE_URL))
    monkeypatch.setattr(terminal[0], "input", terminal_input)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    assert cli.main([]) == 0
    assert terminal_input.call_count == 1
    assert terminal_input.call_args.kwargs["password"]
    assert [r.url.params["service"] for r in calls] == [COURSE, CHAPTERS, VIDEO, PROGRESS, CHAPTERS]
    assert COOKIE_VALUE not in terminal[1].getvalue()


@pytest.mark.parametrize("prefix", ["", "Cookie: "])
def test_direct_cookie_header_preserves_equals_and_default_scope(
    prefix: str,
    argv: list[str],
    offline: Mock,
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    argv[3] = f"{prefix}; sid \t={COOKIE_VALUE}== ; ; marker=; ; "
    assert cli.main(argv) == 0
    assert calls[0].headers["Cookie"] == f"sid={COOKIE_VALUE}==; marker="
    cookies = offline.call_args.kwargs["cookies"]
    assert isinstance(cookies, httpx.Cookies)
    assert all(cookie.domain == ".zjooc.cn" and cookie.secure for cookie in cookies.jar)
    assert COOKIE_VALUE not in terminal[1].getvalue()


@pytest.mark.parametrize(
    "source",
    [
        f" sid ={COOKIE_VALUE}; marker=other; ",
        f"Host: www.zjooc.cn\nCookie: sid={COOKIE_VALUE}; marker=other\nUser-Agent: test\n",
    ],
)
def test_header_file_reaches_native_request(
    source: str,
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    Path(argv[3]).write_text(source, encoding="utf-8-sig")
    assert cli.main(argv) == 0
    assert calls[0].headers["Cookie"] == f"sid={COOKIE_VALUE}; marker=other"
    assert COOKIE_VALUE not in terminal[1].getvalue()


@pytest.mark.parametrize(
    "value",
    [
        f"User-Agent: {COOKIE_VALUE}=value",
        f"={COOKIE_VALUE}",
        f"sid={COOKIE_VALUE}; broken",
        f"sid={COOKIE_VALUE}\r\nCookie: extra=value",
        COOKIE_JSON,
    ],
)
def test_invalid_direct_cookie_input_does_not_echo_credentials(
    value: str,
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    argv[3] = value
    assert cli.main(argv) == 1
    assert not calls
    traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
    assert [stack.exc_type for stack in traces[0].trace.stacks] == ["ValueError"]
    assert COOKIE_VALUE not in terminal[1].getvalue()


def test_header_file_without_cookie_header_fails_safely(
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    Path(argv[3]).write_text(
        f"Host: www.zjooc.cn\nAuthorization: {COOKIE_VALUE}=value", encoding="utf-8"
    )
    assert cli.main(argv) == 1
    assert not calls
    assert COOKIE_VALUE not in terminal[1].getvalue()


def test_invalid_utf8_file_retains_decode_error_without_exposure(
    argv: list[str],
    calls: list[httpx.Request],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    Path(argv[3]).write_bytes(f"sid={COOKIE_VALUE}".encode() + b"\xff")
    assert cli.main(argv) == 1
    assert not calls
    traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
    assert len(traces) == 1
    assert [stack.exc_type for stack in traces[0].trace.stacks] == ["UnicodeDecodeError"]
    assert COOKIE_VALUE not in terminal[1].getvalue()


def test_raw_json_terminal_input_stops_after_one_line(
    monkeypatch: pytest.MonkeyPatch,
    terminal: tuple[Console, io.StringIO, Mock],
    calls: list[httpx.Request],
) -> None:
    terminal_input = Mock(return_value=COOKIE_JSON)
    monkeypatch.setattr(cli.Prompt, "ask", Mock(return_value=COURSE_URL))
    monkeypatch.setattr(terminal[0], "input", terminal_input)
    assert cli.main([]) == 1
    assert terminal_input.call_count == 1
    assert not calls
    assert COOKIE_VALUE not in terminal[1].getvalue()


@pytest.mark.parametrize("cookie_input", [True, False])
def test_rich_keeps_safe_json_cause_and_hides_locals(
    cookie_input: bool,
    argv: list[str],
    responses: dict[tuple[str, str], list[httpx.Response]],
    terminal: tuple[Console, io.StringIO, Mock],
) -> None:
    if cookie_input:
        Path(argv[3]).write_text(COOKIE_JSON[:-1], encoding="utf-8")
    else:
        responses[(COURSE, "")] = [httpx.Response(200, text=COOKIE_JSON[:-1])]
    assert cli.main(argv) == 1
    traces = [i for c in terminal[2].call_args_list for i in c.args if isinstance(i, Traceback)]
    assert len(traces) == 1
    trace = traces[0]
    assert [s.exc_type for s in trace.trace.stacks] == [
        "ValueError" if cookie_input else "RuntimeError",
        "JSONDecodeError",
    ]
    assert all(stack.frames for stack in trace.trace.stacks)
    assert all(not frame.locals for stack in trace.trace.stacks for frame in stack.frames)
    assert COOKIE_VALUE not in terminal[1].getvalue()


def test_terminal_interrupt_returns_130(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.Prompt, "ask", Mock(side_effect=KeyboardInterrupt))
    assert cli.main([]) == 130
