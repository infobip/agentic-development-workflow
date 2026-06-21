# /// script
# requires-python = ">=3.11"
# ///
"""Semantic Scholar export and tracking commands."""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    DEFAULT_PAPER_FIELDS,
    api_request,
    clear_tracked,
    get_tracked,
    load_tracked,
    output,
)

BIBTEX_SPECIAL = str.maketrans({
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
})

CONFERENCE_KEYWORDS = {
    "conference", "proceedings", "proc.", "workshop", "symposium",
    "icml", "neurips", "nips", "iclr", "aaai", "ijcai", "cvpr",
    "iccv", "eccv", "acl", "emnlp", "naacl", "sigir", "kdd",
    "www", "chi", "uist", "siggraph",
}


def _escape_bibtex(text: str) -> str:
    return text.translate(BIBTEX_SPECIAL)


def _normalize_ascii(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _detect_entry_type(paper: dict) -> str:
    pub_types = paper.get("publicationTypes") or []
    if "JournalArticle" in pub_types:
        return "article"
    if "Conference" in pub_types:
        return "inproceedings"

    venue = (paper.get("venue") or "").lower()
    if any(kw in venue for kw in CONFERENCE_KEYWORDS):
        return "inproceedings"

    return "misc"


def _generate_cite_key(paper: dict, fmt: str) -> str:
    if fmt == "paper_id":
        return paper.get("paperId", "unknown")

    authors = paper.get("authors") or []
    if authors:
        name = authors[0].get("name", "unknown")
        last = name.split()[-1] if name.split() else "unknown"
        last = _normalize_ascii(last).lower()
        last = re.sub(r"[^a-z]", "", last)
    else:
        last = "unknown"

    year = paper.get("year") or "nodate"
    key = f"{last}{year}"

    if fmt == "author_year_title":
        title = paper.get("title") or ""
        words = re.findall(r"[a-zA-Z]+", title)
        stop = {"a", "an", "the", "of", "in", "on", "for", "and", "to", "with", "is"}
        first_word = next((w.lower() for w in words if w.lower() not in stop), "")
        if first_word:
            key = f"{key}{first_word}"

    return key


def _paper_to_bibtex(paper: dict, cite_key: str, entry_type: str, config: dict) -> str:
    lines = [f"@{entry_type}{{{cite_key},"]

    title = paper.get("title")
    if title:
        lines.append(f"  title = {{{_escape_bibtex(title)}}},")

    authors = paper.get("authors") or []
    if authors:
        names = " and ".join(a.get("name", "") for a in authors if a.get("name"))
        if names:
            lines.append(f"  author = {{{_escape_bibtex(names)}}},")

    year = paper.get("year")
    if year:
        lines.append(f"  year = {{{year}}},")

    venue = paper.get("venue")
    if venue:
        field = "booktitle" if entry_type == "inproceedings" else "journal"
        lines.append(f"  {field} = {{{_escape_bibtex(venue)}}},")

    journal = paper.get("journal") or {}
    volume = journal.get("volume")
    pages = journal.get("pages")
    if volume:
        lines.append(f"  volume = {{{volume}}},")
    if pages:
        lines.append(f"  pages = {{{pages}}},")

    if config.get("include_abstract"):
        abstract = paper.get("abstract")
        if abstract:
            lines.append(f"  abstract = {{{_escape_bibtex(abstract)}}},")

    ext_ids = paper.get("externalIds") or {}
    if config.get("include_doi"):
        doi = ext_ids.get("DOI")
        if doi:
            lines.append(f"  doi = {{{doi}}},")

    if config.get("include_url"):
        oa = paper.get("openAccessPdf") or {}
        url = oa.get("url")
        if not url:
            doi = ext_ids.get("DOI")
            if doi:
                url = f"https://doi.org/{doi}"
        if url:
            lines.append(f"  url = {{{url}}},")

    lines.append("}")
    return "\n".join(lines)


def _deduplicate_keys(entries: list[tuple[str, str]]) -> list[tuple[str, str]]:
    counts: dict[str, int] = {}
    for key, _ in entries:
        counts[key] = counts.get(key, 0) + 1

    duplicates: dict[str, int] = {}
    result: list[tuple[str, str]] = []
    for key, bib in entries:
        if counts[key] > 1:
            idx = duplicates.get(key, 0)
            suffix = chr(ord("a") + idx) if idx < 26 else f"_{idx + 1}"
            duplicates[key] = idx + 1
            result.append((f"{key}{suffix}", bib.replace(f"{{{key},", f"{{{key}{suffix},", 1)))
        else:
            result.append((key, bib))
    return result


def export_bibtex(args: argparse.Namespace) -> None:
    config = {
        "include_abstract": args.include_abstract,
        "include_url": args.include_url,
        "include_doi": args.include_doi,
    }

    if args.paper_ids:
        ids = [s.strip() for s in args.paper_ids.split(",")]
        tracked = load_tracked()
        papers: list[dict] = []
        for pid in ids:
            if pid in tracked:
                papers.append(tracked[pid]["paper"])
            else:
                resp = api_request(f"/paper/{pid}", {"fields": DEFAULT_PAPER_FIELDS})
                if not resp.get("error"):
                    papers.append(resp)
    else:
        papers = get_tracked()

    if not papers:
        output({"message": "No papers to export. Search or fetch papers first."})
        return

    entries: list[tuple[str, str]] = []
    for p in papers:
        entry_type = _detect_entry_type(p)
        key = _generate_cite_key(p, args.cite_key_format)
        bib = _paper_to_bibtex(p, key, entry_type, config)
        entries.append((key, bib))

    entries = _deduplicate_keys(entries)
    bibtex_str = "\n\n".join(bib for _, bib in entries)

    if args.file_path:
        Path(args.file_path).write_text(bibtex_str + "\n")
        output({"message": f"Exported {len(entries)} entries to {args.file_path}"})
    else:
        print(bibtex_str)


def list_tracked_papers(args: argparse.Namespace) -> None:
    source = getattr(args, "source_tool", None)
    papers = get_tracked(source)
    if not papers:
        msg = "No papers tracked in this session."
        if source:
            msg = f"No papers tracked from source '{source}'."
        output({"message": msg})
        return
    output(papers)


def clear_tracked_papers(args: argparse.Namespace) -> None:
    tracked = load_tracked()
    count = len(tracked)
    clear_tracked()
    output({"message": f"Cleared {count} tracked papers."})


def main() -> None:
    parser = argparse.ArgumentParser(prog="export")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("export-bibtex")
    p.add_argument("--paper-ids")
    p.add_argument("--include-abstract", action="store_true")
    p.add_argument("--no-url", action="store_true")
    p.add_argument("--no-doi", action="store_true")
    p.add_argument("--cite-key-format", choices=["author_year", "author_year_title", "paper_id"], default="author_year")
    p.add_argument("--file-path")

    p = sub.add_parser("list-tracked-papers")
    p.add_argument("--source-tool")

    sub.add_parser("clear-tracked-papers")

    args = parser.parse_args()

    if args.command == "export-bibtex":
        args.include_url = not getattr(args, "no_url", False)
        args.include_doi = not getattr(args, "no_doi", False)

    commands = {
        "export-bibtex": export_bibtex,
        "list-tracked-papers": list_tracked_papers,
        "clear-tracked-papers": clear_tracked_papers,
    }
    try:
        commands[args.command](args)
    except Exception as e:
        output({"error": True, "message": str(e)})


if __name__ == "__main__":
    main()
