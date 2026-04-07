from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from db import get_db
from dependencies import require_admin
from models import Permission, Role, RolePermission, User
from schemas import (
    ChangeUserRoleRequest,
    MessageResponse,
    PermissionGrantRequest,
    PermissionOut,
    PermissionRevokeRequest,
    RoleInfo,
    RoleOut,
    UserWithRoleOut,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[UserWithRoleOut])
def list_users(db: Session = Depends(get_db)):
    users = db.execute(select(User).options(joinedload(User.role))).scalars().all()
    return [
        UserWithRoleOut(
            id=user.id,
            last_name=user.last_name,
            first_name=user.first_name,
            middle_name=user.middle_name,
            email=user.email,
            is_active=user.is_active,
            role=RoleInfo(id=user.role.id, name=user.role.name),
        )
        for user in users
    ]


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    roles = db.execute(
        select(Role).options(joinedload(Role.permissions).joinedload(RolePermission.permission))
    ).unique().scalars().all()

    result = []
    for role in roles:
        result.append(
            RoleOut(
                id=role.id,
                name=role.name,
                description=role.description,
                permissions=[PermissionOut.model_validate(rp.permission) for rp in role.permissions],
            )
        )
    return result


@router.patch("/users/{user_id}/role", response_model=MessageResponse)
def change_user_role(user_id: int, payload: ChangeUserRoleRequest, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.execute(select(Role).where(Role.name == payload.role_name)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user.role_id = role.id
    db.add(user)
    db.commit()
    return MessageResponse(message="User role updated")


@router.post("/permissions/grant", response_model=MessageResponse)
def grant_permission(payload: PermissionGrantRequest, db: Session = Depends(get_db)):
    role = db.execute(select(Role).where(Role.name == payload.role_name)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.execute(
        select(Permission).where(
            Permission.resource == payload.resource,
            Permission.action == payload.action,
        )
    ).scalar_one_or_none()

    if not permission:
        permission = Permission(
            resource=payload.resource,
            action=payload.action,
            description=f"{payload.action} on {payload.resource}",
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)

    existing = db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already granted")

    db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    db.commit()
    return MessageResponse(message="Permission granted")

@router.post("/permissions/revoke", response_model=MessageResponse)
def revoke_permission(payload: PermissionRevokeRequest, db: Session = Depends(get_db)):
    role = db.execute(select(Role).where(Role.name == payload.role_name)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.execute(
        select(Permission).where(
            Permission.resource == payload.resource,
            Permission.action == payload.action,
        )
    ).scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    role_permission = db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
    ).scalar_one_or_none()
    if not role_permission:
        raise HTTPException(status_code=404, detail="This role does not have this permission")

    db.delete(role_permission)
    db.commit()
    return MessageResponse(message="Permission revoked")