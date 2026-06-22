# Claude Code Adapter

Read and follow `AGENTS.md`. It is the canonical instruction file for this autonomous implementation kit.

Claude-specific notes:

- `loop.sh` is agent-agnostic. Configure Claude Code through `LOOP_AGENT_COMMAND`:

  ```bash
  export LOOP_AGENT_COMMAND='claude -p "$(cat "$LOOP_PROMPT_FILE")" --output-format json --dangerously-skip-permissions'
  ./loop.sh 3
  ```

- `.claude/settings.json` is an example sandbox setting file for Claude Code.
- Keep local overrides in `.claude/settings.local.json` and do not commit them.
- `--dangerously-skip-permissions` is Claude-specific; run it only in a trusted, isolated working tree and review commits before merging.
