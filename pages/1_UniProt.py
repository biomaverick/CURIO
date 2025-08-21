# pages/2_UniProt_Search.py

import streamlit as st
from curio.uniprot_api import fetch_uniprot_entry, fetch_uniprot_batch

st.set_page_config(page_title="UniProt Search", page_icon="🔬", layout="wide")

st.title("UniProt Search")
st.markdown("Retrieve **UniProtKB entries** by accession or gene name. Supports JSON, FASTA, and text outputs.")

# Sidebar inputs
st.sidebar.header("Search Options")
organism = st.sidebar.text_input("Organism", "Homo sapiens")
output_format = st.sidebar.radio("Output Format", ["json", "fasta", "txt"], horizontal=True)

# Main input area
query_input = st.text_area(
    "Enter UniProt identifiers or gene names (one per line)",
    "APP\nTPH1\nQ9Y261"
)

if st.button("Search"):
    queries = [q.strip() for q in query_input.splitlines() if q.strip()]
    if not queries:
        st.warning("Please enter at least one identifier or gene name.")
    else:
        with st.spinner("Fetching results from UniProt..."):
            if len(queries) == 1:
                results = {queries[0]: fetch_uniprot_entry(queries[0], organism=organism, output=output_format)}
            else:
                results = fetch_uniprot_batch(queries, organism=organism, output=output_format)
                st.session_state["uniprot"] = results

        st.success(f"Retrieved {sum(v is not None for v in results.values())} / {len(results)} results")

        # Display results
        for identifier, result in results.items():
            st.markdown("---")
            st.subheader(f"{identifier}")

            if result is None:
                st.error("No entry found.")
                continue

            if output_format == "json":
                # Display parsed dict
                with st.expander("Full Entry", expanded=True):
                    for key, value in result.items():
                        if isinstance(value, list):
                            st.markdown(f"**{key}:**")
                            if value:
                                st.write("\n".join(value))
                            else:
                                st.write("—")
                        else:
                            st.markdown(f"**{key}:** {value}")

                # Sequence copy
                if "Sequence" in result and result["Sequence"] != "N/A":
                    st.text_area("Protein Sequence", result["Sequence"], height=150)
                    st.download_button("⬇️ Download Sequence (FASTA)", f">{identifier}\n{result['Sequence']}", file_name=f"{identifier}.fasta")

            else:
                # FASTA or TXT
                with st.expander("Raw Output", expanded=True):
                    st.text_area("Result", result, height=300)
                st.download_button(f"⬇️ Download {output_format.upper()}", result, file_name=f"{identifier}.{output_format}")