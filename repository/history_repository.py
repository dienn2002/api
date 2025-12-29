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

    def delete_by_plate_number(self, session, plate_number: str):
        session.query(History).filter(History.plate_number == plate_number).delete()
        session.flush()  

    def get_all_history(self, session: Session):
        return session.query(History).order_by(History.created_at.desc()).all()
    
    # def get_last_in(self, session: Session, plate_number: str):
    #     return (
    #         session.query(History)
    #         .filter(History.plate_number == plate_number, History.status == 'IN')
    #         .order_by(History.created_at.desc())
    #         .first()
    #     )

    # def get_latest_in_out(self, session: Session, plate_number: str):
        # records = (
        #     session.query(History)
        #     .filter(History.plate_number == plate_number)
        #     .order_by(History.created_at.desc())
        #     .all()
        # )

        # if not records:
        #     return None
        
        # time_out = None
        # time_in = None

        # #1. tìm OUT gần nhất
        # for r in records:
        #     if r.status == "OUT":
        #         time_out = r.created_at
        #         break
        
        # # chưa có OUT  thì kh thanh toán được
        # if not time_out:
        #     return {"plate_number": plate_number, "time_in": None, "time_out": None}

        
        # #2. tìm IN ngay trước OUT
        # for r in records:
        #     if r.status == "IN" and r.created_at < time_out:
        #         time_in = r.created_at
        #         break

        # if not time_in:
        #     return None
        
        # return {
        #     "plate_number": plate_number,
        #     "time_in": time_in,
        #     "time_out": time_out
        # }