"""Shared utilities for Semantic Scholar API scripts."""

import json
import os
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH_API_BASE = "https://api.semanticscholar.org/graph/v1"
RECOMMENDATIONS_API_BASE = "https://api.semanticscholar.org/recommendations/v1"

DEFAULT_PAPER_FIELDS = (
    "paperId,title,abstract,year,citationCount,authors,venue,"
    "publicationTypes,openAccessPdf,fieldsOfStudy,journal,externalIds,"
    "publicationDate,publicationVenue"
)
COMPACT_PAPER_FIELDS = (
    "paperId,title,abstract,year,citationCount,authors,venue,openAccessPdf,fieldsOfStudy"
)
PAPER_FIELDS_WITH_TLDR = f"{DEFAULT_PAPER_FIELDS},tldr"
DEFAULT_AUTHOR_FIELDS = (
    "authorId,name,affiliations,paperCount,citationCount,hIndex,externalIds,homepage"
)

TRACKER_PATH = Path("/tmp/scholar_tracked_papers.json")


def build_nested_fields(prefix: str, *, compact: bool = False) -> str:
    fields = COMPACT_PAPER_FIELDS if compact else DEFAULT_PAPER_FIELDS
    return ",".join(f"{prefix}.{f}" for f in fields.split(","))


def api_request(
    endpoint: str,
    params: dict | None = None,
    *,
    method: str = "GET",
    json_body: dict | None = None,
    base_url: str = GRAPH_API_BASE,
    timeout: int = 30,
) -> dict:
    url = f"{base_url}{endpoint}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {"User-Agent": "scholar-skill/1.0"}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"

    ctx: ssl.SSLContext | None = None
    if os.environ.get("DISABLE_SSL_VERIFY", "").lower() in ("1", "true", "yes"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    last_error: dict = {}
    for attempt in range(3):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()
            except Exception:
                pass
            last_error = {"error": True, "status": e.code, "message": f"HTTP {e.code}: {body}"}
            if e.code == 429 and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            return last_error
        except (urllib.error.URLError, TimeoutError) as e:
            return {"error": True, "message": f"Connection failed: {e}"}
    return last_error


def output(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


# --- Tracking ---

def load_tracked() -> dict:
    try:
        return json.loads(TRACKER_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_tracked(data: dict) -> None:
    tmp = TRACKER_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False))
    tmp.rename(TRACKER_PATH)


def track_papers(papers: list[dict], source: str) -> None:
    tracked = load_tracked()
    for p in papers:
        pid = p.get("paperId")
        if pid:
            tracked[pid] = {"paper": p, "source": source}
    save_tracked(tracked)


def get_tracked(source: str | None = None) -> list[dict]:
    tracked = load_tracked()
    items = tracked.values()
    if source:
        items = [v for v in items if v.get("source") == source]
    return [v["paper"] for v in items]


def clear_tracked() -> None:
    TRACKER_PATH.unlink(missing_ok=True)


# --- Error helpers ---

def paper_not_found_message(paper_id: str) -> str:
    return (
        f"Paper '{paper_id}' not found. Accepted formats: "
        "Semantic Scholar ID, DOI:10.xxxx/xxxxx, ARXIV:xxxx.xxxxx"
    )


def author_not_found_message(author_id: str) -> str:
    return f"Author '{author_id}' not found on Semantic Scholar."
