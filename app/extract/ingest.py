import os
import hashlib
from pathlib import Path
from typing import Tuple

def save_and_hash_upload(run_id: str, filename: str, content: bytes) -> Tuple[str, str]:
    try:
        save_dir = Path("/tmp") / "runs" / run_id
        save_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        save_dir = Path("data") / "runs" / run_id
        save_dir.mkdir(parents=True, exist_ok=True)
        
    file_path = save_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)
        
    sha256_hash = hashlib.sha256(content).hexdigest()
    return str(file_path), sha256_hash
