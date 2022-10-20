"""Dependencies and helper functions related to security"""
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from database.services import get_db
from jose import jwt, JWTError
from database.services.user import get_user_by_email
from settings import AuthSettings
from database.models.user import User, Role, RoleName
from sqlalchemy.orm import Session
from security.password_util import verify_password

INVALID_CREDENTIAL_ERROR = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid username or password')
INVALID_TOKEN_ERROR = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
    detail=f'Invalid token, log in again', headers={"WWW-Authenticate": "Bearer"})
INSUFFICIENT_PERMISSIONS_ERROR = HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
    detail=f'Your permissions are not sufficient')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def auth_user(email: str, password: str, db: Session = Depends(get_db))->User:
    """Checks if the given user exists and the password matches with the database entry

    Args:
        email (str): provided email
        password (str): provided password

    Raises:
        INVALID_CREDENTIAL_ERROR: when the user was not found or the password was wrong

    Returns:
        User: The user in the database
    """
    user = get_user_by_email(db, email)
    if user is None:
        raise INVALID_CREDENTIAL_ERROR
    if not verify_password(password, user.hashed_password):
        raise INVALID_CREDENTIAL_ERROR
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None)->str:
    """Creates a jwt token string

    Args:
        data (dict): The data to encode in the jwt
        expires_delta (timedelta | None, optional): timedelta when the token should expire. Defaults to None.

    Returns:
        str: The encoded jwt token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AuthSettings().secret_key, algorithm=AuthSettings().jwt_algorithm)
    return encoded_jwt

class AuthRules:
    """Class holding all auth rule dependencies"""
    def require_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))->User:
        """Gets the user from the jwt token from the request

        Args:
            token (str, optional): The token. Defaults to Depends(oauth2_scheme).

        Raises:
            INVALID_TOKEN_ERROR: When the token is expired, invalid or the user from the token does not exist

        Returns:
            User: the owner of the token
        """
        try:
            payload = jwt.decode(token, AuthSettings().secret_key, algorithms=[AuthSettings().jwt_algorithm])
            email = payload.get('sub')
            if email is None:
                raise INVALID_TOKEN_ERROR
        except JWTError as e:
            raise INVALID_TOKEN_ERROR
        user = get_user_by_email(db, email)
        if user is None:
            raise INVALID_TOKEN_ERROR
        return user

    async def is_admin(user: User = Depends(require_user))->bool:
        """checks if the current user has the admin role

        Args:
            user (User, optional): the user object to check. Defaults to Depends(require_user).

        Returns:
            bool: true if the user has the admin role
        """
        return user.role_name == RoleName.admin.value

    async def require_admin(user: User = Depends(require_user), is_admin: bool = Depends(is_admin))->User:
        """dependency returning the current user if it has the admin role. 

        Args:
            user (User, optional): the user object to check. Defaults to Depends(require_user).
            is_admin (bool, optional): a boolean indicating wheter the user is admin or not. Defaults to Depends(is_admin).

        Raises:
            INSUFFICIENT_PERMISSIONS_ERROR: when the user is not an admin

        Returns:
            Admin: the admin object
        """
        if not is_admin:
            raise INSUFFICIENT_PERMISSIONS_ERROR
        return user


