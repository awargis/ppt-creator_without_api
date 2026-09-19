from dataclasses import dataclass, field
from typing import Optional
from PIL import Image

@dataclass(frozen=True)
class BoundingBox:
    x0: int; y0: int; x1: int; y1: int
    @property
    def width(self): return max(0, self.x1 - self.x0)
    @property
    def height(self): return max(0, self.y1 - self.y0)

@dataclass
class TextBlock:
    text: str
    box: BoundingBox
    confidence: float = 1.0
    page_index: int = 0
    column_index: int = 0

@dataclass
class Question:
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

@dataclass
class Document:
    pages: list[Image.Image] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    headers: list[TextBlock] = field(default_factory=list)
