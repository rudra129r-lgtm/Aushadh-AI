from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services import claude_service
import requests, os, json

router = APIRouter()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

STATIC_STARTERS_EN = [
    "When should I take each medicine and for how long?",
    "What foods, drinks, or activities should I avoid?",
    "What are the side effects I should watch out for?",
    "When do I need to see the doctor again?",
    "What do I do if I miss a dose?",
    "Are there any warning signs I should go to the hospital for?",
]

STATIC_STARTERS_HI = [
    "मुझे हर दवा कब लेनी चाहिए और कितने दिनों तक?",
    "मुझे कौन से खाने-पीने की चीज़ें या गतिविधियों से बचना चाहिए?",
    "मुझे कौन से साइड इफेक्ट्स का ध्यान रखना चाहिए?",
    "मुझे डॉक्टर को फिर कब दिखाना चाहिए?",
    "अगर मैं एक खुराक छूट जाए तो मुझे क्या करना चाहिए?",
    "क्या कोई चेतावनी के संकेत हैं जिनके लिए मुझे अस्पताल जाना चाहिए?",
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
        print(f"[Chat] Message: {req.message[:50]}...")
        print(f"[Chat] Language: {req.language}")
        print(f"[Chat] Context: {req.context is not None}")
        
        reply, suggestions = await claude_service.chat_reply(
            message=req.message,
            history=[m.dict() for m in req.history],
            context=req.context,
            language=req.language or "English",
        )
        return ChatResponse(reply=reply, suggestions=suggestions)
    except Exception as e:
        print(f"[Chat Error] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {type(e).__name__} - {str(e)[:100]}")


@router.post("/chat/starters", summary="Get dynamic prescription-specific opening questions")
async def starters(req: StarterRequest = StarterRequest()):
    ctx = req.context
    language = req.language or "English"
    
    # Handle context - it might be a string or already a dict
    if isinstance(ctx, str):
        try:
            ctx = json.loads(ctx)
        except:
            ctx = {}
    
    if not ctx or not isinstance(ctx, dict) or not ctx.get("medications"):
        starters = STATIC_STARTERS_HI if language.lower() == "hindi" else STATIC_STARTERS_EN
        return {"questions": starters[:4]}
    try:
        meds = ", ".join(m.get("name", "") for m in ctx.get("medications", [])[:4])
        diagnosis = ctx.get("diagnosis", {}).get("original_jargon", "")
        lang_instruction = "in Hindi (in Devanagari script)" if language.lower() == "hindi" else "in English"
        prompt = f"Generate 4 short patient questions (max 10 words each) about this prescription. Medicines: {meds}. Diagnosis: {diagnosis}. Return ONLY a JSON array of 4 strings {lang_instruction}."
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
    starters = STATIC_STARTERS_HI if language.lower() == "hindi" else STATIC_STARTERS_EN
    return {"questions": starters[:4]}


@router.get("/chat/starters", summary="Get suggested opening questions (legacy)")
async def starters_get():
    return {"questions": STATIC_STARTERS_EN[:4]}


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "Hindi"


@router.post("/translate", summary="Translate text")
async def translate(req: TranslateRequest):
    try:
        lang = req.target_lang if req.target_lang.lower() == "hindi" else "English"
        
        system_msg = f"""You are a medical translator. Translate the following text to {lang}.
Rules:
1. Translate accurately preserving medical terminology
2. Keep medicine names as they are
3. Only translate patient-facing content
4. Return ONLY the translated text, nothing else"""

        res = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": req.text}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=30
        )
        
        if not res.ok:
            raise Exception(f"Translation failed: {res.text}")
        
        translated = res.json()["choices"][0]["message"]["content"].strip()
        return {"translated": translated}
    except Exception as e:
        print(f"[Translate Error] {str(e)}")
        return {"translated": req.text}
