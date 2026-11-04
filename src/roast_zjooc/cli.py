"""Run the terminal workflow with a user-supplied cookie session."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import secrets
import string
import sys
import time
from collections import Counter
from http.cookiejar import Cookie
from pathlib import Path
from typing import Optional, Union

import httpx
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.traceback import Traceback

from . import __version__

type JsonValue = Optional[Union[str, bool, int, float, list[JsonValue], dict[str, JsonValue]]]


def _request(http: httpx.Client, service: str, params: dict[str, JsonValue]) -> JsonValue:
    timestamp = time.time_ns() // 1_000_000
    nonce = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    client_signature = f"appid=D1R0m75G&timestamp={timestamp}&nonce={nonce}"
    headers = {
        "SignCheck": hashlib.md5(
            f"{timestamp}gxpt_lanao".encode(), usedforsecurity=False
        ).hexdigest(),
        "TimeDate": str(timestamp),
        "appid": "D1R0m75G",
        "timestamp": str(timestamp),
        "nonce": nonce,
        "clientsign": hashlib.md5(client_signature.encode(), usedforsecurity=False).hexdigest(),
    }
    query = {
        "time": nonce + str(timestamp),
        "service": service,
        **{f"params[{key}]": str(value) for key, value in params.items()},
        "checkTimeout": "true",
    }
    response = http.get("/ajax", params=query, headers=headers)
    if response.status_code in {301, 302, 303, 307, 308, 401, 403}:
        raise PermissionError("Authentication failed. Export current ZJOOC cookies and run again.")
    response.raise_for_status()
    try:
        payload: JsonValue = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError("The server returned a non-JSON response.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("The server response must be a JSON object.")
    code = payload.get("resultCode")
    if isinstance(code, bool) or not isinstance(code, int):
        raise RuntimeError("The server returned an invalid result code.")
    if code in {1000, 220005, 401, 409}:
        raise PermissionError(
            f"The session is not valid (code {code}). Export current cookies and run again."
        )
    success = payload.get("success")
    if "success" in payload and not isinstance(success, bool):
        raise RuntimeError("The server returned an invalid success flag.")
    if code != 0 or success is False:
        raise RuntimeError(f"The server rejected the request for {service} (code {code}).")
    return payload.get("data")


def _chapters(
    http: httpx.Client, course_id: str
) -> dict[str, tuple[str, int, int, JsonValue, JsonValue]]:
    data = _request(
        http,
        "/jxxt/api/course/courseStudent/v2/getStudentCourseChapters",
        {"pageNo": 1, "courseId": course_id, "urlNeed": 1},
    )
    if not isinstance(data, list):
        raise RuntimeError("The chapter response must contain a list.")
    resources: dict[str, tuple[str, int, int, JsonValue, JsonValue]] = {}

    def walk(nodes: list[JsonValue]) -> None:
        for node in nodes:
            if not isinstance(node, dict):
                raise RuntimeError("The chapter response contains an invalid node.")
            kind = node.get("resourceType")
            if kind is not None and (isinstance(kind, bool) or not isinstance(kind, int)):
                raise RuntimeError("A chapter resource has an invalid type.")
            if kind:
                resource_id = node.get("id")
                if not isinstance(resource_id, str) or not resource_id:
                    raise RuntimeError("A chapter resource has no ID.")
                if resource_id in resources:
                    raise RuntimeError(f"The chapter response repeats ID {resource_id}.")
                if kind not in {1, 2, 3, 4}:
                    raise RuntimeError(f"Unsupported resource type for chapter {resource_id}.")
                status = node.get("learnStatus")
                if (
                    isinstance(status, bool)
                    or not isinstance(status, int)
                    or status not in {0, 1, 2}
                ):
                    raise RuntimeError(f"Invalid learning status for chapter {resource_id}.")
                name = node.get("name")
                resources[resource_id] = (
                    name if isinstance(name, str) and name else resource_id,
                    kind,
                    status,
                    node.get("vedioTimeLength"),
                    node.get("vedioDuration"),
                )
            children = node.get("children")
            if children is not None:
                if not isinstance(children, list):
                    raise RuntimeError("The chapter response contains invalid child nodes.")
                walk(children)

    walk(data)
    return resources


def show_traceback(console: Console, error: BaseException) -> None:
    """Print all exception frames and cause chains with local values hidden.

    Args:
        console: The terminal that owns error output.
        error: The captured exception and its original cause chain.
    """
    console.print(
        Traceback.from_exception(
            type(error),
            error,
            error.__traceback__,
            show_locals=False,
            max_frames=0,
            word_wrap=True,
            width=console.width,
        )
    )


def main(argv: Optional[list[str]] = None) -> int:
    """Run the command and capture operational failures with Rich.

    Args:
        argv: Optional command arguments. The process arguments apply when absent.

    Returns:
        Zero for success, one for failure, or 130 for an interruption.
    """
    console = Console()
    try:
        parser = argparse.ArgumentParser(
            prog="roast-zjooc",
            description="Complete ZJOOC chapter resources and verify server progress.",
            exit_on_error=False,
            add_help=False,
            allow_abbrev=False,
        )
        parser.add_argument("--url", help="Course URL. Omit it for an interactive prompt.")
        parser.add_argument("--cookies", help="Cookies file path or Cookie header string.")
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Print each resource result."
        )
        args, unknown = parser.parse_known_args(argv)
        if unknown:
            raise ValueError("Unrecognized command arguments.")
        course_url: Optional[str] = args.url
        cookie_input: Optional[str] = args.cookies
        verbose: bool = args.verbose
        console.print(f"roast-zjooc {__version__}", style="bold")
        console.rule("1. Inputs")
        value = course_url or Prompt.ask("Course URL", console=console)
        match = re.search(
            r"/ucenter/student/course/study/([0-9a-fA-F]{32})(?=/|[?#]|$)", value.strip()
        )
        if not match:
            raise ValueError(
                "Supply a course URL with /ucenter/student/course/study/<32-character-course-id>/."
            )
        course_id = match.group(1)
        canonical_url = f"https://www.zjooc.cn/ucenter/student/course/study/{course_id}/"
        if cookie_input is None:
            cookie_input = console.input(
                "Cookies file path or Cookie header > ", password=sys.stdin.isatty()
            )
        if not cookie_input.strip() or "\r" in cookie_input or "\n" in cookie_input:
            raise ValueError("Supply a Cookies file path or a valid Cookie header.")
        path = Path(cookie_input.strip().strip("\"'"))
        try:
            path = path.expanduser()
            is_file = path.is_file()
        except OSError, ValueError, RuntimeError:
            is_file = False
        if is_file:
            try:
                source = path.read_text(encoding="utf-8-sig")
            except OSError:
                raise ValueError("The Cookies file cannot be read.") from None
        else:
            if cookie_input.lstrip().startswith(("{", "[")):
                raise ValueError("Supply a Cookies file path or a valid Cookie header.")
            source = cookie_input
        decoded_cookies: JsonValue
        if source.lstrip().startswith(("{", "[")):
            try:
                decoded_cookies = json.loads(source)
            except json.JSONDecodeError as exc:
                raise ValueError("The Cookies file contains invalid JSON.") from exc
        else:
            lines = [line for line in source.splitlines() if line.strip()]
            cookie_lines = [
                line.lstrip()[7:] for line in lines if line.lstrip().lower().startswith("cookie:")
            ]
            if cookie_lines:
                if len(cookie_lines) != 1:
                    raise ValueError("Supply one Cookie header.")
                source = cookie_lines[0]
            elif len(lines) != 1:
                raise ValueError("Supply a Cookies file path or a valid Cookie header.")
            else:
                source = lines[0]
            decoded_cookies = []
            for pair in source.split(";"):
                if not pair.strip():
                    continue
                name, separator, cookie_value = pair.strip().partition("=")
                name = name.strip()
                if (
                    not separator
                    or not re.fullmatch(r"[!#$%&'*+\-.^_`|~0-9A-Za-z]+", name)
                    or any(ord(char) <= 32 or ord(char) >= 127 for char in cookie_value)
                ):
                    raise ValueError("Supply a Cookies file path or a valid Cookie header.")
                decoded_cookies.append({"name": name, "value": cookie_value})
        if isinstance(decoded_cookies, dict):
            if "cookies" in decoded_cookies:
                decoded_cookies = decoded_cookies["cookies"]
            else:
                decoded_cookies = [
                    {"name": name, "value": item} for name, item in decoded_cookies.items()
                ]
        if not isinstance(decoded_cookies, list):
            raise ValueError("Cookies JSON must contain a cookie list or name/value object.")
        cookies = httpx.Cookies()
        for item in decoded_cookies:
            if not isinstance(item, dict):
                raise ValueError("Each cookie must be a JSON object.")
            raw_domain = item.get("domain")
            if raw_domain is not None and not isinstance(raw_domain, str):
                raise ValueError("Cookie domains must be strings.")
            domain = raw_domain or ".zjooc.cn"
            host = domain.lstrip(".").lower()
            if host != "zjooc.cn" and not host.endswith(".zjooc.cn"):
                continue
            name, cookie_value = item.get("name"), item.get("value")
            if not isinstance(name, str) or not name or not isinstance(cookie_value, str):
                raise ValueError("Each cookie needs a nonempty name and a string value.")
            if any(char in name + cookie_value for char in "\r\n"):
                raise ValueError("Cookie names and values must not contain line breaks.")
            raw_path = item.get("path")
            if raw_path is not None and not isinstance(raw_path, str):
                raise ValueError("Cookie paths must start with a slash.")
            cookie_path = raw_path or "/"
            if not cookie_path.startswith("/"):
                raise ValueError("Cookie paths must start with a slash.")
            for flag in ("secure", "hostOnly", "session"):
                if flag in item and not isinstance(item[flag], bool):
                    raise ValueError("Cookie flags must be boolean values.")
            expires = (
                None
                if item.get("session") is True
                else item.get("expirationDate", item.get("expires"))
            )
            if expires is not None:
                if isinstance(expires, bool) or not isinstance(expires, (str, int, float)):
                    raise ValueError("A cookie has an invalid expiry time.")
                try:
                    expires = int(float(expires))
                except ValueError, OverflowError:
                    raise ValueError("A cookie has an invalid expiry time.") from None
                if expires < 0:
                    expires = None
            cookies.jar.set_cookie(
                Cookie(
                    version=0,
                    name=name,
                    value=cookie_value,
                    port=None,
                    port_specified=False,
                    domain=domain,
                    domain_specified=not item.get("hostOnly", False),
                    domain_initial_dot=domain.startswith("."),
                    path=cookie_path,
                    path_specified=True,
                    secure=bool(item.get("secure", True)),
                    expires=expires,
                    discard=expires is None,
                    comment=None,
                    comment_url=None,
                    rest={"HttpOnly": ""} if item.get("httpOnly") is True else {},
                    rfc2109=False,
                )
            )
        if not cookies:
            raise ValueError("The input contains no cookies for zjooc.cn.")
        console.rule("2. Course inventory")
        with httpx.Client(
            base_url="https://www.zjooc.cn",
            cookies=cookies,
            headers={
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": canonical_url,
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
                ),
            },
            timeout=30,
            follow_redirects=False,
        ) as http:
            with console.status("Read course and chapter status..."):
                info = _request(http, "/jxxt/api/course/courseInfo", {"courseId": course_id})
                if not isinstance(info, dict):
                    raise RuntimeError("The course response must contain an object.")
                publish_status = info.get("publishStatus")
                if publish_status is not None and (
                    isinstance(publish_status, bool) or not isinstance(publish_status, int)
                ):
                    raise RuntimeError(
                        "The course response contains an invalid publication status."
                    )
                resources = _chapters(http, course_id)
            if not resources:
                raise RuntimeError("This course has no chapter resources.")
            course_name = course_id
            for field in ("name", "courseName"):
                display_name = info.get(field)
                if isinstance(display_name, str) and display_name:
                    course_name = display_name
                    break
            console.print(Text(course_name, style="bold"))
            console.print(Text(canonical_url, style="dim"))
            type_names = {1: "VIDEO", 2: "AUDIO", 3: "PDF", 4: "TEXT"}
            counts = Counter(item[1] for item in resources.values())
            inventory = Table("Type", "Total", "Complete", "Pending")
            for kind in sorted(counts, key=lambda kind: type_names[kind]):
                completed = sum(item[2] == 2 for item in resources.values() if item[1] == kind)
                inventory.add_row(
                    type_names[kind],
                    str(counts[kind]),
                    str(completed),
                    str(counts[kind] - completed),
                )
            console.print(inventory)
            if publish_status == 4 and any(item[2] != 2 for item in resources.values()):
                raise RuntimeError(
                    "This course is closed. The server no longer records learning progress."
                )
            console.rule("3. Submit and verify")
            verified = failed = 0
            with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}", markup=False),
                BarColumn(),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                console=console,
                expand=True,
            ) as progress:
                task = progress.add_task("Process chapter resources", total=len(resources))
                for resource_id, (name, kind, status, raw_seconds, duration) in resources.items():
                    progress.update(task, description=name[:36])
                    try:
                        if status == 2:
                            if verbose:
                                console.print(Text(f"SKIPPED: {name}"))
                            continue
                        if kind == 1:
                            if raw_seconds is not None:
                                if isinstance(raw_seconds, bool) or not isinstance(
                                    raw_seconds, (str, int, float)
                                ):
                                    raise ValueError(
                                        f"Invalid video duration for chapter {resource_id}."
                                    )
                                seconds_value = float(raw_seconds)
                            elif isinstance(duration, str) and re.fullmatch(
                                r"\d+:\d{2}:\d{2}", duration
                            ):
                                hours, minutes, seconds = map(int, duration.split(":"))
                                if minutes >= 60 or seconds >= 60:
                                    raise ValueError(
                                        f"Invalid video duration for chapter {resource_id}."
                                    )
                                seconds_value = hours * 3600 + minutes * 60 + seconds
                            else:
                                raise ValueError(
                                    f"Missing video duration for chapter {resource_id}."
                                )
                            if not math.isfinite(seconds_value) or seconds_value <= 0:
                                raise ValueError(
                                    f"Invalid video duration for chapter {resource_id}."
                                )
                            seconds = math.ceil(seconds_value)
                            _request(
                                http,
                                "/learningmonitor/api/learning/monitor/videoPlaying",
                                {
                                    "chapterId": resource_id,
                                    "courseId": course_id,
                                    "playTime": seconds,
                                    "percent": 100,
                                },
                            )
                            video = _request(
                                http,
                                "/jxxt/api/course/courseStudent/videoProgress",
                                {"chapterId": resource_id, "courseId": course_id},
                            )
                            if not isinstance(video, dict):
                                raise RuntimeError(
                                    "The video progress response must contain an object."
                                )
                            raw_percent, raw_time = video.get("percent"), video.get("playTime")
                            if (
                                isinstance(raw_percent, bool)
                                or not isinstance(raw_percent, (str, int, float))
                                or isinstance(raw_time, bool)
                                or not isinstance(raw_time, (str, int, float))
                            ):
                                raise RuntimeError(
                                    f"Invalid video progress for chapter {resource_id}."
                                )
                            percent, play_time = float(raw_percent), float(raw_time)
                            if (
                                percent != 100
                                or not math.isfinite(play_time)
                                or play_time < seconds
                            ):
                                raise RuntimeError(
                                    f"The server did not record complete video progress "
                                    f"for chapter {resource_id}."
                                )
                        else:
                            _request(
                                http,
                                "/jxxt/api/course/courseStudentScore/toLearnVideo",
                                {
                                    "courseId": course_id,
                                    "chapterId": resource_id,
                                    "resourceType": kind,
                                },
                            )
                            _request(
                                http,
                                "/learningmonitor/api/learning/monitor/finishTextChapter",
                                {"courseId": course_id, "chapterId": resource_id},
                            )
                            recorded = _chapters(http, course_id).get(resource_id)
                            if recorded is None or recorded[2] != 2:
                                raise RuntimeError(
                                    "The server did not record completion "
                                    f"for chapter {resource_id}."
                                )
                        verified += 1
                        if verbose:
                            console.print(Text(f"VERIFIED: {name}"))
                    except PermissionError:
                        raise
                    except Exception as exc:
                        failed += 1
                        console.print(Text(f"FAILED: {name}", style="red"))
                        show_traceback(console, exc)
                    finally:
                        progress.update(task, advance=1)
                progress.update(task, description="Read final server state")
                final = _chapters(http, course_id)
            console.rule("4. Final result")
            completed = sum(item[2] == 2 for item in final.values())
            remaining = {key: item for key, item in final.items() if item[2] != 2}
            remaining.update({key: item for key, item in resources.items() if key not in final})
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_row("Complete on server", f"{completed}/{len(final)}")
            if verified:
                table.add_row("Newly verified", str(verified))
            if failed:
                table.add_row("Failed checks", str(failed))
            console.print(table)
            if remaining:
                pending = Table("Type", "Resource", "Final state")
                for resource_id, item in remaining.items():
                    state = "Missing" if resource_id not in final else "Incomplete"
                    pending.add_row(type_names[item[1]], Text(item[0]), state)
                console.print(pending)
            return 0 if final and not remaining and not failed else 1
    except KeyboardInterrupt:
        console.print("\nStopped. Run again to process unfinished resources.", style="yellow")
        return 130
    except Exception as error:
        show_traceback(console, error)
        return 1
