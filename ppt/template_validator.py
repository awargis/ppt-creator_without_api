from pptx import Presentation

def validate_template(template_bytes):
    import io
    prs = Presentation(io.BytesIO(template_bytes))
    if not prs.slides: raise ValueError("Template must contain at least one slide")
    return prs
