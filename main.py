import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(__file__))
os.environ["DB_PATH"] = "/tmp/bidproof.db"

startup_error = None

try:
    from seed.make_docs import generate_seed_docs
    generate_seed_docs(output_dir="/tmp/seed/docs")
except Exception as e:
    pass

try:
    from app.main import app
except Exception as e:
    startup_error = traceback.format_exc()
    app = FastAPI()

    @app.get("/{full_path:path}")
    def catch_all_error(full_path: str):
        return JSONResponse(status_code=500, content={"error": "Startup Failed", "traceback": startup_error})
