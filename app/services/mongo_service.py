import os
import requests
import hashlib
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import json
from urllib.parse import quote_plus

load_dotenv()

def get_mongodb_uri():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    if "mongodb+srv://" in uri and "@" in uri:
        parts = uri.split("@")
        if len(parts) == 2:
            creds, rest = parts[0].split("://", 1)
            if ":" in creds:
                user, password = creds.split(":", 1)
                escaped = f"{quote_plus(user)}:{quote_plus(password)}"
                uri = f"{creds.split(':')[0]}://{escaped}@{rest}"
    return uri

MONGODB_URI = get_mongodb_uri()
DB_NAME = os.getenv("MONGODB_DB", "aushadh_ai")

client = None
db = None

def get_db():
    global client, db
    if client is None:
        try:
            client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            db = client[DB_NAME]
            _ensure_indexes()
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return None
    return db

def _ensure_indexes():
    try:
        db.users.create_index("email", unique=True)
        db.users.create_index("google_id", unique=True, sparse=True)
        db.medications.create_index("user_id")
        db.analyses.create_index("user_id")
        db.analysis_history.create_index("user_id")
    except Exception as e:
        print(f"Index creation: {e}")

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def find_user_by_google_id(google_id: str):
    """Find user by Google ID"""
    try:
        db = get_db()
        user = db.users.find_one({"google_id": google_id})
        return user
    except Exception as e:
        print(f"Error finding user by google_id: {e}")
        return None

def find_user_by_email(email: str):
    """Find user by email"""
    try:
        db = get_db()
        user = db.users.find_one({"email": email})
        return user
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None

def register_google_user(google_id: str, email: str, name: str, profile_photo: str = None):
    """Register new user via Google OAuth or link Google to existing account"""
    try:
        db = get_db()
        
        # Check if user exists with this Google ID
        existing_google_user = find_user_by_google_id(google_id)
        if existing_google_user:
            # User already exists with Google, create session
            import secrets
            from datetime import datetime
            token = secrets.token_urlsafe(32)
            db.users.update_one(
                {"_id": existing_google_user["_id"]},
                {"$set": {"session_token": token, "session_created_at": datetime.now()}}
            )
            return {
                "access_token": token,
                "user_id": str(existing_google_user["_id"]),
                "email": existing_google_user["email"],
                "name": existing_google_user.get("name", name),
                "profile_photo": existing_google_user.get("profile_photo", profile_photo),
                "is_new_user": False
            }
        
        # Check if user exists with same email
        existing_email_user = find_user_by_email(email)
        if existing_email_user:
            # Link Google ID to existing account
            import secrets
            from datetime import datetime
            token = secrets.token_urlsafe(32)
            db.users.update_one(
                {"_id": existing_email_user["_id"]},
                {"$set": {"google_id": google_id, "session_token": token, "session_created_at": datetime.now()}}
            )
            return {
                "access_token": token,
                "user_id": str(existing_email_user["_id"]),
                "email": existing_email_user["email"],
                "name": existing_email_user.get("name", name),
                "profile_photo": existing_email_user.get("profile_photo", profile_photo),
                "is_new_user": False,
                "linked_existing": True
            }
        
        # Create new user
        import secrets
        from datetime import datetime
        token = secrets.token_urlsafe(32)
        
        new_user = {
            "email": email,
            "name": name,
            "google_id": google_id,
            "profile_photo": profile_photo,
            "language": "en",
            "created_at": datetime.now(),
            "session_token": token,
            "session_created_at": datetime.now()
        }
        
        result = db.users.insert_one(new_user)
        
        return {
            "access_token": token,
            "user_id": str(result.inserted_id),
            "email": email,
            "name": name,
            "profile_photo": profile_photo,
            "is_new_user": True
        }
        
    except Exception as e:
        print(f"Error registering Google user: {e}")
        raise Exception(f"Failed to register Google user: {str(e)}")

SESSION_TIMEOUT_MINUTES = 30

def verify_token(token: str):
    try:
        db = get_db()
        user = db.users.find_one({"session_token": token})
        if user:
            session_created_at = user.get("session_created_at")
            if session_created_at:
                from datetime import datetime, timedelta
                expiry_time = session_created_at + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
                if datetime.now() > expiry_time:
                    db.users.update_one({"_id": user["_id"]}, {"$set": {"session_token": None, "session_created_at": None}})
                    return None
            return {"id": str(user["_id"]), "email": user["email"], "profile_photo": user.get("profile_photo")}
        return None
    except Exception:
        return None

def login(email: str, password: str):
    try:
        db = get_db()
        password_hash = _hash_password(password)
        user = db.users.find_one({"email": email, "password_hash": password_hash})
        
        if not user:
            raise Exception("Invalid email or password")
        
        import secrets
        from datetime import datetime
        token = secrets.token_urlsafe(32)
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"session_token": token, "session_created_at": datetime.now()}}
        )
        
        # Get all user fields to debug
        all_keys = list(user.keys())
        profile_photo = user.get("profile_photo")
        
        print(f"[MongoDB] Login - user_id: {user['_id']}")
        print(f"[MongoDB] User document keys: {all_keys}")
        print(f"[MongoDB] profile_photo value: {profile_photo}")
        print(f"[MongoDB] profile_photo type: {type(profile_photo)}")
        
        # Build full profile data from MongoDB
        profile_data = {
            "name": user.get("name", ""),
            "age": user.get("age", ""),
            "phone": user.get("phone", ""),
            "city": user.get("city", ""),
            "blood_group": user.get("blood_group", ""),
            "language": user.get("language", "en"),
            "allergies": user.get("allergies", ""),
            "medical_conditions": user.get("medical_conditions", ""),
            "emergency_name": user.get("emergency_name", ""),
            "emergency_phone": user.get("emergency_phone", ""),
            "emergency_relation": user.get("emergency_relation", ""),
            "doctor_name": user.get("doctor_name", ""),
            "doctor_specialty": user.get("doctor_specialty", ""),
            "doctor_hospital": user.get("doctor_hospital", "")
        }
        
        return {
            "access_token": token,
            "user": {
                "id": str(user["_id"]), 
                "email": user["email"], 
                "profile_photo": profile_photo,
                **profile_data
            }
        }
    except Exception as e:
        raise Exception(str(e))

def register(email: str, password: str):
    try:
        db = get_db()
        existing = db.users.find_one({"email": email})
        if existing:
            raise Exception("Email already registered")
        
        password_hash = _hash_password(password)
        import secrets
        from datetime import datetime
        token = secrets.token_urlsafe(32)
        
        result = db.users.insert_one({
            "email": email,
            "password_hash": password_hash,
            "session_token": token,
            "session_created_at": datetime.now(),
            "created_at": None
        })
        
        return {
            "access_token": token,
            "user": {
                "id": str(result.inserted_id), 
                "email": email, 
                "profile_photo": None,
                "name": "", "age": "", "phone": "", "city": "",
                "blood_group": "", "language": "en", "allergies": "",
                "medical_conditions": "", "emergency_name": "",
                "emergency_phone": "", "emergency_relation": "",
                "doctor_name": "", "doctor_specialty": "", "doctor_hospital": ""
            }
        }
    except Exception as e:
        raise Exception(str(e))

def logout():
    pass

def refresh_session(token: str):
    """Refresh session timestamp to extend session"""
    try:
        db = get_db()
        from datetime import datetime
        result = db.users.update_one(
            {"session_token": token},
            {"$set": {"session_created_at": datetime.now()}}
        )
        return result.modified_count > 0
    except Exception:
        return False

def clear_all_user_data(user_id: str):
    """Clear all analysis, medications, and history for a user"""
    try:
        db = get_db()
        
        print(f"[DEBUG] Attempting to clear data for user_id: {user_id}", flush=True)
        
        # Step 1: Find the actual user_id from the users collection
        user_doc = db.users.find_one({"email": user_id})
        
        if user_doc:
            actual_user_id = str(user_doc["_id"])
            print(f"[DEBUG] Found user in users collection, actual_id: {actual_user_id}", flush=True)
        else:
            # Try to find user_id by searching any collection with partial email match
            print(f"[DEBUG] User not found by email, searching other collections...", flush=True)
            
            # Check analyses collection for any matching user
            test_doc = db.analyses.find_one({})
            if test_doc and test_doc.get("user_id"):
                # Check if any document has user_id containing part of email
                partial = user_id.split('@')[0]
                match = db.analyses.find_one({"user_id": {"$regex": partial, "$options": "i"}})
                if match:
                    actual_user_id = match.get("user_id")
                    print(f"[DEBUG] Found user_id in analyses: {actual_user_id}", flush=True)
                else:
                    print(f"[DEBUG] Could not find user data for: {user_id}", flush=True)
                    return True  # Return success anyway, no data to clear
            else:
                actual_user_id = None
        
        if not actual_user_id:
            print(f"[DEBUG] No data found for user: {user_id}", flush=True)
            return True
        
        # Step 2: Delete using the actual user_id
        analyses_result = db.analyses.delete_one({"user_id": actual_user_id})
        history_result = db.analysis_history.delete_one({"user_id": actual_user_id})
        meds_result = db.medications.delete_many({"user_id": actual_user_id})
        adherence_result = db.adherence.delete_many({"user_id": actual_user_id})
        
        print(f"[Aushadh AI] Data cleared for {user_id} (actual: {actual_user_id}): analyses={analyses_result.deleted_count}, history={history_result.deleted_count}, meds={meds_result.deleted_count}, adherence={adherence_result.deleted_count}", flush=True)
        
        return True
    except Exception as e:
        print(f"Clear all data error: {e}", flush=True)
        return False

def save_medications(user_id: str, medications: list):
    try:
        db = get_db()
        
        db.medications.delete_many({"user_id": user_id})
        
        for med in medications:
            data = {
                "user_id": user_id,
                "name": med.get("name", ""),
                "dosage": med.get("dosage", ""),
                "timing": med.get("timing", ""),
                "duration": med.get("duration", ""),
                "with_food": med.get("with_food", ""),
                "simple_instruction": med.get("simple_instruction", "")
            }
            db.medications.insert_one(data)
        
        return True
    except Exception as e:
        print(f"Save medications error: {e}")
        return False

def get_medications(user_id: str):
    try:
        db = get_db()
        meds = list(db.medications.find({"user_id": user_id}).sort("created_at", -1))
        for med in meds:
            med["_id"] = str(med["_id"])
        return meds
    except Exception as e:
        print(f"Get medications error: {e}")
        return []

def delete_medication(med_id: str, user_id: str):
    try:
        db = get_db()
        result = db.medications.delete_one({"_id": ObjectId(med_id), "user_id": user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Delete medication error: {e}")
        return False


# ── Analysis Data Storage ─────────────────────────────────────

def save_analysis(user_id: str, analysis_data: dict):
    """Save current analysis data"""
    try:
        db = get_db()
        data = {
            "user_id": user_id,
            "analysis": analysis_data,
            "updated_at": "now"
        }
        db.analyses.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Save analysis error: {e}")
        return False


def get_analysis(user_id: str):
    """Get current analysis data"""
    try:
        db = get_db()
        record = db.analyses.find_one({"user_id": user_id})
        if record:
            record["_id"] = str(record["_id"])
            return record.get("analysis", {})
        return None
    except Exception as e:
        print(f"Get analysis error: {e}")
        return None


def save_analysis_history(user_id: str, history: list):
    """Save analysis history (last 5 analyses)"""
    try:
        db = get_db()
        data = {
            "user_id": user_id,
            "history": history,
            "updated_at": "now"
        }
        db.analysis_history.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Save analysis history error: {e}")
        return False


def get_analysis_history(user_id: str):
    """Get analysis history"""
    try:
        db = get_db()
        record = db.analysis_history.find_one({"user_id": user_id})
        if record:
            record["_id"] = str(record["_id"])
            return record.get("history", [])
        return []
    except Exception as e:
        print(f"Get analysis history error: {e}")
        return []


# ── Adherence Tracking ─────────────────────────────────────

def save_adherence(user_id: str, date: str, medications: list):
    """Save daily adherence record"""
    try:
        db = get_db()
        data = {
            "user_id": user_id,
            "date": date,  # YYYY-MM-DD format
            "medications": medications,  # list of {name, taken, time_slot}
            "created_at": "now"
        }
        db.adherence.insert_one(data)
        return True
    except Exception as e:
        print(f"Save adherence error: {e}")
        return False


def get_adherence(user_id: str, start_date: str = None, end_date: str = None):
    """Get adherence history"""
    try:
        db = get_db()
        query = {"user_id": user_id}
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["date"] = {"$gte": start_date}
        
        records = list(db.adherence.find(query).sort("date", -1))
        for r in records:
            r["_id"] = str(r["_id"])
        return records
    except Exception as e:
        print(f"Get adherence error: {e}")
        return []


def get_adherence_stats(user_id: str, days: int = 30):
    """Calculate adherence statistics - counts individual doses, not medications"""
    try:
        db = get_db()
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        records = list(db.adherence.find({
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }).sort("date", 1))  # Sort ascending for streak calculation
        
        if not records:
            return {"total_days": 0, "adherence_rate": 0, "streak": 0, "total_doses": 0, "taken_doses": 0}
        
        total_doses = 0
        taken_doses = 0
        
        # Count each dose slot individually
        for record in records:
            for med in record.get("medications", []):
                total_doses += 1
                if med.get("taken"):
                    taken_doses += 1
        
        adherence_rate = round((taken_doses / total_doses * 100), 1) if total_doses > 0 else 0
        
        # Calculate current streak (consecutive days with 100% adherence)
        streak = 0
        records_reversed = sorted(records, key=lambda x: x.get("date", ""), reverse=True)
        
        for record in records_reversed:
            meds = record.get("medications", [])
            day_total = len(meds)
            day_taken = sum(1 for m in meds if m.get("taken"))
            
            # Perfect adherence for the day
            if day_taken == day_total and day_total > 0:
                streak += 1
            else:
                break
        
        return {
            "total_days": len(records),
            "total_doses": total_doses,
            "taken_doses": taken_doses,
            "adherence_rate": adherence_rate,
            "streak": streak
        }
    except Exception as e:
        print(f"Get adherence stats error: {e}")
        import traceback
        traceback.print_exc()
        return {"total_days": 0, "adherence_rate": 0, "streak": 0, "total_doses": 0, "taken_doses": 0}


def update_profile_photo(user_id: str, photo_data: str):
    """Update user's profile photo"""
    try:
        db = get_db()
        from bson import ObjectId
        
        print(f"[MongoDB] update_profile_photo called with user_id: {user_id}")
        print(f"[MongoDB] photo_data length: {len(photo_data) if photo_data else 0}")
        
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_photo": photo_data}}
        )
        
        print(f"[MongoDB] Update result - matched: {result.matched_count}, modified: {result.modified_count}")
        
        # Verify the update worked by reading back
        verify_user = db.users.find_one({"_id": ObjectId(user_id)})
        print(f"[MongoDB] After update - profile_photo exists: {bool(verify_user.get('profile_photo'))}")
        
        return result.modified_count > 0
    except Exception as e:
        print(f"Update profile photo error: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_profile_photo(user_id: str):
    """Get user's profile photo"""
    try:
        db = get_db()
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return user.get("profile_photo")
        return None
    except Exception as e:
        print(f"Get profile photo error: {e}")
        return None


def get_profile_data(user_id: str):
    """Get user's profile data from MongoDB"""
    try:
        db = get_db()
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            # Return all profile fields
            return {
                "name": user.get("name", ""),
                "age": user.get("age", ""),
                "phone": user.get("phone", ""),
                "city": user.get("city", ""),
                "blood_group": user.get("blood_group", ""),
                "language": user.get("language", "en"),
                "allergies": user.get("allergies", ""),
                "medical_conditions": user.get("medical_conditions", ""),
                "emergency_name": user.get("emergency_name", ""),
                "emergency_phone": user.get("emergency_phone", ""),
                "emergency_relation": user.get("emergency_relation", ""),
                "doctor_name": user.get("doctor_name", ""),
                "doctor_specialty": user.get("doctor_specialty", ""),
                "doctor_hospital": user.get("doctor_hospital", "")
            }
        return None
    except Exception as e:
        print(f"Get profile data error: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_profile_data(user_id: str, profile_data: dict):
    """Save user's profile data to MongoDB"""
    try:
        db = get_db()
        from bson import ObjectId
        
        print(f"[MongoDB] save_profile_data called with user_id: {user_id}")
        print(f"[MongoDB] profile_data: {profile_data}")
        
        # Build update dict with only non-None values
        update_dict = {}
        for key, value in profile_data.items():
            if value is not None and value != "":
                update_dict[key] = value
        
        if not update_dict:
            print("[MongoDB] No data to update")
            return True
            
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        
        print(f"[MongoDB] Update result - matched: {result.matched_count}, modified: {result.modified_count}")
        
        return result.matched_count > 0
    except Exception as e:
        print(f"Save profile data error: {e}")
        import traceback
        traceback.print_exc()
        return False


def user_has_data(user_id: str) -> bool:
    """Check if user has any saved data - determines if new or returning user"""
    try:
        db = get_db()
        from bson import ObjectId
        
        analysis = db.analyses.find_one({"user_id": ObjectId(user_id)})
        if analysis:
            return True
        
        medications = db.medications.find_one({"user_id": ObjectId(user_id)})
        if medications:
            return True
            
        checklist = db.checklist.find_one({"user_id": ObjectId(user_id)})
        if checklist:
            return True
            
        # Check users collection for profile data (name, age, etc.)
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            # Check if user has any profile fields filled
            profile_fields = ['name', 'age', 'phone', 'city', 'blood_group', 'allergies', 'medical_conditions']
            for field in profile_fields:
                if user.get(field):
                    return True
            
        return False
    except Exception as e:
        print(f"Check user data error: {e}")
        return False
