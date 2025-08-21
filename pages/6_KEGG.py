import streamlit as st
from curio import kegg_api

st.title("KEGG Pathway Explorer")

query = st.text_input("Enter gene name or ID (e.g., AKR1C3 or 5774)", "")
org = st.text_input("Organism code (default: hsa for human)", "hsa")

if query:
    genes = kegg_api.find_kegg_gene(query, org=org)

    if not genes:
        st.warning("No KEGG gene found.")
    else:
        selected_gene = st.selectbox("Select KEGG Gene ID", genes)

        if selected_gene:
            st.subheader(f"KEGG Entry: {selected_gene}")
            entry = kegg_api.get_kegg_entry(selected_gene)
            st.text_area("Raw KEGG entry", entry, height=200)

            st.subheader("KEGG Pathway Viewer")

            # Fetch all pathways for this gene
            pathways = kegg_api.get_gene_pathways(selected_gene)
            st.session_state["kegg"] = {
                "gene": selected_gene,
                "entry": entry,
                "pathways": pathways
            }


            if pathways:
                # Show dropdown to select pathway
                pathway_id = st.selectbox("Select a pathway", pathways)

                # Build KEGG pathway visualization URL
                pathway_url = f"https://www.kegg.jp/kegg-bin/show_pathway?{pathway_id}+{selected_gene}"

                # Embed pathway in an iframe
                st.markdown(
                    f'<iframe src="{pathway_url}" width="100%" height="600" frameborder="0"></iframe>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("No pathway found for this gene in KEGG.")