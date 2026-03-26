from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services import claude_service
import requests, os, json

router = APIRouter()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

STATIC_STARTERS = [
    "When should I take each medicine and for how long?",
    "What foods, drinks, or activities should I avoid?",
    "What are the side effects I should watch out for?",
    "When do I need to see the doctor again?",
    "What do I do if I miss a dose?",
    "Are there any warning signs I should go to the hospital for?",
]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    context: Optional[dict] = None
    language: Optional[str] = "English"

class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []

class StarterRequest(BaseModel):
    context: Optional[dict] = None
    language: Optional[str] = "English"


@router.post("/chat", response_model=ChatResponse, summary="Chat about the prescription")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        reply, suggestions = await claude_service.chat_reply(
            message=req.message,
            history=[m.dict() for m in req.history],
            context=req.context,
            language=req.language or "English",
        )
        return ChatResponse(reply=reply, suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/chat/starters", summary="Get dynamic prescription-specific opening questions")
async def starters(req: StarterRequest = StarterRequest()):
    ctx = req.context
    if not ctx or not ctx.get("medications"):
        return {"questions": STATIC_STARTERS[:4]}
    try:
        meds = ", ".join(m.get("name", "") for m in ctx.get("medications", [])[:4])
        diagnosis = ctx.get("diagnosis", {}).get("original_jargon", "")
        prompt = f"Generate 4 short patient questions (max 10 words each) about this prescription. Medicines: {meds}. Diagnosis: {diagnosis}. Return ONLY a JSON array of 4 strings."
        res = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.5, "max_tokens": 200},
            timeout=15
        )
        raw = res.json()["choices"][0]["message"]["content"].strip()
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        questions = json.loads(raw)
        if isinstance(questions, list) and len(questions) >= 2:
            return {"questions": questions[:4]}
    except Exception as e:
        print(f"[Aushadh AI] Dynamic starters failed: {e}")
    return {"questions": STATIC_STARTERS[:4]}


@router.get("/chat/starters", summary="Get suggested opening questions (legacy)")
async def starters_get():
    return {"questions": STATIC_STARTERS[:4]}
