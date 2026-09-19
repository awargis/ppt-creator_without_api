import fitz
import re
from PIL import Image

def parse_local_pdf(pdf_bytes: bytes, dpi: int = 300):
    """Extracts exact mathematical coordinates of text blocks from the PDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    scale = dpi / 72.0  # Converts native PDF points to high-res pixels
    
    pages_images = []
    questions = []
    
    # Matches "1.", "1)", "25."
    q_pattern = re.compile(r"^(\d{1,3})\s*[\.\)]")
    
    for page_index, page in enumerate(doc):
        # Render high-resolution image for cropping
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages_images.append(img)
        
        blocks = page.get_text("dict")["blocks"]
        midpoint = page.rect.width / 2
        
        for b in blocks:
            if "lines" not in b: continue
            
            # Reconstruct block text
            text = " ".join([s["text"] for l in b["lines"] for s in l["spans"]]).strip()
            if not text: continue
            
            x0, y0, x1, y1 = b["bbox"]
            col_idx = 0 if x0 < midpoint else 1
            pixel_y0 = y0 * scale
            
            match = q_pattern.match(text)
            if match:
                questions.append({
                    "page_index": page_index,
                    "column_index": col_idx,
                    "y_start": pixel_y0,
                    "number": int(match.group(1))
                })
                
    doc.close()
    return pages_images, questions

def calculate_crop_boxes(questions, pages_images, margin_x=35, margin_y=15):
    """Calculates question height based on the start position of the next question."""
    questions.sort(key=lambda q: (q["page_index"], q["column_index"], q["y_start"]))
    crops = []
    
    for i, q in enumerate(questions):
        img = pages_images[q["page_index"]]
        midpoint = img.width / 2
        
        # X-bounds based on column split
        if q["column_index"] == 0:
            x_min, x_max = margin_x, midpoint - (margin_x / 2)
        else:
            x_min, x_max = midpoint + (margin_x / 2), img.width - margin_x
            
        y_min = max(0, q["y_start"] - margin_y)
        y_max = img.height - margin_y
        
        # Determine the bottom edge by checking the next question's position
        if i + 1 < len(questions):
            next_q = questions[i + 1]
            if next_q["page_index"] == q["page_index"] and next_q["column_index"] == q["column_index"]:
                y_max = next_q["y_start"] - margin_y
                
        if y_max > y_min:
            box = (int(x_min), int(y_min), int(x_max), int(y_max))
            crops.append({
                "number": q["number"],
                "raw_crop": img.crop(box),
                "page_index": q["page_index"]
            })
            
    return crops
