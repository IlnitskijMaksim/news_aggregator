from typing import Optional

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config
from config import STUDENT_ID, SOURCES
import  feedparser

# Додамо CORS (поки що для localhost)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_users_db = {
    STUDENT_ID: {
        "username": STUDENT_ID,
        "full_name": STUDENT_ID,
        "hashed_password": "password123",  # нерекомендовано зберігати так на проді
        "disabled": False,
    }
}



# Пам'ять для збереження джерел (для кожного STUDENT_ID окремо)
store = {STUDENT_ID: SOURCES.copy()}
news_store = {STUDENT_ID: []}
analyzer = SentimentIntensityAnalyzer()
sources_store = {}

@app.on_event("startup")
async def load_initial_sources() -> None:
    student_id = getattr(config, "STUDENT_ID", None)
    sources    = getattr(config, "SOURCES", [])
    if student_id and isinstance(sources, list):
        sources_store[student_id] = list(sources)
        print(f"[startup] loaded {len(sources)} feeds for {student_id}")

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

@app.post("/fetch/{student_id}")
def fetch_news(student_id: str, payload: Optional[dict] = Body(default=None)):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    # Очищаємо попередній кеш
    news_store[student_id].clear()
    fetched = 0
    for url in config.SOURCES:
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link":  entry.get("link", ""),
                "published": entry.get("published", "")
            })
            fetched += 1
    return {"fetched": fetched}

@app.get("/news/{student_id}")
def get_news(student_id: str):
    if student_id not in news_store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store[student_id]}

@app.post("/analyze/{student_id}")
def analyze_tone(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    articles = news_store.get(student_id, [])
    result = []
    for art in articles:
        text = art.get("title", "")
        scores = analyzer.polarity_scores(text)
        comp = scores["compound"]
        if comp >= 0.05:
            label = "positive"
        elif comp <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        # Додаємо поля "sentiment" і "scores" в копію статті
        result.append({**art, "sentiment": label, "scores": scores})
    return {"analyzed": len(result), "articles": result}