# Product Requirements Document

## Problem Statement

Claude Code stores conversation history as JSONL files in `~/.claude/projects/`. When users run sessions with sub-agents powered by non-Opus models (GLM-5, Sonnet, Haiku), those models emit `thinking` blocks without valid cryptographic signatures. The session runs fine under that model. But Opus validates every thinking block signature in the full conversation history on session resume, and rejects the session with a 400 error.

The result: sessions containing hundreds of messages, representing hours of work and valuable context, become permanently inaccessible without a repair tool.

## Goals

1. **Detect corruption.** Scan all sessions and clearly identify which ones have unsigned thinking blocks and how many.
2. **Repair safely.** Strip unsigned thinking blocks while preserving everything else. Never corrupt a session further.
3. **Be zero-friction.** No installation, no configuration, no dependencies. Clone and run.
4. **Integrate with Claude Code.** Provide a `/glmfix` slash command so users can fix sessions without leaving a Claude Code conversation.

## Non-Goals

- This tool does NOT fix every possible type of Claude Code session corruption. It handles one specific case: unsigned thinking blocks.
- This tool does NOT interact with the Anthropic API. It operates purely on local files.
- This tool does NOT manage backups long-term. It creates a single timestamped backup and leaves cleanup to the user.
- This tool does NOT support Windows paths or non-standard Claude Code installation locations (without code modification).

## Users

Claude Code users who:
- Use sub-agents powered by non-Opus models in their workflows
- Hit the "Invalid signature in thinking block" 400 error
- Want to recover sessions they can no longer resume

## Key Requirements

### Functional

| Requirement | Priority |
|-------------|----------|
| Scan all sessions under `~/.claude/projects/*/` for unsigned thinking blocks | Must have |
| Report corrupted sessions with count of bad blocks, message count, project name | Must have |
| Fix a session by full or partial UUID, with automatic backup before modification | Must have |
| Fix all corrupted sessions in one command | Must have |
| Dry run mode that simulates repair without modifying files | Must have |
| Post-repair validation — re-scan the fixed file and restore backup if any unsigned blocks remain | Must have |
| Verbose scan mode showing file path, size, first user message, modification time | Should have |
| Slash command integration (`/glmfix`) for use inside Claude Code sessions | Should have |

### Non-Functional

| Requirement | Priority |
|-------------|----------|
| Zero external dependencies (stdlib only) | Must have |
| Python 3.8+ compatibility | Must have |
| Single-file implementation | Should have |
| Atomic backup via `os.rename()` | Must have |
| Plain text output parseable by both humans and agents | Should have |

## Success Criteria

- A corrupted session that produces a 400 API error resumes successfully after running `glmfix.py fix <id>`.
- No data is lost from sessions that are either clean or successfully repaired.
- A user with Python 3.8+ can go from clone to fixed session in under 2 minutes.

## Constraints

- Stdlib only. This constraint is permanent — adding pip dependencies breaks the zero-friction install story.
- Must not break existing sessions. Every fix is preceded by an atomic backup and followed by validation.
- Python 3.8 minimum. No walrus operators, no `str.removeprefix()`, no structural pattern matching.

## Out of Scope for v1.x

- GUI or web interface
- Automated session monitoring (watching for corruption in real time)
- Support for custom Claude Code session storage locations (via config file or env var)
- Windows native path support
- Formal test suite with synthetic session fixtures
