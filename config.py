from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class AppConfig:
    dpi: int = 240
    pad_x: int = 24
    pad_y: int = 14
    min_question_height: int = 40
    ocr_enabled: bool = True
    style: str = "Premium Light"

JEE_SUBJECTS = ["Physics", "Chemistry", "Mathematics"]
NEET_SUBJECTS = ["Physics", "Chemistry", "Botany", "Zoology"]

def get_subjects(exam_type: str) -> list[str]:
    return NEET_SUBJECTS.copy() if exam_type == "NEET UG" else JEE_SUBJECTS.copy()
