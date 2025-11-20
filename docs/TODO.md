# TODO

## Known Issues

- **Slash command path is hardcoded.** `commands/glmfix.md` references `~/Desktop/Projects/00_github-INPROCESS/glmfix/glmfix.py`. Users who clone the repo to a different location must manually edit the path. There's no auto-detection. A future version should use `$(dirname "$0")` or a config variable.

- **Project name decoding is a heuristic.** The `analyze_session()` function tries to reverse Claude Code's directory name encoding (`-` back to `/`), but the decode is fragile for projects with hyphens in their actual names. It's used only for display — no functional impact — but the output can look wrong for paths like `/home/user/my-cool-project`.

- **`bad_line_numbers` in analysis results is off by one for non-empty lines.** The line number is the index returned by `enumerate(f)` which counts ALL lines including empty ones, but only non-empty lines increment `total_lines`. Minor inconsistency that doesn't affect repair behavior.

## Planned Features

### High Priority

- **Formal test suite.** Create synthetic JSONL fixtures with known corruption patterns and write pytest tests against them. Currently all testing is manual against real sessions. Tracked: no issue yet.

- **Config file or env var for session path.** Allow `CLAUDE_PROJECTS_DIR` environment variable or a `~/.glmfix.conf` file to override the hardcoded `~/.claude/projects/` path. Needed for non-standard Claude Code installations and for future multi-user support.

### Medium Priority

- **GitHub Actions CI.** Add a workflow that runs `python3 -m py_compile glmfix.py` and `flake8` on every push. No test runner yet (since there's no test suite), but syntax and style checking would catch regressions.

- **Auto-detect slash command path.** Update `commands/glmfix.md` to determine the script location dynamically rather than hardcoding it.

- **Configurable backup retention.** Add a `--prune-backups` flag to `fix-all` that removes backups older than N days after successful repair.

### Low Priority

- **Session content search.** Add a `search <term>` command that greps session files for a term and reports which sessions contain it, plus their corruption status. (The slash command already has a `search` mode stub — this would implement it in the CLI too.)

- **JSON output mode.** Add a `--json` flag to `scan` that outputs machine-readable JSON instead of formatted text. Useful for scripting and agent consumption.

- **Windows path support.** Claude Code works on Windows. The path handling (hardcoded `/`, `Path.home()`, `~/.claude/`) may not work correctly on Windows. Not a current priority.

## Tech Debt

- The `main()` function's argument parsing is string-based (`sys.argv` checks). Replacing it with `argparse` would be cleaner and add `--help` output automatically. Avoided in v1 to keep the file small and the parser simple, but worth revisiting if the command interface grows.

- The project name decoding in `analyze_session()` shares no code with anything else. If Claude Code's encoding scheme changes, only this one function needs to update, which is good isolation.
