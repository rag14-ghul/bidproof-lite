import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

os.environ["DB_PATH"] = "/tmp/bidproof.db"

try:
    from seed.make_docs import generate_seed_docs
    generate_seed_docs(output_dir="/tmp/seed/docs")
except Exception:
    pass

from app.main import app
