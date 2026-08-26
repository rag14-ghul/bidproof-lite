from fastapi import FastAPI

app = FastAPI()

@app.get("/")
@app.get("/login")
@app.get("/health")
def root():
    return {"message": "Hello from BidProof-Lite FastAPI on Vercel!"}
