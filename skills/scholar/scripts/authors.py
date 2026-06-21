# /// script
# requires-python = ">=3.11"
# ///
"""Semantic Scholar author commands."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    COMPACT_PAPER_FIELDS,
    DEFAULT_AUTHOR_FIELDS,
    DEFAULT_PAPER_FIELDS,
    api_request,
    author_not_found_message,
    output,
    track_papers,
)


def _fetch_author(author_id: str) -> dict | None:
    resp = api_request(f"/author/{author_id}", {"fields": DEFAULT_AUTHOR_FIELDS})
    if resp.get("error"):
        return None
    return resp


def _fetch_author_papers(
    author_id: str, *, limit: int = 1000, fields: str = COMPACT_PAPER_FIELDS
) -> list[dict]:
    all_papers: list[dict] = []
    offset = 0
    page_size = min(limit, 1000)
    while len(all_papers) < limit:
        remaining = limit - len(all_papers)
        resp = api_request(
            f"/author/{author_id}/papers",
            {"fields": fields, "limit": min(page_size, remaining), "offset": offset},
        )
        if resp.get("error"):
            break
        batch = resp.get("data", [])
        if not batch:
            break
        all_papers.extend(batch)
        if len(batch) < min(page_size, remaining):
            break
        offset += len(batch)
    return all_papers


def _search_authors(query: str, limit: int = 10) -> list[dict]:
    resp = api_request(
        "/author/search",
        {"query": query, "fields": DEFAULT_AUTHOR_FIELDS, "limit": limit},
    )
    if resp.get("error"):
        return []
    return resp.get("data", [])


def _normalize_dblp(dblp: str | list | None) -> str | None:
    if isinstance(dblp, list):
        return dblp[0] if dblp else None
    return dblp


def search_authors(args: argparse.Namespace) -> None:
    authors = _search_authors(args.query, args.limit)
    if not authors:
        output({"message": f"No authors found for query '{args.query}'."})
        return
    output(authors)


def _deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for p in papers:
        pid = p.get("paperId")
        if pid and pid not in seen:
            seen[pid] = p
    return list(seen.values())


def _resolve_author(name: str) -> tuple[dict, list[str]]:
    """Search by name, return merged author profile and all author IDs."""
    results = _search_authors(name, limit=10)
    if not results:
        return {}, []
    if len(results) == 1:
        return results[0], [results[0]["authorId"]]

    all_ids = [a["authorId"] for a in results]
    primary = max(results, key=lambda a: a.get("citationCount") or 0)

    all_names: set[str] = set()
    total_papers = 0
    total_citations = 0
    for a in results:
        all_names.add(a.get("name", ""))
        total_papers += a.get("paperCount") or 0
        total_citations += a.get("citationCount") or 0

    merged = {**primary}
    merged["aliases"] = sorted(all_names - {primary.get("name", "")})
    merged["paperCount"] = total_papers
    merged["citationCount"] = total_citations
    merged["_merged_from"] = all_ids
    return merged, all_ids


def get_author_details(args: argparse.Namespace) -> None:
    if args.name:
        author, author_ids = _resolve_author(args.name)
        if not author:
            output({"error": True, "message": f"No authors found for name '{args.name}'."})
            return
    else:
        author = _fetch_author(args.author_id)
        if not author:
            output({"error": True, "message": author_not_found_message(args.author_id)})
            return
        author_ids = [args.author_id]

    if args.include_papers:
        all_papers: list[dict] = []
        for aid in author_ids:
            all_papers.extend(
                _fetch_author_papers(aid, limit=args.papers_limit, fields=DEFAULT_PAPER_FIELDS)
            )
        papers = _deduplicate_papers(all_papers)
        author["papers"] = papers
        if papers:
            track_papers(papers, "get_author_details")

    output(author)


def get_author_top_papers(args: argparse.Namespace) -> None:
    author = _fetch_author(args.author_id)
    if not author:
        output({"error": True, "message": author_not_found_message(args.author_id)})
        return

    all_papers = _fetch_author_papers(args.author_id)
    all_papers.sort(key=lambda p: p.get("citationCount") or 0, reverse=True)

    if args.min_citations is not None:
        all_papers = [
            p for p in all_papers if (p.get("citationCount") or 0) >= args.min_citations
        ]

    top = all_papers[: args.top_n]
    if top:
        track_papers(top, "get_author_top_papers")

    output({
        "author_id": author.get("authorId"),
        "author_name": author.get("name"),
        "total_papers": author.get("paperCount"),
        "total_citations": author.get("citationCount"),
        "papers_fetched": len(all_papers),
        "top_papers": top,
    })


def find_duplicate_authors(args: argparse.Namespace) -> None:
    names = [n.strip() for n in args.author_names.split(",")]
    seen_ids: set[str] = set()
    all_authors: list[dict] = []

    for name in names:
        results = _search_authors(name, limit=10)
        for a in results:
            aid = a.get("authorId")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                all_authors.append(a)

    orcid_groups: dict[str, list[dict]] = {}
    dblp_groups: dict[str, list[dict]] = {}

    for a in all_authors:
        ext = a.get("externalIds") or {}
        if args.match_by_orcid:
            orcid = ext.get("ORCID")
            if orcid:
                orcid_groups.setdefault(orcid, []).append(a)
        if args.match_by_dblp:
            dblp = _normalize_dblp(ext.get("DBLP"))
            if dblp:
                dblp_groups.setdefault(dblp, []).append(a)

    groups: list[dict] = []
    reported_ids: set[str] = set()

    for key, authors in orcid_groups.items():
        if len(authors) < 2:
            continue
        authors.sort(key=lambda a: a.get("citationCount") or 0, reverse=True)
        group_ids = {a["authorId"] for a in authors}
        if group_ids & reported_ids:
            continue
        reported_ids |= group_ids
        groups.append({
            "primary_author": authors[0],
            "candidates": authors[1:],
            "match_reasons": ["same_orcid"],
        })

    for key, authors in dblp_groups.items():
        if len(authors) < 2:
            continue
        authors.sort(key=lambda a: a.get("citationCount") or 0, reverse=True)
        group_ids = {a["authorId"] for a in authors}
        if group_ids & reported_ids:
            continue
        reported_ids |= group_ids
        groups.append({
            "primary_author": authors[0],
            "candidates": authors[1:],
            "match_reasons": ["same_dblp"],
        })

    if not groups:
        output({"message": "No potential duplicate authors found."})
        return
    output(groups)


def consolidate_authors(args: argparse.Namespace) -> None:
    ids = [s.strip() for s in args.author_ids.split(",")]
    authors: list[dict] = []
    for aid in ids:
        a = _fetch_author(aid)
        if a:
            authors.append(a)

    if len(authors) < 2:
        output({"error": True, "message": "Need at least 2 valid author IDs to consolidate."})
        return

    match_type = "user_confirmed"
    confidence: float | None = None
    orcids = {
        (a.get("externalIds") or {}).get("ORCID")
        for a in authors
        if (a.get("externalIds") or {}).get("ORCID")
    }
    dblps = {
        _normalize_dblp((a.get("externalIds") or {}).get("DBLP"))
        for a in authors
        if (a.get("externalIds") or {}).get("DBLP")
    }
    dblps.discard(None)

    if len(orcids) == 1 and orcids != {None}:
        match_type = "orcid"
        confidence = 1.0
    elif len(dblps) == 1:
        match_type = "dblp"
        confidence = 0.95

    authors.sort(key=lambda a: a.get("citationCount") or 0, reverse=True)
    primary = authors[0]

    all_affiliations: list[str] = []
    all_names: set[str] = set()
    total_papers = 0
    total_citations = 0
    for a in authors:
        all_names.add(a.get("name", ""))
        all_affiliations.extend(a.get("affiliations") or [])
        total_papers += a.get("paperCount") or 0
        total_citations += a.get("citationCount") or 0

    merged = {
        "authorId": primary.get("authorId"),
        "name": primary.get("name"),
        "aliases": sorted(all_names - {primary.get("name", "")}),
        "affiliations": sorted(set(all_affiliations)),
        "paperCount": total_papers,
        "citationCount": total_citations,
        "hIndex": None,
        "externalIds": primary.get("externalIds"),
    }

    result = {
        "merged_author": merged,
        "source_authors": authors,
        "match_type": match_type,
        "confidence": confidence,
        "is_preview": not args.confirm_merge,
    }
    output(result)


def main() -> None:
    parser = argparse.ArgumentParser(prog="authors")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search-authors")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("get-author-details")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--author-id")
    g.add_argument("--name")
    p.add_argument("--no-papers", action="store_true")
    p.add_argument("--papers-limit", type=int, default=10)

    p = sub.add_parser("get-author-top-papers")
    p.add_argument("--author-id", required=True)
    p.add_argument("--top-n", type=int, default=5)
    p.add_argument("--min-citations", type=int)

    p = sub.add_parser("find-duplicate-authors")
    p.add_argument("--author-names", required=True)
    p.add_argument("--no-match-by-orcid", action="store_true")
    p.add_argument("--no-match-by-dblp", action="store_true")

    p = sub.add_parser("consolidate-authors")
    p.add_argument("--author-ids", required=True)
    p.add_argument("--confirm-merge", action="store_true")

    args = parser.parse_args()

    if args.command == "get-author-details":
        args.include_papers = not args.no_papers
    elif args.command == "find-duplicate-authors":
        args.match_by_orcid = not args.no_match_by_orcid
        args.match_by_dblp = not args.no_match_by_dblp

    commands = {
        "search-authors": search_authors,
        "get-author-details": get_author_details,
        "get-author-top-papers": get_author_top_papers,
        "find-duplicate-authors": find_duplicate_authors,
        "consolidate-authors": consolidate_authors,
    }
    try:
        commands[args.command](args)
    except Exception as e:
        output({"error": True, "message": str(e)})


if __name__ == "__main__":
    main()
