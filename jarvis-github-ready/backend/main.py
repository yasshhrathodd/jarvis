"""
FastAPI chat backend.

Run:
    uvicorn backend.main:app --reload --port 8000

Then open http://localhost:8000 in your browser.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .gemini_client import GeminiClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(title="JARVIS", description="Personal AI assistant")

# CORS open for local dev. Lock this down if you deploy publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# One shared Gemini client across requests. Persists chat history in memory.
# If you want per-user sessions, swap this for a dict keyed by session_id.
_client: GeminiClient | None = None


def get_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message.")
    try:
        reply = await get_client().send(req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    return ChatResponse(reply=reply)


@app.post("/reset")
async def reset():
    """Wipe conversation memory and start fresh."""
    get_client().reset()
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the frontend from /
@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


# Static assets (CSS/JS)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
