from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass(frozen=True)
class BoundingBox:
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return max(0, self.x1 - self.x0)

    @property
    def height(self) -> int:
        return max(0, self.y1 - self.y0)

    def clamp(self, width: int, height: int) -> "BoundingBox":
        return BoundingBox(
            max(0, min(self.x0, width)),
            max(0, min(self.y0, height)),
            max(0, min(self.x1, width)),
            max(0, min(self.y1, height)),
        )


@dataclass
class DetectedItem:
    kind: str
    page_index: int
    column_index: int
    box: BoundingBox
    question_number: Optional[int] = None
    subject: Optional[str] = None
    confidence: float = 0.0

    @property
    def sort_key(self):
        return (self.page_index, self.column_index, self.box.y0)


@dataclass
class QuestionCrop:
    number: int
    raw_crop: Image.Image
    page_index: int
    col_index: int
    y0: float
    confidence: float = 1.0
    subject: Optional[str] = None
    ocr_text: str = ""
