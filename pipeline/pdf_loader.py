import fitz
from PIL import Image

def load_pdf(pdf_bytes: bytes, dpi: int = 240) -> tuple[list[Image.Image], fitz.Document]:
    if not pdf_bytes: raise ValueError("The PDF is empty.")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if doc.page_count == 0: raise ValueError("The PDF has no pages.")
    pages = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    return pages, doc
