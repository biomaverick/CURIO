from __future__ import annotations
import requests
import streamlit as st
from pathlib import Path

from curio.reactome_api import embed_url_for_gene
from curio import __version__ as curio_version

st.set_page_config(page_title="Reactome — Pathways", page_icon="🧭", layout="wide")
st.title("Reactome — Pathway Browser")

# Controls
c1, c2, c3 = st.columns([3, 2, 1])
with c1:
    gene = st.text_input("Gene symbol", "")
with c2:
    species = st.text_input("Species", "Homo sapiens")
with c3:
    sample = st.selectbox("Sample (optional)", ["", "TP53", "BRCA1"], index=0)

b1, b2, b3 = st.columns([1, 1, 1])
run_custom = b1.button("Open in Reactome")
run_sample = b2.button("Run Sample Query")
test_button = b3.button("Test Connection")

# Test Connection (UI-only; no persistent logging)
if test_button:
    try:
        r = requests.get(
            "https://reactome.org/ContentService/data/database/info",
            timeout=8,
            headers={"User-Agent": f"CURIO/{curio_version} (test)"}
        )
        st.success("Reactome reachable" if r.status_code == 200 else "Reactome unreachable")
    except Exception as e:
        st.error(f"Reactome unreachable: {e}")

# Determine input
final_gene = None
if run_custom and gene.strip():
    final_gene = gene.strip()
elif run_sample and sample:
    final_gene = sample

# Results
if final_gene:
    try:
        url = embed_url_for_gene(final_gene, species or "Homo sapiens")
        st.session_state["reactome"] = url
        st.caption(f"Embed URL: {url}")
        st.components.v1.iframe(url, height=650)
    except Exception as e:
        st.error(f"Failed to build Reactome embed: {e}")

# Debug logs (visible when global toggle is on)
if st.session_state.get("settings", {}).get("show_debug", False):
    log_path = Path(__file__).resolve().parents[1] / "curio" / "logs" / "curio.log"
    with st.expander(" \Debug logs (last 100 lines)"):
        try:
            txt = log_path.read_text(encoding="utf-8").splitlines()[-100:]
            st.code("\n".join(txt), language="text")
        except Exception as e:
            st.info(f"No logs yet or cannot read: {e}")