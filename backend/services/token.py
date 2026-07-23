import jwt
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()
KEY = os.getenv("SECRET_KEY")


def create_access_token(userid: str) -> str:
    payload = {
        "userid": userid,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "type":"access"
    }
    return jwt.encode(payload=payload, key=KEY, algorithm="HS256")

def create_refresh_token(userid: str) -> str:

    payload = {
            "userid": userid,
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
            "type":"refresh"
        }
    return jwt.encode(payload=payload, key=KEY, algorithm="HS256")
