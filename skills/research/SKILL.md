---
name: research
description: "Research skill. Explores a question, hypothesis, or problem statement through codebase inspection, documentation review, literature review, and user interviews. Strict trigger: only invoke when the user explicitly says `/research` or `research` verbatim."
disable-model-invocation: true
---

Use this skill during the Research phase.

Explore the research question from all relevant angles: code, documentation, literature, existing artifacts, and targeted user questions.

Process:

1. Clarify the research question.
2. Inspect relevant repository files and documentation.
3. Use literature search when it is relevant and available. Confirm with the user before using external paper-search tools.
4. Ask targeted questions to clarify assumptions and validate findings.
5. Synthesize only validated findings into `RESEARCH.md`.

Rules:

- Ask one question at a time and wait for the answer.
- For each question, provide multiple-choice answers plus an option for the user to write their own.
- Mark your top pick and give a short justification.
- Reference relevant files, documentation, papers, or prior artifacts.
- Keep research separate from planning. Do not converge on an implementation plan unless the user explicitly moves to Planning.
- Do not edit code during research unless the user explicitly asks.
- If `RESEARCH.md` already exists, read it before writing so you can extend it rather than duplicate it.
- Confirm the structure, content, and path of the report before writing.

Expected output is `RESEARCH.md` with validated findings, open questions, and suggested next steps.
