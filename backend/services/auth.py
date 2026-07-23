import bcrypt
import jwt


def hashpassword(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verifypassword(plainpassword: str, hashedpassword: str) -> bool:
    return bcrypt.checkpw(plainpassword.encode(), hashedpassword.encode())


