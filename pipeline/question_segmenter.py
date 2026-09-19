"""Turn detected question starts into complete question image regions using YOLO Document Layout Analysis."""

import numpy as np
from PIL import Image
from huggingface_hub import hf_hub_download
from doclayout_yolo import YOLOv10

from models import BoundingBox, QuestionRegion, TextBlock
from .question_detector import question_number

# Download and load the specialized document layout model globally
MODEL_PATH = hf_hub_download(
    repo_id="juliozhao/DocLayout-YOLO-DocStructBench", 
    filename="doclayout_yolo_docstructbench_imgsz1024.pt"
)
LAYOUT_MODEL = YOLOv10(MODEL_PATH)

def _column_bounds(page_width: int, column_index: int, two_columns: bool):
    if not two_columns or column_index == -1:
        return 0, page_width
    return (page_width // 2, page_width) if column_index == 1 else (0, page_width // 2)

def _reading_key(block):
    return (block.page_index, 99 if block.column_index == -1 else block.column_index, block.box.y0, block.box.x0)

def _next_in_same_stream(ordered, index):
    start = ordered[index]
    for candidate in ordered[index + 1:]:
        if candidate.column_index == start.column_index and candidate.page_index >= start.page_index:
            return candidate
    return None

def segment_questions(page_images, questions: list[TextBlock], pad_x=24, pad_y=14):
    """
    Enhanced segmenter combining text anchors with YOLO bounding boxes to ensure
    MCQ options and integer types are completely captured before cropping.
    """
    ordered = sorted(questions, key=_reading_key)
    page_columns = {}
    for q in ordered:
        page_columns.setdefault(q.page_index, set()).add(q.column_index)

    output = []
    
    # Pre-calculate YOLO layouts for all pages to avoid repeated inference bottlenecks
    page_layouts = {}
    for i, page in enumerate(page_images):
        cv_img = np.array(page.convert('RGB'))[:, :, ::-1]
        results = LAYOUT_MODEL.predict(cv_img, imgsz=1024, conf=0.25, device="cpu", verbose=False)[0]
        
        blocks = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_name = results.names[int(box.cls[0].item())]
            # Capture structural elements; ignore headers, footers, and instruction noise
            if class_name in ['text', 'list', 'title', 'figure']:
                blocks.append({"class": class_name, "y0": y1, "y1": y2, "x0": x1, "x1": x2})
        page_layouts[i] = blocks

    for i, start in enumerate(ordered):
        number = question_number(start.text)
        if number is None:
            continue
            
        next_start = _next_in_same_stream(ordered, i)
        page = page_images[start.page_index]
        two_columns = len(page_columns.get(start.page_index, set())) > 1
        left, right = _column_bounds(page.width, start.column_index, two_columns)
        
        x0, x1 = max(0, left + pad_x), min(page.width, right - pad_x)
        y0 = max(0, start.box.y0 - pad_y)
        
        # Determine the absolute hard stop based on the next question anchor
        y_stop = page.height - pad_y
        if next_start is not None and next_start.page_index == start.page_index and next_start.column_index == start.column_index:
            y_stop = next_start.box.y0 - max(2, pad_y // 2)

        # YOLO Expansion: dynamically stretch y1 to encompass all options (lists) and text
        layout_blocks = page_layouts[start.page_index]
        y1 = y0
        for block in layout_blocks:
            # If the block falls vertically between the current question and the next
            if block["y0"] >= (y0 - pad_y) and block["y1"] <= (y_stop + pad_y):
                # Ensure it belongs to the correct horizontal column
                if block["x0"] >= left and block["x1"] <= right:
                    y1 = max(y1, block["y1"] + pad_y)
        
        # Fallback safeguard if YOLO misses a block
        if y1 <= y0 + pad_y: 
            y1 = y_stop

        if x1 <= x0 or y1 <= y0:
            continue
            
        try:
            # Direct single-page crop execution using the finalized YOLO boundaries
            image = page.crop((x0, y0, x1, y1))
        except ValueError:
            continue
            
        output.append(QuestionRegion(
            number=number,
            page_index=start.page_index,
            column_index=start.column_index,
            box=BoundingBox(x0, y0, x1, y1).clamp(page.width, page.height),
            image=image,
            ocr_text=start.text,
            confidence=max(0.0, min(1.0, start.confidence)),
            extraction_method="yolo_hybrid",
            end_page_index=start.page_index,
        ))
        
    return output
