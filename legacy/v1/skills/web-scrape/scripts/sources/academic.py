#!/usr/bin/env python3
"""Academic paper search via OpenAlex (250M+ works) + Unpaywall free-PDF finder.

Both APIs are free and need no key. They reward "polite pool" callers who
identify with an email — set OPENALEX_EMAIL in ~/.claude/.env (a safe default
is used otherwise; see _common.DEFAULT_POLITE_EMAIL).

Client lifted from the AAA Deep Research module's working Academic client.
The only change: full-text extraction shells out to THIS skill's webscrape.py
(Firecrawl) instead of a standalone `firecrawl` CLI we don't ship.

CLI:
    python3 academic.py search "<query>" [--limit 10] [--from-year 2024] [--oa] [--min-cites N] [--sort cites|date]
    python3 academic.py paper --doi 10.xxxx/xxx
    python3 academic.py citations "<openalex_id>" [--limit 10]
    python3 academic.py pdf 10.xxxx/xxx              # find a free PDF via Unpaywall
    python3 academic.py research "<query>" [--papers 5] [--from-year 2024] [--full-text]
Add --json for the raw structured payload.
"""
import argparse
import json
import subprocess
import sys

from _common import WEBSCRAPE, RateLimiter, die, emit, polite_email, requests

OPENALEX_BASE = "https://api.openalex.org"
UNPAYWALL_BASE = "https://api.unpaywall.org/v2"
_RL = RateLimiter(0.2)  # OpenAlex is generous; stay polite


def _reconstruct_abstract(inverted_index):
    """Reconstruct an abstract from OpenAlex's inverted-index format."""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


class AcademicClient:
    """OpenAlex search + Unpaywall free-PDF lookup + (via webscrape.py) full text."""

    def __init__(self):
        self.email = polite_email()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"NavAIgate-Research/1.0 (mailto:{self.email})",
            "Accept": "application/json",
        })

    def search(self, query, limit=10, year_from=None, year_to=None,
               open_access_only=False, sort="relevance_score:desc", cited_by_min=None):
        """Search OpenAlex works. Returns clean paper dicts."""
        _RL.wait()
        filters = []
        if year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if year_to:
            filters.append(f"to_publication_date:{year_to}-12-31")
        if open_access_only:
            filters.append("open_access.is_oa:true")
        if cited_by_min:
            filters.append(f"cited_by_count:>{cited_by_min}")
        params = {"search": query, "per_page": min(limit, 200), "sort": sort,
                  "mailto": self.email}
        if filters:
            params["filter"] = ",".join(filters)
        try:
            resp = self.session.get(f"{OPENALEX_BASE}/works", params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            die(f"OpenAlex search failed: {e}")
        papers = []
        for r in data.get("results", []):
            papers.append(self._parse_work(r))
        return papers

    def get_paper(self, doi=None, openalex_id=None):
        _RL.wait()
        if doi:
            url = f"{OPENALEX_BASE}/works/doi:{doi.replace('https://doi.org/', '')}"
        elif openalex_id:
            url = f"{OPENALEX_BASE}/works/{openalex_id}"
        else:
            return None
        try:
            resp = self.session.get(url, params={"mailto": self.email}, timeout=20)
            if resp.status_code != 200:
                return None
            r = resp.json()
        except Exception:
            return None
        paper = self._parse_work(r)
        paper["referenced_works_count"] = len(r.get("referenced_works", []))
        paper["related_works"] = r.get("related_works", [])[:5]
        return paper

    def get_citations(self, openalex_id, limit=10):
        """Papers that cite a given OpenAlex work."""
        _RL.wait()
        try:
            resp = self.session.get(
                f"{OPENALEX_BASE}/works",
                params={"filter": f"cites:{openalex_id}", "per_page": limit,
                        "sort": "cited_by_count:desc", "mailto": self.email},
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []
        return [
            {
                "title": r.get("title", ""),
                "year": r.get("publication_year"),
                "cited_by": r.get("cited_by_count", 0),
                "doi": (r.get("doi", "") or "").replace("https://doi.org/", ""),
                "openalex_id": r.get("id", ""),
            }
            for r in data.get("results", [])
        ]

    def find_free_pdf(self, doi):
        """Find a free, legal PDF for a DOI via Unpaywall."""
        _RL.wait()
        clean_doi = doi.replace("https://doi.org/", "")
        try:
            resp = self.session.get(f"{UNPAYWALL_BASE}/{clean_doi}",
                                    params={"email": self.email}, timeout=15)
            if resp.status_code != 200:
                return None
            best = resp.json().get("best_oa_location", {}) or {}
            return best.get("url_for_pdf") or best.get("url")
        except Exception:
            return None

    def get_full_text(self, url):
        """Scrape full article text via this skill's webscrape.py (Firecrawl)."""
        try:
            result = subprocess.run(
                [sys.executable, str(WEBSCRAPE), "scrape", url, "--json"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                return None
            payload = json.loads(result.stdout)
            data = payload.get("data", payload) if isinstance(payload, dict) else {}
            return data.get("markdown") or data.get("content") or None
        except Exception:
            return None

    def research(self, query, max_papers=5, search_limit=15, year_from=2024,
                 extract_full_text=False, find_free_pdfs=True):
        """Full pipeline: search, enrich with free PDFs, optionally extract full text."""
        papers = self.search(query, limit=search_limit, year_from=year_from)
        top = papers[:max_papers]
        if find_free_pdfs:
            for p in top:
                if not p.get("open_access") and p.get("doi"):
                    pdf = self.find_free_pdf(p["doi"])
                    if pdf:
                        p["free_pdf_url"] = pdf
                        p["open_access"] = True
        if extract_full_text:
            for p in top:
                url = p.get("oa_url") or p.get("free_pdf_url")
                if url:
                    text = self.get_full_text(url)
                    if text:
                        p["full_text"] = text[:50000]
                        p["full_text_length"] = len(text)
        return {
            "query": query,
            "total_found": len(papers),
            "papers_processed": len(top),
            "papers": top,
        }

    def _parse_work(self, r):
        abstract = _reconstruct_abstract(r.get("abstract_inverted_index", {}))
        authors = []
        for a in r.get("authorships", [])[:5]:
            name = a.get("author", {}).get("display_name", "")
            insts = a.get("institutions", [])
            institution = insts[0].get("display_name", "") if insts else ""
            if name:
                authors.append({"name": name, "institution": institution})
        oa = r.get("open_access", {})
        location = r.get("primary_location", {}) or {}
        source = location.get("source", {}) or {}
        doi = r.get("doi", "") or ""
        doi_short = doi.replace("https://doi.org/", "") if doi.startswith("https://doi.org/") else doi
        return {
            "title": r.get("title", ""),
            "abstract": abstract,
            "year": r.get("publication_year"),
            "cited_by": r.get("cited_by_count", 0),
            "doi": doi_short,
            "doi_url": doi,
            "open_access": oa.get("is_oa", False),
            "oa_url": oa.get("oa_url", ""),
            "authors": authors,
            "venue": source.get("display_name", ""),
            "type": r.get("type", ""),
            "openalex_id": r.get("id", ""),
        }


# ---------------------------------------------------------------- CLI --------
_SORTS = {"relevance": "relevance_score:desc", "cites": "cited_by_count:desc",
          "date": "publication_date:desc"}


def _print_papers(papers):
    if not papers:
        print("No papers.")
        return
    for p in papers:
        names = ", ".join(a["name"] for a in p.get("authors", [])[:2])
        oa = " [OA]" if p.get("open_access") else ""
        print(f"[{p.get('cited_by', 0)} cites | {p.get('year')}]{oa} {p.get('title')}")
        print(f"   {names} — {p.get('venue', '')}")
        if p.get("doi"):
            print(f"   doi:{p['doi']}  {p.get('oa_url') or p.get('free_pdf_url') or ''}")
        if p.get("abstract"):
            print("   " + " ".join(p["abstract"][:280].split()))
        print()


def cmd_search(args, c):
    papers = c.search(args.query, limit=args.limit, year_from=args.from_year,
                      year_to=args.to_year, open_access_only=args.oa,
                      sort=_SORTS[args.sort], cited_by_min=args.min_cites)
    if emit({"query": args.query, "papers": papers}, args.json):
        return
    _print_papers(papers)


def cmd_paper(args, c):
    paper = c.get_paper(doi=args.doi, openalex_id=args.id)
    if not paper:
        die("Paper not found.")
    if emit(paper, args.json):
        return
    _print_papers([paper])
    print(f"References: {paper.get('referenced_works_count', 0)}")


def cmd_citations(args, c):
    cites = c.get_citations(args.openalex_id, limit=args.limit)
    if emit({"openalex_id": args.openalex_id, "citing_works": cites}, args.json):
        return
    for r in cites:
        print(f"[{r['cited_by']} cites | {r['year']}] {r['title']} (doi:{r['doi']})")


def cmd_pdf(args, c):
    url = c.find_free_pdf(args.doi)
    if emit({"doi": args.doi, "free_pdf_url": url}, args.json):
        return
    print(url or "No free PDF found via Unpaywall.")


def cmd_research(args, c):
    result = c.research(args.query, max_papers=args.papers, year_from=args.from_year,
                        extract_full_text=args.full_text)
    if emit(result, args.json):
        return
    print(f"Found {result['total_found']}, processed {result['papers_processed']}\n")
    _print_papers(result["papers"])


def build_parser():
    # Shared --json flag works before OR after the subcommand (matches webscrape.py).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="Print the raw structured payload.")
    p = argparse.ArgumentParser(prog="academic.py", description="OpenAlex + Unpaywall (free, no key).")
    p.add_argument("--json", action="store_true", help="Print the raw structured payload.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", parents=[common], help="Search OpenAlex works.")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--from-year", type=int)
    s.add_argument("--to-year", type=int)
    s.add_argument("--oa", action="store_true", help="Open-access only.")
    s.add_argument("--min-cites", type=int)
    s.add_argument("--sort", default="relevance", choices=list(_SORTS))
    s.set_defaults(func=cmd_search)

    pa = sub.add_parser("paper", parents=[common], help="Get one paper by DOI or OpenAlex ID.")
    pa.add_argument("--doi")
    pa.add_argument("--id", dest="id")
    pa.set_defaults(func=cmd_paper)

    ci = sub.add_parser("citations", parents=[common], help="Works that cite a given OpenAlex ID.")
    ci.add_argument("openalex_id")
    ci.add_argument("--limit", type=int, default=10)
    ci.set_defaults(func=cmd_citations)

    pd = sub.add_parser("pdf", parents=[common], help="Find a free PDF for a DOI via Unpaywall.")
    pd.add_argument("doi")
    pd.set_defaults(func=cmd_pdf)

    r = sub.add_parser("research", parents=[common],
                       help="Full pipeline: search + free PDFs (+ optional full text).")
    r.add_argument("query")
    r.add_argument("--papers", type=int, default=5)
    r.add_argument("--from-year", type=int, default=2024)
    r.add_argument("--full-text", action="store_true", help="Scrape full text via Firecrawl (slower).")
    r.set_defaults(func=cmd_research)
    return p


def main():
    args = build_parser().parse_args()
    if not hasattr(args, "json"):
        args.json = False
    c = AcademicClient()
    args.func(args, c)


if __name__ == "__main__":
    main()
