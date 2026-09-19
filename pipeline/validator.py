from models import ProcessingReport

def validate_regions(regions, answers=None):
    report = ProcessingReport(questions=len(regions))
    report.subject_counts = {}
    seen = set()
    for region in regions:
        report.subject_counts[region.subject] = report.subject_counts.get(region.subject, 0) + 1
        if region.number in seen: report.warnings.append(f"Duplicate question number: {region.number}")
        seen.add(region.number)
        if region.confidence < 0.6: report.low_confidence.append(region.number)
    if answers is not None:
        report.missing_answers = sorted(set(seen) - set(answers))
    return report
