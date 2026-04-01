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
        db.medications.create_index("user_id")
    except Exception as e:
        print(f"Index creation: {e}")

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token: str):
    try:
        db = get_db()
        user = db.users.find_one({"session_token": token})
        if user:
            return {"id": str(user["_id"]), "email": user["email"]}
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
        token = secrets.token_urlsafe(32)
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"session_token": token}}
        )
        
        return {
            "access_token": token,
            "user": {"id": str(user["_id"]), "email": user["email"]}
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
        token = secrets.token_urlsafe(32)
        
        result = db.users.insert_one({
            "email": email,
            "password_hash": password_hash,
            "session_token": token,
            "created_at": None
        })
        
        return {
            "access_token": token,
            "user": {"id": str(result.inserted_id), "email": email}
        }
    except Exception as e:
        raise Exception(str(e))

def logout():
    pass

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
