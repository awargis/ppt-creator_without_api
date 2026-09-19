import fitz
import re
from PIL import Image

def extract_and_crop_pdf(pdf_bytes: bytes, dpi: int, pad_x: int, pad_y: int):
    """
    100% Local, Deterministic Extraction.
    Uses PyMuPDF to find exact bounding boxes of every question, ensuring options are included
    by measuring the distance to the next question.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    scale = dpi / 72.0
    
    pages_images = []
    questions_meta = []
    headers_meta = []
    
    # Matches "1.", "1)", "1:", "01."
    q_pattern = re.compile(r"^(\d{1,3})\s*[\.\):]")
    
    for page_idx, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages_images.append(img)
        
        blocks = page.get_text("dict")["blocks"]
        midpoint = page.rect.width / 2
        
        for b in blocks:
            if "lines" not in b: continue
            text = " ".join([s["text"] for l in b["lines"] for s in l["spans"]]).strip()
            if not text: continue
            
            x0, y0, x1, y1 = b["bbox"]
            col_idx = 0 if (x0 + x1) / 2 < midpoint else 1
            
            # Detect section headers for dynamic Advanced papers
            upper_text = text.upper()
            if any(s in upper_text for s in ["PHYSICS", "CHEMISTRY", "MATHEMATICS", "BOTANY", "ZOOLOGY"]):
                headers_meta.append({
                    "page": page_idx, "col": col_idx, "y0": y0 * scale, "text": upper_text
                })
                continue
                
            match = q_pattern.match(text)
            if match:
                questions_meta.append({
                    "page": page_idx,
                    "col": col_idx,
                    "y0": y0 * scale,
                    "number": int(match.group(1))
                })

    # Chronological sort (Top to bottom, left column then right column)
    questions_meta.sort(key=lambda q: (q["page"], q["col"], q["y0"]))
    headers_meta.sort(key=lambda h: (h["page"], h["col"], h["y0"]))
    
    crops = []
    for i, q in enumerate(questions_meta):
        img = pages_images[q["page"]]
        midpoint_px = img.width / 2
        
        # Set horizontal bounds based on column, applying UI padding
        if q["col"] == 0:
            x_min, x_max = max(0, pad_x), max(0, midpoint_px - pad_x)
        else:
            x_min, x_max = min(img.width, midpoint_px + pad_x), min(img.width, img.width - pad_x)
            
        y_min = max(0, q["y0"] - pad_y)
        y_max = img.height - pad_y 
        
        # Crucial: The bottom bound extends exactly to the start of the next question
        # This guarantees all MCQs options and diagrams are captured seamlessly.
        if i + 1 < len(questions_meta):
            next_q = questions_meta[i+1]
            if next_q["page"] == q["page"] and next_q["col"] == q["col"]:
                y_max = next_q["y0"] - (pad_y / 2)
                
        if y_max <= y_min or x_max <= x_min: continue
        
        box = (int(x_min), int(y_min), int(x_max), int(y_max))
        raw_crop = img.crop(box)
        
        crops.append({
            "number": q["number"],
            "raw_crop": raw_crop,
            "page_index": q["page"],
            "col_index": q["col"],
            "y0": q["y0"]
        })
        
    doc.close()
    return crops, headers_meta
