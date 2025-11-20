# Build and Compilation

glmfix has no build system. It's a single Python file with zero external dependencies. There is nothing to compile, nothing to install, and no build step of any kind.

## Running Directly

```bash
python3 glmfix.py scan
python3 glmfix.py fix SESSION_ID
python3 glmfix.py fix-all --dry-run
```

Python 3.8 or newer is the only requirement. All imports are from the standard library:

- `json` — JSONL parsing and serialization
- `os` — file rename (atomic backup), getmtime, getsize
- `sys` — argv parsing, stderr output, exit codes
- `glob` — discovery of session files
- `datetime` — timestamps for backup filenames
- `pathlib` — Path manipulation for session file discovery

## Optional: PATH Installation

If you want to run `glmfix` without a `python3` prefix or directory path:

```bash
# Symlink into a bin directory that's on your PATH
ln -s /absolute/path/to/glmfix/glmfix.py ~/bin/glmfix
chmod +x ~/bin/glmfix
```

The shebang line at the top of `glmfix.py` handles the rest:

```python
#!/usr/bin/env python3
```

## Slash Command Deployment

The Claude Code slash command is a Markdown file, not compiled code. Deploy it by copying:

```bash
mkdir -p ~/.claude/commands
cp commands/glmfix.md ~/.claude/commands/glmfix.md
```

No restart of Claude Code is needed. The command is available immediately in new sessions.

## Packaging (Not Recommended)

glmfix is intentionally not packaged as a pip-installable module. The design goal is zero installation friction — clone and run. If you want to distribute it as part of a larger tool:

- The `glmfix.py` file is fully self-contained and can be embedded or imported.
- Internal functions (`analyze_session`, `fix_session`, etc.) return structured dicts and can be called programmatically.
- The `main()` function uses `sys.argv` directly — you can bypass it by calling `cmd_scan()`, `cmd_fix()`, or `cmd_fix_all()` directly.

## Compatibility Matrix

| Python | Status |
|--------|--------|
| 3.8 | Supported (minimum) |
| 3.9 | Supported |
| 3.10 | Supported |
| 3.11 | Supported |
| 3.12 | Supported |
| 3.13+ | Expected to work |

The codebase deliberately avoids Python 3.9+ features: no walrus operators (`:=`), no `str.removeprefix()`, no structural pattern matching (`match`/`case`).
