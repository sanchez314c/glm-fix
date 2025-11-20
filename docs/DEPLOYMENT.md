# Deployment

glmfix is a local-only CLI tool. There is no server to deploy, no container to ship, and no cloud infrastructure. "Deployment" means getting the script and slash command onto a user's machine.

## Distribution Methods

### Method 1: Git Clone (primary)

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix
python3 glmfix.py scan
```

That's the full deployment. No post-clone steps are required.

### Method 2: Single-File Copy

Since `glmfix.py` is self-contained, it can be distributed as a raw file download or copy-paste. The GitHub raw URL:

```
https://raw.githubusercontent.com/sanchez314c/glmfix/main/glmfix.py
```

```bash
curl -o glmfix.py https://raw.githubusercontent.com/sanchez314c/glmfix/main/glmfix.py
python3 glmfix.py scan
```

### Method 3: Slash Command Deployment

To activate the `/glmfix` command inside Claude Code sessions:

```bash
mkdir -p ~/.claude/commands
cp commands/glmfix.md ~/.claude/commands/glmfix.md
```

The `commands/glmfix.md` file contains a hardcoded path to `glmfix.py`. If you cloned the repo somewhere other than `~/Desktop/Projects/00_github-INPROCESS/glmfix/`, update that path in the skill file before copying.

## Release Process

Releases are tagged on GitHub. There is no CI/CD pipeline, no automated release workflow, and no PyPI package.

**To cut a new release:**

1. Update `CHANGELOG.md` with the new version entry and date.
2. Update `VERSION_MAP.md` with the new version and any file-level changes.
3. Commit: `git commit -m "chore: release vX.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push origin main --tags`
6. Create a GitHub release from the tag with the changelog entry as the body.

## Version Numbering

glmfix follows semantic versioning (`MAJOR.MINOR.PATCH`):

- **MAJOR** — breaking change to CLI interface or repair behavior
- **MINOR** — new repair strategy, new command, or new feature
- **PATCH** — bug fixes, documentation, non-functional changes

Current version: **1.0.3**

## No Upgrade Path Needed

Since there is no installation (just a cloned repo or a single file), users update by pulling or re-downloading:

```bash
cd glmfix
git pull
```

Backups created by older versions are always safe — the backup format (`filename.backup.YYYYMMDD_HHMMSS`) is stable and never changes.
