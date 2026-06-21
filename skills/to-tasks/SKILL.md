---
name: to-tasks
description: "Converts `PLAN.md` and optional `RESEARCH.md` into a loop-ready `TASKS.md`. Strict trigger: only invoke when the user explicitly says `/to-tasks` or `to-tasks` verbatim."
disable-model-invocation: true
---

# TO-TASKS

Turn `PLAN.md` and optional `RESEARCH.md` into `TASKS.md` for one-task-per-session implementation.

Do not implement anything in this phase. Do not write PRD-style narrative. Stay agent-agnostic: refer to "the coding agent" or "the autonomous loop", not a specific assistant.

## Process

1. Locate inputs: `PLAN.md` is required; `RESEARCH.md` is optional.
2. Read the inputs end to end.
3. Ask only critical clarifying questions if real ambiguity remains.
4. Discover project commands and conventions.
5. Write `TASKS.md` to the project root unless the user specifies another path.

## Locate inputs

Look for `PLAN.md` and `RESEARCH.md` in the project root or the user-specified location.

If `PLAN.md` is missing, stop and ask the user to create it. If `TASKS.md` already exists, follow the Existing `TASKS.md` section below. Never overwrite silently.

## Minimal clarification

Ask questions only if one of these is unclear:

- Objective: what problem this solves.
- Work type: feature, refactor, research, migration, documentation, etc.
- Constraints: time, compute, scope, compatibility.
- Verification: how done is checked.

Use one round of questions at most. If everything is clear, proceed.

## Discover commands and conventions

Determine lint, type-check, test, build, and run commands with this priority:

1. `AGENTS.md` in the project root.
2. Tool-specific adapter files such as `CLAUDE.md` if present.
3. Project config files:
   - `pyproject.toml`
   - `package.json`
   - `Makefile`
   - `Cargo.toml`, `go.mod`, or other language-specific configs
   - `.github/workflows/*.yml`
   - `README.md`
4. Ask the user if commands cannot be determined.

If a command cannot be determined, leave a placeholder: `# TODO: determine <kind> command`.

## Build the task list

### Categories

Pick one category per task:

- `setup`
- `research`
- `feature`
- `refactor`
- `testing`
- `docs`
- `migration`
- `integration`

If none fits cleanly, pick the closest and note the nuance in the description.

### Task sovereignty

Each task runs in a fresh session that has only:

- `AGENTS.md` and any tool-specific adapter file
- `TASKS.md`
- `ACTIVITY.md`, `PATTERNS.md`, `PROMPT.md`
- Git history and the current codebase

The agent has no memory of prior sessions. Therefore:

- Never write "use the function from T-2". Write "use `load_dataset()` from `src/data.py`".
- Never depend on hidden implementation choices from earlier tasks.
- Describe schemas, APIs, files, and expected behavior explicitly.
- Include file paths whenever possible.
- Make each task independently checkable.

### Task size

Good tasks usually cover one concrete change: one config parameter, one function, tests for one module, logging in one stage, or a documentation update.

Split a task if it:

- touches more than 3-4 files,
- combines unrelated work,
- requires broad exploration before any change can start,
- cannot be described in 2-3 factual sentences,
- needs a separate verification strategy.

### Verification

Each task must end with a concrete verification step mapped to a command in Tech Guidelines.

Examples:

- `Type checking passes with <command>`
- `Tests pass with <command>`
- `Documentation renders or links are checked with <command>`
- `Results are logged and reproducible with <command>`

Avoid vague checks such as "works correctly" or "handles edge cases".

### Ordering

Earlier tasks must not require later tasks. Use this rough order:

1. Additional research if needed.
2. Configuration and schema changes.
3. Core logic and data processing.
4. Higher-level functions built on core logic.
5. Tests and validation.
6. Documentation and integration where useful.

## Write `TASKS.md`

Use this structure. Include optional sections only if the input artifacts support them.

```markdown
# TASKS

## Overview
[1-3 sentence summary distilled from PLAN.md / RESEARCH.md.]

## Goals
- [Concrete, testable goal.]

## Non-Goals
- [Scope guardrail.]

## Success Metrics
- [Measurable outcome.]

## Tasks

### T-1: <short title>
- **Category:** <category>
- **Passes:** false
- **Description:** <plain factual sentence>
- **Steps:**
  - <verifiable step with file paths where relevant>
  - <verification step>

## Tech Guidelines

**Tech stack:** <language + version, frameworks, package manager>
**Conventions:** <project-specific rules from AGENTS.md / README / inferred>
**File layout:** <source dir, test dir, config location>

**Linting:** `<command>`
**Type checking:** `<command>`
**Tests:** `<command>`
**Build:** `<command>`
**Run:** `<command>`
```

Task headings must be `### T-N: Title` with sequential IDs starting at `T-1`. `Passes` is always `false` when generated; the implementation loop flips it to `true` after successful verification.

## Existing `TASKS.md`

If `TASKS.md` exists, read it first and ask whether to:

- Update: preserve `Passes: true` tasks, edit incomplete tasks, and add a dated update note.
- Extend: append new tasks with fresh sequential IDs.
- Replace: overwrite after explicit confirmation.

Always preserve completed-task state unless the user explicitly says to replace it.

## Writing style

The readers are a fresh coding-agent session and a human reviewer.

- Be explicit and concrete.
- Number tasks.
- Reference files and functions by path.
- Avoid unexplained jargon.
- Assume zero prior conversation context.
