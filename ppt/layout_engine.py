from pptx.util import Inches

def fit_box(prs, image):
    left, top = Inches(.55), Inches(1.15); width = prs.slide_width - Inches(1.1); height = prs.slide_height - Inches(1.55)
    scale = min(int(width) / image.width, int(height) / image.height)
    w, h = int(image.width * scale), int(image.height * scale)
    return int(left) + (int(width) - w)//2, int(top) + (int(height) - h)//2, w, h
