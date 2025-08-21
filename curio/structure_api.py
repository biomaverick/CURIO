# curio/structure_api.py

import logging
import requests   
import re
from typing import List, Optional, Dict, Any

from .net_utils import (
    HttpConfig,
    make_session,
    get_json,
    get_text,
    post_json,  
)

log = logging.getLogger(__name__)

# RCSB API Endpoints
SUMMARY_URL = "https://data.rcsb.org/rest/v1/core/entry"
PDB_FILE_URL = "https://files.rcsb.org/download"
SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
GRAPHQL_URL = "https://search.rcsb.org/rcsbsearch/v2/graphql"  
UNIPROT_SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_XREF_URL = "https://rest.uniprot.org/uniprotkb"  

# Functions

def resolve_query_to_pdb_ids(query: str, max_hits: int = 12,
                             cfg: Optional[HttpConfig] = None) -> List[str]:
    """
    Resolve a user query (PDB ID, gene symbol, protein name) to a list of valid RCSB PDB IDs.
    Priority:
      1. Direct 4-char PDB ID
      2. RCSB REST Search API
      3. RCSB GraphQL free-text Search
      4. UniProt cross-reference mapping
    """
    query = query.strip()
    if not query:
        return []

    # If the query already looks like a PDB ID (4 chars alphanumeric)
    if re.match(r"^[0-9][A-Za-z0-9]{3}$", query):
        return [query.upper()]

    headers = {"Content-Type": "application/json"}
    if cfg and cfg.headers:
        headers.update(cfg.headers)

    # --- Primary: JSON search API ---
        # --- Fallback: RCSB JSON free-text search ---
    try:
        free_payload = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "struct.title",
                    "operator": "contains_phrase",
                    "value": query
                }
            },
            "return_type": "entry",
            "request_options": {
                "pager": {"start": 0, "rows": max_hits},
                "results_content_type": ["experimental"],
                "sort": [{"sort_by": "score", "direction": "desc"}],
            }
        }
        r2 = requests.post(SEARCH_URL, json=free_payload, headers=headers,
                           timeout=(cfg.timeout_seconds if cfg else 15))
        r2.raise_for_status()
        data2 = r2.json()
        ids = [x["identifier"] for x in data2.get("result_set", [])]
        if ids:
            return ids
    except Exception as e:
        log.warning("Free-text search failed for %s: %s", query, e)
    #  Fallback: UniProt cross-reference search 
    try:
        # 1. Find UniProt accession for this gene/protein
        uparams = {"query": query, "fields": "accession", "size": 1, "format": "json"}
        uresp = requests.get(UNIPROT_SEARCH_URL, params=uparams,
                             timeout=(cfg.timeout_seconds if cfg else 15))
        uresp.raise_for_status()
        udata = uresp.json()
        if not udata.get("results"):
            return []
        accession = udata["results"][0]["primaryAccession"]

        # 2. Get PDB cross-references from UniProt
        xref_url = f"{UNIPROT_XREF_URL}/{accession}/database/PDB"
        xresp = requests.get(xref_url, timeout=(cfg.timeout_seconds if cfg else 15))
        xresp.raise_for_status()
        xdata = xresp.json()

        pdb_ids = []
        for item in xdata.get("results", []):
            if "id" in item:
                pdb_ids.append(item["id"])
        if pdb_ids:
            return pdb_ids[:max_hits]
    except Exception as e:
        log.error("UniProt cross-ref lookup failed for %s: %s", query, e)
    return []


def fetch_entry_summary(pdb_id: str,
                        cfg: Optional[HttpConfig] = None) -> Optional[Dict]:
    """
    Fetch metadata summary for a given PDB entry.
    """
    cfg = cfg or HttpConfig()
    sess = make_session(cfg)

    url = f"{SUMMARY_URL}/{pdb_id}"
    try:
        return get_json(url, session=sess, cfg=cfg)
    except Exception as e:
        log.error("Failed to fetch summary for %s: %s", pdb_id, str(e))
        return None


def fetch_pdb_file(pdb_id: str,
                   cfg: Optional[HttpConfig] = None) -> Optional[str]:
    """
    Download a PDB structure file as text.
    """
    cfg = cfg or HttpConfig()
    sess = make_session(cfg)

    url = f"{PDB_FILE_URL}/{pdb_id}.pdb"
    try:
        return get_text(url, session=sess, cfg=cfg)
    except Exception as e:
        log.error("Failed to fetch PDB file for %s: %s", pdb_id, str(e))
        return None


# NEW: Label Parsing

def parse_pdb_metadata(pdb_text: str) -> Dict[str, Any]:
    """
    Parse chain and residue labels from a PDB file text.
    Returns a dict with chain IDs and residue identifiers.
    """
    chains = set()
    residues = []

    if not pdb_text:
        return {"chains": [], "residues": []}

    for line in pdb_text.splitlines():
        if line.startswith("ATOM") or line.startswith("HETATM"):
            chain_id = line[21].strip() or "?"
            res_name = line[17:20].strip()
            res_seq = line[22:26].strip()
            residue_label = f"{res_name}{res_seq}:{chain_id}"

            chains.add(chain_id)
            residues.append(residue_label)

    return {
        "chains": sorted(list(chains)),
        "residues": residues
    }


def fetch_pdb_with_labels(pdb_id: str,
                          cfg: Optional[HttpConfig] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch a PDB file and return both raw text and parsed labels.
    """
    pdb_text = fetch_pdb_file(pdb_id, cfg=cfg)
    if not pdb_text:
        return None

    labels = parse_pdb_metadata(pdb_text)
    return {
        "pdb_id": pdb_id,
        "pdb_text": pdb_text,
        "chains": labels["chains"],
        "residues": labels["residues"],
    }