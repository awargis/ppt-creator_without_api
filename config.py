from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    render_dpi: int = 240
    pad_x: int = 24
    pad_y: int = 14


def get_subjects(exam_type: str) -> list[str]:
    return (["Physics", "Chemistry", "Mathematics"] if exam_type != "NEET UG"
            else ["Physics", "Chemistry", "Botany", "Zoology"])
