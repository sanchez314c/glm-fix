# Changelog

All notable changes to this project will be documented in this file.

## [1.0.5] - 2026-03-14 17:05

### Fixed
- `fix_session()`: write failure now restores backup automatically so the file is never left missing at its original path
- `analyze_session()`: removed redundant `len(sig) > 0` check after `if sig` (dead code)
- `fix_session()`: removed redundant `len(sig) == 0` branch after `not sig` (unreachable)
- `commands/glmfix.md`: replaced hardcoded `~/Desktop/Projects/...` path with dynamic resolution relative to the installed command file; all users no longer need to manually edit the path after install

### Improved
- `cmd_scan()`: added column header and separator line to scan output
- `glmfix.py`: added `typing` imports and full type annotations on all function signatures
- `analyze_session()`: renamed loop variable `line` to `raw_line` to eliminate shadow variable confusion
- Updated docstrings for clarity throughout

### Added
- `AUDIT_REPORT.md`: full forensic audit findings and fix log

## [1.0.4] - 2026-03-14 16:15

### Added
- run-source-linux.sh, run-source-mac.sh, run-source-windows.bat for consistent launch
- .editorconfig with Python/UTF-8/LF standards
- .python-version pinned to 3.11
- tests/, legacy/, resources/icons/ directories with .gitkeep
- Compliance audit pass: AGENTS.md synced from CLAUDE.md, .gitignore expanded

## [1.0.3] - 2026-03-07 23:45

### Added
- SECURITY.md with file path handling, JSONL parsing, and data exposure considerations
- CLAUDE.md for AI assistant context (project purpose, tech stack, key decisions)
- AGENTS.md documenting how AI agents interact with the codebase
- .github/PULL_REQUEST_TEMPLATE.md with checklist for stdlib-only, backup safety, and 3.8 compat
- docs/README.md as documentation index
- docs/ARCHITECTURE.md detailing the 8-step repair process and data flow
- docs/INSTALLATION.md covering CLI and slash command setup
- docs/DEVELOPMENT.md with dev environment, testing workflow, and guide for adding new repair strategies

## [1.0.2] - 2026-03-07

### Fixed
- Removed empty `docs/` directory that was created but never populated

## [1.0.1] - 2026-03-07 23:10

### Changed
- Rewrote README.md with clearer problem description, usage examples with sample output, and better structure
- Updated CONTRIBUTING.md to remove reference to non-existent CODE_OF_CONDUCT.md
- Standardized all documentation for consistency and clarity

## [1.0.0] - 2026-02-15 18:40

### Added
- Core `glmfix.py` repair engine with scan, fix, and fix-all modes
- Claude Code slash command `/glmfix` with full argument support
- Auto-detection of corrupted sessions across all projects
- Partial UUID matching for session identification
- Timestamped backup creation before any modification
- Post-repair validation with automatic rollback on failure
- Dry-run mode for preview without modification
- Verbose scan output
- GitHub repo with issue templates, contributing guide, and MIT license
