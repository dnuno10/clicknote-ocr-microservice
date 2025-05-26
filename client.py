import os
import hmac
import hashlib
import secrets
from datetime import datetime, timezone

from supabase import create_client, Client
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
EMAIL = "user@gmail.com"
PASSWORD = "test123"
SERVER_API_URL = "https://api.clicknote.app/prediction/ftp_upload_and_predict/"
LOCAL_IMAGE_PATH = "/Users/dnuno/Documents/ClickNote/clicknote/python_ocr/scripts/uploaded_images_full/08_all.jpg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def supabase_login(email, password):
    print("[INFO] Authenticating with Supabase...")
    user_session = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    return user_session

def generate_api_credentials():
    new_api_key = secrets.token_hex(16)
    new_api_secret = secrets.token_hex(32)
    return new_api_key, new_api_secret

def create_or_update_api_client(user_id, new_api_key, new_api_secret):
    print("Updating or creating API credentials...")

    result = supabase.from_("api_clients").select("idAPI").eq("idUser", user_id).limit(1).execute()

    if result.data and len(result.data) > 0:
        id_api = result.data[0]["idAPI"]
        supabase.from_("api_clients").update({
            "apiKey": new_api_key,
            "apiSecret": new_api_secret,
            "lastUsedAt": datetime.now(timezone.utc).isoformat()
        }).eq("idAPI", id_api).execute()
    else:
        supabase.from_("api_clients").insert({
            "idUser": user_id,
            "apiKey": new_api_key,
            "apiSecret": new_api_secret,
            "usageCounter": 0,
            "lastUsedAt": datetime.now(timezone.utc).isoformat()
        }).execute()

def generate_signature(api_secret, timestamp, path):
    payload = f"{timestamp}{path}"
    signature = hmac.new(
        api_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def send_file(api_key, api_secret, file_path):
    timestamp = datetime.now(timezone.utc).isoformat()
    path = "/prediction/ftp_upload_and_predict/"
    signature = generate_signature(api_secret, timestamp, path)

    headers = {
        "X-API-KEY": api_key,
        "X-TIMESTAMP": timestamp,
        "X-SIGNATURE": signature
    }

    files = {
        "file": open(file_path, "rb")
    }

    print("Enviando archivo...")
    response = requests.post(
        SERVER_API_URL,
        headers=headers,
        files=files,
        params={"email": "dnuno@cetys.edu.mx"}
    )

    print("Status Code:", response.status_code)
    try:
        print("Response:", response.json())
    except Exception:
        print("Response error:", response.text)

if __name__ == "__main__":
    session = supabase_login(EMAIL, PASSWORD)
    user_id = session.user.id

    new_api_key, new_api_secret = generate_api_credentials()

    create_or_update_api_client(user_id, new_api_key, new_api_secret)
    send_file(new_api_key, new_api_secret, LOCAL_IMAGE_PATH)
