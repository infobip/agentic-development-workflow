# Paper Commands

Run from the skill root: `uv run scripts/papers.py <subcommand> [args]`

## search-papers

Search for papers by keyword or phrase.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--query` | yes | — | Search query string |
| `--limit` | no | 10 | Max results (1–100) |
| `--year` | no | — | Year or range: `"2020"` or `"2020-2024"` |
| `--min-citation-count` | no | — | Minimum citation count filter |
| `--fields-of-study` | no | — | Comma-separated: `"Computer Science,Medicine"` |

```bash
uv run scripts/papers.py search-papers --query "transformer attention mechanism" --limit 5
```

## get-paper-details

Get full metadata for a single paper.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--paper-id` | yes | — | S2 ID, `DOI:10.xxx/xxx`, or `ARXIV:xxxx.xxxxx` |
| `--no-tldr` | no | false | Skip AI-generated summary |

```bash
uv run scripts/papers.py get-paper-details --paper-id "ARXIV:1706.03762"
```

## get-paper-citations

Get papers that cite a given paper.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--paper-id` | yes | — | Paper identifier |
| `--limit` | no | 100 | Max results (1–1000) |
| `--year` | no | — | Year or range filter |

```bash
uv run scripts/papers.py get-paper-citations --paper-id "ARXIV:1706.03762" --limit 20
```

## get-paper-references

Get papers that a given paper references.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--paper-id` | yes | — | Paper identifier |
| `--limit` | no | 100 | Max results (1–1000) |

```bash
uv run scripts/papers.py get-paper-references --paper-id "ARXIV:1706.03762" --limit 20
```

## get-recommendations

ML-based paper recommendations from a seed paper.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--paper-id` | yes | — | Seed paper identifier |
| `--limit` | no | 10 | Max results |
| `--from-pool` | no | recent | `recent` or `all-cs` |

```bash
uv run scripts/papers.py get-recommendations --paper-id "ARXIV:1706.03762" --limit 5
```

## get-related-papers

Multi-paper recommendations with positive/negative examples.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--positive-paper-ids` | yes | — | Comma-separated paper IDs |
| `--negative-paper-ids` | no | — | Comma-separated paper IDs to avoid |
| `--limit` | no | 10 | Max results |

```bash
uv run scripts/papers.py get-related-papers --positive-paper-ids "ARXIV:1706.03762,ARXIV:1810.04805" --limit 5
```
