<p align="center">
  <img src="assets/CURIO.png" alt="CURIO Logo" width="200"/>
</p>

<h1 align="center">CURIO — Unified Bioinformatics Data Retrieval Dashboard</h1>

<p align="center">
  A Python bioinformatics toolkit and interactive dashboard integrating 
  <b>UniProt</b>, <b>NCBI Gene</b>, <b>PubMed</b>, <b>KEGG</b>, <b>STRING</b>, and <b>Reactome</b> APIs.
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python"/>
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Streamlit-App-red.svg" alt="Streamlit"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/>
  </a>
  <a href="https://github.com/biomaverick/CURIO/actions/workflows/tests.yml">
    <img src="https://github.com/biomaverick/CURIO/actions/workflows/tests.yml/badge.svg" alt="Tests"/>
  </a>
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat" alt="Contributions Welcome"/>
  </a>
</p>

---

## Overview  

**CURIO** is a **multi-API integrated bioinformatics dashboard** built with [Streamlit](https://streamlit.io/).  
It provides researchers with a **single interactive workspace** for querying multiple biological databases without juggling multiple scripts, APIs, or web portals.  
CURIO streamlines **data discovery, visualization, and reporting**, making it a useful tool for:  
- Molecular biologists exploring gene/protein function  
- Bioinformatics researchers integrating data across resources  
- Students learning to work with biological databases  
- Developers building pipelines that require consistent query endpoints  

---

## Key Features  

- **Unified Access** to major biological data sources:
  - **UniProt** — protein metadata, sequences, subcellular localization, GO annotations  
  - **PubMed** — publication search, metadata, and abstracts  
  - **NCBI Gene** — gene metadata by gene name or accession number  
  - **STRING** — protein–protein interaction networks  
  - **Reactome** — curated pathway exploration  
  - **Structures** — 3D protein models via AlphaFold & PDB with [3Dmol.js](https://3dmol.csb.pitt.edu/)  
  - **KEGG** — pathway visualizations  
- **Reporting Engine** — auto-generate publication-ready summaries in HTML/PDF  
- **Crash-resistant queries** — retries and error handling for unstable APIs  
- **Multipage dashboard** — modular Streamlit pages for each data source  
- **Extensible** — add your own APIs with minimal code changes  

---

## Installation  

```bash
# 1. Clone the repository
git clone https://github.com/biomaverick/curio.git
cd curio

# 2. Create a virtual environment
python3 -m venv curio_env
source curio_env/bin/activate   # Linux/macOS
curio_env\Scripts\activate      # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```
---

## Usage  

Launch the dashboard with:  

```bash
streamlit run Home.py
```

By default, it runs on: [http://localhost:8501](http://localhost:8501)  

Modules available from the sidebar:  
- **UniProt** – query proteins by accession or name  
- **NCBI Gene** – retrieve gene info and sequences  
- **PubMed** – fetch literature metadata  
- **STRING** – visualize interaction networks  
- **Reactome** – browse pathway maps  
- **KEGG** – explore pathway visualizations  
- **Structures** – load AlphaFold/PDB structures in 3D  
- **Report** – export queries as PDF/HTML  

---
## Example (API Usage as Python Library)

CURIO can also be used as a **Python package**, not just as a dashboard:

``` python
from curio import uniprot_api
result = uniprot_api.fetch_uniprot_entry("BACE1")
print(result)
```
---
## Project Scaffold  

```
curio/
│── Home.py                  # Streamlit entrypoint
│── curio/                  # Core Python package
│   │── __init__.py
│   │── uniprot_api.py
│   │── ncbi_gene_api.py
│   │── kegg_api.py
│   │── pubmed_api.py
│   │── reactome_api.py
│   │── string_api.py
│   │── structure_api.py
│   │── report.py
│   └── net_utils.py
│── pages/                  # Streamlit multipage system
│   │── 1_UniProt.py
│   │── 2_PubMed.py
│   │── ...
│── docs/                   # Documentation
│── tests/                  # Unit tests for APIs
│── examples/               # Sample queries (JSON)
│── requirements.txt
│── pyproject.toml / setup.py
│── LICENSE
│── README.md
```
---

## Testing  

Run the test suite:  

```bash
pytest tests/
```  
---

## Configuration  

- **Streamlit settings** → `.streamlit/config.toml`  
- **Logs** and **settings** → handled via `pages/9_Settings_&_Logs.py`  

---

## Future Roadmap  

- [ ] Docker support for reproducible deployment  
- [ ] REST API wrapper (so CURIO can be queried programmatically)  
- [ ] Advanced caching layer for faster queries  
- [ ] Export to Excel/CSV in addition to PDF/HTML  
- [ ] Plugin system for custom APIs  

---

## Contributing  
Contributions are welcome!  
- See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.  
- Please run tests before submitting pull requests.  

---
## License  
This project is licensed under the [MIT License](LICENSE).  

---
CURIO allows you to **query multiple biological databases in one place** — no more switching between UniProt, NCBI, PubMed, KEGG, STRING, or Reactome separately.  

---
## Authors

- [Debojyoti Chatterjee](https://github.com/biomaverick) — Creator & Maintainer  
- [Samiul Haque](https://github.com/samiowl) — Creator & Maintainer  

