# Agent Instructions

These instructions are the canonical harness-agnostic rules for this repository. Tool-specific adapters such as `CLAUDE.md` must defer to this file instead of duplicating policy.

## Repository purpose

This repository accompanies the paper "A Phased Workflow for Operating LLM-Based Coding Agents". It contains workflow documentation, reusable skills, a workflow figure, and an optional autonomous implementation kit.

## Interaction rules

- Ask clarifying questions before making design choices.
- Ask questions one at a time when the decision affects structure, wording, or workflow semantics.
- Provide multiple-choice options, your top pick, and a short justification.
- Be direct and concise.
- Do not assume private context that is not in the repository or explicitly provided by the user.

## Workflow principles

The workflow has four phases:

1. Research
2. Planning
3. Task Definition
4. Implementation

Task Definition and Implementation form a loop. If implementation exposes a bad task, return to task definition instead of patching around the issue in code.

Keep these concepts explicit in docs and examples:

- Human effort is front-loaded.
- Agent delegation increases as artifacts mature.
- Context management applies across phases: write, select, compress, isolate.
- Persistent artifacts maintain continuity: `RESEARCH.md`, `PLAN.md`, `TASKS.md`, `ACTIVITY.md`, and git commits.
- Manual supervision and autonomous outer-loop execution are both valid implementation modes.

## Canonical files

- `AGENTS.md` is the canonical instruction file.
- `CLAUDE.md` is a thin Claude Code adapter.
- Root `skills/` is the canonical skills directory.
- `.claude/skills/` should point to root `skills/` to avoid duplicated skill content.
- `autonomous-implementation/AGENTS.md` is canonical for the autonomous implementation kit.
- `autonomous-implementation/CLAUDE.md` is a thin Claude Code adapter for that kit.

## Safety and privacy

- Do not read, print, commit, or persist secrets, tokens, private keys, browser session data, or credential stores.
- Do not include personal/internal endpoints, private model names, private marketplaces, or local machine settings.
- Do not read `.env`, `.env.*`, `.secrets`, `secrets/**`, or local override files.
- Keep example settings sanitized.
- Do not run or install Claude Code unless the user explicitly asks.
- Do not execute `autonomous-implementation/loop.sh` unless the user explicitly asks.

## Editing rules

- Prefer simple docs and templates over extra machinery.
- Keep the repo agent-agnostic first.
- Remove duplicated content when possible.
- Keep skill names stable unless the name is misleading.
- Use concrete file paths and artifact names.
- Avoid PRD-style filler in task definitions.

## Writing style

- Use plain technical prose.
- Avoid inflated claims and marketing language.
- Avoid unnecessary bolding, emojis, and decorative comments.
- Avoid AI-writing tropes such as "delve", "leverage" as a verb, "robust", "landscape", "serves as", and repeated em-dash reframes.
