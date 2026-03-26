import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

def verify_token(token: str):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_KEY
        }
        res = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return None
    except Exception:
        return None

def login(email: str, password: str):
    try:
        res = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            },
            json={"email": email, "password": password},
            timeout=15
        )
        print(f"Login response: {res.status_code} - {res.text}")
        if res.status_code == 200:
            data = res.json()
            if "access_token" not in data:
                print("No access_token in response!")
                raise Exception("No access token")
            return data
        raise Exception(res.json().get("msg", res.text))
    except Exception as e:
        print(f"Login error: {e}")
        raise Exception(str(e))

def register(email: str, password: str):
    try:
        res = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            },
            json={"email": email, "password": password, "data": {"skip_email_verification": True}},
            timeout=15
        )
        print(f"Register response: {res.status_code} - {res.text}")
        if res.status_code >= 200 and res.status_code < 300:
            return res.json()
        raise Exception(res.json().get("msg", res.text))
    except Exception as e:
        raise Exception(str(e))

def logout():
    pass