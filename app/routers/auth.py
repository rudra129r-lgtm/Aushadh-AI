from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import re
from app.services import mongo_service
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

router = APIRouter()

# Email validation regex pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(EMAIL_PATTERN.match(email))

# In-memory rate limiter storage
rate_limit_store = defaultdict(list)

def get_remote_address(request: Request) -> str:
    return request.client.host if request.client else "127.0.0.1"

def check_rate_limit(request: Request, max_requests: int = 5, window_minutes: int = 15) -> bool:
    """Check if request exceeds rate limit. Returns True if allowed, raises HTTPException if not."""
    client_ip = get_remote_address(request)
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # Clean old entries and filter to current window
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip]
        if t > window_start
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[client_ip]) >= max_requests:
        remaining_time = (rate_limit_store[client_ip][0] - window_start).total_seconds()
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Max {max_requests} per {window_minutes} minutes. Try again later."
        )
    
    # Add current request timestamp
    rate_limit_store[client_ip].append(now)
    return True

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=1, max_length=100)

class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = mongo_service.verify_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


@router.post("/auth/register", response_model=AuthResponse, summary="Register new user")
async def register(req: RegisterRequest, request: Request):
    check_rate_limit(request, max_requests=5, window_minutes=15)
    
    # Validate email format
    if not validate_email(req.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    try:
        result = mongo_service.register(req.email, req.password)
        
        if "access_token" not in result:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        user_data = mongo_service.verify_token(result["access_token"])
        
        return AuthResponse(
            access_token=result["access_token"],
            user={
                "id": user_data.get("id", ""),
                "email": user_data.get("email", req.email),
                "profile_photo": user_data.get("profile_photo"),
                "name": user_data.get("name", ""),
                "age": user_data.get("age", ""),
                "phone": user_data.get("phone", ""),
                "city": user_data.get("city", ""),
                "blood_group": user_data.get("blood_group", ""),
                "language": user_data.get("language", "en"),
                "allergies": user_data.get("allergies", ""),
                "medical_conditions": user_data.get("medical_conditions", ""),
                "emergency_name": user_data.get("emergency_name", ""),
                "emergency_phone": user_data.get("emergency_phone", ""),
                "emergency_relation": user_data.get("emergency_relation", ""),
                "doctor_name": user_data.get("doctor_name", ""),
                "doctor_specialty": user_data.get("doctor_specialty", ""),
                "doctor_hospital": user_data.get("doctor_hospital", "")
            }
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "already registered" in error_msg or "already exists" in error_msg:
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.post("/auth/login", response_model=AuthResponse, summary="Login user")
async def login(req: LoginRequest, request: Request):
    check_rate_limit(request, max_requests=5, window_minutes=15)
    
    # Validate email format
    if not validate_email(req.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    try:
        print(f"Login request: {req.email}")
        result = mongo_service.login(req.email, req.password)
        print(f"Login result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        
        if not result or "access_token" not in result:
            raise HTTPException(status_code=401, detail="Invalid credentials - no token")
        
        user_data = mongo_service.verify_token(result["access_token"])
        
        return AuthResponse(
            access_token=result["access_token"],
            user={
                "id": user_data.get("id", "") if user_data else "",
                "email": user_data.get("email", req.email) if user_data else req.email,
                "profile_photo": user_data.get("profile_photo") if user_data else None,
                "name": user_data.get("name", "") if user_data else "",
                "age": user_data.get("age", "") if user_data else "",
                "phone": user_data.get("phone", "") if user_data else "",
                "city": user_data.get("city", "") if user_data else "",
                "blood_group": user_data.get("blood_group", "") if user_data else "",
                "language": user_data.get("language", "en") if user_data else "en",
                "allergies": user_data.get("allergies", "") if user_data else "",
                "medical_conditions": user_data.get("medical_conditions", "") if user_data else "",
                "emergency_name": user_data.get("emergency_name", "") if user_data else "",
                "emergency_phone": user_data.get("emergency_phone", "") if user_data else "",
                "emergency_relation": user_data.get("emergency_relation", "") if user_data else "",
                "doctor_name": user_data.get("doctor_name", "") if user_data else "",
                "doctor_specialty": user_data.get("doctor_specialty", "") if user_data else "",
                "doctor_hospital": user_data.get("doctor_hospital", "") if user_data else ""
            }
        )
    except Exception as e:
        print(f"Login exception: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/auth/logout", summary="Logout user")
async def logout(authorization: Optional[str] = Header(None)):
    mongo_service.logout()
    return {"message": "Logged out successfully"}


@router.post("/auth/refresh-session", summary="Refresh session to extend timeout")
async def refresh_session(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    success = mongo_service.refresh_session(token)
    
    if success:
        return {"message": "Session refreshed successfully"}
    raise HTTPException(status_code=401, detail="Failed to refresh session")


@router.get("/auth/me", response_model=UserResponse, summary="Get current user")
async def get_me(current_user = Depends(get_current_user)):
    return UserResponse(
        id=current_user.get("id", ""),
        email=current_user.get("email", "")
    )


class MedicationsRequest(BaseModel):
    medications: list


@router.post("/auth/medications", summary="Save medications for user")
async def save_medications(req: MedicationsRequest, current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    success = mongo_service.save_medications(user_id, req.medications)
    if success:
        return {"message": "Medications saved successfully"}
    raise HTTPException(status_code=500, detail="Failed to save medications")


@router.get("/auth/medications", summary="Get medications for current user")
async def get_medications(current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    medications = mongo_service.get_medications(user_id)
    return {"medications": medications}


@router.delete("/auth/medications/{med_id}", summary="Delete a medication")
async def delete_medication(med_id: str, current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    success = mongo_service.delete_medication(med_id, user_id)
    if success:
        return {"message": "Medication deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete medication")


# ── Adherence Tracking ─────────────────────────────────────

class AdherenceRequest(BaseModel):
    date: str
    medications: list


@router.post("/auth/adherence", summary="Save daily adherence")
async def save_adherence(req: AdherenceRequest, current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    success = mongo_service.save_adherence(user_id, req.date, req.medications)
    if success:
        return {"message": "Adherence saved successfully"}
    raise HTTPException(status_code=500, detail="Failed to save adherence")


@router.get("/auth/adherence", summary="Get adherence history")
async def get_adherence(
    start_date: str = None,
    end_date: str = None,
    current_user = Depends(get_current_user)
):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    records = mongo_service.get_adherence(user_id, start_date, end_date)
    return {"records": records}


@router.get("/auth/adherence/stats", summary="Get adherence statistics")
async def get_adherence_stats(
    days: int = 30,
    current_user = Depends(get_current_user)
):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    stats = mongo_service.get_adherence_stats(user_id, days)
    return stats


# ── Analysis Data Storage ─────────────────────────────────────

class AnalysisRequest(BaseModel):
    analysis: dict


class AnalysisHistoryRequest(BaseModel):
    history: list


@router.post("/auth/analysis", summary="Save current analysis data")
async def save_analysis(req: AnalysisRequest, current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    success = mongo_service.save_analysis(user_id, req.analysis)
    if success:
        return {"message": "Analysis saved successfully"}
    raise HTTPException(status_code=500, detail="Failed to save analysis")


@router.get("/auth/analysis", summary="Get current analysis data")
async def get_analysis(current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    analysis = mongo_service.get_analysis(user_id)
    return {"analysis": analysis}


@router.post("/auth/analysis/history", summary="Save analysis history")
async def save_analysis_history(req: AnalysisHistoryRequest, current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    success = mongo_service.save_analysis_history(user_id, req.history)
    if success:
        return {"message": "Analysis history saved successfully"}
    raise HTTPException(status_code=500, detail="Failed to save analysis history")


@router.get("/auth/analysis/history", summary="Get analysis history")
async def get_analysis_history(current_user = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    history = mongo_service.get_analysis_history(user_id)
    return {"history": history}


@router.post("/auth/clear-all-data", summary="Clear all user data")
async def clear_all_data(current_user = Depends(get_current_user)):
    """Clear all analysis, medications, adherence and history for the current user"""
    try:
        user_id = current_user.get("email") or current_user.get("sub")
        print(f"[DEBUG] Clear data endpoint called for user: {user_id}", flush=True)
        
        if not user_id:
            print("[DEBUG] No user_id found in token!", flush=True)
            return {"error": "No user ID found in token"}, 400
        
        success = mongo_service.clear_all_user_data(user_id)
        
        if success:
            return {"message": "All data cleared successfully", "user_id": user_id}
        else:
            return {"error": "Failed to clear data", "user_id": user_id}, 500
    except Exception as e:
        print(f"[DEBUG] Error in clear_all_data: {e}", flush=True)
        return {"error": str(e)}, 500