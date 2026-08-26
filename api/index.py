import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

os.environ["DB_PATH"] = "/tmp/bidproof.db"

from app.main import app

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "BidProof-Lite"}
