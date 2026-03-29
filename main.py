from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

from app.routers import analyse, chat, export

@asynccontextmanager
async def lifespan(app: FastAPI):
    groq = os.environ.get("GROQ_API_KEY", "")
    if groq:
        print(f"  [OK] Groq API Key loaded: ...{groq[-6:]}")
        print(f"  [AI] AI Model: Llama 3.3 70B (Free)")
    else:
        print("  [X] GROQ_API_KEY not found in .env!")
    
    gemini = os.environ.get("GEMINI_API_KEY", "")
    if gemini and gemini != "your_gemini_api_key_here":
        print(f"  [OK] Gemini API Key loaded: ...{gemini[-6:]}")
        print(f"  [AI] Vision Model: Gemini 1.5 Flash (Medical Images)")
    else:
        print("  [X] GEMINI_API_KEY not configured in .env (X-ray/MRI analysis disabled)")
    
    supabase_url = os.environ.get("SUPABASE_URL", "")
    if supabase_url:
        print(f"  [OK] Supabase URL loaded")
    else:
        print("  [X] SUPABASE_URL not found in .env!")
    
    yield

app = FastAPI(title="Aushadh AI API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse.router, prefix="/api", tags=["Analysis"])
app.include_router(chat.router,    prefix="/api", tags=["Chat"])
app.include_router(export.router,  prefix="/api", tags=["Export"])

STATIC_FILES = [
    "index.html", "login.html", "dashboard.html", "documents.html", 
    "medications.html", "checklist.html", "diagnosis.html", "chat.html",
    "profile.html", "medbuddy.js", "logo_green.png", "logo_white.png"
]

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ai": "groq-llama3",
        "key_loaded": bool(os.environ.get("GROQ_API_KEY"))
    }

@app.get("/")
async def root():
    if (BASE_DIR / "index.html").exists():
        return FileResponse(BASE_DIR / "index.html")
    return {"message": "Aushadh AI API running!", "docs": "/docs"}

@app.get("/{filename}")
async def serve(filename: str):
    if filename == "api":
        return {"message": "Aushadh AI API", "docs": "/docs"}
    if filename in STATIC_FILES:
        file_path = BASE_DIR / filename
        if file_path.exists():
            # Determine correct media type
            if filename.endswith(".png"):
                media_type = "image/png"
                logger.info(f"📷 Serving image: {filename} from {file_path}")
            elif filename.endswith(".html"):
                media_type = "text/html; charset=utf-8"
                logger.info(f"📄 Serving HTML: {filename}")
            elif filename.endswith(".js"):
                media_type = "application/javascript"
            else:
                media_type = "application/octet-stream"
            return FileResponse(file_path, media_type=media_type)
        else:
            logger.error(f"❌ File not found: {file_path}")
    if (BASE_DIR / "index.html").exists():
        return FileResponse(BASE_DIR / "index.html", media_type="text/html; charset=utf-8")
    return {"error": "File not found"}, 404
