from typing import Any
from pydantic import BaseModel, EmailStr, Field

from database.models.user import RoleName

class UserRole(BaseModel):
    name: RoleName
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """user fields that are updatable """
    pass

class RoleUpdate(BaseModel):
    """role fields that are updatable"""
    role_name: RoleName

class User(BaseModel):
    email: EmailStr
    role: UserRole
    class Config:
        orm_mode = True


