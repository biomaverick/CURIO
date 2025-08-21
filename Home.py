import streamlit as st
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="CURIO Bioinformatics Dashboard",
    page_icon="assets/curio_window.png",
    layout="wide"
)

# Session State Initialization
if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "default_organism": ("Homo sapiens", 9606),
        "timeout_seconds": 20,
        "show_debug": False,
        "trend_years": 10,
        "contact_email": "",
    }

if "curio" not in st.session_state:
    st.session_state["curio"] = {}
    
# Sidebar Logo
with st.sidebar:
    st.image("assets/CURIO_logo.png", use_container_width=True)  

# Page Header
st.markdown("<h1 style='text-align: center;'>CURIO</h1>", unsafe_allow_html=True)
st.caption(
    "A modular, integrated Streamlit dashboard for **UniProt**, **NCBI Gene**, "
    "**PubMed**, **KEGG**, **Reactome**, **RCSB PDB**, and **STRING**."
)

# Banner image
st.image("assets/CURIO.png", use_container_width=True)

# Welcome Section
st.markdown(
    """
    ### Welcome to **CURIO Bioinformatics Dashboard**

    CURIO is a **modular, interactive dashboard** designed to simplify access to 
    essential bioinformatics resources and streamline research workflows.
    """
)

# Key Features
st.markdown(
    """
    ---
    #### Key Features
    - **Unified Access** → Query major biological databases in one place:  
      *UniProt, NCBI Gene, PubMed, KEGG, Reactome, PDB Structures, STRING*
    - **Performance** → Optimized with caching, retries, and optional debug logging  
    - **Data Visualization** → Trend analysis, plots, and interactive tables for biological insights  
    - **Export Options** → Generate clean, publication-ready **reports** (HTML & PDF)  
    - **Modular Design** → Easily extendable with new APIs or tools  
    """
)

# Sidebar Navigation Hint
st.info("Use the sidebar to navigate between modules.", icon="➡️")

# Current Settings Panel
with st.expander("Current Settings"):
    s = st.session_state["settings"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Default organism", s["default_organism"][0])
    col2.metric("NCBI TaxId", s["default_organism"][1])
    col3.metric("Timeout (s)", s["timeout_seconds"])
    col4.metric("Trend years", s["trend_years"])
    
    st.write(f"Show debug logs: **{s['show_debug']}**")
    if s.get("contact_email"):
        st.write(f"Contact email in User-Agent: {s['contact_email']}")
