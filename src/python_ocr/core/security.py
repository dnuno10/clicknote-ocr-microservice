import hmac
import hashlib
import secrets
from datetime import datetime, timezone

def generate_signature(api_secret: str, timestamp: str, path: str) -> str:
    payload = f"{timestamp}{path}"
    signature = hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return signature

def verify_signature(api_secret: str, timestamp: str, path: str, provided_signature: str) -> bool:
    expected_signature = generate_signature(api_secret, timestamp, path)
    return hmac.compare_digest(provided_signature, expected_signature)

def generate_api_key() -> str:
    return secrets.token_hex(16)

def generate_api_secret() -> str:
    return secrets.token_hex(32)