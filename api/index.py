import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

os.environ["DB_PATH"] = "/tmp/bidproof.db"

try:
    from app.main import app
except Exception as e:
    tb = traceback.format_exc()
    app = FastAPI()

    @app.get("/{full_path:path}")
    def show_error(full_path: str):
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": tb})
