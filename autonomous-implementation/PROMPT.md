# Loop iteration prompt

You are one iteration in an autonomous implementation loop. Each iteration is a fresh session with no memory of prior runs. Complete **exactly one task** from `TASKS.md`, then terminate.

## Context sources

Read these before touching code:

- `AGENTS.md` — canonical project stack, commands, conventions, and loop rules.
- `TASKS.md` — full task list.
- `ACTIVITY.md` — log entries from prior sessions: blockers, decisions, notes.
- `PATTERNS.md` — human-curated corrections. Treat as binding.
- The codebase and `git log` — all prior work is committed.

If a tool-specific adapter file exists, such as `CLAUDE.md`, read it after `AGENTS.md` and treat it as adapter-specific guidance only.

## Workflow

1. **Pick the task.** Find the first task in `TASKS.md` with a task-status line `- **Passes:** false`. That is your task. Ignore mentions of `**Passes:** false` in comments, examples, or instructions. If none exist, output exactly `<all-tasks-done/>` and stop.
2. **Plan.** Re-read the task's `Description` and `Steps`. Identify the files to change. Use subagents or isolated research sessions for parallel exploration only when available and useful.
3. **Execute.** Work through the steps. Stay strictly in scope. Do not fix unrelated issues, refactor outside the task, or start the next task.
4. **Verify.** Run the lint, type-check, test, or build commands from `AGENTS.md` that apply to this task. Fix failures within the task scope.
5. **Log.** Append an entry to `ACTIVITY.md` using the template in that file. This is required even if the task failed.
6. **Mark passing.** If every step verified, change `**Passes:** false` to `**Passes:** true` for this task in `TASKS.md`. Otherwise leave it `false`.
7. **Commit.** `git add -A && git commit -m "loop: T-N — short description"`. Commit even on failure so partial progress and the activity log are preserved.
8. **Stop.** Do not start the next task. Do not output anything after the commit. Terminate completely.

## Rules

- One task per session.
- No look-ahead work.
- Stay in scope.
- If a fix requires work outside this task, log it as a blocker and leave `Passes: false`.
- Only mark `Passes: true` if every required step is verified.
- Always update `ACTIVITY.md` and always commit, regardless of outcome.
- Trust the codebase, not memory. Verify prior outputs exist before depending on them.

## Failure protocol

If you cannot finish the task:

1. Document what went wrong under **Blockers** in `ACTIVITY.md`.
2. Note what you tried and what the next session should try under **Notes for next session**.
3. Leave `**Passes:** false`.
4. Commit the current state.
5. Stop.
