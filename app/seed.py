from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Permission, Role, RolePermission, User
from security import hash_password


PERMISSIONS = [
    ("documents", "read", "Read documents"),
    ("documents", "create", "Create documents"),
    ("documents", "update", "Update documents"),
    ("documents", "delete", "Delete documents"),
    ("reports", "read", "Read reports"),
]

ROLES = {
    "admin": [
        ("documents", "read"),
        ("documents", "create"),
        ("documents", "update"),
        ("documents", "delete"),
        ("reports", "read"),
    ],
    "manager": [
        ("documents", "read"),
        ("documents", "create"),
        ("documents", "update"),
        ("reports", "read"),
    ],
    "viewer": [
        ("documents", "read"),
    ],
}


def seed_data(db: Session) -> None:
    for role_name in ROLES.keys():
        role = db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
        if not role:
            db.add(Role(name=role_name, description=f"System role: {role_name}"))
    db.commit()

    for resource, action, description in PERMISSIONS:
        permission = db.execute(
            select(Permission).where(Permission.resource == resource, Permission.action == action)
        ).scalar_one_or_none()
        if not permission:
            db.add(Permission(resource=resource, action=action, description=description))
    db.commit()

    roles = {role.name: role for role in db.execute(select(Role)).scalars().all()}
    permissions = {(p.resource, p.action): p for p in db.execute(select(Permission)).scalars().all()}

    for role_name, perms in ROLES.items():
        role = roles[role_name]
        existing_permission_ids = {rp.permission_id for rp in role.permissions}
        for resource, action in perms:
            permission = permissions[(resource, action)]
            if permission.id not in existing_permission_ids:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    db.commit()

    demo_users = [
        ("admin@example.com", "Admin", "System", None, "Admin12345", "admin"),
        ("manager@example.com", "Manager", "Demo", None, "Manager12345", "manager"),
        ("viewer@example.com", "Viewer", "Demo", None, "Viewer12345", "viewer"),
    ]

    for email, last_name, first_name, middle_name, password, role_name in demo_users:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user:
            db.add(
                User(
                    email=email,
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    password_hash=hash_password(password),
                    is_active=True,
                    role_id=roles[role_name].id,
                )
            )
    db.commit()