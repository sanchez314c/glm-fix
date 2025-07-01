---
description: "GLM Fix — Repair Claude Code sessions corrupted by cross-model thinking block signatures"
argument-hint: "[SESSION_ID | scan | fix-all]"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
model-invocable: false
---

# /glmfix — Cross-Model Session Repair

You are Master Control. A session has been corrupted by unsigned thinking blocks from cross-model usage (GLM sub-agents producing thinking blocks without cryptographic signatures that Opus rejects).

The error manifests as:
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error",
"message":"messages.N.content.0: Invalid `signature` in `thinking` block"}}
```

## TOOL: glmfix.py

The repair engine is resolved at runtime. The slash command file lives inside
the `commands/` directory of the glmfix repo. The script is one level up:

```bash
# Locate glmfix.py relative to this command file's installed location
GLMFIX_CMD_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}" 2>/dev/null || echo "$0")")"
GLMFIX_SCRIPT="$(dirname "$GLMFIX_CMD_DIR")/glmfix.py"
# Fallback to the installed copy in ~/.claude/commands/ parent
if [ ! -f "$GLMFIX_SCRIPT" ]; then
  GLMFIX_SCRIPT="$HOME/.local/bin/glmfix.py"
fi
```

If the script cannot be found, report the path that was checked and ask the
User to run:
```bash
cp /path/to/cloned/glmfix/commands/glmfix.md ~/.claude/commands/glmfix.md
```
and ensure `glmfix.py` is accessible.

## PARSE ARGUMENTS

Parse `$ARGUMENTS` to determine operating mode:

### Mode 1: SCAN (no args, or "scan")
**Trigger**: `/glmfix` or `/glmfix scan`
**Action**: Scan all sessions for corruption, present results.

```bash
python3 "$GLMFIX_SCRIPT" scan --verbose
```

Present results as a table:

```
| # | Session ID | Project | Bad Blocks | Messages | Topic | Fix Command |
|---|------------|---------|------------|----------|-------|-------------|
```

If corrupted sessions are found, ask the User if they want to fix a specific one or fix all.

### Mode 2: FIX by SESSION_ID (partial or full UUID)
**Trigger**: `/glmfix b85fc237` or `/glmfix fix b85fc237-332b-446a-942e-4cbadea72c2b`
**Action**: Fix the specified session.

If the argument looks like a UUID (or partial UUID — 8+ hex characters), treat it as a session ID:

```bash
python3 "$GLMFIX_SCRIPT" fix SESSION_ID
```

Report:
- Session identified and pre-analysis
- Backup created
- Blocks removed count
- Lines removed count
- Post-repair validation result
- Resume command: `cd {project_dir} && claude --resume {session_id}`

### Mode 3: FIX ALL
**Trigger**: `/glmfix fix-all`
**Action**: Repair all corrupted sessions.

```bash
python3 "$GLMFIX_SCRIPT" fix-all
```

Report per-session results and summary.

### Mode 4: FIND AND FIX (search term)
**Trigger**: `/glmfix search TERM` or `/glmfix find TERM`
**Action**: Search for a session by content, then offer to fix if corrupted.

1. Use the session registry or search JSONL files for the term:
```bash
python3 ~/.claude/scripts/session-search.py "TERM" 2>/dev/null || grep -rl "TERM" ~/.claude/projects/*/*.jsonl | head -10
```

2. For each match, run the analyzer to check for corruption
3. Present matches with corruption status
4. Offer to fix any that are corrupted

## EXECUTION PROTOCOL

1. **ALWAYS** announce what you're about to do before running commands
2. **ALWAYS** confirm the backup was created before declaring success
3. **ALWAYS** show the resume command after a successful fix
4. If the glmfix.py script is not found, offer to create it from the repo

## OUTPUT FORMAT

### Scan Results
```
SCANNING for cross-model thinking block corruption...

| # | ID       | Project    | Bad  | Good | Msgs | Topic                    |
|---|----------|------------|------|------|------|--------------------------|
| 1 | b85fc237 | tasks      |   85 |    5 |  233 | Master Control task HUD  |

Found N corrupted sessions with M total unsigned thinking blocks.
```

### Fix Results
```
REPAIRING session b85fc237...

  Pre-analysis:  85 unsigned thinking blocks, 5 signed (preserved)
  Backup:        b85fc237...c2b.jsonl.backup.20260215_183401
  Blocks removed: 85
  Lines removed:  85 (empty after stripping)
  Validation:    CLEAN — 0 unsigned blocks remaining

  Resume: cd ~/Desktop/Projects/tasks && claude --resume b85fc237-332b-446a-942e-4cbadea72c2b

REPAIR COMPLETE.
```

## ARGUMENTS

$ARGUMENTS
