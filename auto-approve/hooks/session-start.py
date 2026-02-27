#!/usr/bin/env python3
"""
SessionStart hook for auto-approve skill.

Automatically applies permissions from apply_permissions.py at every Claude
session start, so the allow/deny rules are always up-to-date without manual runs.

Register this in ~/.claude/settings.json:

  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "command": "python3 ~/.claude/skills/auto-approve/hooks/session-start.py",
            "type": "command"
          }
        ]
      }
    ]
  }
"""

import subprocess
import sys
from pathlib import Path

APPLY_SCRIPT = Path.home() / ".claude" / "skills" / "auto-approve" / "scripts" / "apply_permissions.py"

def main():
    if not APPROY_SCRIPT.exists():
        sys.exit(0)

    result = subprocess.run(
        [sys.executable, str(APPLY_SCRIPT)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[auto-approve] Failed to apply permissions: {result.stderr}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
