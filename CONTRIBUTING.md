# Contributing to glmfix

Thanks for your interest in contributing.

## Dev Setup

No dependencies beyond Python 3.8+. Clone the repo and you're ready.

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix
python3 glmfix.py scan  # verify it works
```

## How the Code is Structured

Everything lives in `glmfix.py`. There are no external dependencies, just stdlib.

Key functions:

- `find_session_files()` — globs for JSONL files under `~/.claude/projects/`
- `analyze_session(filepath)` — reads a JSONL file, counts unsigned thinking blocks
- `fix_session(filepath, dry_run)` — strips unsigned thinking blocks, creates backup, validates the result
- `cmd_scan()` / `cmd_fix()` / `cmd_fix_all()` — CLI entry points

The Claude Code slash command lives at `commands/glmfix.md`.

## Making Changes

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-fix-name`
3. Make changes — keep it simple, stdlib only, no external deps
4. Test against real Claude Code session files:
   ```bash
   python3 glmfix.py scan --verbose
   python3 glmfix.py fix-all --dry-run
   ```
5. Update CHANGELOG.md with what you changed
6. Open a PR

## Code Style

- Follow existing patterns in `glmfix.py`
- 4-space indentation
- Docstrings on all functions
- No external dependencies, ever. Stdlib only
- Functions return dicts with consistent keys for easy parsing

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:

- Your Python version
- Claude Code version
- The exact error you're seeing
- A redacted session ID if relevant

## Questions

Open an issue or reach out via GitHub: [@sanchez314c](https://github.com/sanchez314c)
