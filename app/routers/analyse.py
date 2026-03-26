from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services import claude_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "text/plain",
}

MAX_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/analyse/file", summary="Analyse uploaded prescription file")
async def analyse_file(
    file: UploadFile = File(...),
    age:      Optional[str] = Form(None),
    language: Optional[str] = Form("English"),
):
    logger.info(f"Received file upload: {file.filename}, type: {file.content_type}")
    
    # Validate file type
    if file.content_type not in ALLOWED:
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Use PDF, JPG, PNG or TXT."
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

        elif file.content_type in ("image/jpeg", "image/jpg", "image/png"):
            logger.info("Processing as image...")
            result = await claude_service.analyse_image(data, file.content_type, age or "", language or "English")

        else:  # text/plain
            text = data.decode("utf-8", errors="replace")
            result = await claude_service.analyse_text(text, age or "", language or "English")

        logger.info("Analysis completed successfully")
        return result

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
