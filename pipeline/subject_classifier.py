from .question_detector import find_headers
from services.subject_service import normalize_subject

def classify_subjects(regions, headers, known_subjects, exam_type):
    for region in regions:
        subject = None
        for header in sorted(headers, key=lambda x: (x.page_index, x.column_index, x.box.y0)):
            if (header.page_index, header.column_index, header.box.y0) <= (region.page_index, region.column_index, region.box.y0):
                subject = normalize_subject(header.text, known_subjects) or subject
        if subject is None:
            if exam_type.startswith("JEE"):
                subject = "Physics" if region.number <= 25 else "Chemistry" if region.number <= 50 else "Mathematics"
            elif region.number <= 45: subject = "Physics"
            elif region.number <= 90: subject = "Chemistry"
            elif region.number <= 135: subject = "Botany"
            else: subject = "Zoology"
        region.subject = subject if subject in known_subjects else "Unclassified"
    return regions
