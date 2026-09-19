from PIL import Image
from models import BoundingBox, TextBlock

def extract_native_blocks(page, page_index: int, scale: float) -> list[TextBlock]:
    blocks = []
    for raw in page.get_text("blocks"):
        if len(raw) < 5 or int(raw[5]) if len(raw) > 5 else False: continue
        text = " ".join(str(raw[4]).split())
        if not text: continue
        box = BoundingBox(*(int(v * scale) for v in raw[:4]))
        blocks.append(TextBlock(text, box, 1.0, page_index, 0))
    return blocks

def detect_columns(blocks: list[TextBlock], width: int) -> list[TextBlock]:
    midpoint = width / 2
    for block in blocks:
        center = (block.box.x0 + block.box.x1) / 2
        block.column_index = 0 if center < midpoint else 1
    return blocks
