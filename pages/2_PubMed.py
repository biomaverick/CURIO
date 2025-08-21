from __future__ import annotations
import io
import json
import requests
from pathlib import Path

import pandas as pd
import streamlit as st

from curio.pubmed_api import (
    search_pubmed,
    fetch_pubmed_summaries,
    fetch_pubmed_abstract,
    plot_trend,
    extract_keywords,
)
from curio.net_utils import HttpConfig
from curio import __version__ as curio_version

st.set_page_config(page_title="PubMed — Literature Search", page_icon="📚", layout="wide")
st.title("PubMed — Literature Search")

# Session settings (fallbacks)
default_years = st.session_state.get("settings", {}).get("trend_years", 10)
timeout_seconds = st.session_state.get("settings", {}).get("timeout_seconds", 20)

# Controls
colq1, colq2, colq3 = st.columns([4, 2, 2])
with colq1:
    query = st.text_input("Query", "")
with colq2:
    sample = st.selectbox(
        "Sample query (optional)",
        ["", "TP53 AND cancer", "BRCA1 AND DNA repair"],
        index=0,
    )
with colq3:
    years = st.number_input("Trend window (years)", min_value=3, max_value=30, value=int(default_years), step=1)

c1, c2, c3 = st.columns([1, 1, 1])
run_custom = c1.button("Run")
run_sample = c2.button("Run Sample Query")
test_button = c3.button("Test Connection")

# Test Connection (UI-only; minimal unauth call; avoid logging via our net utils)
if test_button:
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi",
            params={"db": "pubmed", "retmode": "json"},
            timeout=8,
            headers={"User-Agent": f"CURIO/{curio_version} (test)"},
        )
        ok = (r.status_code == 200)
        st.success("PubMed reachable" if ok else "PubMed unreachable")
    except Exception as e:
        st.error(f"PubMed unreachable: {e}")

# Decide query
final_query = None
if run_custom and query.strip():
    final_query = query.strip()
elif run_sample and sample:
    final_query = sample

# Results area
if final_query:
    cfg = HttpConfig(timeout_seconds=timeout_seconds)
    with st.spinner("Searching PubMed…"):
        pmids = search_pubmed(final_query, cfg=cfg)

    if not pmids:
        st.warning("No results found.")
    else:
        summaries = fetch_pubmed_summaries(pmids[:200], cfg=cfg)
        st.session_state["pubmed"] = summaries

        # Show table
        df = pd.DataFrame(summaries)
        st.subheader("Results")
        st.dataframe(df, use_container_width=True)

        # Downloads
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_buf.getvalue().encode("utf-8"),
            file_name="pubmed_results.csv",
            mime="text/csv",
        )

        # Trend plot
        st.subheader("Trend")
        fig = plot_trend(summaries, years=int(years))
        st.pyplot(fig, use_container_width=True)

        # Fetch a few abstracts for keywords
        st.subheader("Top keywords")
        top_n = st.slider("Number of abstracts to scan", 5, min(25, len(pmids)), 10)
        abstracts = []
        with st.spinner("Fetching abstracts…"):
            for pid in pmids[:top_n]:
                try:
                    abstracts.append(fetch_pubmed_abstract(pid, cfg=cfg))
                except Exception:
                    pass
        kw = extract_keywords(abstracts, topk=25)
        if kw:
            st.write(", ".join(f"`{k}` ({v})" for k, v in kw))
        else:
            st.info("No keywords extracted.")

# Debug log viewer (visible when global toggle is on)
if st.session_state.get("settings", {}).get("show_debug", False):
    from curio import get_logger
    log_path = Path(__file__).resolve().parents[1] / "curio" / "logs" / "curio.log"
    with st.expander("Debug logs (last 100 lines)"):
        try:
            txt = log_path.read_text(encoding="utf-8").splitlines()[-100:]
            st.code("\n".join(txt), language="text")
        except Exception as e:
            st.info(f"No logs yet or cannot read: {e}")