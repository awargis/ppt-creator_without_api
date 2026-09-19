import streamlit as st

def render_report(report):
    st.subheader("Quality report")
    st.json({"pages": report.pages, "questions": report.questions, "subjects": report.subject_counts, "warnings": report.warnings, "low_confidence": report.low_confidence, "missing_answers": report.missing_answers})
