from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services import claude_service
from app.services.ocr_service import detect_if_medical_image
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "text/plain",
    "image/dicom",      # DICOM medical images
    "application/dicom",
}

MEDICAL_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg", 
    "image/png",
}

# Image type detection keywords
IMAGE_TYPE_KEYWORDS = {
    "xray": ["x-ray", "xray", "chest xray", "chest x-ray", "lung xray"],
    "mri": ["mri", "magnetic"],
    "ct": ["ct scan", "cat scan", "computed tomography"],
    "ultrasound": ["ultrasound", "usg", "sonography"],
}

MAX_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/analyse/file", summary="Analyse uploaded prescription file")
async def analyse_file(
    file: UploadFile = File(...),
    age:       Optional[str] = Form(None),
    language:  Optional[str] = Form("English"),
    doc_type:  Optional[str] = Form(None),
):
    logger.info(f"Received file upload: {file.filename}, type: {file.content_type}")
    
    # Validate file type
    if file.content_type not in ALLOWED:
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Use PDF, JPG, PNG, DICOM or TXT."
        )

    data = await file.read()
    logger.info(f"File size: {len(data)} bytes")

    # Validate file size
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")

    try:
        if file.content_type == "application/pdf":
            logger.info("Processing as PDF...")
            result = await claude_service.analyse_pdf(data, age or "", language or "English")

        elif file.content_type in MEDICAL_IMAGE_TYPES:
            # Detect if this is a medical image (X-ray, MRI, CT, etc.)
            is_medical = doc_type in ["xray", "mri", "ct", "ultrasound", "medical"] if doc_type else False
            
            # Also check filename for hints
            filename_lower = (file.filename or "").lower()
            for img_type, keywords in IMAGE_TYPE_KEYWORDS.items():
                if any(kw in filename_lower for kw in keywords):
                    is_medical = True
                    doc_type = img_type
                    break
            
            # Also analyze image content for medical scan patterns
            if not is_medical:
                try:
                    is_medical = detect_if_medical_image(data)
                    if is_medical:
                        logger.info("[Analyse] Content-based detection identified medical image")
                except Exception as e:
                    logger.warning(f"[Analyse] Medical image detection error: {e}")
            
            # BLOCK medical images - reject with helpful message
            if is_medical:
                logger.warning(f"[Analyse] Blocked medical image upload: {file.filename}")
                raise HTTPException(
                    status_code=400,
                    detail="This appears to be a medical scan (X-ray, MRI, CT, or Ultrasound). Prescription upload is only for text-based prescriptions. Please use the Medical Image Analysis feature instead."
                )
            
            # Regular prescription/image analysis
            logger.info(f"Processing as prescription image... language: {language}")
            result = await claude_service.analyse_image(data, file.content_type, age or "", language or "English")

        else:  # text/plain
            text = data.decode("utf-8", errors="replace")
            result = await claude_service.analyse_text(text, age or "", language or "English")

        logger.info("Analysis completed successfully")
        return result

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyse/text", summary="Analyse pasted prescription text")
async def analyse_text(
    text:     str = Form(...),
    age:      Optional[str] = Form(None),
    language: Optional[str] = Form("English"),
):
    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short to analyse.")

    try:
        result = await claude_service.analyse_text(text, age or "", language or "English")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyse/sample", summary="Analyse built-in sample prescription")
async def analyse_sample(language: Optional[str] = Form("English")):
    sample = """DISCHARGE SUMMARY — Apollo Hospitals, New Delhi

Patient: Rahul Sharma, 58M
Admission: 18-Mar-2026 | Discharge: 23-Mar-2026
Ward: ICU - Cardiac Care Unit

PRIMARY DIAGNOSIS:
STEMI (ST-Elevation Myocardial Infarction) - Acute Anterior Wall Myocardial Infarction
Emergency admission with chest pain and breathlessness

PROCEDURES DONE:
- Primary Percutaneous Coronary Intervention (PCI)
- Drug-eluting stent placement in LAD artery
- Triple vessel disease confirmed on angiography

SECONDARY DIAGNOSIS:
- Type 2 Diabetes Mellitus
- Hypertension (High Blood Pressure)
- Dyslipidemia

MEDICATIONS ON DISCHARGE:
1. Tab. Aspirin 75mg OD x Lifetime
2. Tab. Clopidogrel 75mg OD x 12 months (DAPT)
3. Tab. Atorvastatin 40mg ON x Lifetime
4. Tab. Metoprolol 25mg BD x Lifetime
5. Tab. Ramipril 5mg OD x Lifetime
6. Tab. Metformin 500mg BD
7. Tab. Glimeperide 1mg OD

CRITICAL INSTRUCTIONS:
- IMMEDIATE EMERGENCY: If chest pain, breathlessness, sweating, or fainting occurs, call 102/108 ambulance immediately
- Dual antiplatelet therapy (Aspirin + Clopidogrel) is mandatory for 12 months
- No skipping of antiplatelet drugs - risk of stent thrombosis and death
- Strict bed rest for 2 weeks, then cardiac rehabilitation

FOLLOW-UP:
- Review with Cardiologist in 2 weeks
- ECG after 2 weeks
- Lipid profile after 1 month
- Echocardiography after 3 months

DISCHARGE ADVICE:
- No smoking, no alcohol
- Low salt, low fat diet
- Monitor BP daily
- Light walking after 4 weeks only
- No heavy lifting for 8 weeks

Electronically signed by Dr. Rajesh Kumar, Interventional Cardiologist"""

    try:
        result = await claude_service.analyse_text(sample, "58", language or "English")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample analysis failed: {str(e)}")


@router.post("/analyse/medical-image", summary="Analyse X-ray, MRI, CT scan or other medical images")
async def analyse_medical_image(
    file:       UploadFile = File(...),
    age:        Optional[str] = Form(None),
    language:   Optional[str] = Form("English"),
    image_type: Optional[str] = Form("X-ray"),
):
    """Dedicated endpoint for analyzing medical images (X-rays, MRIs, CT scans, ultrasounds)"""
    logger.info(f"Received medical image: {file.filename}, type: {file.content_type}, image_type: {image_type}")
    
    if file.content_type not in MEDICAL_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Medical image analysis supports JPG, PNG only. Received: {file.content_type}"
        )
    
    data = await file.read()
    logger.info(f"File size: {len(data)} bytes")
    
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")
    
    try:
        result = await claude_service.analyse_medical_image(
            data, file.content_type, age or "", language or "English", image_type or "X-ray"
        )
        logger.info("Medical image analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"Medical image analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
