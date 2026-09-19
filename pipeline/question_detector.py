import re
from models import TextBlock

QUESTION_PATTERNS = [re.compile(r"^\s*(?:question\s*|q\.?\s*)?(\d{1,3})\s*[.):]", re.I), re.compile(r"^\s*\((\d{1,3})\)")]
HEADER_WORDS = ("physics", "chemistry", "mathematics", "maths", "botany", "zoology", "biology")

def question_number(text: str):
    for pattern in QUESTION_PATTERNS:
        match = pattern.match(text)
        if match: return int(match.group(1))
    return None

def find_questions(blocks: list[TextBlock]) -> list[TextBlock]:
    return [block for block in blocks if question_number(block.text) is not None]

def find_headers(blocks: list[TextBlock]) -> list[TextBlock]:
    return [block for block in blocks if len(block.text) < 120 and any(word in block.text.lower() for word in HEADER_WORDS)]
