from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import Role, User
from schemas import MessageResponse, TokenResponse, UserLogin, UserOut, UserRegister
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if payload.password != payload.password_repeat:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    default_role = db.execute(select(Role).where(Role.name == "viewer")).scalar_one()

    user = User(
        last_name=payload.last_name,
        first_name=payload.first_name,
        middle_name=payload.middle_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=True,
        role_id=default_role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")

    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token)


@router.post("/logout", response_model=MessageResponse)
def logout():
    return MessageResponse(message="Logout successful. Delete token on client side.")