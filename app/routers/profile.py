from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Header
from pydantic import BaseModel
from typing import Optional
import base64
import io
from PIL import Image
import logging

from app.routers.auth import get_current_user
from app.services import mongo_service

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DIMENSION = 200


class ProfilePhotoResponse(BaseModel):
    status: str
    profile_photo: Optional[str] = None


class ProfilePhotoDeleteResponse(BaseModel):
    status: str
    message: str = "Photo removed successfully"


def process_image(file_data: bytes) -> str:
    """Resize and compress image, return base64 string"""
    try:
        img = Image.open(io.BytesIO(file_data))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=80, optimize=True)
        buffer.seek(0)
        
        b64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise ValueError("Invalid image file")


@router.post("/profile/photo", summary="Upload profile photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Upload and save user profile photo"""
    user = get_current_user(authorization)
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )
    
    data = await file.read()
    
    if len(data) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_SIZE // (1024*1024)}MB"
        )
    
    try:
        processed_photo = process_image(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    user_id = user.get("id")
    mongo_service.update_profile_photo(user_id, processed_photo)
    
    logger.info(f"Profile photo uploaded for user {user_id}")
    
    return {"status": "success", "profile_photo": processed_photo}


@router.get("/profile/photo", summary="Get profile photo")
async def get_profile_photo(authorization: Optional[str] = Header(None)):
    """Get user's profile photo"""
    user = get_current_user(authorization)
    
    user_id = user.get("id")
    photo = mongo_service.get_profile_photo(user_id)
    
    return {"profile_photo": photo}


@router.delete("/profile/photo", summary="Delete profile photo")
async def delete_profile_photo(authorization: Optional[str] = Header(None)):
    """Remove user's profile photo"""
    user = get_current_user(authorization)
    
    user_id = user.get("id")
    mongo_service.update_profile_photo(user_id, None)
    
    logger.info(f"Profile photo deleted for user {user_id}")
    
    return {"status": "success", "message": "Photo removed successfully"}


# ── Profile Data Endpoints ─────────────────────────────────

class ProfileDataRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    blood_group: Optional[str] = None
    language: Optional[str] = "en"
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_name: Optional[str] = None
    emergency_phone: Optional[str] = None
    emergency_relation: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_specialty: Optional[str] = None
    doctor_hospital: Optional[str] = None


@router.get("/profile/data", summary="Get user profile data")
async def get_profile_data(authorization: Optional[str] = Header(None)):
    """Get user's profile data from MongoDB"""
    user = get_current_user(authorization)
    user_id = user.get("id")
    
    profile_data = mongo_service.get_profile_data(user_id)
    
    if profile_data is None:
        # Return empty structure if no data exists
        profile_data = {
            "name": "", "age": "", "phone": "", "city": "",
            "blood_group": "", "language": "en", "allergies": "",
            "medical_conditions": "", "emergency_name": "",
            "emergency_phone": "", "emergency_relation": "",
            "doctor_name": "", "doctor_specialty": "", "doctor_hospital": ""
        }
    
    return profile_data


@router.post("/profile/data", summary="Save user profile data")
async def save_profile_data(
    req: ProfileDataRequest,
    authorization: Optional[str] = Header(None)
):
    """Save user's profile data to MongoDB"""
    user = get_current_user(authorization)
    user_id = user.get("id")
    
    # Convert Pydantic model to dict, excluding None values
    profile_dict = req.dict(exclude_none=True)
    
    success = mongo_service.save_profile_data(user_id, profile_dict)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save profile data")
    
    logger.info(f"Profile data saved for user {user_id}")
    
    return {"status": "success", "message": "Profile data saved successfully"}


@router.get("/profile/status", summary="Check if user is new")
async def get_user_status(authorization: Optional[str] = Header(None)):
    """Check if user is new (no saved data) or returning"""
    user = get_current_user(authorization)
    user_id = user.get("id")
    
    has_data = mongo_service.user_has_data(user_id)
    
    return {"is_new_user": not has_data}