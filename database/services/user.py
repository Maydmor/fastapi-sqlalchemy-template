from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from database.models import User, Role, RoleName
from pydantic import BaseModel
from security.password_util import hash_password

class UserFilters(BaseModel):
    role_name: Optional[RoleName]

class UserUpdateFields(BaseModel):
    role_name: Optional[RoleName]
    is_active: Optional[bool]
    class Config:
        use_enum_values = True

def get_user_by_email(db: Session, email: str)->User|None:
    return db.query(User).filter_by(email=email).first()

def get_user_by_id(db: Session, id: str)->User|None:
    return db.query(User).get(id)

def get_users(db: Session, skip: Optional[int] = None , limit: Optional[int] = None, filters: Optional[List] = None)->List[User]:
    query = db.query(User)
    if skip != None:
        query = query.offset(skip)
    if limit != None:
        query = query.limit(limit)
    if filters != None:
        query = query.filter(*filters)
    return query.all()

def create_user(db: Session, email: str, password: str, role_name: RoleName)->User:
    user = User(email=email, hashed_password=hash_password(password), role_name=role_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, update_fields: BaseModel|Dict)->User:
    fields = UserUpdateFields.parse_obj(update_fields).dict(exclude_none=True)
    for k,v in fields.items():
        setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User)->None:
    db.delete(user)
    db.commit()