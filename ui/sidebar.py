import streamlit as st
from config import get_subjects


def render_sidebar():
    st.sidebar.header("⚙️ Production configuration")
    exam_type = st.sidebar.selectbox("Exam type", ["JEE Main", "JEE Advanced", "NEET UG"])
    dpi = st.sidebar.slider("Render quality (DPI)", 160, 360, 240, 20)
    pad_x = st.sidebar.slider("Horizontal crop margin", 0, 80, 24)
    pad_y = st.sidebar.slider("Vertical crop margin", 0, 80, 14)
    style = st.sidebar.selectbox("Visual style", ["Premium Light", "Premium Dark", "High Contrast"])
    use_ocr = st.sidebar.checkbox("OCR scanned pages automatically", value=True)
    return {"exam_type": exam_type, "subjects": get_subjects(exam_type), "pad_x": pad_x,
            "pad_y": pad_y, "render_dpi": dpi, "style": style, "use_ocr": use_ocr}
