from sqlalchemy.orm import Session
from persistences.entitys.users import User

class UserRepository:

    def get_by_plate_number(self, session: Session, plate_number: str):
        return session.query(User).filter(User.plate_number == plate_number).order_by(User.created_at.desc()).first()

    def get_by_email(self, session: Session, email: str):
        return session.query(User).filter(User.email == email).first()

    def add_user(self, session: Session, user: User):
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def update_user(self, session: Session, plate_number: str, data: dict):
        session.query(User).filter(User.plate_number == plate_number).update(data, synchronize_session='fetch')
        session.commit()
        return session.query(User).filter(User.plate_number == plate_number).first()

    def delete_user(self, session: Session, plate_number: str):
        deleted = session.query(User).filter(User.plate_number == plate_number).delete()
        session.commit()
        return deleted > 0

    def update_status(self, session: Session, plate_number: str, status: str):
        session.query(User).filter(User.plate_number == plate_number).update({User.status: status}, synchronize_session='fetch')
        session.commit()
