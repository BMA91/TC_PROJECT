from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.crud import user as user_crud
from app.dependencies import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing = user_crud.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = user_crud.create_user(db=db, user_in=user_in)
    return user


@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return user_crud.get_users(db=db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = user_crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    deleted = user_crud.delete_user(db=db, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # 204 responses should not return a body
    return None


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login endpoint that returns a JWT token.
    Validates email and password, then generates an access token valid for 30 minutes.
    """
    user = user_crud.verify_user_credentials(
        db=db, email=credentials.email, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post(
    "/verify",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def verify_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Verify user existence by email and password.
    Returns user information if credentials are valid.
    """
    user = user_crud.verify_user_credentials(
        db=db, email=credentials.email, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


@router.get(
    "/by-role/agt",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def get_users_with_agt_role(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get all users with roles matching the pattern "agt_%".
    Returns users whose role starts with "agt_" (e.g., agt_1, agt_2, agt_admin, etc.).
    """
    users = user_crud.get_users_by_role_pattern(
        db=db, role_pattern="agt_%", skip=skip, limit=limit
    )
    return users


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """
    Protected endpoint - Returns current user information.
    Requires valid JWT token in Authorization header: Authorization: Bearer <token>
    """
    return current_user


