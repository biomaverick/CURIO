# pages/3_NCBI_Search.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st   

from curio.ncbi_gene_api import fetch_ncbi_entry, fetch_ncbi_batch

st.set_page_config(page_title="NCBI Search", page_icon="🧬", layout="wide")

st.title("NCBI Search")
st.markdown("Query **NCBI Gene, Protein, or Nucleotide** databases. Supports JSON metadata, FASTA sequences, and GenBank text.")

# Sidebar controls
st.sidebar.header("Search Options")
db_choice = st.sidebar.selectbox("Database", ["gene", "protein", "nucleotide"])
organism = st.sidebar.text_input("Organism", "Homo sapiens")
output_format = st.sidebar.radio("Output Format", ["json", "fasta", "txt"], horizontal=True)

# Main query input
query_input = st.text_area(
    "Enter NCBI identifiers or gene names (one per line)",
    "APP\nNP_000475.1\nNM_000546"
)

if st.button("Search"):
    queries = [q.strip() for q in query_input.splitlines() if q.strip()]
    if not queries:
        st.warning("Please enter at least one identifier or gene name.")
    else:
        with st.spinner(f"Fetching results from NCBI ({db_choice})..."):
            if len(queries) == 1:
                results = {queries[0]: fetch_ncbi_entry(
                    queries[0], db=db_choice, organism=organism, output=output_format
                )}
            else:
                results = fetch_ncbi_batch(
                    queries, db=db_choice, organism=organism, output=output_format
                )
                st.session_state["ncbi_gene"] = results

        st.success(f"Retrieved {sum(v is not None for v in results.values())} / {len(results)} results")

        # Display results
        for identifier, result in results.items():
            st.markdown("---")
            st.subheader(f"{identifier}")

            if result is None:
                st.error("No entry found.")
                continue

            if output_format == "json":
                with st.expander("Entry Details", expanded=True):
                    for key, value in result.items():
                        if isinstance(value, list):
                            st.markdown(f"**{key}:**")
                            st.write("\n".join(value) if value else "—")
                        else:
                            st.markdown(f"**{key}:** {value}")
            else:
                with st.expander("Raw Output", expanded=True):
                    st.text_area("Result", result, height=300)
                st.download_button(
                    f"⬇️ Download {output_format.upper()}",
                    result,
                    file_name=f"{identifier}.{output_format}"
                )