# Version Map

## Current Version

**1.0.4** (2026-03-14)

## File Versions

| File | Version | Last Modified | Notes |
|------|---------|---------------|-------|
| `glmfix.py` | 1.0.0 | 2026-02-15 | Core repair engine, unchanged since initial release |
| `commands/glmfix.md` | 1.0.0 | 2026-02-15 | Slash command definition for `/glmfix` |
| `run-source-linux.sh` | 1.0.0 | 2026-03-14 | Linux run-from-source script |
| `run-source-mac.sh` | 1.0.0 | 2026-03-14 | macOS run-from-source script |
| `run-source-windows.bat` | 1.0.0 | 2026-03-14 | Windows run-from-source script |
| `.editorconfig` | 1.0.0 | 2026-03-14 | Editor configuration |
| `.python-version` | 1.0.0 | 2026-03-14 | Python version pin (3.11) |

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 1.0.4 | 2026-03-14 | Compliance audit: run scripts, .editorconfig, .python-version, updated .gitignore, directories (tests/, legacy/, resources/icons/), AGENTS.md synced |
| 1.0.3 | 2026-03-07 | Added SECURITY.md, CLAUDE.md, AGENTS.md, GitHub templates, docs/ directory with ARCHITECTURE, INSTALLATION, DEVELOPMENT |
| 1.0.2 | 2026-03-07 | Removed empty docs/ directory |
| 1.0.1 | 2026-03-07 | Rewrote README.md, updated CONTRIBUTING.md |
| 1.0.0 | 2026-02-15 | Initial release with scan, fix, fix-all, dry-run, slash command, backup/restore |

## Author

- **Author**: J. Michaels
- **GitHub**: https://github.com/sanchez314c/glmfix

## Dependencies

- **Runtime**: Python 3.8+ (stdlib only, zero external packages)
- **Build**: None (no build step, single .py file)
- **Test**: None (manual validation against real session files)

## Compatibility

| Python Version | Supported |
|---------------|-----------|
| 3.8 | Yes |
| 3.9 | Yes |
| 3.10 | Yes |
| 3.11 | Yes |
| 3.12 | Yes |
| 3.13+ | Yes (expected) |

The codebase avoids Python 3.9+ features (no `str.removeprefix()`, no walrus operators, no `match` statements) to maintain 3.8 compatibility.
