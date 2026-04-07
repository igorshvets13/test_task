from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Permission, RolePermission, User
from app.security import decode_token


UNAUTHORIZED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not authenticate user",
)

FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden",
)


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise UNAUTHORIZED_EXCEPTION

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UNAUTHORIZED_EXCEPTION

    return parts[1]


def get_current_user(token: str = Depends(get_bearer_token), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
    except Exception:
        raise UNAUTHORIZED_EXCEPTION

    user_id = payload.get("sub")
    if not user_id:
        raise UNAUTHORIZED_EXCEPTION

    stmt = select(User).options(joinedload(User.role)).where(User.id == int(user_id))
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not user.is_active:
        raise UNAUTHORIZED_EXCEPTION

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != "admin":
        raise FORBIDDEN_EXCEPTION
    return current_user


def require_permission(resource: str, action: str):
    def checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if current_user.role.name == "admin":
            return current_user

        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == current_user.role_id,
                Permission.resource == resource,
                Permission.action == action,
            )
        )
        permission = db.execute(stmt).scalar_one_or_none()
        if not permission:
            raise FORBIDDEN_EXCEPTION
        return current_user

    return checker