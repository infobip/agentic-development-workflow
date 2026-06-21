# Claude Code Adapter

Read and follow `AGENTS.md`. It is the canonical instruction file for this repository.

Claude-specific notes:

- Root `skills/` is canonical. `.claude/skills/` points to those skills to avoid duplicated skill content.
- `.claude/settings.json` is an example project setting file. Keep local overrides in `.claude/settings.local.json` and do not commit them.
- Do not run `autonomous-implementation/loop.sh` unless the user explicitly asks.
- Do not install or configure Claude Code unless the user explicitly asks.
