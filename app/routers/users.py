from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from dependencies import get_current_user
from models import User
from schemas import MessageResponse, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", response_model=MessageResponse)
def soft_delete_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.is_active = False
    db.add(current_user)
    db.commit()
    return MessageResponse(message="User deactivated")