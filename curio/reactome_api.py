from __future__ import annotations
from urllib.parse import quote_plus

from . import get_logger

log = get_logger("reactome")


def embed_url_for_gene(gene: str, species: str = "Homo sapiens") -> str:
    """Return a safe Reactome PathwayBrowser embed URL for a gene/species.

    Args:
        gene: Gene symbol (e.g., "TP53").
        species: Species name (e.g., "Homo sapiens").

    Returns:
        A fully-formed HTTPS URL suitable for embedding in an iframe.
    """
    g = (gene or "").strip()
    s = (species or "Homo sapiens").strip()
    if not g:
        raise ValueError("Gene symbol is required for Reactome embed URL.")
    url = f"https://reactome.org/PathwayBrowser/#?q={quote_plus(g)}&species={quote_plus(s)}"
    log.info("Reactome embed URL for %s/%s -> %s", g, s, url)
    return url