import streamlit as st

from services.extraction_service import parse_local_pdf, calculate_crop_boxes
from services.subject_service import assign_subject_by_number
from services.crop_service import crop_question
from utils.image_utils import apply_dark_mode
from services.answer_key_service import parse_answer_key_text
from services.ppt_service import build_subject_ppt
from services.output_service import create_subject_outputs
from ui.sidebar import render_sidebar
from ui.preview import render_question_preview
from ui.report import render_counts

st.set_page_config(page_title="Vidyapeeth PPT Generator", layout="wide")
st.title("📚 Vidyapeeth Test PPT Generator (Local Engine)")

settings = render_sidebar()

pdf_file = st.file_uploader("1. Question Paper PDF", type=["pdf"])
template_file = st.file_uploader("2. Sample PPT Template", type=["pptx"])
answer_key_text = st.text_area("3. Answer key", placeholder="1: A\n2: B\n3: C")

def process_pipeline(app_settings, uploaded_pdf):
    # 1. Parse PDF mathematically (Instant)
    pages_images, raw_coords = parse_local_pdf(uploaded_pdf.read(), dpi=app_settings.get("render_dpi", 300))
    
    # 2. Calculate spatial bounding boxes
    crops = calculate_crop_boxes(raw_coords, pages_images)
    
    grouped = {sub: [] for sub in app_settings["subjects"]}
    grouped["Unclassified"] = []
    
    # 3. Apply strict boundaries and image filters
    for q in crops:
        sub = assign_subject_by_number(q["number"], app_settings["exam_type"])
        dark_img = apply_dark_mode(q["raw_crop"])
        
        if sub in grouped:
            grouped[sub].append({
                "number": q["number"], 
                "image": dark_img, 
                "page_index": q["page_index"]
            })
        else:
            grouped["Unclassified"].append({
                "number": q["number"], 
                "image": dark_img, 
                "page_index": q["page_index"]
            })

    return grouped

if st.button("🚀 Process & Generate", type="primary"):
    if not pdf_file or not template_file:
        st.error("Upload required files to begin.")
        st.stop()

    try:
        with st.spinner("Processing PDF locally... (This will only take a few seconds)"):
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
        
        safe_filename = str(settings.get('exam_type', 'Test')).replace('/', '_')
        st.download_button(
            label="📦 Download Formatted PPTs",
            data=zip_buffer,
            file_name=f"{safe_filename}_Presentations.zip",
            mime="application/zip",
            type="primary"
        )
        
    except Exception as e:
        st.error(f"Processing Failed: {str(e)}")
        st.exception(e)
