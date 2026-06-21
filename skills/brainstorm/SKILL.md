---
name: brainstorm
description: "Planning skill. Interviews the user about a plan or design until goals, constraints, and decisions are clear. Strict trigger: only invoke when the user explicitly says `/brainstorm` or `brainstorm` verbatim."
disable-model-invocation: true
---

Use this skill during the Planning phase.

Interview the user about the plan until you reach shared understanding. Walk through the decision tree one branch at a time, resolving dependencies between decisions before moving on.

Rules:

- Ask one question at a time and wait for the answer.
- For each question, provide multiple-choice answers plus an option for the user to write their own.
- Mark your top pick and give a short justification.
- If the question can be answered by reading code, docs, research artifacts, or the working tree, inspect those first.
- Ground questions in evidence by referencing relevant files, lines, docs, or prior artifacts.
- Do not implement anything during brainstorming unless the user explicitly changes the task.

Expected output is a settled implementation approach that can be curated into `PLAN.md`.
