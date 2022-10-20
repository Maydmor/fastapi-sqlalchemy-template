import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from database.models import Base

class RoleName(enum.Enum):
    user = 'user'
    admin = 'admin'

class Role(Base):
    __tablename__ = 'roles'
    name = Column(Enum(RoleName), primary_key=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role_name = Column(String, ForeignKey('roles.name'))
    role = relationship('Role')
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

