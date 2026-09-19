def assign_subject(q_num: int, exam_type: str, headers: list, q_page: int, q_col: int, q_y0: float) -> str:
    """
    Determines subject using strict standard boundaries for Main/NEET,
    and falls back to dynamic header tracking for unpredictable Advanced papers.
    """
    # 1. Strict Formatting for Standardized Exams
    if exam_type == "JEE Main":
        if 1 <= q_num <= 25: return "Physics"
        elif 26 <= q_num <= 50: return "Chemistry"
        elif 51 <= q_num <= 75: return "Mathematics"
        
    elif exam_type == "NEET UG":
        if 1 <= q_num <= 45: return "Physics"
        elif 46 <= q_num <= 90: return "Chemistry"
        elif 91 <= q_num <= 135: return "Botany"
        elif 136 <= q_num <= 180: return "Zoology"

    # 2. Dynamic Tracking for JEE Advanced (Scans for previous headers)
    current_subject = "Unclassified"
    for h in headers:
        # If the header appeared before this question chronologically
        if (h["page"] < q_page) or \
           (h["page"] == q_page and h["col"] < q_col) or \
           (h["page"] == q_page and h["col"] == q_col and h["y0"] < q_y0):
            
            if "PHYSICS" in h["text"]: current_subject = "Physics"
            elif "CHEMISTRY" in h["text"]: current_subject = "Chemistry"
            elif "MATHEMATICS" in h["text"]: current_subject = "Mathematics"
            elif "BOTANY" in h["text"]: current_subject = "Botany"
            elif "ZOOLOGY" in h["text"]: current_subject = "Zoology"
            
    return current_subject
