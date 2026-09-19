import streamlit as st

def render_style():
    return st.sidebar.selectbox("Presentation style", ["Premium Light", "Premium Dark"])
