from models import BoundingBox, QuestionRegion, TextBlock
from .question_detector import question_number

def segment_questions(page_images, blocks: list[TextBlock], questions: list[TextBlock], pad_x=24, pad_y=14):
    ordered = sorted(questions, key=lambda b: (b.page_index, b.column_index, b.box.y0))
    output = []
    for index, start in enumerate(ordered):
        number = question_number(start.text)
        page = page_images[start.page_index]
        same_column = [b for b in ordered[index + 1:] if b.page_index == start.page_index and b.column_index == start.column_index]
        next_block = same_column[0] if same_column else None
        left = 0 if start.column_index == 0 else page.width // 2
        right = page.width // 2 if start.column_index == 0 else page.width
        x0, x1 = max(0, left + pad_x), min(page.width, right - pad_x)
        y0 = max(0, start.box.y0 - pad_y)
        y1 = min(page.height, next_block.box.y0 - max(4, pad_y // 2) if next_block else page.height - pad_y)
        if x1 > x0 and y1 - y0 >= 40:
            box = BoundingBox(x0, y0, x1, y1)
            output.append(QuestionRegion(number, start.page_index, start.column_index, box, page.crop((x0, y0, x1, y1)), confidence=start.confidence))
    return output
