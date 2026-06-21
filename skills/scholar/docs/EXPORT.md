# Export & Tracking Commands

Run from the skill root: `uv run scripts/export.py <subcommand> [args]`

Papers are automatically tracked when fetched by paper/author commands (stored in `/tmp/scholar_tracked_papers.json`).

## export-bibtex

Export tracked or specific papers to BibTeX format.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--paper-ids` | no | — | Comma-separated paper IDs (defaults to all tracked) |
| `--include-abstract` | no | false | Include abstracts in output |
| `--no-url` | no | false | Exclude URLs |
| `--no-doi` | no | false | Exclude DOIs |
| `--cite-key-format` | no | author_year | `author_year`, `author_year_title`, or `paper_id` |
| `--file-path` | no | — | Write to file instead of stdout |

```bash
uv run scripts/export.py export-bibtex --cite-key-format author_year_title
uv run scripts/export.py export-bibtex --file-path references.bib
```

## list-tracked-papers

List papers tracked during this session.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--source-tool` | no | — | Filter by source (e.g., `search_papers`, `get_paper_details`) |

```bash
uv run scripts/export.py list-tracked-papers
uv run scripts/export.py list-tracked-papers --source-tool search_papers
```

## clear-tracked-papers

Remove all tracked papers.

```bash
uv run scripts/export.py clear-tracked-papers
```
