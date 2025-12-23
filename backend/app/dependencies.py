from collections.abc import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.security import decode_access_token
from app.crud import user as user_crud

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to validate JWT token and get current user.
    Can be used to protect routes.
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if not token_data or not token_data.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

