import streamlit as st
from services.extraction_service import extract_and_crop_pdf
from services.subject_service import assign_subject
from utils.image_utils import enhance_question
from services.answer_key_service import parse_answer_key_text
from services.ppt_service import build_subject_ppt
from services.output_service import create_subject_outputs
from ui.sidebar import render_sidebar

st.set_page_config(page_title="Vidyapeeth Studio", page_icon="📚", layout="wide")
st.title("📚 Vidyapeeth Test Presentation Studio")
st.caption("Local-first • deterministic extraction • no AI API or API key required")
settings = render_sidebar()
pdf_file = st.file_uploader("1. Upload question-paper PDF", type=["pdf"])
template_file = st.file_uploader("2. Upload sample PPT template", type=["pptx"])
answer_key_text = st.text_area("3. Answer key (optional)", placeholder="1: A\n2: B\n3: C")


def process_pipeline(app_settings, pdf_bytes):
    crops, headers = extract_and_crop_pdf(pdf_bytes, dpi=app_settings["render_dpi"],
                                          pad_x=app_settings["pad_x"], pad_y=app_settings["pad_y"],
                                          use_ocr=app_settings["use_ocr"])
    grouped = {subject: [] for subject in app_settings["subjects"]}
    grouped["Unclassified"] = []
    for crop in crops:
        subject = assign_subject(crop.number, app_settings["exam_type"], headers,
                                 crop.page_index, crop.col_index, crop.y0)
        subject = subject if subject in grouped else "Unclassified"
        grouped[subject].append({"number": crop.number, "image": enhance_question(crop.raw_crop, app_settings["style"]),
                                 "page_index": crop.page_index, "confidence": crop.confidence})
    for values in grouped.values():
        values.sort(key=lambda item: item["number"])
    return grouped


if st.button("🚀 Analyze and generate premium PPTs", type="primary", use_container_width=True):
    if not pdf_file or not template_file:
        st.error("Upload both the PDF and PPT template.")
        st.stop()
    try:
        pdf_bytes = pdf_file.getvalue()
        with st.spinner("Extracting layout, OCR, and question regions locally..."):
            subject_questions = process_pipeline(settings, pdf_bytes)
        answers = parse_answer_key_text(answer_key_text)
        counts = {subject: len(items) for subject, items in subject_questions.items() if items}
        st.success(f"Detected {sum(counts.values())} questions across {len(counts)} subject(s).")
        st.dataframe([{"Subject": k, "Questions": v} for k, v in counts.items()], use_container_width=True, hide_index=True)
        with st.expander("Preview first questions"):
            for subject, items in subject_questions.items():
                if items:
                    st.subheader(subject)
                    cols = st.columns(min(3, len(items)))
                    for index, item in enumerate(items[:3]):
                        cols[index].image(item["image"], caption=f"Q{item['number']}", use_container_width=True)
        with st.spinner("Building validated PowerPoint files..."):
            archive = create_subject_outputs(template_file.getvalue(), subject_questions, answers, build_subject_ppt, settings["style"])
        st.download_button("📦 Download subject-wise PPT ZIP", archive, f"{settings['exam_type'].replace(' ', '_')}_Presentations.zip", "application/zip", type="primary", use_container_width=True)
    except Exception as exc:
        st.error(f"Processing failed: {exc}")
        st.exception(exc)
