# Author Commands

Run from the skill root: `uv run scripts/authors.py <subcommand> [args]`

## search-authors

Search for researchers by name.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--query` | yes | — | Author name to search |
| `--limit` | no | 10 | Max results (1–1000) |

```bash
uv run scripts/authors.py search-authors --query "Geoffrey Hinton" --limit 5
```

## get-author-details

Get full author profile with optional publication list. Use `--name` to auto-search and merge all matching profiles (handles duplicate S2 profiles for the same person). Use `--author-id` if you already know the exact ID.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--author-id` | one of id/name | — | Semantic Scholar author ID |
| `--name` | one of id/name | — | Author name (searches, merges all matching profiles, fetches combined papers) |
| `--no-papers` | no | false | Skip fetching papers |
| `--papers-limit` | no | 10 | Max papers per profile |

```bash
uv run scripts/authors.py get-author-details --name "Ante Kapetanovic" --papers-limit 50
uv run scripts/authors.py get-author-details --author-id "1741101" --papers-limit 5
```

## get-author-top-papers

Get an author's most cited papers (paginates all papers, sorts client-side).

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--author-id` | yes | — | Semantic Scholar author ID |
| `--top-n` | no | 5 | Number of top papers |
| `--min-citations` | no | — | Minimum citation count filter |

```bash
uv run scripts/authors.py get-author-top-papers --author-id "1741101" --top-n 3
```

## find-duplicate-authors

Find potential duplicate author records by searching multiple name variants.

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--author-names` | yes | — | Comma-separated name variants |
| `--no-match-by-orcid` | no | false | Disable ORCID matching |
| `--no-match-by-dblp` | no | false | Disable DBLP matching |

```bash
uv run scripts/authors.py find-duplicate-authors --author-names "Geoffrey Hinton,G. Hinton"
```

## consolidate-authors

Preview or confirm merging duplicate author records (local operation only).

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--author-ids` | yes | — | Comma-separated author IDs to merge |
| `--confirm-merge` | no | false | Return final merged result instead of preview |

```bash
uv run scripts/authors.py consolidate-authors --author-ids "1741101,12345678"
```
