from models import Document
from .pdf_loader import load_pdf
from .text_extractor import extract_native_blocks, detect_columns
from .ocr_engine import ocr_blocks
from .question_detector import find_questions, find_headers
from .question_segmenter import segment_questions
from .subject_classifier import classify_subjects
from .confidence import score_region
from .validator import validate_regions

def run_pipeline(pdf_bytes, exam_type, subjects, dpi=240, pad_x=24, pad_y=14, use_ocr=True, answers=None):
    pages, doc = load_pdf(pdf_bytes, dpi)
    all_blocks = []; all_questions = []; all_headers = []
    try:
        scale = dpi / 72.0
        for index, page in enumerate(doc):
            blocks = detect_columns(extract_native_blocks(page, index, scale), pages[index].width)
            if use_ocr and sum(len(b.text) for b in blocks) < 30:
                blocks = detect_columns(ocr_blocks(pages[index], index), pages[index].width)
            all_blocks.extend(blocks); all_questions.extend(find_questions(blocks)); all_headers.extend(find_headers(blocks))
    finally: doc.close()
    regions = segment_questions(pages, all_blocks, all_questions, pad_x, pad_y)
    regions = classify_subjects(regions, all_headers, subjects, exam_type)
    for region in regions: region.confidence = score_region(region)
    return regions, validate_regions(regions, answers)
