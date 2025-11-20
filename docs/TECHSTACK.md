# Tech Stack

## Runtime

| Component | Version | Rationale |
|-----------|---------|-----------|
| Python | 3.8+ | Minimum version with f-strings, walrus-free, stable pathlib. Ubiquitous on developer machines. |

## Standard Library Modules

| Module | Used For |
|--------|----------|
| `json` | Parsing JSONL lines, re-serializing repaired lines with `json.loads()` / `json.dumps()` |
| `os` | `os.rename()` for atomic backup creation, `os.path.getmtime()`, `os.path.getsize()`, `os.remove()` |
| `sys` | `sys.argv` for CLI argument parsing, `sys.stderr` for error output, `sys.exit()` for exit codes |
| `glob` | `glob.glob()` to discover all `*.jsonl` session files under `~/.claude/projects/*/` |
| `datetime` | `datetime.fromtimestamp()` for last-modified display, `datetime.now().strftime()` for backup timestamps |
| `pathlib` | `Path.home()`, `Path.stem`, `Path.parent.name` for path manipulation without string hacking |

**External dependencies: zero.** No pip packages. No virtual environment needed.

## File Formats

| Format | Description |
|--------|-------------|
| JSONL | Claude Code session files. Each line is a separate JSON object. Not a JSON array — each line is parsed independently. |
| Markdown | All documentation files. No special Markdown extensions or processors required. |

## Claude Code Slash Command

| Component | Details |
|-----------|---------|
| Skill file format | Markdown with YAML frontmatter |
| Activation | Copy to `~/.claude/commands/glmfix.md` |
| Execution | Claude Code agent invokes the skill, runs `glmfix.py` via `Bash` tool |
| Protocol | `model-invocable: false` — only invokable by human user typing `/glmfix` |

## Design Decisions

**Single file.** Everything in `glmfix.py`. No package structure, no local imports, no `__init__.py`. The goal was a tool you can download as one file and run immediately.

**Stdlib only.** Eliminates the need for pip, venvs, or any dependency management. The tool needs to run on any machine with Python 3.8+, including environments where the user may not have permissions to install packages.

**No test framework.** The tool operates on real user data (session files) that can't be mocked meaningfully without recreating Claude Code's session format. Testing is done by running against real sessions with `--dry-run`. A formal test suite with synthetic session fixtures is a planned improvement (see `docs/TODO.md`).

**Python 3.8 floor.** The codebase avoids walrus operators (`:=`), `str.removeprefix()`, structural pattern matching (`match`/`case`), and other post-3.8 additions. This keeps the tool usable on older macOS and Linux systems that ship with 3.8.

**Functions return dicts.** `analyze_session()` and `fix_session()` return structured dicts with consistent keys rather than printing directly. This separates data from display, making the functions callable programmatically and making the output format changeable without touching the core logic.

## What glmfix Does NOT Use

- No subprocess calls
- No network calls (no `urllib`, `requests`, `httpx`)
- No database
- No file watching
- No threading or async
- No external process spawning
- No eval/exec on session content
