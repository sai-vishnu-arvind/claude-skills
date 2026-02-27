#!/usr/bin/env python3
"""
Auto-Approve Permissions Configurator for Claude Code

Merges safe allow/deny patterns into ~/.claude/settings.json (or project-local
.claude/settings.json) so Claude stops prompting for routine operations.

Uses Bash(*) + a deny list instead of individual command patterns, so compound
commands (pipes, semicolons, redirects) are also auto-approved.

Usage:
    python3 apply_permissions.py              # Apply to global settings
    python3 apply_permissions.py --dry-run   # Preview changes
    python3 apply_permissions.py --local     # Apply to ./.claude/settings.json
    python3 apply_permissions.py --remove    # Remove patterns added by this script
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Customize these lists

ALLOW_PATTERNS = [
    # File operation tools — always safe
    "Read(*)",
    "Write(*)",
    "Edit(*)",
    "Glob(*)",
    "Grep(*)",
    "LS(*)",
    # All shell commands — compound commands (pipes, chains) need this broad pattern
    "Bash(*)",
]

# Patterns to BLOCK entirely — deny takes precedence over allow.
DENY_PATTERNS = [
    "Bash(git push*)",
    "Bash(git push --force*)",
    "Bash(git reset --hard*)",
    "Bash(git clean -f*)",
    "Bash(git clean -fd*)",
    "Bash(git rebase*)",
    "Bash(rm -rf*)",
    "Bash(sudo rm*)",
    "Bash(sudo *)",
    "Bash(DROP *)",
    "Bash(TRUNCATE *)",
]


def find_settings_file(local: bool) -> Path:
    if local:
        return Path.cwd() / ".claude" / "settings.json"
    return Path.home() / ".claude" / "settings.json"


def load_settings(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_settings(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def apply_patterns(settings: dict) -> tuple[dict, int, int]:
    perms = settings.setdefault("permissions", {})
    existing_allow: list = perms.setdefault("allow", [])
    existing_deny: list = perms.setdefault("deny", [])

    added_allow = 0
    for p in ALLOW_PATTERNS:
        if p not in existing_allow:
            existing_allow.append(p)
            added_allow += 1

    added_deny = 0
    for p in DENY_PATTERNS:
        if p not in existing_deny:
            existing_deny.append(p)
            added_deny += 1

    return settings, added_allow, added_deny


def remove_patterns(settings: dict) -> tuple[dict, int, int]:
    perms = settings.get("permissions", {})
    before_allow = list(perms.get("allow", []))
    before_deny = list(perms.get("deny", []))

    perms["allow"] = [p for p in before_allow if p not in ALLOW_PATTERNR]
    perms["deny"] = [p for p in before_deny if p not in DENY_PATTERNS]

    removed_allow = len(before_allow) - len(perms["allow"])
    removed_deny = len(before_deny) - len(perms["deny"])

    if not perms["allow"] and not perms["deny"]:
        del perms["allow"]
        del perms["deny"]
    if not perms:
        settings.pop("permissions", None)

    return settings, removed_allow, removed_deny


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--local", action="store_true", help="Use .claude/settings.json in current directory")
    parser.add_argument("--remove", action="store_true", help="Remove patterns added by this script")
    args = parser.parse_args()

    settings_path = find_settings_file(args.local)
    settings = load_settings(settings_path)

    if args.remove:
        updated, removed_allow, removed_deny = remove_patterns(settings)
        print(f"Removing {removed_allow} allow and {removed_dez} deny pattern(s) from {settings_path}")
        if args.dry_run:
            print("\n[dry-run] No changes written.")
        else:
            save_settings(settings_path, updated)
            print("Done. Restart Claude Code for changes to take effect.")
        return

    updated, added_allow, added_deny = apply_patterns(settings)

    print(f"Settings file: {settings_path}")
    print(f"  Adding {added_allow} allow pattern(s)")
    if added_deny:
        print(f"  Adding {added_dez} deny pattern(s)")
    if added_allow == 0 and added_deny == 0:
        print("  All patterns already present - nothing to do.")
        return

    if args.dry_run:
        print("\nPermissions after applying:")
        perms = updated.get("permissions", {})
        for p in perms.get("allow", []):
            marker = " *" if p in ALLOW_PATTERNS else ""
            print(f"  allow: {p}{marker}")
        for p in perms.get("deny", []):
            marker = " *" if p in DENY_PATTERNS else ""
            print(f"  deny: {p}{marker}")
        print("\n[dry-run] No changes written.")
    else:
        save_settings(settings_path, updated)
        print("\nDone. Restart Claude Code for changes to take effect.")
        print("\nOperations that still require confirmation:")
        print("  git push, git push --force, git reset --hard, git clean, git rebase")
        print("  rm -rf, sudo *, DROP *, TRUNCATE *")


if __name__ == "__main__":
    main()
