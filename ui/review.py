import streamlit as st

def render_review(regions):
    with st.expander("Review detected questions"):
        for region in regions:
            st.write(f"Q{region.number} · {region.subject} · confidence {region.confidence:.0%}")
            st.image(region.image, width=320)
