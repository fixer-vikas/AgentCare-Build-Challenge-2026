import hashlib
from typing import Optional


def compute_checksum(file_obj) -> Optional[str]:
    if file_obj is None:
        return None
    file_obj.seek(0)
    content = file_obj.read()
    file_obj.seek(0)
    return hashlib.sha256(content).hexdigest()
