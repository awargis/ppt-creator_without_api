import io
import re
from collections import defaultdict
import fitz
import pytesseract
from PIL import Image
from pytesseract import Output

from models import QuestionCrop

QUESTION_RE = re.compile(r"^\s*(?:Q(?:uestion)?\s*\.?\s*)?(\d{1,3})\s*[.):]", re.I)
SUBJECT_RE = re.compile(r"physics|chemistry|mathematics|maths|botany|zoology|biology", re.I)


def _text_blocks(page):
    blocks = []
    for block in page.get_text("blocks"):
        if len(block) < 5:
            continue
        text = " ".join(str(block[4]).split())
        if text:
            blocks.append((text, tuple(float(x) for x in block[:4])))
    return blocks


def _ocr_blocks(image):
    data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
    lines = defaultdict(list)
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines[key].append((text, data["left"][i], data["top"][i], data["width"][i], data["height"][i]))
    blocks = []
    for words in lines.values():
        text = " ".join(w[0] for w in words)
        x0 = min(w[1] for w in words); y0 = min(w[2] for w in words)
        x1 = max(w[1] + w[3] for w in words); y1 = max(w[2] + w[4] for w in words)
        blocks.append((text, (x0, y0, x1, y1)))
    return blocks


def extract_and_crop_pdf(pdf_bytes: bytes, dpi: int = 240, pad_x: int = 24, pad_y: int = 14, use_ocr: bool = True):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    questions = []
    headers = []
    try:
        for page_index, page in enumerate(doc):
            scale = dpi / 72.0
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            pages.append(image)
            blocks = _text_blocks(page)
            # Scans have no native blocks; OCR only those pages to control runtime.
            if use_ocr and sum(len(t) for t, _ in blocks) < 30:
                blocks = _ocr_blocks(image)
                block_scale = 1.0
            else:
                block_scale = scale
            midpoint = page.rect.width / 2 if block_scale != 1.0 else image.width / 2
            for text, (x0, y0, x1, y1) in blocks:
                px0, py0, px1, py1 = [int(v * block_scale) for v in (x0, y0, x1, y1)]
                col = 0 if (x0 + x1) / 2 < midpoint else 1
                subject_match = SUBJECT_RE.search(text)
                if subject_match and len(text) < 120:
                    headers.append({"page": page_index, "col": col, "y0": py0, "text": text, "subject": subject_match.group(0)})
                match = QUESTION_RE.match(text)
                if match:
                    questions.append({"page": page_index, "col": col, "y0": py0, "number": int(match.group(1))})
        questions.sort(key=lambda q: (q["page"], q["col"], q["y0"]))
        # De-duplicate OCR/native detections while retaining reading order.
        unique = []
        seen = set()
        for q in questions:
            key = (q["page"], q["col"], q["number"])
            if key not in seen:
                unique.append(q); seen.add(key)
        questions = unique
        crops = []
        for index, q in enumerate(questions):
            image = pages[q["page"]]
            col_width = image.width // 2
            x0 = max(0, (0 if q["col"] == 0 else col_width) + pad_x)
            x1 = min(image.width, (col_width if q["col"] == 0 else image.width) - pad_x)
            y0 = max(0, int(q["y0"]) - pad_y)
            y1 = image.height - pad_y
            if index + 1 < len(questions):
                nxt = questions[index + 1]
                if (nxt["page"], nxt["col"]) == (q["page"], q["col"]):
                    y1 = max(y0 + 1, int(nxt["y0"]) - max(4, pad_y // 2))
            if x1 > x0 and y1 > y0:
                crops.append(QuestionCrop(q["number"], image.crop((x0, y0, x1, y1)), q["page"], q["col"], q["y0"]))
        return crops, headers
    finally:
        doc.close()
