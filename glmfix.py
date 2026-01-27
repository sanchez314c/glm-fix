#!/usr/bin/env python3
"""
glmfix — Repair Claude Code sessions corrupted by cross-model thinking block signatures.

Scans, detects, and surgically removes unsigned thinking blocks from Claude Code
JSONL session files, allowing sessions to be resumed under models that validate
thinking block signatures (e.g., Opus).

Usage:
    python3 glmfix.py scan [--verbose]
    python3 glmfix.py fix SESSION_ID
    python3 glmfix.py fix-all [--dry-run]
"""

import json
import os
import sys
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"


def find_session_files() -> List[str]:
    """Find all JSONL session files across all Claude projects."""
    pattern = str(PROJECTS_DIR / "*" / "*.jsonl")
    return sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)


def analyze_session(filepath: str) -> Dict[str, Any]:
    """Analyze a session file for unsigned thinking blocks.

    Returns a dict with:
        - filepath: path to the file
        - session_id: UUID from filename
        - project: project directory name
        - total_lines: number of lines in the file
        - total_messages: number of messages parsed
        - good_thinking: count of signed thinking blocks
        - bad_thinking: count of unsigned thinking blocks
        - bad_line_numbers: list of 0-indexed line positions with bad blocks
        - first_user_msg: first user message text (truncated to 150 chars)
        - last_modified: file modification time as datetime
        - file_size: file size in bytes
    """
    session_id = Path(filepath).stem
    project_dir = Path(filepath).parent.name

    # Decode project name from directory encoding (/ replaced with -)
    project_name = project_dir.replace("-", "/").lstrip("/")
    if project_name.startswith("home/"):
        parts = project_name.split("/")
        if len(parts) >= 4:
            project_name = parts[-1]
        else:
            project_name = project_dir

    result: Dict[str, Any] = {
        "filepath": filepath,
        "session_id": session_id,
        "project": project_name,
        "total_lines": 0,
        "total_messages": 0,
        "good_thinking": 0,
        "bad_thinking": 0,
        "bad_line_numbers": [],
        "first_user_msg": "",
        "last_modified": datetime.fromtimestamp(os.path.getmtime(filepath)),
        "file_size": os.path.getsize(filepath),
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f):
                result["total_lines"] += 1
                line = raw_line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = data.get("message", {})
                if msg.get("role"):
                    result["total_messages"] += 1

                # Capture first user message
                if not result["first_user_msg"] and msg.get("role") == "user":
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        result["first_user_msg"] = content[:150]
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                result["first_user_msg"] = block.get("text", "")[:150]
                                break
                            elif isinstance(block, str):
                                result["first_user_msg"] = block[:150]
                                break

                # Check thinking blocks in content array
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "thinking":
                            sig = block.get("signature", "")
                            if sig:
                                result["good_thinking"] += 1
                            else:
                                result["bad_thinking"] += 1
                                result["bad_line_numbers"].append(line_num)

    except Exception as e:
        print(f"  Error reading {filepath}: {e}", file=sys.stderr)

    return result


def fix_session(filepath: str, dry_run: bool = False) -> Dict[str, Any]:
    """Remove unsigned thinking blocks from a session file.

    Creates a timestamped backup before any modification. If post-repair
    validation finds remaining unsigned blocks, the backup is restored and
    the function returns success=False.

    If the write step fails (e.g., disk full), the backup is restored
    automatically to prevent the file from being left missing at its original
    path.

    Returns a dict with repair statistics.
    """
    result: Dict[str, Any] = {
        "filepath": filepath,
        "backup_path": None,
        "removed_blocks": 0,
        "removed_lines": 0,
        "original_lines": 0,
        "final_lines": 0,
        "success": False,
        "dry_run": dry_run,
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        result["original_lines"] = len(lines)

        fixed_lines = []
        removed_blocks = 0
        removed_lines = 0

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                fixed_lines.append(line)
                continue

            try:
                data = json.loads(line_stripped)
            except json.JSONDecodeError:
                # Preserve malformed lines as-is; do not discard data
                fixed_lines.append(line)
                continue

            msg = data.get("message", {})
            content = msg.get("content", [])

            if isinstance(content, list):
                new_content = []
                line_had_bad_blocks = False

                for block in content:
                    if isinstance(block, dict) and block.get("type") == "thinking":
                        sig = block.get("signature", "")
                        if not sig:
                            # Unsigned thinking block — strip it
                            removed_blocks += 1
                            line_had_bad_blocks = True
                            continue
                    new_content.append(block)

                if line_had_bad_blocks:
                    # Drop assistant lines that become fully empty after stripping.
                    # Non-assistant messages (user, tool_result) are kept even if
                    # empty — removing them could break tool-call pair continuity.
                    if len(new_content) == 0 and msg.get("role") == "assistant":
                        removed_lines += 1
                        continue

                    msg["content"] = new_content

            fixed_lines.append(json.dumps(data) + "\n")

        result["removed_blocks"] = removed_blocks
        result["removed_lines"] = removed_lines
        result["final_lines"] = len(fixed_lines)

        if dry_run:
            result["success"] = True
            return result

        if removed_blocks == 0:
            # Nothing to repair — return without touching the file
            result["success"] = True
            return result

        # Atomic backup: rename original before writing the repaired version.
        # os.rename() is atomic on the same filesystem, so there is no window
        # where both the original and backup exist as partial writes.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.backup.{timestamp}"
        os.rename(filepath, backup_path)
        result["backup_path"] = backup_path

        try:
            # Write repaired file
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(fixed_lines)
        except Exception as write_err:
            # Write failed — restore backup so the file is not left missing
            if os.path.exists(backup_path):
                os.rename(backup_path, filepath)
                result["backup_path"] = None
            print(f"  Write failed, backup restored: {write_err}", file=sys.stderr)
            result["success"] = False
            return result

        # Post-repair validation: re-scan the written file.
        # If any unsigned blocks remain, the repair logic has a bug.
        # Restore backup and report failure rather than leaving a bad file.
        validation = analyze_session(filepath)
        if validation["bad_thinking"] > 0:
            os.remove(filepath)
            os.rename(backup_path, filepath)
            result["backup_path"] = None
            result["success"] = False
            print("  VALIDATION FAILED — restored backup", file=sys.stderr)
        else:
            result["success"] = True

    except Exception as e:
        print(f"  Error fixing {filepath}: {e}", file=sys.stderr)
        result["success"] = False

    return result


def find_session_by_id(session_id_partial: str) -> List[str]:
    """Find a session file by full or partial UUID.

    Matches against the filename stem (UUID without extension). Returns all
    files whose stem equals or starts with the provided string.
    """
    files = find_session_files()
    matches = []

    for f in files:
        stem = Path(f).stem
        if stem == session_id_partial or stem.startswith(session_id_partial):
            matches.append(f)

    return matches


def cmd_scan(verbose: bool = False) -> List[Dict[str, Any]]:
    """Scan all sessions and report corrupted ones."""
    files = find_session_files()

    if not files:
        print("No session files found.")
        return []

    corrupted = []
    clean = 0
    total_bad_blocks = 0

    print(f"{'ID':8}  {'BAD':>3}  {'MSGS':>4}  PROJECT")
    print("-" * 50)

    for filepath in files:
        analysis = analyze_session(filepath)

        if analysis["bad_thinking"] > 0:
            corrupted.append(analysis)
            total_bad_blocks += analysis["bad_thinking"]

            short_id = analysis["session_id"][:8]
            print(
                f"  CORRUPTED  {short_id}  "
                f"{analysis['bad_thinking']:>3} bad blocks  "
                f"{analysis['total_messages']:>4} msgs  "
                f"{analysis['project']}"
            )

            if verbose:
                print(f"             File: {analysis['filepath']}")
                print(f"             Size: {analysis['file_size']:,} bytes")
                print(f"             Good thinking blocks: {analysis['good_thinking']}")
                print(f"             Topic: {analysis['first_user_msg'][:80]}")
                print(f"             Modified: {analysis['last_modified']}")
                print()
        else:
            clean += 1

    print()
    print(
        f"Scanned {len(files)} sessions: "
        f"{len(corrupted)} corrupted, {clean} clean, "
        f"{total_bad_blocks} total unsigned thinking blocks"
    )

    return corrupted


def cmd_fix(session_id_partial: str) -> bool:
    """Fix a specific session by full or partial UUID."""
    matches = find_session_by_id(session_id_partial)

    if not matches:
        print(f"No session found matching: {session_id_partial}")
        print("Run 'python3 glmfix.py scan' to list corrupted sessions.")
        return False

    if len(matches) > 1:
        print(f"Multiple sessions match '{session_id_partial}':")
        for m in matches:
            print(f"  {Path(m).stem}")
        print("\nProvide more characters to narrow the match.")
        return False

    filepath = matches[0]
    session_id = Path(filepath).stem
    short_id = session_id[:8]

    # Pre-check before committing to a repair
    analysis = analyze_session(filepath)
    if analysis["bad_thinking"] == 0:
        print(f"Session {short_id} is already clean. No repair needed.")
        return True

    print(f"Repairing session {short_id}...")
    print(f"  File: {filepath}")
    print(f"  Bad thinking blocks: {analysis['bad_thinking']}")
    print(f"  Good thinking blocks: {analysis['good_thinking']}")
    print(f"  Total messages: {analysis['total_messages']}")

    result = fix_session(filepath)

    if result["success"]:
        print("\n  REPAIR COMPLETE")
        print(f"  Backup: {result['backup_path']}")
        print(f"  Thinking blocks removed: {result['removed_blocks']}")
        print(f"  Empty lines removed: {result['removed_lines']}")
        print(f"  Lines: {result['original_lines']} -> {result['final_lines']}")
        return True
    else:
        print("\n  REPAIR FAILED — original file restored")
        return False


def cmd_fix_all(dry_run: bool = False) -> bool:
    """Fix all corrupted sessions."""
    print("Scanning for corrupted sessions...")
    files = find_session_files()
    corrupted_files = []

    for filepath in files:
        analysis = analyze_session(filepath)
        if analysis["bad_thinking"] > 0:
            corrupted_files.append((filepath, analysis))

    if not corrupted_files:
        print("No corrupted sessions found.")
        return True

    print(f"Found {len(corrupted_files)} corrupted sessions.\n")

    success_count = 0
    fail_count = 0

    for filepath, analysis in corrupted_files:
        short_id = analysis["session_id"][:8]
        label = "[DRY RUN] " if dry_run else ""
        print(f"{label}Fixing {short_id} ({analysis['bad_thinking']} bad blocks)...")

        result = fix_session(filepath, dry_run=dry_run)

        if result["success"]:
            print(
                f"  OK — removed {result['removed_blocks']} blocks, "
                f"{result['removed_lines']} empty lines"
            )
            success_count += 1
        else:
            print("  FAILED")
            fail_count += 1

    print(f"\nDone: {success_count} fixed, {fail_count} failed")
    return fail_count == 0


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "scan":
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        cmd_scan(verbose=verbose)

    elif command == "fix":
        if len(sys.argv) < 3:
            print("Usage: python3 glmfix.py fix SESSION_ID")
            sys.exit(1)
        session_id = sys.argv[2]
        success = cmd_fix(session_id)
        sys.exit(0 if success else 1)

    elif command == "fix-all":
        dry_run = "--dry-run" in sys.argv
        success = cmd_fix_all(dry_run=dry_run)
        sys.exit(0 if success else 1)

    else:
        # Treat an unrecognized argument as a partial session ID to fix
        success = cmd_fix(command)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
