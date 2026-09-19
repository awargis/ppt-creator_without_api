import io
from .slide_builder import build_slides

def export_subject_ppts(template_bytes, regions, answers):
    result = {}
    for subject in sorted({r.subject for r in regions}):
        selected = [r for r in regions if r.subject == subject]
        prs = build_slides(template_bytes, selected, answers); out = io.BytesIO(); prs.save(out); result[subject] = out.getvalue()
    return result
