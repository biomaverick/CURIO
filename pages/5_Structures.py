# pages/5_Structures.py
from __future__ import annotations

import re
from typing import Dict, List

import streamlit as st
import streamlit.components.v1 as components
import requests
from curio.structure_api import (
    resolve_query_to_pdb_ids,  # str -> List[str] (PDB IDs)
    fetch_entry_summary,       # pdb_id -> dict | None
    fetch_pdb_file             # pdb_id -> str (PDB text) | None
)
from curio.net_utils import HttpConfig
from curio import __version__ as curio_version

# Page setup
st.set_page_config(page_title="Protein Structures", page_icon="🧬", layout="wide")
st.title("RCSB Protein Structure Search")

# HTTP config
cfg = HttpConfig(timeout_seconds=20)
cfg.headers["User-Agent"] = f"CURIO/structures v{curio_version}"

# Query input
st.markdown(
    "Search by **PDB ID** (e.g., `7JXH`)."
)
with st.container():
    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Query", placeholder="PDB ID like 1CRN")
    with c2:
        run = st.button("Search", use_container_width=True)

# Helper: compact one-line summary for a PDB entry
def _compact_summary_for_list(js: dict) -> str:
    title = js.get("struct", {}).get("title", "")
    exptl = js.get("exptl") or []
    method = ", ".join([e.get("method", "") for e in exptl if e.get("method")]) or "—"

    info = js.get("rcsb_entry_info", {}) or {}
    res = info.get("resolution_combined") or []
    res_txt = ", ".join([f"{r:.2f} Å" if isinstance(r, (int, float)) else str(r) for r in res]) or "—"

    acc = js.get("rcsb_accession_info", {}) or {}
    rel = acc.get("initial_release_date", "—")

    return f"{method} • {res_txt} • {rel} • {title[:80]}"

# Helper:block summary under the chooser
def _rich_summary_block(js: dict) -> str:
    lines: List[str] = []
    title = js.get("struct", {}).get("title")
    if title:
        lines.append(f"**Title:** {title}")

    exptl = js.get("exptl") or []
    if exptl:
        methods = ", ".join([e.get("method", "") for e in exptl if e.get("method")])
        if methods:
            lines.append(f"**Experimental method:** {methods}")

    info = js.get("rcsb_entry_info", {}) or {}
    res = info.get("resolution_combined") or []
    if res:
        res_txt = ", ".join([f"{r:.2f} Å" if isinstance(r, (int, float)) else str(r) for r in res])
        lines.append(f"**Resolution:** {res_txt}")
    for key, label in [
        ("polymer_entity_count_protein", "Protein chains"),
        ("polymer_entity_count_dna", "DNA chains"),
        ("polymer_entity_count_rna", "RNA chains"),
    ]:
        if key in info:
            lines.append(f"**{label}:** {info.get(key)}")

    acc = js.get("rcsb_accession_info", {}) or {}
    if "deposit_date" in acc:
        lines.append(f"**Deposited:** {acc['deposit_date']}")
    if "initial_release_date" in acc:
        lines.append(f"**Released:** {acc['initial_release_date']}")

    return "\n".join(lines) if lines else "_No summary details available._"

# RESULTS STATE
if "rcsb_candidates" not in st.session_state:
    st.session_state.rcsb_candidates = []
if "rcsb_meta" not in st.session_state:
    st.session_state.rcsb_meta = {}
if "rcsb_chosen" not in st.session_state:
    st.session_state.rcsb_chosen = None

# Search action
if run:
    st.session_state.rcsb_candidates = []
    st.session_state.rcsb_meta = {}
    st.session_state.rcsb_chosen = None

    q = (query or "").strip()
    if not q:
        st.warning("Please enter a query.")
    else:
        with st.spinner(f"Searching RCSB for `{q}`…"):
            ids = resolve_query_to_pdb_ids(q, max_hits=12, cfg=cfg)

        if not ids:
            st.error("No results found. Try a different query.")
        else:
            st.session_state.rcsb_candidates = ids
            with st.spinner("Fetching entry metadata…"):
                meta: Dict[str, dict] = {}
                for pid in ids:
                    try:
                        js = fetch_entry_summary(pid, cfg=cfg)
                        if js:
                            meta[pid] = js
                    except Exception:
                        pass
                st.session_state.rcsb_meta = meta

# Candidates section
cands = st.session_state.rcsb_candidates
meta = st.session_state.rcsb_meta

if cands:
    st.markdown("### Results")
    labeled = []
    for pid in cands:
        if pid in meta:
            labeled.append((pid, f"{pid} — {_compact_summary_for_list(meta[pid])}"))
        else:
            labeled.append((pid, pid))

    label_map = {lab: pid for pid, lab in labeled}
    label_list = [lab for _, lab in labeled]
    chosen_label = st.selectbox("Select a structure to view:", label_list, index=0)
    chosen_pid = label_map.get(chosen_label)
    st.session_state.rcsb_chosen = chosen_pid

    if meta:
        import pandas as pd
        rows = []
        for pid in cands:
            js = meta.get(pid, {})
            title = js.get("struct", {}).get("title", "—")
            methods = ", ".join([e.get("method", "") for e in (js.get("exptl") or []) if e.get("method")]) or "—"
            info = js.get("rcsb_entry_info", {}) or {}
            res = info.get("resolution_combined") or []
            res_txt = ", ".join([f"{r:.2f} Å" if isinstance(r, (int, float)) else str(r) for r in res]) or "—"
            rel = (js.get("rcsb_accession_info") or {}).get("initial_release_date", "—")
            rows.append({
                "PDB ID": pid,
                "Method": methods,
                "Resolution": res_txt,
                "Released": rel,
                "Title": title[:120]
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# Show chosen entry summary + viewer
pid = st.session_state.get("rcsb_chosen")
if pid:
    st.markdown("---")
    st.subheader(f"Structure: {pid}")

    summary = meta.get(pid)
    if not summary:
        with st.spinner(f"Fetching summary for {pid}…"):
            try:
                summary = fetch_entry_summary(pid, cfg=cfg)
                if summary:
                    st.session_state.rcsb_meta[pid] = summary
            except Exception:
                summary = None

    if summary:
        st.markdown(_rich_summary_block(summary))
    else:
        st.warning("No summary available for this entry.")

    # Official RCSB tabs
    st.markdown("#### Explore Structure (RCSB)")

    tab1, tab2, tab3, tab4 = st.tabs(["3D View", "Sequence", "Annotations", "Interactions"])

    with tab1:
        viewer_url = f"https://www.rcsb.org/3d-view/{pid}"
        components.iframe(viewer_url, height=800, width="100%", scrolling=True)

    with tab2:
        seq_url = f"https://www.rcsb.org/fasta/entry/{pid}"
        components.iframe(seq_url, height=800, width="100%", scrolling=True)

    with tab3:
        annot_url = f"https://www.rcsb.org/structure/{pid}"
        components.iframe(annot_url, height=800, width="100%", scrolling=True)

    with tab4:
        inter_url = f"https://www.rcsb.org/structure/{pid}#interactions"
        components.iframe(inter_url, height=800, width="100%", scrolling=True)

    # Download PDB
    with st.spinner(f"Fetching PDB file for {pid}…"):
        pdb_text = None
        try:
            pdb_text = fetch_pdb_file(pid, cfg=cfg)
        except Exception:
            pdb_text = None

    if pdb_text:
        st.download_button(
            label=f"Download {pid}.pdb",
            data=pdb_text.encode("utf-8"),
            file_name=f"{pid}.pdb",
            mime="chemical/x-pdb",
            use_container_width=True
        )
      # Save chosen structure summary into session for reports
    if summary:
        st.session_state["pdb"] = summary
