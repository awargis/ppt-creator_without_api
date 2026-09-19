import streamlit as st
from config import get_subjects

def render_sidebar():
    st.sidebar.header("⚙️ Configuration")
    exam_type = st.sidebar.selectbox("Exam Type", ["JEE Main", "JEE Advanced", "NEET UG"])
    
    st.sidebar.subheader("📐 Adjustable Crop Dimensions")
    st.sidebar.markdown("*Fine-tune these if options are being cut off.*")
    pad_x = st.sidebar.slider("Horizontal Margin (Left/Right)", 0, 80, 25)
    pad_y = st.sidebar.slider("Vertical Spacing (Top/Bottom)", 0, 80, 15)

    return {
        "exam_type": exam_type,
        "subjects": get_subjects(exam_type),
        "pad_x": pad_x,
        "pad_y": pad_y,
        "render_dpi": 300
    }
