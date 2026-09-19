import re
from typing import Optional

def assign_subject_by_number(q_num: int, exam_type: str) -> str:
    """Strictly routes questions to subjects based on standard numbering patterns."""
    if "JEE" in exam_type:
        # JEE Main standard format (25 or 30 questions per subject)
        if 1 <= q_num <= 30: return "Physics"
        elif 31 <= q_num <= 60: return "Chemistry"
        elif 61 <= q_num <= 90: return "Mathematics"
        # Fallback for the 75-question format you mentioned
        elif 1 <= q_num <= 25: return "Physics"
        elif 26 <= q_num <= 50: return "Chemistry"
        elif 51 <= q_num <= 75: return "Mathematics"
        
    elif "NEET" in exam_type:
        # NEET UG standard format (50 questions per section)
        if 1 <= q_num <= 50: return "Physics"
        elif 51 <= q_num <= 100: return "Chemistry"
        elif 101 <= q_num <= 150: return "Botany"
        elif 151 <= q_num <= 200: return "Zoology"
    
    return "Unclassified"

def normalize_subject(value: Optional[str], known_subjects: list[str]) -> Optional[str]:
    """Fallback text normalization if headers are ever used again."""
    if not value: return None
    value = re.sub(r"[^a-z\s]", " ", str(value).lower()).strip()
    for subject in known_subjects:
        if subject.lower() in value: return subject
    return None
