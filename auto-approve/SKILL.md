---
name: auto-approve
description: Configure Claude Code to auto-approve safe operations without prompting. Adds permissions.allow patterns to settings.json so routine tasks (file reads/writes/edits, searches, build commands, read-only git) run without confirmation. Risky operations (git reset --hard, git push --force, rm -rf, DROP TABLE, sudo) still prompt. Use when Claude is asking permission too often and you want to reduce friction for safe day-to-day work. Triggers on "auto approve", "stop asking me", "approve everything", "fewer prompts", "permission mode", or "configure permissions".
---

# Auto-Approve Permissions

Adds broad `permissions.allow` patterns to your Claude Code `settings.json` so safe operations run silently. Risky destructive operations are left out — Claude still asks for those.

## What Gets Auto-Approved

| Category | Examples |
|----------|---------|
| File tools | Read, Write, Edit, Glob, Grep (all paths) |
| Read-only git | status, diff, log, show, branch, fetch, stash list |
| Safe git writes | add, commit, checkout, switch, restore, stash save/pop/apply |
| Build/test | go, npm, yarn, pnpm, bun, make, python3, pip |
| Shell utilities | ls, cat, grep, find, echo, mkdir, touch, head, tail, wc, sort, awk, sed, jq, curl, which, pwd |

## What Still Prompts

- `git push` (pushes to remote — always good to confirm)
- `git reset --hard`, `git clean -f`, `git rebase`
- `rm` (any form, especially `rm -rf`)
- `sudo`
- SQL `DROP`, `TRUNCATE`, `DELETE FROM`
- `git push --force` / `git push -f`

## How to Apply

Run the setup script — it reads your existing `settings.json` and merges in the allow patterns without touching anything else:

```bash
python3 ~/.claude/skills/auto-approve/scripts/apply_permissions.py
```

To preview changes without writing:

```bash
python3 ~/.claude/skills/auto-approve/scripts/apply_permissions.py --dry-run
```

To target a project-level settings file instead of global:

```bash
python3 ~/.claude/skills/auto-approve/scripts/apply_permissions.py --local
```

To undo (removes only the patterns this skill added):

```bash
python3 ~/.claude/skills/auto-approve/scripts/apply_permissions.py --remove
```

After applying, restart Claude Code for the changes to take effect.

## Customizing

The allow/deny lists are defined at the top of `scripts/apply_permissions.py`. Edit `ALLOW_PATTERNS` to add or remove patterns. Use `DENY_PATTERNS` for operations that should be blocked entirely (not just prompted).

Pattern format: `ToolName(glob)` — e.g., `Bash(go test*)`, `Read(*)`, `Bash(docker *)`.
