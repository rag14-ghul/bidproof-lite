import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ["DB_PATH"] = "/tmp/bidproof.db"

try:
    from seed.make_docs import generate_seed_docs
    generate_seed_docs(output_dir="/tmp/seed/docs")
except Exception:
    pass

from app.main import app
