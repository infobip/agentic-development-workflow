# Sandboxing Autonomous Implementation

The autonomous implementation kit starts fresh coding-agent sessions that can edit files and commit changes. Run it only when the task list is clear and the working tree is isolated.

## Baseline safety

Use all of these by default:

- Run on a dedicated feature branch.
- Start from a clean working tree.
- Keep secrets out of the repository and out of readable files.
- Review generated commits before merging.
- Keep `PATTERNS.md` short and update it when sessions repeat mistakes.
- Stop the loop when task failures indicate unclear requirements rather than implementation errors.

## Isolation options

### 1. Permission and tool scoping

Use agent settings to deny secret reads, remote pushes, destructive commands, and file access outside the project. This is useful but not a hard security boundary.

Recommended for low-risk documentation or small code tasks.

### 2. Git branch or worktree

Run the loop on a dedicated branch or in a separate git worktree:

```bash
git worktree add ../agentic-demo-worktree -b demo-loop
cd ../agentic-demo-worktree
```

Review commits before merging or delete the worktree if the run goes poorly.

Recommended default for normal project work.

### 3. Container or dev container

Run the agent inside a container with only the project mounted read-write. Keep credentials and host directories out of the container unless explicitly needed.

Recommended for tasks that run tests, install packages, or execute generated code.

### 4. Disposable VM or cloud sandbox

Run the agent in a disposable VM or cloud environment and discard the machine after the run.

Recommended for high-risk code execution, unknown dependencies, or untrusted repositories.

## Review cadence

Choose review frequency by risk:

- Per task: safest, slowest.
- Batch review: useful for low-risk task lists.
- Checkpoint review: review after a feature slice or failed task.

Never merge autonomous output without human review.

## Failure handling

If the loop repeatedly fails:

1. Stop running new iterations.
2. Read `ACTIVITY.md` and inspect the last commits.
3. Fix the task definition in `TASKS.md` or return to `PLAN.md`.
4. Add a concise correction to `PATTERNS.md` only if the same mistake is likely to recur.
