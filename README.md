# claude-skills

A collection of installable skills for [Claude Code](https://claude.ai/claude-code) — modular extensions that give Claude specialized knowledge and workflows.

## What are Skills?

Skills are self-contained packages (`SKILL.md` + optional scripts/assets) that you install into Claude Code. Once installed, Claude automatically uses the right skill based on what you ask.

## Skills

### [`auto-approve`](./auto-approve/)

Configures Claude Code to auto-approve safe operations without prompting. Adds `permissions.allow` patterns to `settings.json` so routine tasks run silently, while keeping confirmation for risky operations.

**Auto-approves:** file reads/writes/edits, searches, git (non-destructive), go/npm/yarn/make, shell utilities
**Still prompts:** `git push`, `git reset --hard`, `rm`, `sudo`, `DROP TABLE`, force push

## Installing a Skill

Download the `.skill` file and install it:

```bash
# Install from this repo
curl -L https://github.com/sai-vishnu-arvind/claude-skills/raw/main/auto-approve.skill -o auto-approve.skill

# Then in Claude Code
/install-skill auto-approve.skill
```

Or install directly from source by copying the skill folder into `~/.claude/skills/`.

## Using a Skill

Once installed, just ask Claude naturally:

- *"Claude is asking permission too often, fix it"* → triggers `auto-approve`
- *"Set up auto-approve permissions"* → triggers `auto-approve`

## Building Your Own

Skills follow the [Claude Code skill format](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf):

```
my-skill/
├── SKILL.md          # Frontmatter (name, description) + instructions
└── scripts/          # Optional executable helpers
```

The `description` field in `SKILL.md` frontmatter is what Claude reads to decide when to trigger the skill — make it specific and include trigger phrases.
