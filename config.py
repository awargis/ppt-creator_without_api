import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    render_dpi: int = 300

    @property
    def poppler_path(self) -> Optional[str]:
        return os.getenv("POPPLER_PATH") or None

JEE_SUBJECTS = ["Physics", "Chemistry", "Mathematics"]
NEET_SUBJECTS = ["Physics", "Chemistry", "Botany", "Zoology"]

def get_subjects(exam_type: str) -> list[str]:
    return JEE_SUBJECTS.copy() if "JEE" in exam_type else NEET_SUBJECTS.copy()
