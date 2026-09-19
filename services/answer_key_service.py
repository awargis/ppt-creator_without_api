import re

def parse_answer_key_text(text: str) -> dict[int, str]:
    """Gracefully handles standard answer key formats: '1: A', '1. B', '1-C'"""
    answer_key = {}
    if not text: return answer_key
    pattern = r"(\d{1,3})\s*[:\.\-\)]*\s*\(?([1-4A-Da-d]+)\)?"
    
    for match in re.finditer(pattern, text):
        q_num, ans = match.groups()
        answer_key[int(q_num)] = ans.upper()
    return answer_key
