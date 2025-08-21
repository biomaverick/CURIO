from __future__ import annotations
import pandas as pd
import streamlit as st
import networkx as nx
from pyvis.network import Network
from pathlib import Path

from curio.string_api import fetch_interactions
from curio.net_utils import HttpConfig

st.set_page_config(page_title="STRING — Interactions", page_icon="🕸️", layout="wide")
st.title("STRING — Protein Interaction Network")

# Controls
c1, c2, c3 = st.columns([3, 2, 1])
with c1:
    gene = st.text_input("Gene symbol", "")
with c2:
    tax_id = st.number_input("Taxonomy ID", value=9606, step=1)
with c3:
    limit = st.slider("Max interactions", min_value=5, max_value=50, value=20, step=5)

run_btn = st.button("Fetch STRING network")

if run_btn and gene.strip():
    cfg = HttpConfig(timeout_seconds=st.session_state.get("settings", {}).get("timeout_seconds", 20))
    with st.spinner("Fetching STRING interactions…"):
        data = fetch_interactions(gene.strip(), int(tax_id), limit=limit, cfg=cfg)
        st.session_state["string"] = data

    if not data:
        st.warning("No interactions found.")
    else:
        st.success(f"Fetched {len(data)} interactions")

        # Table view
        df = pd.DataFrame(data)
        st.dataframe(df[["preferredName_A", "preferredName_B", "score"]], use_container_width=True)

        # Build networkx graph
        G = nx.Graph()
        for row in data:
            a, b = row["preferredName_A"], row["preferredName_B"]
            score = row.get("score", 0.0)
            G.add_edge(a, b, weight=score)

        # Pyvis visualization
        net = Network(height="550px", width="100%", bgcolor="#ffffff", font_color="black")
        net.from_nx(G)
        net.repulsion(node_distance=150, spring_length=100)
        html_path = Path("string_net.html")
        net.save_graph(str(html_path))
        st.components.v1.html(html_path.read_text(encoding="utf-8"), height=600, scrolling=True)