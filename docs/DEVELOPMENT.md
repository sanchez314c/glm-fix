# Development

## Dev Environment

There's no setup. Clone the repo, open `glmfix.py`, and start editing. No virtual environments, no dependencies, no build system.

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix
```

The only requirement is Python 3.8+. The entire tool is stdlib-only, and that's a hard rule. Don't add external dependencies.

## Project Layout

```
glmfix.py              # Everything. All logic, all CLI handling.
commands/glmfix.md     # Claude Code slash command definition
```

That's the functional code. Everything else is documentation and GitHub config.

## Code Conventions

- 4-space indentation
- Docstrings on all functions
- Functions that do analysis or repair return dicts with consistent keys
- `cmd_*` functions handle CLI output (printing). Internal functions return data.
- No classes. Just functions and a `main()` entry point.
- Python 3.8 compatible. No walrus operators, no `str.removeprefix()`, no `match` statements.

## Testing

There's no automated test suite. The tool operates on real Claude Code session files, so testing means running it against your own sessions.

**Safe testing workflow:**

```bash
# See what's out there
python3 glmfix.py scan --verbose

# Preview what a full repair would do (no files modified)
python3 glmfix.py fix-all --dry-run

# Fix one specific session to verify repair logic
python3 glmfix.py fix <partial-uuid>

# Check that the backup was created
ls -la ~/.claude/projects/*/*.backup.*
```

The `--dry-run` flag is your friend. It runs the full repair pipeline but skips the file write step. Use it before every `fix-all`.

After fixing a session, verify it actually works by resuming it:

```bash
claude --resume <session-id>
```

## How to Add New Repair Strategies

Right now, glmfix only handles one type of corruption: unsigned thinking blocks. If you need to handle a new corruption type, here's the pattern:

### 1. Add detection to `analyze_session()`

The `analyze_session()` function reads every line and checks for problems. Add a new counter to the result dict and a new check in the content-walking loop.

```python
result["new_problem_count"] = 0

# Inside the content loop:
if isinstance(block, dict) and block.get("type") == "your_type":
    if some_condition:
        result["new_problem_count"] += 1
```

### 2. Add repair logic to `fix_session()`

The `fix_session()` function walks the same content arrays and builds `new_content` lists with the bad stuff filtered out. Add your filter condition alongside the existing thinking block check.

```python
if isinstance(block, dict) and block.get("type") == "your_type":
    if should_remove(block):
        removed_new_problem += 1
        continue
new_content.append(block)
```

### 3. Update validation

The post-repair validation re-runs `analyze_session()` on the fixed file. If you added a new counter in step 1, check it in the validation step inside `fix_session()`:

```python
if validation["bad_thinking"] > 0 or validation["new_problem_count"] > 0:
    # Restore backup
```

### 4. Update the scan output

Add your new problem type to the `cmd_scan()` output so users can see it.

### 5. Update the slash command

If the new repair type changes how users should invoke the tool, update `commands/glmfix.md` to match.

### 6. Update CHANGELOG.md

Document what you added and when.

## Common Gotchas

- **JSONL, not JSON.** Each line is a separate JSON object. Don't try to parse the whole file as one JSON document.
- **Content can be a string or a list.** User message content is sometimes a plain string, sometimes a list of blocks. Always check `isinstance(content, list)` before iterating.
- **Backup uses `os.rename()`, not copy.** This is atomic on the same filesystem but will fail across filesystem boundaries. Since backups go in the same directory as the original, this isn't a problem in practice.
- **Line numbers are 0-indexed** in the analysis results (`bad_line_numbers`), matching `enumerate(f)` behavior.
