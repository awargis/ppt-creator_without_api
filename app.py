import streamlit as st

from services.extraction_service import extract_and_crop_pdf
from services.subject_service import assign_subject
from utils.image_utils import apply_dark_mode
from services.answer_key_service import parse_answer_key_text
from services.ppt_service import build_subject_ppt
from services.output_service import create_subject_outputs
from ui.sidebar import render_sidebar
from ui.preview import render_question_preview
from ui.report import render_counts

st.set_page_config(page_title="Vidyapeeth PPT Generator", layout="wide")
st.title("📚 Vidyapeeth Test PPT Generator")
st.markdown("*100% Local, deterministic extraction engine with zero AI rate limits.*")

settings = render_sidebar()

pdf_file = st.file_uploader("1. Question Paper PDF", type=["pdf"])
template_file = st.file_uploader("2. Sample PPT Template", type=["pptx"])
answer_key_text = st.text_area("3. Answer key (Optional)", placeholder="1: A\n2: B\n3: C")

def process_pipeline(app_settings, uploaded_pdf):
    # 1. Parse PDF mathematically
    crops, headers = extract_and_crop_pdf(
        pdf_bytes=uploaded_pdf.read(), 
        dpi=app_settings["render_dpi"], 
        pad_x=app_settings["pad_x"], 
        pad_y=app_settings["pad_y"]
    )
    
    grouped = {sub: [] for sub in app_settings["subjects"]}
    grouped["Unclassified"] = []
    
    # 2. Route strictly by JEE/NEET boundaries and apply aesthetics
    for q in crops:
        sub = assign_subject(
            q_num=q["number"], 
            exam_type=app_settings["exam_type"], 
            headers=headers, 
            q_page=q["page_index"], 
            q_col=q["col_index"], 
            q_y0=q["y0"]
        )
        
        dark_img = apply_dark_mode(q["raw_crop"])
        
        if sub in grouped:
            grouped[sub].append({
                "number": q["number"], "image": dark_img, "page_index": q["page_index"]
            })
        else:
            grouped["Unclassified"].append({
                "number": q["number"], "image": dark_img, "page_index": q["page_index"]
            })

    return grouped

if st.button("🚀 Process & Generate PPTs", type="primary"):
    if not pdf_file or not template_file:
        st.error("Upload the PDF and PPT template to begin.")
        st.stop()

    try:
        with st.spinner("Processing PDF locally... (Usually takes < 5 seconds)"):
            subject_questions = process_pipeline(settings, pdf_file)
            answers = parse_answer_key_text(answer_key_text)
            
            zip_buffer = create_subject_outputs(
                template_bytes=template_file.read(),
                subject_questions=subject_questions,
                answers=answers,
                build_ppt_function=build_subject_ppt
            )

        st.success("Extraction Complete.")
        
        subject_counts = {s: len(i) for s, i in subject_questions.items() if i}
        render_counts(subject_counts)
        render_question_preview(subject_questions)
        
        safe_filename = str(settings['exam_type']).replace('/', '_')
        st.download_button(
            label="📦 Download Premium Formatted PPTs",
            data=zip_buffer,
            file_name=f"{safe_filename}_Presentations.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Processing Failed: {str(e)}")
        st.exception(e)
