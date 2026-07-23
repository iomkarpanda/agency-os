import jwt
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()
KEY = os.getenv("SECRET_KEY")


def create_access_token(userid: str) -> tuple[str, datetime]:
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "userid": userid,
        "exp":expiry_time ,
        "type":"access"
    }
    return jwt.encode(payload=payload, key=KEY, algorithm="HS256") , expiry_time

def create_refresh_token(userid: str) -> tuple[str, datetime]:

    expiry_time = datetime.now(timezone.utc) + timedelta(days=30)

    payload = {
            "userid": userid,
            "exp": expiry_time,
            "type":"refresh"
        }
    return jwt.encode(payload=payload, key=KEY, algorithm="HS256") , expiry_time

def revalidate_access_token(refresh_token: str) -> tuple[str, datetime, str] | None:
    if not refresh_token:
        return None
    try:
        payload = jwt.decode(
            refresh_token,
            key=KEY,
            algorithms=["HS256"]
        )
        if payload.get("type") == "refresh":
            userid = payload["userid"]
            new_access_token, new_expiry_time = create_access_token(userid)
            return new_access_token, new_expiry_time, userid

        return None
    except jwt.ExpiredSignatureError:
        print("Refresh token expired")
        return None
    except Exception as e:
        print(f"Token is not valid: {e}")
        return None