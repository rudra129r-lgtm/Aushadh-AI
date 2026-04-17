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

# System prompt for vision/OCR - medical document extraction
VISION_SYSTEM = """You are an expert at reading handwritten and printed medical prescriptions from India.

TASK: Extract ALL information from this medical document and format as JSON.

COMMON PRESCRIPTION PATTERNS:
- Medicine forms: Tab (tablet), Cap (capsule), Syp (syrup), Inj (injection), Cre/Cream, Lot (lotion), Dt (dissolve tablet), Gran (granules)
- Timing: Morning/M/Morn, Afternoon/A, Evening/E, Night/N/HS (at bedtime), empty stomach (AC)
- Frequency: OD (once daily), BD/TW (twice daily), TDS/TDS/3D (3 times daily), QID (4 times daily), SOS (when needed), PRN (as needed)
- With food: PC (after food), AC (before food), with food, with milk, with water
- Dosage units: mg, ml, g, mcg, IU, units, drops
- Duration: days, weeks, months, until review

CRITICAL RULES:
1. Read VERY carefully - some text may be faint, overlapping, or handwritten
2. Extract EXACT medicine names as written - common brands: Crocin, Dolo, Augmentin, Glucored, Janumet, Metformin, Azithromycin, Omeprazole, etc.
3. If text is unclear, note "Cannot read" - DO NOT guess or make up information
4. For timing abbreviations: OD=once, BD=twice, TDS=three times, QID=four times
5. Extract dosage exactly as written (e.g., "500mg", "650mg", "10ml")
6. Look for duration: "for 5 days", "for 1 week", "for 1 month", "until review"
7. Extract patient name, age, gender, date, doctor name, hospital/clinic name
8. Extract any tests/investigations: blood tests, X-ray, ECG, ultrasound, etc.
9. Extract all advice: diet restrictions, exercise limits, follow-up instructions

Output ONLY valid JSON. Start with { and end with }"""

# System prompt for text analysis - medical document simplifier
SYSTEM = """You are Aushadh AI, a strict medical document simplifier for Indian patients.

CRITICAL RULES:
1. Extract ONLY what is written in the document — never add outside advice
2. Medications must EXACTLY match the document — never change dosages
3. If info is missing use "Not specified" — never invent
4. Return ONLY raw JSON — no markdown, no code blocks
5. Your response must be valid JSON starting with { and ending with }
6. Extract tests/investigations separately from medications

SIDEEFFECTS SEVERITY (classify EACH accurately, never default all to 'low'):
- HIGH 🚨: difficulty breathing, severe rash/hives, chest pain, swelling of face/throat, severe vomiting - needs IMMEDIATE hospital
- MEDIUM ⚠️: nausea, vomiting, dizziness, severe headache, diarrhea - monitor and contact doctor if worsens
- LOW 💊: mild stomach upset, slight drowsiness, dry mouth, mild headache - usually temporary

7. plain_english explanations: 2-4 sentences, conversational, family-friendly
8. side_effects: extract from medications listed - top 2-3 warnings with accurate severity
9. checklist: tests, diet, activity limits, follow-up, medicine reminders
10. For antibiotics: ALWAYS include "complete full course" in checklist
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

Analyse this medical document and return ONLY this exact JSON structure. Start directly with {{

CONFIDENTIALITY SCORING:
- 90-100: Clear printed prescription, all details visible, easy to read
- 70-89: Mostly clear, minor unclear text, minor handwriting issues
- 50-69: Several unclear items, partial extraction possible
- Below 50: Mostly unclear, significant guessing required, mention what was unreadable

{{
  "confidence": 85,
  "confidence_note": "Brief note about document clarity (e.g., 'Clear printed text', 'Some handwritten portions unclear')",
  "summary_en": "One sentence plain English summary for family - max 25 words, no jargon",
  "summary_hi": "Same summary in Hindi script (देवनागरी)",
  "diagnosis": {{
    "original_jargon": "Exact medical diagnosis/condition as written in document",
    "simple_english": "2-3 sentences plain English explanation - what this means for the patient",
    "simple_hindi": "Same explanation in Hindi script"
  }},
  "watch_for": {{
    "original": "Exact clinical observations, vitals, or concerns noted by doctor",
    "simple": "Plain English - what symptoms or signs the patient should watch for"
  }},
  "medications": [
    {{
      "name": "Exact medicine name as written (e.g., 'Dolo 650', 'Metformin 500', 'Augmentin 625')",
      "dosage": "Always in English (e.g., '500mg', '650mg', '10ml', '2 drops')",
      "timing": "Clear English (e.g., 'Morning and Night', 'Three times daily after meals', 'At bedtime')",
      "duration": "Always in English (e.g., '7 days', '2 weeks', '1 month', 'Until review')",
      "with_food": "Before meals / After meals / With food / With milk / As prescribed / Not specified",
      "simple_instruction": "One sentence in plain English (e.g., 'Take one tablet after breakfast with water')",
      "simple_instruction_hi": "Same instruction in Hindi script"
    }}
  ],
  "side_effects": [
    {{
      "icon": "🚨 for HIGH / ⚠️ for MEDIUM / 💊 for LOW",
      "text": "Side effect in plain language (e.g., 'May cause drowsiness', 'Nausea if taken empty stomach')",
      "severity": "HIGH / MEDIUM / LOW - classify EACH side effect accurately"
    }}
  ],
  "emergency": "Seek emergency care if: [specific warning signs from document, e.g., 'difficulty breathing, swelling of face/throat, severe vomiting']",
  "checklist": [
    {{"category": "Follow-up", "text": "e.g., 'Review with doctor in 1 week', 'Get blood tests done'}},
    {{"category": "Diet", "text": "e.g., 'Avoid oily food', 'Take light meals', 'Avoid alcohol'}},
    {{"category": "Activity", "text": "e.g., 'Complete bed rest for 3 days', 'No strenuous exercise for 1 week'}},
    {{"category": "Test", "text": "e.g., 'Complete blood count after 1 week', 'Follow-up X-ray in 1 month'}},
    {{"category": "Medicine", "text": "e.g., 'Complete full antibiotic course even if feeling better', 'Store in cool place'"}}
  ],
  "recovery_days_min": null,
  "recovery_days_max": null,
  "recovery_note": "Brief note about expected recovery (e.g., 'Most symptoms improve within 1-2 weeks with proper rest and medication')",
  "patient_age": "Patient age from document or null",
  "patient_gender": "Male / Female / Other / null",
  "doctor_name": "Doctor name from document or null",
  "doctor_specialty": "Doctor specialty (e.g., Cardiologist, General Physician) or null"
}}

Medical Document:
{document}"""


def detect_medical_modality(image_data: bytes) -> str:
    """
    Analyze image characteristics to detect medical imaging modality.
    Returns: 'xray', 'mri', 'ct', 'ultrasound', 'unknown'
    """
    try:
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to grayscale for analysis
        if img.mode != 'L':
            gray = img.convert('L')
        else:
            gray = img
        
        # Use getdata() for compatibility with older PIL
        try:
            pixels = list(gray.getdata())
        except:
            pixels = list(gray.get_flattened_data())
        
        width, height = img.size
        
        # Calculate histogram
        histogram = [0] * 256
        for p in pixels:
            if isinstance(p, tuple):
                p = p[0]
            histogram[p] += 1
        
        total_pixels = len(pixels)
        
        # Calculate brightness metrics
        mean_brightness = sum(p * histogram[p] for p in range(256)) / total_pixels
        
        # Calculate contrast (standard deviation)
        variance = sum(((p - mean_brightness) ** 2) * histogram[p] for p in range(256)) / total_pixels
        std_dev = variance ** 0.5
        
        # Calculate dark pixel ratio (common in X-ray)
        dark_pixels = sum(histogram[p] for p in range(0, 50))
        dark_ratio = dark_pixels / total_pixels
        
        # Calculate bright pixel ratio (bone in X-ray)
        bright_pixels = sum(histogram[p] for p in range(200, 256))
        bright_ratio = bright_pixels / total_pixels
        
        # Calculate mid-tone distribution
        mid_pixels = sum(histogram[p] for p in range(80, 180))
        mid_ratio = mid_pixels / total_pixels
        
        # Count histogram peaks (multiple peaks = likely MRI)
        peak_count = 0
        prev_count = histogram[0]
        for p in range(1, 255):
            curr_count = histogram[p]
            next_count = histogram[p + 1] if p < 255 else 0
            if curr_count > prev_count and curr_count > next_count and curr_count > total_pixels * 0.005:
                peak_count += 1
            prev_count = curr_count
        
        # Edge detection for text detection (common in ultrasound with measurements)
        try:
            from PIL import ImageFilter
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_pixels = list(edges.getdata())
            high_edge_pixels = sum(1 for p in edge_pixels if p > 30)
            edge_ratio = high_edge_pixels / total_pixels
        except:
            edge_ratio = 0
        
        # Detection logic - more refined thresholds
        print('[Aushadh AI] Image stats: dark=' + str(round(dark_ratio,2)) + ', mid=' + str(round(mid_ratio,2)) + ', std=' + str(round(std_dev,1)) + ', peaks=' + str(peak_count) + ', edges=' + str(round(edge_ratio,3)))
        
        # Priority 1: CT - very uniform grayscale (very high mid, very low contrast)
        # CT scans have very uniform density distribution (cross-sectional)
        if mid_ratio > 0.7 and std_dev < 40 and dark_ratio < 0.2:
            print('[Aushadh AI] Detected: CT (uniform cross-section)')
            return 'ct'
        
        # Priority 2: X-ray - high contrast with dark background (bone imaging)
        # Classic X-ray has dark background with bright bones/structures
        if dark_ratio > 0.3 and std_dev > 50 and peak_count < 5:
            print('[Aushadh AI] Detected: X-ray (high contrast skeletal)')
            return 'xray'
        
        # Priority 3: MRI - multiple tissue intensities (many peaks, moderate contrast)
        # MRI shows different tissue types with varying signal intensities
        if peak_count >= 6 and std_dev > 45:
            print('[Aushadh AI] Detected: MRI (multiple tissue intensities)')
            return 'mri'
        
        # Priority 4: Ultrasound - typically has measurement text overlays
        # Ultrasound images often have text annotations and measurement markers
        if edge_ratio > 0.35 and bright_ratio < 0.15:
            print('[Aushadh AI] Detected: Ultrasound (measurement overlays)')
            return 'ultrasound'
        
        # Fallback: default to X-ray as most common
        print('[Aushadh AI] Detected: Unknown (defaulting to X-ray)')
        return 'unknown'
        
    except Exception as e:
        print('[Aushadh AI] Modality detection error: ' + str(e))
        return 'unknown'


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


async def analyse_medical_image(data: bytes, media_type: str, age: str, language: str, image_type: str = None) -> dict:
    """Analyze X-ray, MRI, CT scan using multi-model ensemble for best accuracy"""
    
    # If no image_type provided, let AI auto-detect
    if not image_type:
        image_type = "auto-detect"
        print(f"[Aushadh AI] No image type specified, will auto-detect from image content")
    
    # Use ensemble for better accuracy
    return await analyse_medical_image_ensemble(data, media_type, age, language, image_type)


async def analyse_medical_image_ensemble(data: bytes, media_type: str, age: str, language: str, image_type: str = None) -> dict:
    if not image_type:
        image_type = 'auto-detect'
    
    print('[Aushadh AI] Starting medical image analysis with Azure...')
    
    tasks = {}
    
    if AZURE_VISION_KEY and AZURE_VISION_ENDPOINT:
        tasks['azure'] = asyncio.create_task(
            _analyse_with_azure_safe(data, media_type, age, language, image_type)
        )
    
    results = {}
    for name, task in tasks.items():
        try:
            result = await task
            if result:
                results[name] = result
                print('[Aushadh AI] ' + name.upper() + ' completed: confidence=' + str(result.get('confidence', 0)) + '%')
        except Exception as e:
            print('[Aushadh AI] ' + name.upper() + ' failed: ' + str(e))
    
    if not results:
        raise Exception('Azure analysis failed. Please try again.')
    
    merged = _consensus_merge(results, language)
    merged['pipeline'] = 'Azure Vision Analysis'
    merged['ensemble_results'] = results
    merged['ensemble_models_count'] = len(results)
    
    print('[Aushadh AI] Analysis complete: Azure succeeded')
    return merged


async def _analyse_with_azure_safe(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Safe wrapper for Azure analysis"""
    try:
        return await _analyse_with_azure(data, media_type, age, language, image_type)
    except Exception as e:
        print(f"[Aushadh AI] Azure safe wrapper error: {e}")
        return None


async def _analyse_with_gemini_safe(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Safe wrapper for Gemini analysis"""
    try:
        return await _analyse_with_gemini(data, media_type, age, language, image_type)
    except Exception as e:
        print(f"[Aushadh AI] Gemini safe wrapper error: {e}")
        return None


async def _analyse_with_groq_vision_safe(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Safe wrapper for Groq vision analysis"""
    try:
        return await _analyse_with_groq_vision(data, media_type, age, language, image_type)
    except Exception as e:
        print(f"[Aushadh AI] Groq safe wrapper error: {e}")
        return None


def _consensus_merge(results: dict, language: str) -> dict:
    if not results:
        return {'error': 'No results to merge'}
    
    model_weights = {'azure': 1.5}
    
    weighted_sum = 0
    weight_total = 0
    for name, r in results.items():
        weight = model_weights.get(name, 1.0)
        conf = r.get('confidence', 0)
        weighted_sum += conf * weight
        weight_total += weight
    
    avg_confidence = weighted_sum / weight_total if weight_total > 0 else 50
    
    winning_model = max(results.items(), key=lambda x: x[1].get('confidence', 0))[0] if results else 'unknown'
    
    diagnoses = [r.get('diagnosis', {}).get('original_jargon', '').lower() for r in results.values() if r]
    models_agree = len(set(diagnoses)) <= 1 if diagnoses else False
    
    all_findings = []
    seen_areas = set()
    for r in results.values():
        for f in r.get('findings', []):
            area = f.get('area', '').lower()
            if area and area not in seen_areas:
                all_findings.append(f)
                seen_areas.add(area)
            elif not area:
                all_findings.append(f)
    
    all_abnormalities = []
    seen_ab = set()
    for r in results.values():
        for ab in r.get('abnormalities', []):
            ab_text = str(ab).lower()
            if ab_text and ab_text not in seen_ab:
                all_abnormalities.append(ab)
                seen_ab.add(ab_text)
    
    emergency_msgs = []
    for r in results.values():
        em = r.get('emergency', '')
        if em and em not in emergency_msgs:
            emergency_msgs.append(em)
    merged_emergency = ' | '.join(emergency_msgs) if emergency_msgs else ''
    
    winning = results.get(winning_model, results.get(list(results.keys())[0], {}))
    
    agreement = 'agree' if models_agree else 'disagree'
    
    merged = {
        'confidence': round(avg_confidence),
        'confidence_note': f'Ensemble of {len(results)} models. Azure prioritized. Models {agreement} on diagnosis.',
        'ensemble_confidence_avg': round(avg_confidence),
        'winning_model': winning_model,
        'models_agree': models_agree,
        'models_disagree': not models_agree and len(results) > 1,
        'summary_en': winning.get('summary_en', ''),
        'summary_hi': winning.get('summary_hi', ''),
        'diagnosis': winning.get('diagnosis', {}),
        'findings': all_findings,
        'abnormalities': all_abnormalities,
        'watch_for': winning.get('watch_for', {'original': '', 'simple': ''}),
        'emergency': merged_emergency,
        'medications': winning.get('medications', []),
        'checklist': winning.get('checklist', [])
    }
    
    return merged


async def _analyse_with_azure(data: bytes, media_type: str, age: str, language: str, image_type: str) -> dict:
    """Analyze using Azure Computer Vision OCR + Groq for medical analysis"""
    if not AZURE_VISION_KEY or not AZURE_VISION_ENDPOINT:
        raise Exception("Azure not configured")
    
    # Auto-detect medical image modality
    detected_modality = detect_medical_modality(data)
    if detected_modality != 'unknown':
        actual_type = detected_modality
    elif image_type and image_type != 'auto-detect':
        actual_type = image_type
    else:
        actual_type = 'unknown'
    
    # If modality cannot be determined, return friendly error message
    if actual_type == 'unknown':
        print('[Aushadh AI] Could not determine image modality')
        return {
            'confidence': 0,
            'summary_en': 'Unable to determine image modality. Please try with a clearer medical image or specify the image type (X-ray, MRI, CT, Ultrasound).',
            'summary_hi': 'छवि का प्रकार निर्धारित करने में असमर्थ। कृपया एक स्पष्ट चिकित्सा छवि का प्रयास करें या छवि का प्रकार निर्दिष्ट करें।',
            'modality_detected': 'unknown',
            'diagnosis': {
                'original_jargon': 'Image modality could not be determined',
                'simple_english': 'Could not identify what type of medical image this is',
                'simple_hindi': 'इस चिकित्सा छवि का प्रकार पहचान नहीं सका'
            },
            'findings': [],
            'abnormalities': [],
            'watch_for': {'original': '', 'simple': ''},
            'emergency': '',
            'medications': [],
            'checklist': [],
            'error': 'Could not determine image modality'
        }
    
    print('[Aushadh AI] Analyzing ' + actual_type + ' with Azure Vision (auto-detected)...')
    
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
            raise Exception(f"Azure API error: {response.status_code} - {response.text[:300]}")
        
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
        context_parts.append('Image modality: ' + actual_type)
        
# Use Groq to generate medical analysis from Azure results
        prompt = f'''You are a board-certified radiologist with 15+ years of experience in diagnostic imaging.

CONTEXT:
- Patient age: {age or 'Not specified'}
- Image modality: {actual_type}

IMPORTANT: This is a {actual_type.upper()} image. Analyze it specifically as {actual_type.upper()}.

AZURE VISION ANALYSIS:
{chr(10).join(context_parts)}

MODALITY-SPECIFIC ANALYSIS:
For X-RAY: Focus on bones, lungs, heart, joints. Common findings: pneumonia, TB, fractures, cardiomegaly
For MRI: Focus on soft tissues, brain, spine, organs. Common findings: hemorrhage, tumors, disc issues
For CT: Focus on cross-sectional anatomy, internal organs. Common findings: bleeding, organ damage, stones
For ULTRASOUND: Focus on organ morphology, measurements, fluid. Common findings: cysts, stones, fluid

EMERGENCY INDICATORS (flag as CRITICAL if present):
- Pneumoperitoneum, pleural effusion, pneumothorax
- Cardiomegaly, pulmonary edema
- Fractures (especially skull, spine)
- Mass lesions, tumors
- Bowel obstruction, free fluid
- Brain hemorrhage, mass effect

SEVERITY GUIDELINES:
- NORMAL: No abnormality detected
- MILD: Minor findings, likely benign, follow-up recommended
- MODERATE: Significant findings requiring attention
- SEVERE: Serious findings needing prompt medical review
- CRITICAL: Emergency findings requiring immediate action

CRITICAL INSTRUCTIONS:
1. Output VALID JSON with double quotes only
2. Use 5-tier severity: normal, mild, moderate, severe, critical
3. For emergency findings, set severity to "critical" and include in emergency field
4. summary_en should be 1-2 sentences, family-friendly, no jargon

OUTPUT ONLY valid JSON (double quotes required):
{{
  "confidence": 80,
  "confidence_note": "Brief note about image quality and analysis confidence",
  "modality_detected": "{actual_type}",
  "summary_en": "One sentence summary - what was found and what it means for the patient in plain English",
  "summary_hi": "Same summary in Hindi script (देवनागरी)",
  "diagnosis": {{
    "original_jargon": "Technical radiological findings as reported",
    "simple_english": "2-3 sentences plain English explanation of what this means",
    "simple_hindi": "Same explanation in Hindi script"
  }},
  "findings": [
    {{"area": "Body part/region examined", "observation": "What was observed", "severity": "normal|mild|moderate|severe|critical"}}
  ],
  "abnormalities": ["List of abnormal findings that need attention"],
  "watch_for": {{
    "original": "Clinical observations from report",
    "simple": "Warning signs patient should watch for in plain English"
  }},
  "emergency": "Emergency signs to watch for (e.g., 'Seek emergency care if symptoms worsen, new weakness develops, or severe pain occurs')",
  "medications": [],
  "checklist": [
    {{"category": "Follow-up", "text": "e.g., 'Review imaging report with doctor within 1 week'"}},
    {{"category": "Test", "text": "e.g., 'Additional tests may be recommended based on findings'"}}
  ]
}}'''
        
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
    
    prompt = f"""You are an expert radiologist analyzing medical images for Indian patients.

Patient age: {age or 'Not specified'}
Image type: {image_type if image_type != 'auto-detect' else 'Detect the image type from the image (X-ray, MRI, CT, Ultrasound, etc.)'}

TASK: First identify what type of medical image this is, then analyze it and provide a detailed report in JSON format.

MODALITY-SPECIFIC ANALYSIS:
For X-RAY: Focus on bones, lungs, heart, joints. Common findings: pneumonia, TB, fractures, cardiomegaly
For MRI: Focus on soft tissues, brain, spine, organs. Common findings: hemorrhage, tumors, disc issues
For CT: Focus on cross-sectional anatomy, internal organs. Common findings: bleeding, organ damage, stones
For ULTRASOUND: Focus on organ morphology, measurements, fluid. Common findings: cysts, stones, fluid

EMERGENCY INDICATORS (flag as CRITICAL if present):
- Pneumoperitoneum, pleural effusion, pneumothorax
- Cardiomegaly, pulmonary edema
- Fractures (especially skull, spine)
- Mass lesions, tumors
- Bowel obstruction, free fluid
- Brain hemorrhage, mass effect

SEVERITY GUIDELINES:
- NORMAL: No abnormality detected
- MILD: Minor findings, likely benign, follow-up recommended
- MODERATE: Significant findings requiring attention
- SEVERE: Serious findings needing prompt medical review
- CRITICAL: Emergency findings requiring immediate action

CRITICAL INSTRUCTIONS:
1. Output VALID JSON with double quotes only - no markdown code blocks
2. Use 5-tier severity: normal, mild, moderate, severe, critical
3. For emergency findings, set severity to "critical" and include warning in emergency field
4. summary_en should be 1-2 sentences, family-friendly, no medical jargon
5. For Hindi fields, use Hindi script (देवनागरी), not transliterated Hindi

OUTPUT ONLY this exact JSON structure:
{{
  "confidence": 85,
  "confidence_note": "Brief note about image quality and analysis confidence",
  "summary_en": "One sentence summary - what was found and what it means for the patient in plain English",
  "summary_hi": "Same summary in Hindi script (देवनागरी)",
  "diagnosis": {{
    "original_jargon": "Technical radiological findings as reported",
    "simple_english": "2-3 sentences plain English explanation of what this means",
    "simple_hindi": "Same explanation in Hindi script"
  }},
  "findings": [
    {{
      "area": "Body part/region examined",
      "observation": "What was observed",
      "severity": "normal|mild|moderate|severe|critical"
    }}
  ],
  "abnormalities": ["List of abnormal findings that need attention"],
  "watch_for": {{
    "original": "Clinical observations from report",
    "simple": "Warning signs patient should watch for in plain English"
  }},
  "emergency": "Emergency signs to watch for (e.g., 'Seek emergency care if symptoms worsen, new weakness develops, or severe pain occurs')",
  "medications": [],
  "checklist": [
    {{"category": "Follow-up", "text": "e.g., 'Review imaging report with doctor within 1 week'"}},
    {{"category": "Test", "text": "e.g., 'Additional tests may be recommended based on findings'"}}
  ]
}}"""

    # Try the updated API format
    # Use the correct model name - gemini-1.5-flash is available
    gemini_models = [("v1", "gemini-2.0-flash-exp"), ("v1", "gemini-2.0-flash"), ("v1", "gemini-1.5-flash")]
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    
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
            url2 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
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
        
        prompt = f"""You are a medical expert. Analyze this medical image report/prescription for Indian patients.

Image type: {image_type}
Patient age: {age or 'Not specified'}

Extracted text from image:
{extracted_text[:2000]}

INSTRUCTIONS:
1. Analyze the extracted text and provide medical findings
2. Output VALID JSON with double quotes only
3. summary_en should be 1-2 sentences, family-friendly, no jargon
4. For Hindi fields, use Hindi script (देवनागरी)

Provide a medical analysis in JSON format:
{{
  "confidence": 80,
  "confidence_note": "Note about analysis confidence based on text extraction quality",
  "summary_en": "One sentence summary in plain English",
  "summary_hi": "Same summary in Hindi script (देवनागरी)",
  "diagnosis": {{
    "original_jargon": "Technical medical terms from report",
    "simple_english": "2-3 sentences plain English explanation",
    "simple_hindi": "Same explanation in Hindi script"
  }},
  "findings": [
    {{"area": "Body part", "observation": "What was observed", "severity": "normal|mild|moderate|severe|critical"}}
  ],
  "abnormalities": ["List of abnormal findings"],
  "watch_for": {{"original": "Clinical observations", "simple": "Warning signs in plain English"}},
  "emergency": "Emergency signs to watch for",
  "medications": [],
  "checklist": [
    {{"category": "Follow-up", "text": "Review with doctor"}}
  ]
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
    
    system = f"""You are Aushadh AI, a friendly medical assistant for Indian patients.

PRESCRIPTION DATA:
{ctx}

CRITICAL RULES:
1. Answer ONLY from PRESCRIPTION DATA above. NOTHING ELSE.
2. If the question is NOT answered in the prescription data above, ONLY reply: "{not_found_msg}"
3. Do NOT add any additional information when using rule 2.
4. If question is not medical/prescription related, ONLY reply: "{medical_refuse}"
5. Keep answers simple, clear, and encouraging.
6. If answering about medications, include: medicine name, dosage, when to take, how to take (with food/before/after).
7. Use simple language - patients may not understand medical terms.
8. If asking about side effects, explain in plain terms what to expect and when to worry.

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
