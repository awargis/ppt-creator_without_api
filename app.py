import io, re, zipfile
import streamlit as st
from config import get_subjects
from pipeline.orchestrator import run_pipeline
from answer_key.parser import parse
from answer_key.validator import validate
from image.enhancement import enhance
from ppt.exporter import export_subject_ppts
from ui.review import render_review
from ui.report import render_report

st.set_page_config(page_title="Vidyapeeth Studio", page_icon="📚", layout="wide")
st.title("📚 Vidyapeeth Test Presentation Studio")
st.caption("Local-first • OCR fallback • no AI API")
exam = st.sidebar.selectbox("Exam", ["JEE Main", "JEE Advanced", "NEET UG"])
dpi = st.sidebar.slider("Render DPI", 160, 320, 240, 20)
pad_x = st.sidebar.slider("Horizontal margin", 0, 80, 24)
pad_y = st.sidebar.slider("Vertical margin", 0, 80, 14)
style = st.sidebar.selectbox("Visual style", ["Premium Light", "Premium Dark"])
pdf = st.file_uploader("1. Question paper PDF", type=["pdf"])
template = st.file_uploader("2. Sample PPT template", type=["pptx"])
answer_text = st.text_area("3. Answer key (optional)", placeholder="1: A\n2: B\n3: C")

if st.button("🚀 Analyze and generate", type="primary", use_container_width=True):
    if not pdf or not template:
        st.error("Upload both the PDF and PPT template."); st.stop()
    try:
        answers = parse(answer_text)
        with st.spinner("Extracting text, detecting layout, and creating crops..."):
            regions, report = run_pipeline(pdf.getvalue(), exam, get_subjects(exam), dpi, pad_x, pad_y, True, answers)
            for region in regions: region.image = enhance(region.image, style)
            report.pages = len({r.page_index for r in regions})
            report.missing_answers = validate(regions, answers)["missing"]
        render_report(report); render_review(regions)
        if not regions: raise ValueError("No questions detected. Try a higher DPI or a selectable-text PDF.")
        with st.spinner("Building subject-wise PowerPoint files..."):
            outputs = export_subject_ppts(template.getvalue(), regions, answers)
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
                for subject, data in outputs.items():
                    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", subject)
                    z.writestr(f"{safe}/{safe}_Discussion.pptx", data)
            archive.seek(0)
        st.success(f"Generated {len(outputs)} presentation(s) from {len(regions)} question(s).")
        st.download_button("📦 Download PPT ZIP", archive.getvalue(), f"{exam.replace(' ', '_')}_Presentations.zip", "application/zip", type="primary", use_container_width=True)
    except Exception as exc:
        st.error(f"Processing failed: {exc}")
        st.exception(exc)
