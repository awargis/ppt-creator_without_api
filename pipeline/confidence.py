def score_region(region) -> float:
    size_score = min(1.0, region.box.width / 500) * 0.25 + min(1.0, region.box.height / 120) * 0.25
    return round(max(0.0, min(1.0, region.confidence * 0.5 + size_score)), 3)
