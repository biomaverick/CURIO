from __future__ import annotations
import streamlit as st
import datetime as dt
from curio.report import build_report, build_pdf

# Page Configuration
st.set_page_config(page_title="Reports", page_icon="📑", layout="wide")
st.title("CURIO Report Generator")

st.info("This report is automatically generated from the searches you performed across the modules.")

# Mapping: session keys → display names
MODULE_KEYS = {
    "uniprot": "UniProt",
    "ncbi_gene": "NCBI Gene",
    "pubmed": "PubMed",
    "kegg": "KEGG",
    "reactome": "Reactome",
    "string": "STRING",
    "pdb": "PDB",
}

# Collect results dynamically
sections = {}
for key, label in MODULE_KEYS.items():
    if key in st.session_state and st.session_state[key]:
        sections[label] = st.session_state[key]

# Build report if data exists
if sections:
    content = {
        "title": "CURIO Analysis Report",
        "author": "CURIO Dashboard",
        "date": dt.date.today().isoformat(),
        "sections": sections,
    }

    html = build_report(content)
    pdf_bytes = build_pdf(content)

    st.success("Comprehensive Report Built")

    # Preview
    st.subheader("Report Preview")
    st.components.v1.html(html, height=600, scrolling=True)

    # Downloads
    st.download_button("⬇️ Download HTML", data=html, file_name="curio_report.html", mime="text/html")
    st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name="curio_report.pdf", mime="application/pdf")

else:
    st.warning("No module results found yet. Please run searches in UniProt, PubMed, NCBI Gene, etc. first.")