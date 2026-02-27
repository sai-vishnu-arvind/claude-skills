#!/usr/bin/env python3
"""
Auto-Approve Permissions Configurator for Claude Code

Merges safe allow/deny patterns into ~/.claude/settings.json (or project-local
.claude/settings.json) so Claude stops prompting for routine operations.

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

# ── Customize these lists ────────────────────────────────────────────────────

ALLOW_PATTERNS = [
    # File operation tools — always safe
    "Read(*)",
    "Write(*)",
    "Edit(*)",
    "Glob(*)",
    "Grep(*)",
    "LS(*)",

    # Read-only git
    "Bash(git status*)",
    "Bash(git diff*)",
    "Bash(git log*)",
    "Bash(git show*)",
    "Bash(git branch*)",
    "Bash(git fetch*)",
    "Bash(git stash list*)",
    "Bash(git stash show*)",

    # Safe git writes (no remote mutations, no history rewrites)
    "Bash(git add*)",
    "Bash(git commit*)",
    "Bash(git checkout*)",
    "Bash(git switch*)",
    "Bash(git restore*)",
    "Bash(git stash save*)",
    "Bash(git stash pop*)",
    "Bash(git stash apply*)",
    "Bash(git stash drop*)",
    "Bash(git tag*)",

    # Go toolchain
    "Bash(go build*)",
    "Bash(go test*)",
    "Bash(go run*)",
    "Bash(go mod*)",
    "Bash(go generate*)",
    "Bash(go vet*)",
    "Bash(go lint*)",
    "Bash(go fmt*)",
    "Bash(go install*)",
    "Bash(go clean*)",
    "Bash(golangci-lint*)",

    # Node/JS toolchains
    "Bash(npm *)",
    "Bash(yarn *)",
    "Bash(pnpm *)",
    "Bash(bun *)",
    "Bash(node *)",
    "Bash(npx *)",

    # Python
    "Bash(python *)",
    "Bash(python3 *)",
    "Bash(pip *)",
    "Bash(pip3 *)",
    "Bash(poetry *)",
    "Bash(uv *)",

    # Build tools
    "Bash(make *)",
    "Bash(cargo *)",

    # Common shell utilities (safe reads/inspection)
    "Bash(ls*)",
    "Bash(cat *)",
    "Bash(head *)",
    "Bash(tail *)",
    "Bash(grep *)",
    "Bash(rg *)",
    "Bash(find *)",
    "Bash(echo *)",
    "Bash(printf *)",
    "Bash(mkdir *)",
    "Bash(touch *)",
    "Bash(cp *)",
    "Bash(mv *)",
    "Bash(wc *)",
    "Bash(sort *)",
    "Bash(uniq *)",
    "Bash(awk *)",
    "Bash(sed *)",
    "Bash(jq *)",
    "Bash(curl *)",
    "Bash(which *)",
    "Bash(type *)",
    "Bash(pwd*)",
    "Bash(env*)",
    "Bash(export *)",
    "Bash(source *)",
    "Bash(chmod *)",
    "Bash(test *)",
    "Bash(true*)",
    "Bash(false*)",
    "Bash(date*)",
    "Bash(whoami*)",
    "Bash(id *)",
]

# Patterns to BLOCK entirely (Claude refuses, not just prompts).
# Leave empty to let dangerous commands still prompt rather than block.
DENY_PATTERNS: list[str] = []

# Marker used to track which patterns we added (for --remove)
MARKER = "# auto-approve-skill"

# ─────────────────────────────────────────────────────────────────────────────


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
    """Merge allow/deny patterns into settings. Returns (updated, added_allow, added_deny)."""
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
    """Remove only the patterns this script manages."""
    perms = settings.get("permissions", {})
    before_allow = list(perms.get("allow", []))
    before_deny = list(perms.get("deny", []))

    perms["allow"] = [p for p in before_allow if p not in ALLOW_PATTERNS]
    perms["deny"] = [p for p in before_deny if p not in DENY_PATTERNS]

    removed_allow = len(before_allow) - len(perms["allow"])
    removed_deny = len(before_deny) - len(perms["deny"])

    # Clean up empty permissions key
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
        print(f"Removing {removed_allow} allow and {removed_deny} deny pattern(s) from {settings_path}")
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
        print(f"  Adding {added_deny} deny pattern(s)")
    if added_allow == 0 and added_deny == 0:
        print("  All patterns already present — nothing to do.")
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
        print("  git push, git reset, git clean, git rebase")
        print("  rm (all variants), sudo, DROP/TRUNCATE, git push --force")


if __name__ == "__main__":
    main()
