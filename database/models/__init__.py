from database import Base, SessionLocal,engine
from sqlalchemy.orm import Session
from database.models.user import User, Role, RoleName
from database.services.user import create_user, get_user_by_email, get_users 

def setup():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    for role_name in RoleName:
        role = db.query(Role).get(role_name.name)
        if role is None:
            db.add(Role(name=role_name))
    db.commit()
    admin_role = db.query(Role).get(RoleName.admin)
    assert admin_role != None
    all_admins = get_users(db, filters=[User.role_name == RoleName.admin.value])
    if len(all_admins) == 0:
        create_user(db, email='a@s.d', password='1', role_name=RoleName.admin.value)
