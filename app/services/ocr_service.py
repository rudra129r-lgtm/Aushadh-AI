"""
OCR Service - OCR.space API (Cloud)
====================================
Uses OCR.space free API - no local dependencies needed
"""

import io
import base64
import requests
import logging

logger = logging.getLogger(__name__)

OCR_SPACE_API_KEY = None
OCR_SPACE_URL = "https://api.ocr.space/parse/image"


def init_ocr():
    global OCR_SPACE_API_KEY
    from dotenv import load_dotenv
    import os
    load_dotenv()
    OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "")
    if OCR_SPACE_API_KEY:
        print("[OCR] OCR.space API key loaded")
    else:
        print("[OCR] WARNING: OCR_SPACE_API_KEY not found in .env")


def extract_text(image_bytes: bytes) -> dict:
    """Extract text using OCR.space API"""
    global OCR_SPACE_API_KEY
    
    if not OCR_SPACE_API_KEY:
        init_ocr()
    
    if not OCR_SPACE_API_KEY:
        return {"text": None, "method": "failed", "error": "OCR API key not configured"}
    
    try:
        logger.info("[OCR] Calling OCR.space API...")
        
        # Convert image to base64
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare payload
        payload = {
            "apikey": OCR_SPACE_API_KEY,
            "base64Image": f"data:image/jpeg;base64,{b64_image}",
            "language": "eng",  # English
            "isOverlayRequired": "false",
            "detectOrientation": "true",
            "scale": "true",
            "OCREngine": "2",  # Engine 2 is faster and better
        }
        
        # Make request
        response = requests.post(OCR_SPACE_URL, data=payload, timeout=30)
        
        if not response.ok:
            logger.error(f"[OCR] API error: {response.status_code} - {response.text}")
            return {"text": None, "method": "ocr_space", "error": f"API error: {response.status_code}"}
        
        result = response.json()
        
        # Check for errors
        if result.get("IsErroredOnProcessing"):
            error_msg = result.get("ErrorMessage", ["Unknown error"])
            logger.error(f"[OCR] Processing error: {error_msg}")
            return {"text": None, "method": "ocr_space", "error": str(error_msg)}
        
        # Extract text from results
        parsed_results = result.get("ParsedResults", [])
        if not parsed_results:
            logger.warning("[OCR] No text found in image")
            return {"text": None, "method": "ocr_space", "error": "No text found"}
        
        # Combine all text
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