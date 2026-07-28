def classify_document(file_name: str) -> str:
    lowered = file_name.lower()
    if "ecg" in lowered or "electrocardiogram" in lowered:
        return "ecg"
    if "blood" in lowered or "report" in lowered:
        return "blood_report"
    if "insurance" in lowered:
        return "insurance_card"
    if "id" in lowered or "passport" in lowered:
        return "id_proof"
    return "misc_document"
