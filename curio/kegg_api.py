from __future__ import annotations
from typing import Dict, Optional, Any, List
import requests

from .net_utils import get_text, get_bytes, HttpConfig, make_session
from . import get_logger

log = get_logger("kegg")

# KEGG endpoints
FIND_URL = "https://rest.kegg.jp/find/genes/{org}%20{query}"
GET_URL = "https://rest.kegg.jp/get/{kid}"
LINK_PATHWAY_URL = "https://rest.kegg.jp/link/pathway/{kid}"


def find_kegg_gene(query: str, org: str = "hsa") -> List[str]:
    """Find KEGG genes by query and organism code."""
    url = FIND_URL.format(org=org, query=query)
    log.info(f"Fetching KEGG genes from {url}")
    text = get_text(url)
    results = []
    for line in text.strip().split("\n"):
        if line:
            parts = line.split("\t")
            if len(parts) > 1:
                results.append(parts[0])
    return results


def get_kegg_entry(kid: str) -> str:
    """Retrieve KEGG entry details by KEGG ID."""
    url = GET_URL.format(kid=kid)
    log.info(f"Fetching KEGG entry from {url}")
    return get_text(url)


def get_gene_pathways(kid: str) -> List[str]:
    """Retrieve all pathways associated with a given KEGG gene ID."""
    url = LINK_PATHWAY_URL.format(kid=kid)
    log.info(f"Fetching pathways for {kid} from {url}")
    resp = requests.get(url)
    if resp.status_code == 200 and resp.text.strip():
        pathways = [line.split("\t")[1].replace("path:", "").strip()
                    for line in resp.text.strip().split("\n") if "\t" in line]
        return pathways
    return []