import requests
import os
from app.config import settings

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "your-fcm-server-key")
FCM_URL = "https://fcm.googleapis.com/fcm/send"

def send_push_notification(device_token: str, title: str, message: str) -> bool:
    if not device_token or not FCM_SERVER_KEY:
        return False
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": message
        }
    }
    response = requests.post(FCM_URL, json=payload, headers=headers)
    return response.status_code == 200 