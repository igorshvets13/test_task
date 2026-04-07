from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_repeat: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)


class RoleInfo(BaseModel):
    id: int
    name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    email: EmailStr
    is_active: bool
    role_id: int


class UserWithRoleOut(BaseModel):
    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    email: EmailStr
    is_active: bool
    role: RoleInfo


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource: str
    action: str
    description: str | None

class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None
    permissions: list[PermissionOut]


class ChangeUserRoleRequest(BaseModel):
    role_name: str


class PermissionGrantRequest(BaseModel):
    role_name: str
    resource: str
    action: str


class PermissionRevokeRequest(BaseModel):
    role_name: str
    resource: str
    action: str


class MessageResponse(BaseModel):
    message: str


class MockResourceOut(BaseModel):
    resource: str
    action: Literal["read", "create", "update", "delete"]
    data: list[dict]