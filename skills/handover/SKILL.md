---
name: handover
description: "Compacts the current conversation into a handover document for a fresh coding-agent session. Strict trigger: only invoke when the user explicitly says `/handover` or `handover` verbatim."
disable-model-invocation: true
---

Write a handover document so a fresh coding-agent session can continue the work.

Save it to `HANDOVER.md` unless the user specifies another path. If the file already exists, do not overwrite it without confirmation.

Include:

- Current goal and status.
- Decisions already made.
- Open questions and blockers.
- Files changed or inspected.
- Relevant commands run and their outcomes.
- Constraints the next session must preserve.
- Concrete next step.

Reference existing artifacts by path, such as `RESEARCH.md`, `PLAN.md`, `TASKS.md`, `ACTIVITY.md`, and `PATTERNS.md`. Do not duplicate their full content.
