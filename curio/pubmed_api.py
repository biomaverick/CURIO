from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter

from matplotlib.figure import Figure

from .net_utils import get_json, get_text, HttpConfig, make_session
from . import get_logger

log = get_logger("pubmed")

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query: str, retmax: int = 200, cfg: Optional[HttpConfig] = None) -> List[str]:
    """Return a list of PMIDs for a query, sorted by pubdate (desc)."""
    cfg = cfg or HttpConfig()
    sess = make_session(cfg)
    params = {"db": "pubmed", "term": query, "retmax": retmax, "sort": "pubdate", "retmode": "json"}
    js = get_json(f"{EUTILS}/esearch.fcgi", params=params, session=sess, cfg=cfg)
    pmids = (js.get("esearchresult") or {}).get("idlist", [])
    log.info("PubMed search '%s' -> %d PMIDs", query, len(pmids))
    return pmids


def fetch_pubmed_summaries(pmids: List[str], cfg: Optional[HttpConfig] = None) -> List[Dict[str, Any]]:
    """Return summaries with fields: pmid, title, journal, pubdate (YYYY-MM-DD), doi, link."""
    if not pmids:
        return []
    cfg = cfg or HttpConfig()
    sess = make_session(cfg)
    ids = ",".join(pmids)
    js = get_json(f"{EUTILS}/esummary.fcgi", params={"db": "pubmed", "id": ids, "retmode": "json"}, session=sess, cfg=cfg)
    result = js.get("result", {})
    out: List[Dict[str, Any]] = []
    for pid in pmids:
        r = result.get(pid)
        if not r:
            continue
        pubdate = r.get("sortpubdate") or r.get("pubdate") or ""
        # Normalize pubdate to YYYY-MM-DD when possible
        pubdate_norm = _normalize_pubdate(pubdate)
        doi = ""
        for idobj in r.get("articleids", []):
            if idobj.get("idtype") == "doi":
                doi = idobj.get("value", "")
                break
        link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
        out.append({
            "pmid": pid,
            "title": r.get("title"),
            "journal": (r.get("fulljournalname") or r.get("source")),
            "pubdate": pubdate_norm,
            "doi": doi,
            "link": link,
        })
    return out


def fetch_pubmed_abstract(pmid: str, cfg: Optional[HttpConfig] = None) -> str:
    """Return abstract text (may be empty)."""
    cfg = cfg or HttpConfig()
    sess = make_session(cfg)
    xml = get_text(f"{EUTILS}/efetch.fcgi", params={"db": "pubmed", "id": pmid, "retmode": "xml"}, session=sess, cfg=cfg)
    # Very light XML scrape to avoid heavy deps
    m = re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", xml, flags=re.S)
    text = " ".join(_strip_xml_tags(t).strip() for t in m).strip()
    return re.sub(r"\s+", " ", text)


def plot_trend(records: List[Dict[str, Any]], years: int = 10) -> Figure:
    """Return a matplotlib Figure: publications per year over the past `years`."""
    this_year = datetime.utcnow().year
    bins = list(range(this_year - years + 1, this_year + 1))
    counts = {y: 0 for y in bins}
    for r in records:
        d = r.get("pubdate") or ""
        y = _year_from_date(d)
        if y in counts:
            counts[y] += 1

    fig = Figure(figsize=(7, 3.6))
    ax = fig.subplots()
    ax.bar(list(counts.keys()), list(counts.values()))
    ax.set_xlabel("Year")
    ax.set_ylabel("Publications")
    ax.set_title(f"PubMed results per year (last {years} years)")
    ax.grid(True, axis="y", linestyle=":", linewidth=0.5)
    return fig


_STOP = {
    "the","and","of","in","to","for","a","on","with","by","as","from","at","is","are",
    "we","our","be","this","that","these","those","an","or","it","its","was","were",
    "into","using","use","can","may","also","have","has","had","but","not","than"
}


def extract_keywords(abstracts: List[str], topk: int = 25) -> List[Tuple[str, int]]:
    """Very simple TF counts (lowercased tokens, alnum-only), minus stopwords."""
    cnt: Counter[str] = Counter()
    for a in abstracts:
        for tok in re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", a.lower()):
            if tok in _STOP:
                continue
            cnt[tok] += 1
    return cnt.most_common(topk)


def _normalize_pubdate(s: str) -> str:
    # Try common formats else return original
    s = s.strip()
    for fmt in ("%Y %b %d", "%Y %b", "%Y-%m-%d", "%Y/%m/%d", "%Y"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    # last resort: extract year
    y = _year_from_date(s)
    return f"{y}-01-01" if y else s


def _year_from_date(s: str) -> Optional[int]:
    m = re.search(r"\b(19|20)\d{2}\b", s)
    return int(m.group(0)) if m else None


def _strip_xml_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)