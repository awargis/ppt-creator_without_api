import streamlit as st

def render_counts(subject_counts: dict[str, int]):
    st.subheader("Subject-wise Question Extraction")
    st.table([{"Subject": s, "Questions Extracted": c} for s, c in subject_counts.items()])
