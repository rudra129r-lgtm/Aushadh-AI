"""
OCR Service - Google Cloud Vision API (Primary) + OCR.space (Fallback)
======================================================================
Google Cloud Vision has excellent handwriting recognition (1,000 free req/month)
"""

import io
import base64
import requests
import logging
from PIL import Image, ImageEnhance, ImageFilter
import os

logger = logging.getLogger(__name__)

OCR_SPACE_API_KEY = None
OCR_SPACE_URL = "https://api.ocr.space/parse/image"

GOOGLE_VISION_AVAILABLE = False
vision_client = None


def init_ocr():
    global OCR_SPACE_API_KEY, GOOGLE_VISION_AVAILABLE, vision_client
    
    from dotenv import load_dotenv
    load_dotenv()
    
    OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "")
    
    # Try to initialize Google Cloud Vision
    try:
        from google.cloud import vision
        import json
        
        GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
        
        print(f"[OCR] Debug - GOOGLE_APPLICATION_CREDENTIALS: {'set' if GOOGLE_APPLICATION_CREDENTIALS else 'empty'}")
        print(f"[OCR] Debug - GOOGLE_APPLICATION_CREDENTIALS_JSON: {'set' if creds_json else 'empty'}")
        
        google_ok = False
        if not GOOGLE_APPLICATION_CREDENTIALS and not creds_json:
            print("[OCR] WARNING: Google credentials not found")
            print("[OCR] Falling back to OCR.space")
        else:
            # Check if it's JSON content or a file path
            if creds_json and creds_json.strip().startswith("{"):
                import tempfile
                creds_path = os.path.join(tempfile.gettempdir(), "google_credentials.json")
                with open(creds_path, "w") as f:
                    f.write(creds_json)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
                print(f"[OCR] Google credentials loaded from env var")
                google_ok = True
            elif GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
                print(f"[OCR] Google credentials loaded from file")
                google_ok = True
            else:
                print("[OCR] Google credentials file not found, using OCR.space")
            
            if google_ok:
                vision_client = vision.ImageAnnotatorClient()
                GOOGLE_VISION_AVAILABLE = True
                print("[OCR] Google Cloud Vision API initialized")
    except ImportError:
        print("[OCR] google-cloud-vision not installed. Run: pip install google-cloud-vision")
        print("[OCR] Using OCR.space only (limited handwriting support)")
    except Exception as e:
        print(f"[OCR] Error initializing: {e}")
    
    if OCR_SPACE_API_KEY:
        print("[OCR] OCR.space API loaded")


def preprocess_image_for_ocr(image_bytes: bytes) -> bytes:
    """Enhance image for better OCR results - especially for handwritten text"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to grayscale for better text extraction
        img = img.convert('L')
        
        # Increase contrast significantly
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Sharpen the image
        img = img.filter(ImageFilter.SHARPEN)
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logger.warning(f"[OCR] Image preprocessing failed: {e}")
        return image_bytes


def extract_text_google_vision(image_bytes: bytes) -> dict:
    """Extract text using Google Cloud Vision API (better for handwriting)"""
    global vision_client
    
    try:
        from google.cloud import vision as gvision
        
        logger.info("[OCR] Calling Google Cloud Vision API...")
        
        # Preprocess image
        enhanced_bytes = preprocess_image_for_ocr(image_bytes)
        
        image = gvision.Image(content=enhanced_bytes)
        
        # Use document_text_detection for full text extraction (better for handwriting)
        response = vision_client.document_text_detection(image=image)
        
        if response.error and response.error.message:
            logger.error(f"[OCR] Google Vision error: {response.error.message}")
            return {"text": None, "method": "google_vision", "error": response.error.message}
        
        # Extract full text
        full_text = ""
        if response.full_text_annotation:
            full_text = response.full_text_annotation.text
        
        if full_text and len(full_text.strip()) >= 10:
            logger.info(f"[OCR] Google Vision extracted {len(full_text)} chars")
            return {"text": full_text, "method": "google_vision"}
        
        logger.warning(f"[OCR] Google Vision returned empty/short text: '{full_text[:100] if full_text else 'None'}'")
        return {"text": None, "method": "google_vision", "error": "No text detected"}
        
    except Exception as e:
        logger.error(f"[OCR] Google Vision error: {e}")
        return {"text": None, "method": "google_vision", "error": str(e)}


def extract_text(image_bytes: bytes) -> dict:
    """Extract text using both OCR methods, returns the best result"""
    
    # Ensure OCR is initialized
    if not globals().get('GOOGLE_VISION_AVAILABLE', False) and not globals().get('OCR_SPACE_API_KEY'):
        init_ocr()
    
    results = []
    
    # Run Google Vision if available
    if globals().get('GOOGLE_VISION_AVAILABLE', False):
        gv_result = extract_text_google_vision(image_bytes)
        if gv_result.get("text"):
            gv_result["score"] = _calculate_text_score(gv_result["text"])
            results.append(gv_result)
            logger.info(f"[OCR] Google Vision score: {gv_result['score']:.2f}")
    
    # Run OCR.space if available
    if globals().get('OCR_SPACE_API_KEY'):
        ocr_result = extract_text_ocr_space(image_bytes)
        if ocr_result.get("text"):
            ocr_result["score"] = _calculate_text_score(ocr_result["text"])
            results.append(ocr_result)
            logger.info(f"[OCR] OCR.space score: {ocr_result['score']:.2f}")
    
    if not results:
        return {"text": None, "method": "failed", "error": "No OCR method succeeded"}
    
    # Return best result
    best = max(results, key=lambda x: x["score"])
    logger.info(f"[OCR] Best result: {best['method']} (score: {best['score']:.2f})")
    return best


def _calculate_text_score(text: str) -> float:
    """Calculate a quality score for extracted text"""
    if not text:
        return 0.0
    
    score = 0.0
    
    # More characters = higher score (up to a point)
    char_count = len(text.strip())
    score += min(char_count / 500, 1.0) * 30
    
    # Word count
    words = text.split()
    word_count = len(words)
    score += min(word_count / 100, 1.0) * 20
    
    # Check for common prescription patterns (medical terms, dosages, etc.)
    prescription_indicators = [
        r'\d+mg', r'\d+ml', r'\d+mcg', r'tablet', r'capsule', r'syrup',
        r'once', r'twice', r'daily', r'morning', r'night', r'mg/',
        r'Rx', r' prescription', r'patient', r'doctor', r'date',
        r'\d+/\d+', r'\+\d{10,}', r'\d{10}'
    ]
    import re
    for pattern in prescription_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            score += 5
    
    # Penalize garbled text (too many special characters)
    special_char_ratio = sum(1 for c in text if c in '�??') / max(char_count, 1)
    score -= special_char_ratio * 30
    
    # Penalize very short text
    if char_count < 50:
        score *= 0.5
    
    return min(score, 100)


def extract_text_ocr_space(image_bytes: bytes) -> dict:
    """Extract text using OCR.space API (fallback)"""
    global OCR_SPACE_API_KEY
    
    if not OCR_SPACE_API_KEY:
        init_ocr()
    
    if not OCR_SPACE_API_KEY:
        return {"text": None, "method": "failed", "error": "OCR API key not configured"}
    
    try:
        logger.info("[OCR] Calling OCR.space API (fallback)...")
        
        # Debug: Log API key first few chars
        logger.info(f"[OCR] API key: {OCR_SPACE_API_KEY[:8]}..." if OCR_SPACE_API_KEY else "[OCR] No API key")
        
        # Preprocess image
        enhanced_bytes = preprocess_image_for_ocr(image_bytes)
        
        # Convert image to base64
        b64_image = base64.b64encode(enhanced_bytes).decode('utf-8')
        logger.info(f"[OCR] Image size: {len(b64_image)} chars base64")
        
        # Prepare payload - use files for multipart upload
        files = {
            'apikey': (None, OCR_SPACE_API_KEY),
            'language': (None, 'eng'),
            'isOverlayRequired': (None, 'false'),
            'detectOrientation': (None, 'true'),
            'scale': (None, 'true'),
            'OCREngine': (None, '2'),
            'file': ('image.png', enhanced_bytes, 'image/png')
        }
        
        # Make request with multipart form
        response = requests.post(OCR_SPACE_URL, files=files, timeout=30)
        
        if not response.ok:
            logger.error(f"[OCR] API error: {response.status_code}")
            return {"text": None, "method": "ocr_space", "error": f"API error: {response.status_code}"}
        
        result = response.json()
        
        if result.get("IsErroredOnProcessing"):
            error_msg = result.get("ErrorMessage", ["Unknown error"])
            logger.error(f"[OCR] Processing error: {error_msg}")
            return {"text": None, "method": "ocr_space", "error": str(error_msg)}
        
        parsed_results = result.get("ParsedResults", [])
        if not parsed_results:
            return {"text": None, "method": "ocr_space", "error": "No text found"}
        
        text_parts = []
        for parsed in parsed_results:
            text = parsed.get("ParsedText", "")
            if text:
                text_parts.append(text)
        
        text = " ".join(text_parts)
        logger.info(f"[OCR] OCR.space extracted {len(text)} chars")
        
        if len(text.strip()) >= 20:
            return {"text": text, "method": "ocr_space"}
        
        return {"text": None, "method": "ocr_space", "error": "Text too short"}
        
    except Exception as e:
        logger.error(f"[OCR] OCR.space error: {e}")
        return {"text": None, "method": "failed", "error": str(e)}


def extract_text_from_pdf(data: bytes) -> str:
    """Extract text from PDF using OCR.space API"""
    try:
        import pdfplumber
        import re
        
        skip = re.compile(
            r'(important instruction|test results are|laboratory|please retry|'
            r'court|jurisdiction|iso \d|accredited|tel:|fax:|e-mail|page \d|'
            r'computer generated|authorized medical|specimen|sample drawn)',
            re.IGNORECASE
        )
        
        # First try direct text extraction
        parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    lines = [l.strip() for l in t.splitlines()
                             if len(l.strip()) > 3 and not skip.search(l)]
                    parts.append("\n".join(lines))
        
        text = "\n".join(parts).strip()
        
        # If minimal text, try OCR
        if len(text) < 100:
            logger.info("[OCR] PDF has minimal text, trying OCR...")
            try:
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(data, dpi=200)
                ocr_parts = []
                for img in images[:3]:
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    result = extract_text(buf.getvalue())
                    if result["text"]:
                        ocr_parts.append(result["text"])
                text = "\n".join(ocr_parts)
            except ImportError:
                logger.warning("[OCR] pdf2image not installed, using direct extraction")
        
        logger.info(f"[OCR] PDF: {len(text)} chars extracted")
        return text[:4000]
        
    except Exception as e:
        logger.error(f"[OCR] PDF extraction error: {e}")
        raise Exception(str(e))