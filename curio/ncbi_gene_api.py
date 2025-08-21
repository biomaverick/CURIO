# curio/ncbi_api.py
import requests
from typing import Dict, List, Optional

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

HEADERS = {"User-Agent": "CURIO_Dashboard/1.0"}

def _esearch(identifier: str, db: str, organism: str = "Homo sapiens") -> Optional[str]:
    """Search NCBI and return the first UID (ID)."""
    query = f"{identifier}[All Fields] AND {organism}[Organism]"
    url = f"{NCBI_BASE}esearch.fcgi?db={db}&term={query}&retmode=json"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code != 200:
        return None
    data = resp.json()
    ids = data.get("esearchresult", {}).get("idlist", [])
    return ids[0] if ids else None


def _esummary(uid: str, db: str) -> Dict:
    """Fetch summary info for a UID."""
    url = f"{NCBI_BASE}esummary.fcgi?db={db}&id={uid}&retmode=json"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.json().get("result", {}).get(uid, {})


def _efetch(uid: str, db: str, rettype: str) -> str:
    """Fetch raw data (FASTA, GenBank, etc.)."""
    url = f"{NCBI_BASE}efetch.fcgi?db={db}&id={uid}&rettype={rettype}&retmode=text"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def fetch_ncbi_entry(identifier: str, db: str = "gene", organism: str = "Homo sapiens", output: str = "json"):
    """
    Fetch an NCBI entry by identifier (gene/protein/nucleotide).
    output = 'json' | 'fasta' | 'txt'
    """
    uid = _esearch(identifier, db=db, organism=organism)
    if not uid:
        return None

    if output == "json":
        summary = _esummary(uid, db)
        if db == "gene":
            return {
                "Gene ID": summary.get("uid", uid),
                "Symbol": summary.get("name"),
                "Description": summary.get("description"),
                "Organism": summary.get("organism", {}).get("scientificname"),
                "Chromosome": summary.get("chromosome"),
                "Map Location": summary.get("maplocation"),
                "Other Designations": summary.get("otherdesignations", []),
            }
        else:
            # proteins/nucleotide: minimal metadata
            return {
                "ID": uid,
                "Title": summary.get("title"),
                "Length": summary.get("slen"),
                "Molecule Type": summary.get("moltype"),
            }
    elif output == "fasta":
        return _efetch(uid, db=db, rettype="fasta")
    else:  # GenBank / flatfile
        return _efetch(uid, db=db, rettype="gb")


def fetch_ncbi_batch(identifiers: List[str], db: str = "gene", organism: str = "Homo sapiens", output: str = "json") -> Dict[str, Optional[Dict]]:
    """Fetch multiple NCBI entries in batch."""
    results = {}
    for ident in identifiers:
        ident = ident.strip()
        if not ident:
            continue
        try:
            results[ident] = fetch_ncbi_entry(ident, db=db, organism=organism, output=output)
        except Exception:
            results[ident] = None
    return results


# Manual test
if __name__ == "__main__":
    print(fetch_ncbi_entry("APP", db="gene", output="json"))
    print(fetch_ncbi_entry("NP_000475.1", db="protein", output="fasta")[:200])