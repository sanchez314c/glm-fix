# Development Workflow

## Branching

glmfix is a small, single-file project. The branching strategy is simple:

- `main` — stable, always works against real session files
- `fix/<description>` — bug fixes
- `feat/<description>` — new features or repair strategies

Direct commits to `main` are acceptable for documentation and small patches. For anything touching `glmfix.py`, use a feature branch.

## Making a Change

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix

# Create a branch
git checkout -b fix/empty-content-edge-case

# Edit glmfix.py
# ...

# Test manually against real sessions
python3 glmfix.py scan --verbose
python3 glmfix.py fix-all --dry-run

# Fix one specific session to validate the repair
python3 glmfix.py fix <partial-uuid>

# Verify the repaired session actually works
claude --resume <session-id>

# Update changelog
# Edit CHANGELOG.md with the new entry

# Commit
git add glmfix.py CHANGELOG.md
git commit -m "fix: handle empty content array in non-assistant messages"

# Push and open PR
git push origin fix/empty-content-edge-case
```

## Commit Message Format

Follow conventional commits:

```
<type>: <short description>
```

Types:
- `fix` — bug fix in repair logic
- `feat` — new command, new repair strategy
- `refactor` — code change without behavior change
- `docs` — documentation only
- `chore` — release, version bump, tooling

Examples:
```
fix: restore backup correctly when target path is on different mount
feat: add search mode to find sessions by content
docs: expand troubleshooting section
chore: release v1.1.0
```

## Testing Protocol

There's no automated test suite. All testing is manual against real Claude Code session files.

**Before opening a PR:**

1. `python3 glmfix.py scan --verbose` — confirm scan output looks correct
2. `python3 glmfix.py fix-all --dry-run` — confirm repair logic runs without errors
3. If the change touches repair logic: pick one corrupted session and run the full fix, then resume it in Claude Code to confirm the session works

**If you don't have any corrupted sessions:**

Create a synthetic one:

```python
import json, tempfile, os

line = json.dumps({
    "message": {
        "role": "assistant",
        "content": [
            {"type": "thinking", "thinking": "some reasoning", "signature": ""},
            {"type": "text", "text": "Here is the answer."}
        ]
    }
}) + "\n"

with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
    f.write(line)
    print(f.name)
```

Then run `python3 glmfix.py fix <path-stem>` against that file.

## Pull Request Process

1. Branch from `main`
2. Make changes
3. Test manually (see above)
4. Update `CHANGELOG.md`
5. Open a PR with the template filled out
6. PRs are reviewed by [@sanchez314c](https://github.com/sanchez314c)

The PR checklist in `.github/PULL_REQUEST_TEMPLATE.md` covers the key requirements: no external deps, backup safety, 3.8 compat, CHANGELOG updated.

## CI/CD

There is no CI/CD pipeline currently. Adding GitHub Actions to run a basic syntax check (`python3 -m py_compile glmfix.py`) and lint (`flake8`) is on the roadmap. See `docs/TODO.md`.
