# /// script
# requires-python = ">=3.11"
# ///
"""Semantic Scholar paper commands."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    COMPACT_PAPER_FIELDS,
    DEFAULT_PAPER_FIELDS,
    PAPER_FIELDS_WITH_TLDR,
    RECOMMENDATIONS_API_BASE,
    api_request,
    build_nested_fields,
    output,
    paper_not_found_message,
    track_papers,
)


def search_papers(args: argparse.Namespace) -> None:
    params: dict = {
        "query": args.query,
        "fields": COMPACT_PAPER_FIELDS,
        "limit": args.limit,
    }
    if args.year:
        params["year"] = args.year
    if args.min_citation_count is not None:
        params["minCitationCount"] = args.min_citation_count
    if args.fields_of_study:
        params["fieldsOfStudy"] = args.fields_of_study

    resp = api_request("/paper/search", params)
    if resp.get("error"):
        output(resp)
        return

    papers = resp.get("data") or []
    if not papers:
        output({"message": f"No papers found for query '{args.query}'."})
        return

    track_papers(papers, "search_papers")
    output(papers)


def get_paper_details(args: argparse.Namespace) -> None:
    fields = DEFAULT_PAPER_FIELDS if args.no_tldr else PAPER_FIELDS_WITH_TLDR
    resp = api_request(f"/paper/{args.paper_id}", {"fields": fields})
    if resp.get("error"):
        if resp.get("status") == 404:
            output({"error": True, "message": paper_not_found_message(args.paper_id)})
        else:
            output(resp)
        return

    track_papers([resp], "get_paper_details")
    output(resp)


def get_paper_citations(args: argparse.Namespace) -> None:
    params: dict = {
        "fields": build_nested_fields("citingPaper", compact=True),
        "limit": args.limit,
    }
    if args.year:
        params["year"] = args.year

    resp = api_request(f"/paper/{args.paper_id}/citations", params)
    if resp.get("error"):
        if resp.get("status") == 404:
            output({"error": True, "message": paper_not_found_message(args.paper_id)})
        else:
            output(resp)
        return

    papers = [
        item["citingPaper"]
        for item in (resp.get("data") or [])
        if item.get("citingPaper")
    ]
    if papers:
        track_papers(papers, "get_paper_citations")
    output(papers)


def get_paper_references(args: argparse.Namespace) -> None:
    params = {
        "fields": build_nested_fields("citedPaper", compact=True),
        "limit": args.limit,
    }
    resp = api_request(f"/paper/{args.paper_id}/references", params)
    if resp.get("error"):
        if resp.get("status") == 404:
            output({"error": True, "message": paper_not_found_message(args.paper_id)})
        else:
            output(resp)
        return

    papers = [
        item["citedPaper"]
        for item in (resp.get("data") or [])
        if item.get("citedPaper")
    ]
    if papers:
        track_papers(papers, "get_paper_references")
    output(papers)


def get_recommendations(args: argparse.Namespace) -> None:
    params = {
        "fields": DEFAULT_PAPER_FIELDS,
        "limit": args.limit,
        "from": args.from_pool,
    }
    resp = api_request(
        f"/papers/forpaper/{args.paper_id}",
        params,
        base_url=RECOMMENDATIONS_API_BASE,
    )
    if resp.get("error"):
        output(resp)
        return

    papers = resp.get("recommendedPapers", [])
    if not papers:
        output({"message": "No recommendations found."})
        return

    track_papers(papers, "get_recommendations")
    output(papers)


def get_related_papers(args: argparse.Namespace) -> None:
    positive_ids = [s.strip() for s in args.positive_paper_ids.split(",")]
    negative_ids = (
        [s.strip() for s in args.negative_paper_ids.split(",")]
        if args.negative_paper_ids
        else []
    )

    body: dict = {"positivePaperIds": positive_ids}
    if negative_ids:
        body["negativePaperIds"] = negative_ids

    params = {"fields": DEFAULT_PAPER_FIELDS, "limit": args.limit}
    resp = api_request(
        "/papers/",
        params,
        method="POST",
        json_body=body,
        base_url=RECOMMENDATIONS_API_BASE,
    )
    if resp.get("error"):
        output(resp)
        return

    papers = resp.get("recommendedPapers", [])
    if not papers:
        output({"message": "No related papers found."})
        return

    track_papers(papers, "get_related_papers")
    output(papers)


def main() -> None:
    parser = argparse.ArgumentParser(prog="papers")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search-papers")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--year")
    p.add_argument("--min-citation-count", type=int)
    p.add_argument("--fields-of-study")

    p = sub.add_parser("get-paper-details")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--no-tldr", action="store_true")

    p = sub.add_parser("get-paper-citations")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--year")

    p = sub.add_parser("get-paper-references")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("get-recommendations")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--from-pool", choices=["recent", "all-cs"], default="recent")

    p = sub.add_parser("get-related-papers")
    p.add_argument("--positive-paper-ids", required=True)
    p.add_argument("--negative-paper-ids")
    p.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "search-papers": search_papers,
        "get-paper-details": get_paper_details,
        "get-paper-citations": get_paper_citations,
        "get-paper-references": get_paper_references,
        "get-recommendations": get_recommendations,
        "get-related-papers": get_related_papers,
    }
    try:
        commands[args.command](args)
    except Exception as e:
        output({"error": True, "message": str(e)})


if __name__ == "__main__":
    main()
