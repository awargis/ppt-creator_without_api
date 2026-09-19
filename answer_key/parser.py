import re

def parse(text):
    result = {}
    for match in re.finditer(r"(?:Q\s*)?(\d{1,3})\s*(?:[:.\-)=]|->|\s)\s*\(?([A-Da-d1-4](?:\s*[,/&]\s*[A-Da-d1-4])*)", text or ""):
        result[int(match.group(1))] = re.sub(r"\s+", "", match.group(2)).upper()
    return result
