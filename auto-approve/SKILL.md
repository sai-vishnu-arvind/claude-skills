---
name: auto-approve
description: Configure Claude Code to auto-approve safe operations without prompting. Adds permissions.allow patterns to settings.json so routine tasks (file reads/writes/edits, searches, build commands, read-only git) run without confirmation. Risky operations (git reset --hard, git push --force, rm -rf, DROP TABLE, sudo) still prompt. Use when Claude is asking permission too often and you want to reduce friction for safe day-to-day work. Triggers on "auto approve", "stop asking me", "approve everything", "fewer prompts", "permission mode", or "configure permissions".
---

# Auto-Approve Permissions

Adds a broad `Bash(*)` allow pattern to your Claude Code `settings.json` so all shell commands run silently, including compound commands (pipes, semicolons, redirects). Risky destructive operations are explicitly denied — Claude still asks for those.

## What Gets Auto-Approved

| Category | Pattern |
|----------|---------|
| File tools | Read(*), Write(*), Edit(*), Glob(*), Grep(*), LS(*) |
| All shell commands | Bash(*) — including pipes, chains, compound commands |

## What Still Prompts (deny list)

- `git push` — pushes to remote
- `git push --force` — force push
- `git reset --hard` — destructive local reset
- `git clean -f`, `git clean -fd` — deletes untracked files
- `git rebase` — history rewrite
- `rm -rf` — recursive delete
- `sudo rm`, `sudo *` — any sudo command
- SQL `DROP *`, `TRUNCATE *`

## How to Apply

Run the setup script — it reads your existing `settings.json` and merges in the allow/deny patterns without touching anything else:

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

## Why Bash(*) instead of individual patterns?

Individual patterns like `Bash(find *)` only match commands that start with that exact word. Compound commands like `find ... | head -5; ls ...` don't match any single pattern and still prompt. Using `Bash(*)` + a deny list for dangerous commands is simpler and covers all cases.

## Customizing

The allow/deny lists are defined at the top of `scripts/apply_permissions.py`. Edit `DENY_PATTERNS` to add more operations that should be blocked. Pattern format: `ToolName(glob)` — e.g., `Bash(docker rm*)`.
