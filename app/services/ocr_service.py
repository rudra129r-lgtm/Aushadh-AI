"""
OCR Service - EasyOCR (already installed)
==========================================
"""

import io
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

EASYOCR_READER = None


def init_easy_ocr():
    global EASYOCR_READER
    if EASYOCR_READER is not None:
        return True
    
    try:
        import easyocr
        print("[OCR] Initializing EasyOCR...")
        EASYOCR_READER = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("[OCR] EasyOCR ready")
        return True
    except Exception as e:
        print(f"[OCR] EasyOCR init error: {e}")
        return False


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Load and preprocess image for OCR"""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img_array = np.array(img)
    
    max_size = 2048
    h, w = img_array.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        img_pil = Image.fromarray(img_array)
        img_pil = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        img_array = np.array(img_pil)
        logger.info(f"[OCR] Image resized to {new_h}x{new_w}")
    
    return img_array


def extract_text(image_bytes: bytes) -> dict:
    """Extract text using EasyOCR"""
    global EASYOCR_READER
    
    if not init_easy_ocr():
        return {"text": None, "method": "failed", "error": "EasyOCR init failed"}
    
    try:
        logger.info("[OCR] Processing with EasyOCR...")
        img_array = preprocess_image(image_bytes)
        
        result = EASYOCR_READER.readtext(img_array, detail=0)
        
        text_lines = [str(line).strip() for line in result if line]
        text = ' '.join(text_lines)
        
        logger.info(f"[OCR] EasyOCR extracted {len(text)} chars")
        
        if len(text.strip()) >= 20:
            return {"text": text, "method": "easyocr"}
        
        return {"text": None, "method": "easyocr", "error": "Text too short"}
        
    except Exception as e:
        logger.error(f"[OCR] EasyOCR error: {e}")
        return {"text": None, "method": "failed", "error": str(e)}


def extract_text_from_pdf(data: bytes) -> str:
    """Extract text from PDF - tries direct extraction first, then OCR"""
    import pdfplumber
    import re
    
    try:
        skip = re.compile(
            r'(important instruction|test results are|laboratory|please retry|'
            r'court|jurisdiction|iso \d|accredited|tel:|fax:|e-mail|page \d|'
            r'computer generated|authorized medical|specimen|sample drawn)',
            re.IGNORECASE
        )
        
        parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    lines = [l.strip() for l in t.splitlines()
                             if len(l.strip()) > 3 and not skip.search(l)]
                    parts.append("\n".join(lines))
        
        text = "\n".join(parts).strip()
        
        # If PDF has minimal text, try OCR
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
                logger.warning("[OCR] pdf2image not installed")
        
        logger.info(f"[OCR] PDF: {len(text)} chars extracted")
        return text[:4000]
        
    except Exception as e:
        logger.error(f"[OCR] PDF extraction error: {e}")
        raise Exception(str(e))