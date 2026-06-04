"""Local FastAPI wrapper around the VinWonders rule-based engine."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .main import answer_with_rules


app = FastAPI(title="VinWonders AI Assistant Rule-Based API")


class ChatRequest(BaseModel):
    """Incoming chat payload for the local demo API."""

    message: str
    use_llm: bool = True


@app.get("/health")
def health() -> dict:
    """Simple health check for the local service."""
    return {
        "status": "ok",
        "service": "vinwonders-ai-assistant-rule-based",
    }


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    """Return a rule-based answer for the provided message."""
    return answer_with_rules(request.message, use_llm=request.use_llm)
