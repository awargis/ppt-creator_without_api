import io
import re
import zipfile


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_") or "Unclassified"


def create_subject_outputs(template_bytes: bytes, subject_questions: dict, answers: dict, build_ppt_function, style: str = "Premium Light"):
    from services.ppt_service import build_subject_ppt
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for subject, questions in subject_questions.items():
            if not questions:
                continue
            ppt = build_ppt_function(template_bytes, questions, answers, style=style)
            name = safe_name(subject)
            archive.writestr(f"{name}/{name}_Discussion.pptx", ppt)
    output.seek(0)
    return output
