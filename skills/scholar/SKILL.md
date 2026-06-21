---
name: scholar
description: "Searches and analyzes academic papers through Semantic Scholar. Use when the user asks about papers, authors, citations, related literature, or invokes `/scholar` or `scholar`."
---

Search, analyze, and export academic paper metadata using the Semantic Scholar API.

Before acting, read the relevant doc for the task:

- Paper search, details, citations, references, recommendations: `docs/PAPERS.md`
- Author search, details, top papers, duplicates: `docs/AUTHORS.md`
- BibTeX export and paper tracking: `docs/EXPORT.md`

Run scripts from this skill's directory:

```bash
uv run scripts/<name>.py <subcommand> [args]
```

Rules:

- Prefer existing MCP tools for Semantic Scholar if the current agent environment provides them.
- Confirm with the user before making external requests unless they explicitly invoked `/scholar` for that purpose.
- Do not store API keys in the repository.
- Use normal TLS verification by default. Disable verification only when the user explicitly approves it for the current environment.
