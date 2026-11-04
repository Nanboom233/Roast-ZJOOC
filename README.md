# Roast ZJOOC

Roast your ZJOOC MOOC in SECONDS.

## Usage

Run this project with `uv`:

```sh
uv sync --locked
uv run roast-zjooc
```

Enter the course URL when prompted. For example:

```text
https://www.zjooc.cn/ucenter/student/course/study/<your_course_id>/
```

At the next prompt, enter a Cookies file path or a Cookie header string on one line.
Cookie files can contain Cookies JSON or a Cookie header.

You can also supply inputs as command options:

| Option | Purpose |
| --- | --- |
| `--url URL` | Supply the course URL. |
| `--cookies VALUE` | Supply a Cookies file path or Cookie header string. |
| `--verbose`, `-v` | Print each resource result. |

## Preview

![Terminal preview][preview]

## Disclaimer

**USE THIS AT YOUR OWN RISK.**

Roast ZJOOC is provided **AS IS**, without express or implied warranties.
The [MIT License](LICENSE) excludes warranties of merchantability, fitness for a particular purpose, and noninfringement.

## Development

The uv environment uses Python 3.14.

Use these commands to check and build the project:

```sh
uv sync --locked --group dev
uv run pyright
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv lock --check
uv build
```

Tests use a mock HTTP transport. They do not change live course progress.
They check CLI inputs, HTTP requests, recorded state, exception types, and Rich output objects.


[preview]: assets/preview.png
