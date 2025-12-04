from sqlalchemy.orm import Session
from persistences.entitys.history import History
from sqlalchemy import func

class HistoryRepository:

    def get_by_plate_number(self, session: Session, plate_number: str, limit: int = 20):
        return session.query(History).filter(History.plate_number == plate_number).order_by(History.created_at.desc()).limit(limit).all()

    def create_history(self, session: Session, history: History):
        session.add(history)
        session.commit()
        session.refresh(history)
        return history

    def max_count_for_plate(self, session: Session, plate_number: str, status: str):
        max_count = session.query(func.max(History.count)).filter(History.plate_number == plate_number, History.status == status).scalar()
        return 0 if max_count is None else max_count

    def count_by_plate_and_status(self, session: Session, plate_number: str, status: str):
        return session.query(History).filter(History.plate_number == plate_number, History.status == status).count()
