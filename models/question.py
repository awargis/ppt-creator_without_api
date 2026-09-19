from dataclasses import dataclass
from typing import Optional
from PIL import Image
from .document import BoundingBox

@dataclass
class QuestionRegion:
    number: int
    page_index: int
    column_index: int
    box: BoundingBox
    image: Optional[Image.Image] = None
    subject: str = "Unclassified"
    answer: Optional[str] = None
    ocr_text: str = ""
    confidence: float = 0.0
    needs_review: bool = False
