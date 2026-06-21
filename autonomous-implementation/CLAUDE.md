# Claude Code Adapter

Read and follow `AGENTS.md`. It is the canonical instruction file for this autonomous implementation kit.

Claude-specific notes:

- `loop.sh` invokes the `claude` CLI for each iteration.
- `.claude/settings.json` is an example sandbox setting file for Claude Code.
- Keep local overrides in `.claude/settings.local.json` and do not commit them.
- The loop uses `--dangerously-skip-permissions`; run it only in a trusted, isolated working tree and review commits before merging.
