from collections import defaultdict
from PIL import Image
import pytesseract
from pytesseract import Output
from models import BoundingBox, TextBlock

def ocr_blocks(image: Image.Image, page_index: int) -> list[TextBlock]:
    data = pytesseract.image_to_data(image, config="--psm 6", output_type=Output.DICT)
    lines = defaultdict(list)
    for i, value in enumerate(data["text"]):
        value = value.strip()
        if value: lines[(data["block_num"][i], data["par_num"][i], data["line_num"][i])].append(i)
    result = []
    for indexes in lines.values():
        text = " ".join(data["text"][i].strip() for i in indexes)
        x0 = min(data["left"][i] for i in indexes); y0 = min(data["top"][i] for i in indexes)
        x1 = max(data["left"][i] + data["width"][i] for i in indexes)
        y1 = max(data["top"][i] + data["height"][i] for i in indexes)
        confidence = sum(float(data["conf"][i]) for i in indexes if float(data["conf"][i]) >= 0) / max(1, len(indexes)) / 100
        result.append(TextBlock(text, BoundingBox(x0, y0, x1, y1), confidence, page_index))
    return result
