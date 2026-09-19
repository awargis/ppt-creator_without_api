def validate(questions, answers):
    numbers = {q.number for q in questions}
    return {"missing": sorted(numbers - set(answers)), "unused": sorted(set(answers) - numbers)}
