# Autonomous implementation kit

This directory contains an optional agent-agnostic driver for the Implementation phase. It starts one fresh coding-agent session per iteration and relies on files plus git history for continuity.

Use it only after Research, Planning, and Task Definition are complete:

```text
RESEARCH.md -> PLAN.md -> TASKS.md -> ACTIVITY.md + commits
```

## Files

- `AGENTS.md` — canonical instructions for each loop session.
- `CLAUDE.md` — thin Claude Code adapter notes.
- `PROMPT.md` — prompt passed to each fresh agent session.
- `TASKS.md` — task registry; the loop looks for `**Passes:** false`.
- `ACTIVITY.md` — append-only session log.
- `PATTERNS.md` — concise human corrections for recurring mistakes.
- `SANDBOX.md` — isolation and review guidance.
- `loop.sh` — single generic loop driver.

## Agent command contract

`loop.sh` does not assume a specific coding agent. Configure one command that starts a fresh non-interactive agent session:

```bash
export LOOP_AGENT_COMMAND='your-agent-cli --non-interactive < "$LOOP_PROMPT_FILE"'
./loop.sh 3
```

The command must:

1. Run unattended from this directory.
2. Read `PROMPT.md` directly or through `$LOOP_PROMPT_FILE`.
3. Complete exactly one task from `TASKS.md`.
4. Update `ACTIVITY.md` and mark the task passing only after verification.
5. Commit changes with a message that starts with `loop:`.
6. Exit without starting another task.

If all tasks are complete, the agent should print exactly:

```text
<all-tasks-done/>
```

## Claude Code adapter example

```bash
export LOOP_AGENT_COMMAND='claude -p "$(cat "$LOOP_PROMPT_FILE")" --output-format json --dangerously-skip-permissions'
./loop.sh 3
```

The `--dangerously-skip-permissions` flag is Claude-specific. Use it only in a trusted, isolated working tree and review generated commits before merging.

## Safety baseline

- Run on a dedicated branch or worktree.
- Start from a clean working tree.
- Keep secrets and private data outside the repository.
- Review `SANDBOX.md` before running.
- Stop the loop when failures indicate unclear tasks; return to `TASKS.md` or `PLAN.md` instead of letting the loop improvise.
