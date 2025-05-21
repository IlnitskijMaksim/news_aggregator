from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import STUDENT_ID, SOURCES

app = FastAPI()

# Додамо CORS (поки що для localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["<http://localhost:8001>"],  # фронтенд на 8001
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пам'ять для збереження джерел (для кожного STUDENT_ID окремо)
store = {STUDENT_ID: SOURCES.copy()}

@app.get("/sources/{student_id}")
def get_sources(student_id: str):
    if student_id not in store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"sources": store[student_id]}

@app.post("/sources/{student_id}")
def add_source(student_id: str, payload: dict):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    store[student_id].append(url)
    return {"sources": store[student_id]}
