"""
Aushadh AI AI Service — Maximum Accuracy Pipeline
==================================================
Step 1: PaddleOCR + EasyOCR   → Extract text from images/PDFs
Step 2: Groq (Llama)          → Fast first-pass extraction
Step 3: OpenFDA API           → Validate & enrich drug info
"""

import os
import json
import base64
import requests
import re
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")
GROQ_URL          = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL        = "llama-3.3-70b-versatile"
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")
AZURE_VISION_KEY  = os.environ.get("AZURE_VISION_KEY", "")
AZURE_VISION_ENDPOINT = os.environ.get("AZURE_VISION_ENDPOINT", "")
OPENFDA_URL       = "https://api.fda.gov/drug/label.json"

# In-memory cache for OpenFDA (survives across requests)
OPENFDA_CACHE = {}

# Better system prompt for medical document extraction
VISION_SYSTEM = """You are an expert at reading handwritten and printed medical prescriptions.

TASK: Extract ALL information from this medical document and format as JSON.

CRITICAL RULES:
1. Read VERY carefully - some text may be faint or handwritten
2. Extract EXACT medicine names - they are usually brand names like: Glucored, Januvia, Metformin, Azithromycin, etc.
3. For timing, look for: Morning (M), Afternoon (A), Evening (E), Night (N) or BD (twice daily), OD (once daily), TDS (3 times daily)
4. Extract dosage: usually in mg or ml
5. If you CANNOT read something, write "Cannot read" - DO NOT make up information
6. List each medication as: name, dosage, timing, duration (if stated), with_food (if stated)
7. Extract patient name, age, gender, date, doctor name
8. Extract any tests/investigations mentioned
9. Extract any advice: diet, exercise, follow-up

Output ONLY valid JSON. Start with { and end with }"""

# System prompt for text analysis
SYSTEM = """You are Aushadh AI, a strict medical document simplifier for Indian patients.
CRITICAL RULES:
1. Extract ONLY what is written in the document — never add outside advice
2. Medications must EXACTLY match the document — never change dosages
3. If info is missing use "Not specified" — never invent
4. Return ONLY raw JSON — no markdown, no code blocks
5. Your response must be valid JSON starting with { and ending with }
6. Extract tests/investigations separately from medications
7. plain_english explanations: 2-4 sentences, conversational
8. side_effects from medications listed - top 2-3 warnings
9. checklist: tests, diet, activity limits, follow-up
10. For side_effects severity: 'high'=needs hospital immediately, 'medium'=expected but monitor, 'low'=mild discomfort. NEVER default all to 'low'. Classify each accurately.
11. recovery_days_min/max: extract from document (e.g. "rest for 7 days" → min=7, max=7; "2-3 weeks" → min=14, max=21). Return null only if truly not mentioned."""


# ── STEP 1: OCR using PaddleOCR + EasyOCR fallback ──────────────────────────

def ocr_image(image_bytes: bytes) -> str:
    """Extract text from image using PaddleOCR with EasyOCR fallback"""
    try:
        from app.services.ocr_service import extract_text
        print("[Aushadh AI] Step 1: OCR processing...")
        result = extract_text(image_bytes)
        
        if result["text"]:
            print(f"[Aushadh AI] OCR extracted {len(result['text'])} chars using {result['method']}")
            return result["text"]
        
        print("[Aushadh AI] OCR failed to extract text")
        return ""
        
    except Exception as e:
        print(f"[Aushadh AI] OCR error: {e}")
        import traceback
        traceback.print_exc()
        return ""


def extract_pdf_text(data: bytes) -> str:
    try:
        from app.services.ocr_service import extract_text_from_pdf
        print("[Aushadh AI] Extracting text from PDF...")
        text = extract_text_from_pdf(data)
        print(f"[Aushadh AI] PDF: {len(text)} chars extracted")
        return text[:4000]
    except Exception as e:
        raise Exception(str(e))


# ── STEP 2: GROQ ─────────────────────────────────────

def retry_with_backoff(max_retries: int = 4, base_delay: float = 2.0):
    def decorator(func):
        import time
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    error_msg = str(e)
                    is_rate_limit = '429' in error_msg or 'rate_limit' in error_msg.lower()
                    if is_rate_limit:
                        delay = base_delay * (2 ** attempt)
                        print(f"[Aushadh AI] Rate limited, waiting {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator


@retry_with_backoff(max_retries=4, base_delay=2.0)
def call_groq(prompt: str, system_prompt: str) -> str:
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not found in .env")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Aushadh AIApp/1.0"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 3500
    }
    res = requests.post(GROQ_URL, headers=headers, json=data, timeout=60)
    if res.status_code != 200:
        raise Exception(f"Groq error {res.status_code}: {res.text}")
    return res.json()["choices"][0]["message"]["content"]


# ── STEP 3: OpenFDA ───────────────────────────────────

def lookup_openfda(drug_name: str) -> dict:
    try:
        clean = re.sub(r'\d+\s*(mg|ml|mcg|g|%)', '', drug_name, flags=re.IGNORECASE).strip()
        clean = clean.split('/')[0].strip()
        if len(clean) < 3:
            return {}

        for search in [f'openfda.generic_name:"{clean}"', f'openfda.generic_name:{clean}']:
            res = requests.get(OPENFDA_URL, params={"search": search, "limit": 1}, timeout=8)
            if res.ok and res.json().get("results"):
                break
        else:
            return {}

        r = res.json()["results"][0]
        info = {}
        for field, key in [("warnings", "warnings"), ("drug_interactions", "interactions"),
                           ("adverse_reactions", "adverse_reactions"), ("storage_and_handling", "storage")]:
            val = r.get(field, r.get(field + "_and_cautions", []))
            if val:
                info[key] = (val[0] if isinstance(val, list) else str(val))[:200]

        print(f"[Aushadh AI] OpenFDA: found info for {drug_name}")
        return info
    except Exception as e:
        print(f"[Aushadh AI] OpenFDA error for {drug_name}: {e}")
        return {}


def enrich_with_fda(medications: list) -> list:
    for med in medications:
        fda = lookup_openfda(med.get("name", ""))
        if fda:
            med["fda_warnings"]     = fda.get("warnings", "")
            med["fda_interactions"] = fda.get("interactions", "")
            med["fda_side_effects"] = fda.get("adverse_reactions", "")
            med["storage"]          = fda.get("storage", "")
    return medications


async def enrich_with_fda_parallel(medications: list) -> list:
    """Enrich medications with OpenFDA data in parallel + use cache"""
    
    async def fetch_fda(med):
        name = med.get("name", "")
        clean = re.sub(r'\d+\s*(mg|ml|mcg|g|%)', '', name, flags=re.IGNORECASE).strip()
        clean = clean.split('/')[0].strip()
        
        if len(clean) < 3:
            return name, {}
        
        # Check cache first
        if name in OPENFDA_CACHE:
            return name, OPENFDA_CACHE[name]
        
        # Fetch in thread pool (requests is sync)
        def sync_fetch():
            for search in [f'openfda.generic_name:"{clean}"', f'openfda.generic_name:{clean}']:
                try:
                    res = requests.get(OPENFDA_URL, params={"search": search, "limit": 1}, timeout=8)
                    if res.ok and res.json().get("results"):
                        break
                except:
                    continue
            else:
                return {}
            
            r = res.json()["results"][0]
            info = {}
            for field, key in [("warnings", "warnings"), ("drug_interactions", "interactions"),
                               ("adverse_reactions", "adverse_reactions"), ("storage_and_handling", "storage")]:
                val = r.get(field, r.get(field + "_and_cautions", []))
                if val:
                    info[key] = (val[0] if isinstance(val, list) else str(val))[:200]
            return info
        
        try:
            result = await asyncio.to_thread(sync_fetch)
            if name and result:
                OPENFDA_CACHE[name] = result
            return name, result
        except Exception as e:
            print(f"[Aushadh AI] OpenFDA fetch error for {name}: {e}")
            return name, {}
    
    # Run all fetches in parallel
    tasks = [fetch_fda(med) for med in medications]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Apply results to medications
    for med in medications:
        med_name = med.get("name", "")
        for res in results:
            if isinstance(res, tuple) and res[0] == med_name and isinstance(res[1], dict):
                fda = res[1]
                med["fda_warnings"] = fda.get("warnings", "")
                med["fda_interactions"] = fda.get("interactions", "")
                med["fda_side_effects"] = fda.get("adverse_reactions", "")
                med["storage"] = fda.get("storage", "")
                break
    
    return medications


def check_drug_interactions(medications: list) -> list:
    pairs = []
    seen = set()
    for i, med in enumerate(medications):
        interactions_text = med.get("fda_interactions", "").lower()
        if not interactions_text:
            continue
        for j, other in enumerate(medications):
            if i == j:
                continue
            name = re.sub(r'\d+\s*(mg|ml|mcg|g|%)', '', other.get("name", ""), flags=re.IGNORECASE).strip().lower()
            if len(name) > 3 and name in interactions_text:
                key = tuple(sorted([i, j]))
                if key not in seen:
                    seen.add(key)
                    pairs.append({
                        "drug_a": med["name"],
                        "drug_b": other["name"],
                        "severity": "medium",
                        "description": interactions_text[:200]
                    })
    return pairs






# ── JSON Helpers ──────────────────────────────────────

def build_prompt(age: str, language: str, document: str) -> str:
    return f"""Patient age: {age or 'Not specified'}
Output language: {language}

Analyse this medical document and return ONLY this exact JSON. Start directly with {{

{{
  "confidence": 85,
  "confidence_note": "Brief note about document clarity",
  "summary_en": "One sentence plain English summary for family, max 25 words",
  "summary_hi": "Same summary in Hindi script",
  "diagnosis": {{
    "original_jargon": "Exact medical diagnosis terms from document",
    "simple_english": "2-4 sentences plain English explanation",
    "simple_hindi": "Same in Hindi script"
  }},
  "watch_for": {{
    "original": "Exact clinical observations from document",
    "simple": "Plain English what to watch for"
  }},
  "medications": [
    {{
      "name": "Exact medicine name (keep in original language)",
      "dosage": "e.g. 500mg (ALWAYS keep in English)",
      "timing": "e.g. Morning and Night (ALWAYS keep in English)",
      "duration": "e.g. 30 days (ALWAYS keep in English)",
      "with_food": "Yes/No/Before meals/After meals/As prescribed (ALWAYS keep in English)",
      "simple_instruction": "One plain sentence instruction in English ONLY",
      "simple_instruction_hi": "Same instruction in Hindi script ONLY"
    }}
  ],
  "side_effects": [
    {{"icon": "🚨 for high / ⚠️ for medium / 💊 for low", "text": "Side effect in plain language", "severity": "high|medium|low — classify accurately, not all low"}}
  ],
  "emergency": "Call doctor immediately if: [specific warning signs]",
  "checklist": [
    {{"category": "Follow-up", "text": "Action item", "done": false}}
  ],
  "recovery_days_min": 7,
  "recovery_days_max": 14,
  "recovery_note": "Plain sentence summary of recovery period",
  "patient_age": "from document or null",
  "patient_gender": "Male/Female/Other or null",
  "doctor_name": null,
  "doctor_specialty": null
}}

Medical Document:
{document}"""


def parse_json(raw: str) -> dict:
    raw = raw.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    raw = raw.strip()
    s = raw.find("{")
    e = raw.rfind("}") + 1
    if s != -1 and e > s:
        raw = raw[s:e]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as ex:
        raise Exception(f"Invalid JSON: {ex}\nRaw: {raw[:300]}")


# ── MAIN PIPELINE ─────────────────────────────────────

async def analyse_text(text: str, age: str, language: str) -> dict:
    print("[Aushadh AI] Step 1/3: Groq extraction...")
    raw = call_groq(build_prompt(age, language, text), SYSTEM)
    result = parse_json(raw)

    # OpenFDA enrichment (parallel + cached)
    try:
        print("[Aushadh AI] Step 2/3: OpenFDA enrichment (parallel)...")
        if result.get("medications"):
            result["medications"] = await enrich_with_fda_parallel(result["medications"])
    except Exception as e:
        print(f"[Aushadh AI] OpenFDA skipped: {e}")

    # Drug-drug interaction cross-check
    try:
        print("[Aushadh AI] Step 3/3: Drug interaction check...")
        result["drug_interactions"] = check_drug_interactions(result.get("medications", []))
        if result["drug_interactions"]:
            print(f"[Aushadh AI] Found {len(result['drug_interactions'])} interaction(s)")
    except Exception as e:
        print(f"[Aushadh AI] Interaction check skipped: {e}")
        result["drug_interactions"] = []

    result["pipeline"] = "Groq + OpenFDA"
    print("[Aushadh AI] Done! Groq + OpenFDA complete.")
    return result


async def analyse_image(data: bytes, media_type: str, age: str, language: str) -> dict:
    try:
        print(f"[Aushadh AI] Processing image: {len(data)} bytes, type: {media_type}")
        
        print("[Aushadh AI] Running OCR...")
        extracted_text = ocr_image(data)
        
        if extracted_text and len(extracted_text.strip()) >= 20:
            print(f"[Aushadh AI] OCR extracted {len(extracted_text)} chars")
            return await analyse_text(extracted_text, age, language)
        
        # Step 3: If OCR failed, show error
        raise Exception("Could not extract text from image. Please try with a clearer image or use text input.")
    except Exception as e:
        print(f"[Aushadh AI] Image analysis error: {str(e)}")
        raise Exception(str(e))


async def analyse_pdf(data: bytes, age: str, language: str) -> dict:
    try:
        text = extract_pdf_text(data)
        if len(text) < 100:
            raise Exception("Could not extract text from PDF. Please use 'Paste Text' instead.")
        return await analyse_text(text, age, language)
    except Exception as e:
        raise Exception(str(e))


async def analyse_medical_image(data: bytes, media_type: str, age: str, language: str, image_type: str = "X-ray") -> dict:
    """Analyze X-ray, MRI, CT scan - Azure primary, Gemini fallback, Groq last"""
    
    # First try with Azure (primary)
    if AZURE_VISION_KEY and AZURE_VISION_ENDPOINT:
        try:
            result = await _analyse_with_azure(data, media_type, age, language, image_type)
            return result
        except Exception as e:
            print(f"[Aushadh AI] Azure failed: {e}")
    
    # Second try with Gemini
    try:
        result = await _analyse_with_gemini(data, media_type, age, language, image_type)
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"[Aushadh AI] Gemini failed: {error_msg}")
    
    # Last fallback with Groq
    try:
        result = await _analyse_with_groq_vision(data, media_type, age, language, image_type)
        return result
    except Exception as groq_err:
        print(f"[Aushadh AI] Groq fallback also failed: {groq_err}")
    
    raise Exception("All image analysis services failed. Please try again later.")


async def _analyse_with_azure(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Analyze using Azure Computer Vision OCR + Groq for medical analysis"""
    if not AZURE_VISION_KEY or not AZURE_VISION_ENDPOINT:
        raise Exception("Azure not configured")
    
    print(f"[Aushadh AI] Analyzing {image_type} with Azure Vision...")
    
    base64_image = base64.b64encode(data).decode("utf-8")
    
    # Use Azure OCR to extract text from image
    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY
    }
    
    params = {
        "visualFeatures": "Categories,Description,Tags",
        "language": "en"
    }
    
    azure_url = f"{AZURE_VISION_ENDPOINT.rstrip('/')}/vision/v3.2/analyze"
    
    try:
        response = requests.post(azure_url, headers=headers, params=params, data=data, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"Azure API error: {response.status_code}")
        
        azure_result = response.json()
        print(f"[Aushadh AI] Azure OCR result: {json.dumps(azure_result)[:500]}")
        
        # Extract useful info from Azure
        categories = azure_result.get("categories", [])
        description = azure_result.get("description", {}).get("captions", [])
        tags = azure_result.get("tags", [])
        
        # Build context for Groq to analyze
        context_parts = []
        if categories:
            context_parts.append(f"Image categories: {', '.join([c.get('name', '') for c in categories[:5]])}")
        if description:
            context_parts.append(f"Image description: {description[0].get('text', '') if description else ''}")
        if tags:
            context_parts.append(f"Tags: {', '.join([t.get('name', '') for t in tags[:10]])}")
        
        context_parts.append(f"Patient age: {age or 'Not specified'}")
        context_parts.append(f"Image type: {image_type}")
        
        # Use Groq to generate medical analysis from Azure results
        prompt = f"""You are an expert radiologist. Based on Azure Computer Vision analysis of a medical image, provide a detailed medical report.

Azure Vision Analysis:
{chr(10).join(context_parts)}

Patient age: {age or 'Not specified'}
Image type: {image_type}
Language: {language}

Provide medical analysis in this JSON format:
{{
  "confidence": 75,
  "confidence_note": "Analysis based on image recognition",
  "summary_en": "Brief summary in English",
  "summary_hi": "Brief summary in Hindi",
  "diagnosis": {{
    "original_jargon": "Technical observations from image analysis",
    "simple_english": "Simple explanation in English",
    "simple_hindi": "Simple explanation in Hindi"
  }},
  "findings": [],
  "abnormalities": [],
  "watch_for": {{"original": "Key observations", "simple": "Plain warning signs"}},
  "emergency": "",
  "medications": [],
  "checklist": []
}}"""

        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 2000},
            timeout=45
        )
        
        if response.ok:
            raw = response.json()["choices"][0]["message"]["content"]
            result_data = parse_json(raw)
            result_data["pipeline"] = "Azure Vision + Groq"
            print(f"[Aushadh AI] Azure + Groq analysis complete")
            return result_data
        else:
            raise Exception("Groq failed to generate analysis")
            
    except Exception as e:
        raise Exception(f"Azure analysis failed: {str(e)}")


async def _analyse_with_gemini(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Analyze using Gemini Vision API - using vertex AI"""
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    print(f"[Aushadh AI] Analyzing {image_type} with Gemini Vision...")
    
    base64_image = base64.b64encode(data).decode("utf-8")
    
    prompt = f"""You are an expert radiologist analyzing medical images.

Patient age: {age or 'Not specified'}
Image type: {image_type}

TASK: Analyze this medical image and provide a detailed report in JSON format.

Output ONLY this exact JSON structure:
{{
  "confidence": 85,
  "confidence_note": "Note about image quality",
  "summary_en": "One sentence summary of findings in English",
  "summary_hi": "Same summary in Hindi script",
  "diagnosis": {{
    "original_jargon": "Technical radiological findings",
    "simple_english": "2-3 sentences explaining findings in plain English",
    "simple_hindi": "Same explanation in Hindi"
  }},
  "findings": [
    {{
      "area": "Area/body part examined",
      "observation": "What was observed",
      "severity": "normal|abnormal|critical"
    }}
  ],
  "abnormalities": [],
  "watch_for": {{
    "original": "Clinical observations requiring attention",
    "simple": "Plain English warning signs"
  }},
  "emergency": "",
  "medications": [],
  "checklist": []
}}"""

    # Try the updated API format
    # Use the correct model name - gemini-2.0-flash is available
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Updated payload format
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": media_type,
                        "data": base64_image
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 3500,
            "topP": 0.95,
            "topK": 40
        }
    }
    
    try:
        print(f"[Aushadh AI] Calling Gemini API...")
        response = requests.post(url, json=payload, timeout=120)
        
        print(f"[Aushadh AI] Response status: {response.status_code}")
        
        # Handle rate limits with multiple retries
        if response.status_code == 429:
            for wait_time in [15, 30, 60]:  # Wait 15s, 30s, 60s
                print(f"[Aushadh AI] Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
                response = requests.post(url, json=payload, timeout=120)
                if response.status_code != 429:
                    break
        
        if response.status_code == 404:
            # Try alternative model
            url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent?key={GEMINI_API_KEY}"
            print(f"[Aushadh AI] Trying alternative model...")
            response = requests.post(url2, json=payload, timeout=120)
        
        if response.status_code == 503:
            raise Exception("Gemini service temporarily unavailable (503)")
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text[:200]}")
        
        result = response.json()
        
        if "candidates" not in result or not result["candidates"]:
            raise Exception("No response from Gemini model")
        
        raw = result["candidates"][0]["content"]["parts"][0]["text"]
        
        result_data = parse_json(raw)
        result_data["pipeline"] = "Gemini Vision"
        
        print(f"[Aushadh AI] Success! Confidence: {result_data.get('confidence', 0)}%")
        return result_data
        
    except Exception as e:
        print(f"[Aushadh AI] Gemini error: {str(e)}")
        raise Exception(f"Gemini failed: {str(e)}")


async def _analyse_with_groq_vision(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Fallback: Use Groq with vision analysis via text description"""
    try:
        print(f"[Aushadh AI] Using Groq fallback for {image_type}...")
        
        # First extract text from image using OCR
        extracted_text = await extract_text_from_image(data, media_type)
        
        # Then use Groq to analyze the extracted text
        lang_suffix = "" if language == "English" else "_hi"
        
        prompt = f"""You are a medical expert. Analyze this medical image report/prescription.

Image type: {image_type}
Patient age: {age or 'Not specified'}

Extracted text from image:
{extracted_text[:2000]}

Provide a medical analysis in JSON format:
{{
  "confidence": 80,
  "confidence_note": "Analysis based on extracted text",
  "summary_en": "Brief summary in English",
  "summary_hi": "Summary in Hindi",
  "diagnosis": {{
    "original_jargon": "Original medical terms found",
    "simple_english": "Simple explanation in English",
    "simple_hindi": "Simple explanation in Hindi"
  }},
  "findings": [],
  "abnormalities": [],
  "watch_for": {{"original": "", "simple": ""}},
  "emergency": "",
  "medications": [],
  "checklist": []
}}"""

        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 2000},
            timeout=60
        )
        
        if not response.ok:
            raise Exception(f"Groq API error: {response.status_code}")
        
        raw = response.json()["choices"][0]["message"]["content"]
        result_data = parse_json(raw)
        result_data["pipeline"] = "Groq Text Analysis (Fallback)"
        
        print(f"[Aushadh AI] Groq fallback analysis complete")
        return result_data
        
    except Exception as e:
        raise Exception(f"Groq fallback failed: {str(e)}")


async def chat_reply(message: str, history: list, context: dict, language: str) -> tuple[str, list]:
    # Handle context - it might be a string or already a dict
    if isinstance(context, str):
        try:
            context = json.loads(context)
        except:
            context = {}
    
    if not context or not isinstance(context, dict):
        if language.lower() == "hindi":
            return "अभी तक कोई prescription upload नहीं किया गया है। सवाल पूछने से पहले कृपया prescription upload करें।", []
        return "No prescription has been uploaded yet. Please upload a prescription first to ask questions.", []
    
    # Build comprehensive context from prescription data
    ctx_parts = []
    
    if context.get('diagnosis'):
        dx = context['diagnosis']
        ctx_parts.append(f"DIAGNOSIS:\n- Original: {dx.get('original_jargon', 'N/A')}\n- Simple: {dx.get('simple_english', 'N/A')}")
    
    if context.get('medications'):
        ctx_parts.append("\nMEDICATIONS:")
        for med in context['medications']:
            if isinstance(med, dict):
                name = med.get('name', 'Unknown')
                dosage = med.get('dosage', '')
                timing = med.get('timing', '')
                duration = med.get('duration', '')
                ctx_parts.append(f"- {name}: {dosage} - {timing} for {duration}")
                if med.get('simple_instruction'):
                    ctx_parts.append(f"  Instructions: {med.get('simple_instruction')}")
            else:
                ctx_parts.append(f"- {str(med)}")
    
    if context.get('side_effects'):
        ctx_parts.append("\nSIDE EFFECTS TO WATCH:")
        for se in context['side_effects']:
            if isinstance(se, dict):
                severity = se.get('severity', '').upper()
                ctx_parts.append(f"- [{severity}] {se.get('text', '')}")
            else:
                ctx_parts.append(f"- {str(se)}")
    
    if context.get('emergency'):
        ctx_parts.append(f"\nEMERGENCY WARNINGS: {context.get('emergency')}")
    
    if context.get('checklist'):
        ctx_parts.append("\nFOLLOW-UP CHECKLIST:")
        for item in context['checklist'][:10]:
            if isinstance(item, dict):
                ctx_parts.append(f"- [{item.get('category', 'General')}] {item.get('text', str(item))}")
            else:
                ctx_parts.append(f"- {str(item)}")
    
    if context.get('recovery_note'):
        ctx_parts.append(f"\nRECOVERY: {context.get('recovery_note')}")
    
    ctx = "\n".join(ctx_parts)
    
    # Set messages based on language
    if language.lower() == "hindi":
        not_found_msg = "यह जानकारी आपकी prescription में नहीं है, कृपया अपने डॉक्टर से पूछें।"
        medical_refuse = "मैं Aushadh AI हूँ, मैं सिर्फ आपकी prescription के बारे में जानकारी दे सकता हूँ। कृपया अपनी prescription से जुड़े सवाल पूछें।"
    else:
        not_found_msg = "This information is not in your prescription, please ask your doctor."
        medical_refuse = "I'm Aushadh AI. I can only answer questions about your prescription. Please ask medical questions related to your prescription."
    
    system = f"""You are Aushadh AI, a medical assistant for patients.

PRESCRIPTION DATA:
{ctx}

CRITICAL RULES:
1. Answer ONLY from PRESCRIPTION DATA above. NOTHING ELSE.
2. If the question is NOT answered in the prescription data above, ONLY reply: "{not_found_msg}"
3. Do NOT add any additional information when using rule 2.
4. If question is not medical/prescription related, ONLY reply: "{medical_refuse}"
5. Keep answers simple and concise.
6. If answering about medications, include: name, dosage, timing.

Reply in {language}. JUST reply with your answer text only. DO NOT use JSON format."""

    try:
        msgs = [{"role": "system", "content": system}]
        for m in history[-8:]:
            msgs.append({"role": m["role"], "content": m["content"]})
        msgs.append({"role": "user", "content": message})
        res = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json", "User-Agent": "Aushadh AIApp/1.0"},
            json={"model": GROQ_MODEL, "messages": msgs, "temperature": 0.3, "max_tokens": 1500},
            timeout=45
        )
        if not res.ok:
            raise Exception(f"Chat error: {res.text}")
        raw = res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        return "Sorry, I'm having trouble responding right now. Please try again in a moment.", []

    raw = raw.strip()
    # Clean up JSON artifacts
    if raw.startswith("{"):
        try:
            d = json.loads(raw)
            if isinstance(d, dict) and "reply" in d:
                return d.get("reply", ""), []
        except:
            pass
    # Remove common formatting
    for art in ['{"reply": "', '{"reply": "', '```json', '```', '"}', '"}]}']:
        if raw.startswith(art) or raw.endswith(art):
            raw = raw.replace(art, "")
    return raw.strip(), []
