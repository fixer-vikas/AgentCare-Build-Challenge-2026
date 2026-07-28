from typing import List


def parse_document_request(request: str) -> List[str]:
    lowered = request.lower()
    docs: List[str] = []
    if "insurance" in lowered or "insurance card" in lowered:
        docs.append("insurance_card")
    if "id" in lowered or "identification" in lowered or "passport" in lowered:
        docs.append("id_proof")
    if "medical history" in lowered or "history" in lowered:
        docs.append("medical_history")
    if "report" in lowered or "test result" in lowered or "blood report" in lowered:
        docs.append("blood_report")
    if "ecg" in lowered:
        docs.append("ecg")
    if "document" in lowered or "documents" in lowered:
        docs.append("misc_document")
    return docs
