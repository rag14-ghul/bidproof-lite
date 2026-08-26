from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
@app.get("/login")
def root():
    return HTMLResponse("<h1>BidProof-Lite Live</h1><p>FastAPI Serverless running on Vercel!</p>")

handler = app
