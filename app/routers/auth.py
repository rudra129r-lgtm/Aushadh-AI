from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from app.services import mongo_service

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

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
async def register(req: RegisterRequest):
    try:
        result = mongo_service.register(req.email, req.password)
        
        if "access_token" not in result:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        user_data = mongo_service.verify_token(result["access_token"])
        
        return AuthResponse(
            access_token=result["access_token"],
            user={
                "id": user_data.get("id", ""),
                "email": user_data.get("email", req.email)
            }
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "already registered" in error_msg or "already exists" in error_msg:
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.post("/auth/login", response_model=AuthResponse, summary="Login user")
async def login(req: LoginRequest):
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
                "email": user_data.get("email", req.email) if user_data else req.email
            }
        )
    except Exception as e:
        print(f"Login exception: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/auth/logout", summary="Logout user")
async def logout(authorization: Optional[str] = Header(None)):
    mongo_service.logout()
    return {"message": "Logged out successfully"}


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