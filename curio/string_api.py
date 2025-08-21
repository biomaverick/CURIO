from __future__ import annotations
from typing import List, Dict, Optional

from .net_utils import get_json, HttpConfig, make_session
from . import get_logger

log = get_logger("string")

BASE = "https://string-db.org/api/json"


def fetch_interactions(
    gene: str,
    species: int = 9606,
    limit: int = 20,
    cfg: Optional[HttpConfig] = None
) -> List[Dict]:
    """Fetch protein-protein interactions for a given gene from STRING-DB.

    Args:
        gene: Protein name or gene symbol (e.g., "TP53").
        species: NCBI taxonomy ID (default: 9606 = human).
        limit: Max number of interactions to return.
        cfg: Optional HttpConfig.

    Returns:
        A list of interaction records with scores and partner info.
    """
    cfg = cfg or HttpConfig()
    sess = make_session(cfg)
    url = f"{BASE}/network"
    params = {
        "identifiers": gene,
        "species": species,
        "limit": limit,
    }
    js = get_json(url, params=params, session=sess, cfg=cfg)
    if not js:
        log.warning("No STRING data for %s (species %s)", gene, species)
    else:
        log.info("STRING fetched %d interactions for %s", len(js), gene)
    return js or []