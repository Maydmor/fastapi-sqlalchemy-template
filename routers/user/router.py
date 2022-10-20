from typing import List
from fastapi import APIRouter, Depends, HTTPException
from database.models import User as DBUser
from database.models.user import RoleName
from database.services import get_db, user as user_service
from security.auth import AuthRules
from .schemas.user import RoleUpdate, User, UserCreate, UserRole, UserUpdate
from sqlalchemy.orm import Session 
router = APIRouter()


def user_by_email(email: str, db: Session = Depends(get_db))->DBUser:
    """Dependency to get a user by email or throw an HTTPException if user was not found

    Args:
        email (str): email of the user
    Raises:
        HTTPException: 404 if user was not found
    Returns:
        DBUser: user in database
    """
    user = user_service.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=404, detail=f'could not find user with email {email}')
    return user

@router.get('', operation_id='get_users', response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)

@router.post('', response_model=User, operation_id='create_user')
def create_user(user: UserCreate, db: Session = Depends(get_db))->User:
    if user_service.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail=f'an user with the given email already exists')
    new_user = user_service.create_user(db, email=user.email, password=user.password, role_name=RoleName.user.value)
    return new_user

@router.patch('/{email}', response_model=User, operation_id='update_user')
def patch_user(user_update_fields: UserUpdate, update_user: DBUser = Depends(user_by_email), is_admin: bool = Depends(AuthRules.is_admin), 
                     user: DBUser = Depends(AuthRules.require_user), db: Session = Depends(get_db)):
    if not is_admin and user.id != update_user.id:
        raise HTTPException(status_code=403, detail=f'only the owner or an admin can update this ressource')
    updated_user = user_service.update_user(db, update_user, user_update_fields)
    return updated_user
    
@router.patch('/{email}/role', response_model=User, operation_id='update_user_role')
def patch_role(role_update_fields: RoleUpdate, update_user: DBUser = Depends(user_by_email), is_admin: bool = Depends(AuthRules.is_admin), db: Session = Depends(get_db)):
    if not is_admin:
        raise HTTPException(status_code=403, detail=f'only the owner or an admin can update this ressource')
    print(role_update_fields)
    return user_service.update_user(db, update_user, role_update_fields)

@router.delete('/{email}', response_model=User, operation_id='delete_user')
def delete_user(delete_user: DBUser = Depends(user_by_email), is_admin: bool = Depends(AuthRules.is_admin), user: DBUser = Depends(AuthRules.require_user), db: Session = Depends(get_db)):
    deleted_user = User.from_orm(delete_user)
    if not is_admin and not user.id == delete_user.id:
        raise HTTPException(status_code=403, detail=f'only the owner or an admin can delete this ressource')
    user_service.delete_user(db, delete_user)
    return deleted_user

