import bcrypt
from datetime import timedelta, datetime
from jose import jwt
from app.config.settings import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)  
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(data:dict , expires_delta:timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=settings.EXPIRE_IN_TIME)
    to_encode.update({"exp":expire,"type":"access"})
    return jwt.encode(to_encode , settings.SECRET_KEY , algorithm=settings.ALGORITHM)