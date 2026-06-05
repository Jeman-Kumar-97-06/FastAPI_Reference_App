from  datetime        import UTC, datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from pwdlib           import PasswordHash
from config           import settings
import jwt

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "api/users/token")

def hash_password(password:str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data:dict, expires_delta:timedelta|None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({""})