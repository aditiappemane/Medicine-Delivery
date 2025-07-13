import random
import redis
from typing import Optional
from twilio.rest import Client
from app.config import settings

# Redis client for storing verification codes
redis_client = redis.from_url(settings.REDIS_URL)

# Twilio client
twilio_client = None
if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def generate_verification_code() -> str:
    """Generate a 6-digit verification code."""
    return str(random.randint(100000, 999999))

def send_verification_sms(phone: str, code: str) -> bool:
    """Send verification SMS using Twilio."""
    if not twilio_client:
        # In development, just print the code
        print(f"Verification code for {phone}: {code}")
        return True
    
    try:
        message = twilio_client.messages.create(
            body=f"Your medicine delivery verification code is: {code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        return message.sid is not None
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def store_verification_code(phone: str, code: str, expiry_minutes: int = 10) -> None:
    """Store verification code in Redis with expiry."""
    key = f"verification_code:{phone}"
    redis_client.setex(key, expiry_minutes * 60, code)

def get_verification_code(phone: str) -> Optional[str]:
    """Get stored verification code from Redis."""
    key = f"verification_code:{phone}"
    return redis_client.get(key)

def delete_verification_code(phone: str) -> None:
    """Delete verification code from Redis."""
    key = f"verification_code:{phone}"
    redis_client.delete(key)

def verify_phone_code(phone: str, code: str) -> bool:
    """Verify phone number with provided code."""
    stored_code = get_verification_code(phone)
    if stored_code and stored_code.decode() == code:
        delete_verification_code(phone)
        return True
    return False 