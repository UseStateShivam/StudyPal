"""Authentication API endpoints: register, login, logout, me."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import ConflictException, UnauthorizedAccessException
from app.schemas import UserRegister, UserLogin, UserOut, TokenResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new student account."""
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise ConflictException(f"User with email '{user_in.email}' already exists.")

    new_user = User(
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        display_name=user_in.display_name,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=new_user.id)
    return TokenResponse(access_token=token, user=new_user)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate student using standard OAuth2 form username (email) and password."""
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedAccessException("Incorrect email or password.")

    if not user.is_active:
        raise UnauthorizedAccessException("User account is inactive.")

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token, user=user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Stateless JWT logout confirmation endpoint."""
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve authenticated student's profile."""
    return current_user
