import os
import sys

# Ensure project root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configure Vercel serverless writable SQLite DB path under /tmp
os.environ["DB_PATH"] = "/tmp/bidproof.db"

# Ensure seed docs exist for demo runs
try:
    from seed.make_docs import generate_seed_docs
    generate_seed_docs(output_dir="/tmp/seed/docs")
except Exception:
    pass

from app.main import app
