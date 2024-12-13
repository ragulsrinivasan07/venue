from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from decouple import config
from .config import Config
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, HTTPException, Depends, Request

# JWT Authorization configuration
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
TOKEN_EXP_LIMIT = Config.TOKEN_EXP_LIMIT
PWD_CRYPTO_SCHEMA = Config.PWD_CRYPTO_SCHEMA
PWD_CRYPTO_DEPRECATED = Config.PWD_CRYPTO_DEPRECATED

# Configure hashing algorithms with Argon2
pwd_context = CryptContext(schemes=[PWD_CRYPTO_SCHEMA], deprecated=PWD_CRYPTO_DEPRECATED)

def hash_password(password: str) -> str:
    """
    Hashes the given password using Argon2.
    
    Args:
        password (str): Plaintext password to hash.
    
    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies the given plaintext password against the hashed password.
    
    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The hashed password to verify against.
    
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Creates a JWT access token with an expiration time.
    
    Args:
        data (dict): Data to include in the token payload.
    
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXP_LIMIT)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

security = HTTPBearer()

# Function to verify the JWT token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")