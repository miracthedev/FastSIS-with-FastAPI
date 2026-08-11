import os
from typing import TYPE_CHECKING, Annotated

from dotenv import load_dotenv
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from sql import get_session
from models.User import User, UserRole
import bcrypt

if TYPE_CHECKING:
    from models.Student import Student
    from models.Teacher import Teacher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

password_hash = PasswordHash((Argon2Hasher(),))

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY_FOR_TOKEN")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




def get_password_hash(password: str) -> str:
    """Hashes a password before saving it to the database."""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the provided password matches the database hash."""
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Generates a JWT token valid for a specific duration."""

    # We copy the dictionary (usually {"sub": "user@email.com"}) so we don't mutate original data
    to_encode = data.copy()
    
    # Calculate exactly when this token should die (using UTC to avoid timezone bugs)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # "exp" is a reserved JWT keyword. The JWT library looks for this specific key 
    # to automatically reject expired tokens later.
    to_encode.update({"exp": expire})
    
    # We sign the payload using your SECRET_KEY. 
    # The output is a secure Base64 string consisting of: Header.Payload.Signature
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def get_current_user(
    # FastAPI automatically finds the "Authorization: Bearer <token>" header 
    # and extracts just the token string for us.
    token: Annotated[str, Depends(oauth2_scheme)], 
    session: Annotated[Session, Depends(get_session)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the token. 
        # If the SECRET_KEY is wrong, or if the 'exp' time has passed, 
        # PyJWT instantly raises an InvalidTokenError and execution drops to the except block.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extract the email address from the payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except InvalidTokenError:
        raise credentials_exception
        
    # 3. Security check: Ensure the user still exists in the database.
    # (This prevents an edge case where a user is deleted, but their token hasn't expired yet).
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
        
    # 4. Return the full SQLModel User object
    return user

def require_role(required_role: UserRole):
    """Creates a dependency that strictly enforces a specific user role."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return current_user
    return role_checker