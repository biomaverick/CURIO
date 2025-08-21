# curio/uniprot_api.py

import requests
import re
from typing import Dict, List, Optional, Union

BASE_URL = "https://rest.uniprot.org/uniprotkb"

HEADERS = {"User-Agent": "CURIO_Dashboard/1.0"}


def fetch_uniprot_entry(
    identifier: str,
    organism: str = "Homo sapiens",
    output: str = "json"
) -> Optional[Union[Dict, str]]:
    """
    Fetch a UniProt entry by accession or gene name.

    Args:
        identifier (str): UniProt accession or gene name
        organism (str): organism name to restrict search
        output (str): "json", "fasta", or "txt"

    Returns:
        Dict if output="json", str otherwise.
    """
    identifier = identifier.strip()
    organism = organism.strip()

    # Check if accession number format (O/P/Q followed by pattern)
    is_accession = re.match(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$", identifier.upper()) is not None

    # Build URL depending on mode
    if is_accession:
        url = f"{BASE_URL}/{identifier}?format={output}"
    else:
        query = f'gene_exact:"{identifier.replace(" ", "")}" AND organism_name:"{organism}"'
        url = f"{BASE_URL}/search?query={query}&format={output}&size=50"

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 404:
            return None
        elif response.status_code != 200:
            return None
    except requests.exceptions.RequestException:
        return None

    if output == "json":
        data = response.json()
        if is_accession:
            return parse_uniprot_entry(data)
        elif data.get("results"):
            # Pick exact gene match
            for entry in data["results"]:
                gene_name = entry.get("genes", [{}])[0].get("geneName", {}).get("value", "").upper()
                if gene_name == identifier.replace(" ", "").upper():
                    return parse_uniprot_entry(entry)
            return None
        else:
            return None
    else:
        # FASTA or TXT returns raw string
        return response.text


def fetch_uniprot_batch(
    identifiers: List[str],
    organism: str = "Homo sapiens",
    output: str = "json"
) -> Dict[str, Optional[Union[Dict, str]]]:
    """
    Handle batch queries to UniProt.

    Args:
        identifiers (List[str]): list of accessions or gene names
        organism (str): organism name
        output (str): "json", "fasta", "txt"

    Returns:
        Dict mapping identifier -> result
    """
    results = {}
    for identifier in identifiers:
        results[identifier] = fetch_uniprot_entry(identifier, organism, output)
    return results


def parse_uniprot_entry(entry: Dict) -> Dict:
    """
    Parse a UniProt JSON entry into a structured dict.
    """
    try:
        go_terms = {"Biological Process": [], "Molecular Function": [], "Cellular Component": []}

        for ref in entry.get("uniProtKBCrossReferences", []):
            if ref.get("database") == "GO":
                go_id = ref.get("id", "")
                for prop in ref.get("properties", []):
                    term = prop.get("value", "")
                    if term.startswith("P:"):
                        go_terms["Biological Process"].append(f"{go_id} ({term[2:]})")
                    elif term.startswith("F:"):
                        go_terms["Molecular Function"].append(f"{go_id} ({term[2:]})")
                    elif term.startswith("C:"):
                        go_terms["Cellular Component"].append(f"{go_id} ({term[2:]})")

        subcellular_locations = []
        for comment in entry.get("comments", []):
            if comment.get("commentType") == "SUBCELLULAR LOCATION":
                for loc in comment.get("subcellularLocations", []):
                    parts = [
                        loc.get("location", {}).get("value"),
                        loc.get("topology", {}).get("value"),
                        loc.get("orientation", {}).get("value"),
                    ]
                    loc_string = ", ".join([p for p in parts if p])
                    if loc_string:
                        subcellular_locations.append(loc_string)

        return {
            "Gene Name": entry.get("genes", [{}])[0].get("geneName", {}).get("value", "N/A"),
            "UniProt ID": entry.get("primaryAccession", "N/A"),
            "Protein Name": (
                entry.get("proteinDescription", {})
                .get("recommendedName", {})
                .get("fullName", {})
                .get("value", "N/A")
            ),
            "Organism": entry.get("organism", {}).get("scientificName", "N/A"),
            "Length": entry.get("sequence", {}).get("length", "N/A"),
            "Sequence": entry.get("sequence", {}).get("value", "N/A"),
            "GO: Biological Process": go_terms["Biological Process"],
            "GO: Molecular Function": go_terms["Molecular Function"],
            "GO: Cellular Component": go_terms["Cellular Component"],
            "Subcellular Localization": subcellular_locations,
        }
    except Exception:
        return {}


# Quick test
if __name__ == "__main__":
    test_ids = ["TPH1", "APP", "Q9Y261"]
    results = fetch_uniprot_batch(test_ids, organism="Homo sapiens", output="json")
    for k, v in results.items():
        print(f"\n{k}: {v.get('Protein Name') if v else 'Not found'}")