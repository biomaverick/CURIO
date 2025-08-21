# tests/test_apis.py
import pytest
from unittest.mock import patch

from curio import (
    kegg_api,
    ncbi_gene_api,
    pubmed_api,
    reactome_api,
    string_api,
    structure_api,
    uniprot_api,
)

# KEGG API (mocked)
@patch("curio.kegg_api.get_text", return_value="hsa:7157\tTP53\n")
def test_kegg_find_gene(mock_get):
    results = kegg_api.find_kegg_gene("TP53")
    assert results == ["hsa:7157"]


@patch("curio.kegg_api.get_text", return_value="ENTRY       hsa:7157\nNAME        TP53")
def test_kegg_entry(mock_get):
    entry = kegg_api.get_kegg_entry("hsa:7157")
    assert "TP53" in entry


@patch("requests.get")
def test_kegg_pathways(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "hsa:7157\tpath:hsa04115\n"
    pathways = kegg_api.get_gene_pathways("hsa:7157")
    assert pathways == ["hsa04115"]

# NCBI Gene API (mocked)
@patch("curio.ncbi_gene_api._esearch", return_value="7157")
@patch("curio.ncbi_gene_api._esummary", return_value={"uid": "7157", "name": "TP53", "description": "tumor protein"})
def test_ncbi_gene_entry(mock_summary, mock_search):
    result = ncbi_gene_api.fetch_ncbi_entry("TP53", db="gene", output="json")
    assert result["Symbol"] == "TP53"


@patch("curio.ncbi_gene_api.fetch_ncbi_entry", side_effect=[{"Symbol": "TP53"}, {"Symbol": "APP"}])
def test_ncbi_batch(mock_fetch):
    result = ncbi_gene_api.fetch_ncbi_batch(["TP53", "APP"])
    assert "TP53" in result and "APP" in result

# PubMed API (mocked)
@patch("curio.pubmed_api.get_json")
def test_pubmed_search_and_summary(mock_get_json):
    mock_get_json.return_value = {"esearchresult": {"idlist": ["12345", "67890"]}}
    pmids = pubmed_api.search_pubmed("TP53", retmax=2)
    assert pmids == ["12345", "67890"]

    mock_get_json.return_value = {
        "result": {
            "12345": {"title": "Test Article", "fulljournalname": "Nature", "sortpubdate": "2020"},
            "67890": {"title": "Another Article", "source": "Science", "pubdate": "2019"},
        }
    }
    summaries = pubmed_api.fetch_pubmed_summaries(["12345", "67890"])
    assert summaries[0]["title"] == "Test Article"


@patch("curio.pubmed_api.get_text", return_value="<AbstractText>Mock abstract</AbstractText>")
def test_pubmed_abstract_and_keywords(mock_get_text):
    abstract = pubmed_api.fetch_pubmed_abstract("12345")
    assert "Mock abstract" in abstract

    keywords = pubmed_api.extract_keywords([abstract], topk=5)
    assert ("mock", 1) in keywords

# Reactome API
def test_reactome_embed_url():
    url = reactome_api.embed_url_for_gene("TP53")
    assert "TP53" in url and url.startswith("https://reactome.org")

# STRING API (mocked)
@patch("curio.string_api.get_json", return_value=[{"preferredName": "TP53", "stringId": "9606.ENSP00000269305"}])
def test_string_interactions(mock_get_json):
    results = string_api.fetch_interactions("TP53")
    assert results[0]["preferredName"] == "TP53"

# Structure API (mocked)
@patch("requests.post")
def test_structure_resolve_query(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"result_set": [{"identifier": "1TUP"}]}
    pdb_ids = structure_api.resolve_query_to_pdb_ids("p53")
    assert "1TUP" in pdb_ids


@patch("curio.structure_api.get_json", return_value={"struct": {"title": "p53 protein"}})
def test_structure_entry_summary(mock_get_json):
    summary = structure_api.fetch_entry_summary("1TUP")
    assert "struct" in summary


@patch("curio.structure_api.get_text", return_value="ATOM      1  N   MET A   1")
def test_structure_fetch_and_parse(mock_get_text):
    pdb_text = structure_api.fetch_pdb_file("1TUP")
    meta = structure_api.parse_pdb_metadata(pdb_text)
    assert "chains" in meta and "residues" in meta

    labeled = structure_api.fetch_pdb_with_labels("1TUP")
    assert labeled["pdb_id"] == "1TUP"

# UniProt API (mocked)
@patch("requests.get")
def test_uniprot_entry(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "primaryAccession": "P04637",
        "genes": [{"geneName": {"value": "TP53"}}],
        "proteinDescription": {"recommendedName": {"fullName": {"value": "Cellular tumor antigen p53"}}},
        "organism": {"scientificName": "Homo sapiens"},
        "sequence": {"length": 393, "value": "MEEPQSDPSV..."},
        "uniProtKBCrossReferences": [],
        "comments": [],
    }
    result = uniprot_api.fetch_uniprot_entry("TP53")
    assert result["Gene Name"] == "TP53"


@patch("curio.uniprot_api.fetch_uniprot_entry", side_effect=[{"Gene Name": "TP53"}, {"Gene Name": "APP"}])
def test_uniprot_batch(mock_fetch):
    results = uniprot_api.fetch_uniprot_batch(["TP53", "APP"])
    assert "TP53" in results and "APP" in results
