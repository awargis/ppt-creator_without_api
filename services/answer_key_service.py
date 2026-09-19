import re


def parse_answer_key_text(text: str) -> dict[int, str]:
    answers = {}
    if not text:
        return answers
    pattern = re.compile(r"(?:Q\s*)?(\d{1,3})\s*(?:[:.\-)=]|->|\s)\s*\(?([A-Da-d1-4](?:\s*[,/&]\s*[A-Da-d1-4])*)\)?")
    for match in pattern.finditer(text):
        number = int(match.group(1))
        answer = re.sub(r"\s+", "", match.group(2)).upper()
        answers[number] = answer
    return answers
