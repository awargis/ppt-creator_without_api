import streamlit as st

def render_uploads():
    return (st.file_uploader("Question paper PDF", type=["pdf"]), st.file_uploader("PPT template", type=["pptx"]), st.text_area("Answer key", placeholder="1: A\n2: B"))
