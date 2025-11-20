# Installation

## Prerequisites

- **Python 3.8 or newer.** That's it. No pip packages, no virtual environments, no build tools.
- **Claude Code** installed and used at least once (so `~/.claude/projects/` exists with session files).

Check your Python version:

```bash
python3 --version
```

## Option 1: CLI Tool (standalone)

Clone the repo and run it directly. There's no install step.

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix
python3 glmfix.py scan
```

You can put it anywhere. The script finds session files by looking at `~/.claude/projects/` regardless of where glmfix itself lives.

If you want it on your PATH:

```bash
# Symlink to a directory that's already on PATH
ln -s /path/to/glmfix/glmfix.py ~/bin/glmfix
chmod +x ~/bin/glmfix
```

Then just run `glmfix scan` from anywhere.

## Option 2: Claude Code Slash Command (recommended)

This lets you type `/glmfix` inside any Claude Code session to scan and fix sessions without leaving the conversation.

Copy the slash command definition:

```bash
mkdir -p ~/.claude/commands
cp commands/glmfix.md ~/.claude/commands/glmfix.md
```

The slash command calls `glmfix.py` via Bash, so the script needs to be accessible. Update the path inside `commands/glmfix.md` if you cloned the repo somewhere other than the default location.

### Verify it works

Start a Claude Code session and type:

```
/glmfix scan
```

You should see a scan of all your sessions with a count of corrupted vs clean files.

## Both at Once

You can use both. The CLI is good for quick checks from any terminal. The slash command is good when you're already in a Claude Code session and hit the thinking block error.
