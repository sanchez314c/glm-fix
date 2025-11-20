# Quick Start

Clone to running in under a minute.

## Prerequisites

- Python 3.8 or newer
- Claude Code installed with at least one session on disk

## Steps

**1. Clone the repo**

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix
```

**2. Scan for corrupted sessions**

```bash
python3 glmfix.py scan
```

Expected output if corruption exists:
```
  CORRUPTED  b85fc237    85 bad blocks   233 msgs  tasks
  CORRUPTED  d3a9f112     3 bad blocks    47 msgs  portfolio

Scanned 42 sessions: 2 corrupted, 40 clean, 88 total unsigned thinking blocks
```

**3. Fix all corrupted sessions at once**

```bash
python3 glmfix.py fix-all
```

Or fix a specific one:

```bash
python3 glmfix.py fix b85fc237
```

**4. Resume your session**

```bash
claude --resume <full-session-uuid>
```

---

## Optional: Slash Command

Copy the skill file to activate `/glmfix` inside Claude Code sessions:

```bash
mkdir -p ~/.claude/commands
cp commands/glmfix.md ~/.claude/commands/glmfix.md
```

Then from any Claude Code session:

```
/glmfix scan
/glmfix fix-all
/glmfix b85fc237
```

---

That's it. No configuration, no environment variables, no services.
