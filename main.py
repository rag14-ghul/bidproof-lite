import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ["DB_PATH"] = "/tmp/bidproof.db"

try:
    from seed.make_docs import generate_seed_docs
    generate_seed_docs(output_dir="/tmp/seed/docs")
except Exception:
    pass

from app.main import app
