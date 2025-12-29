from sqlalchemy import Column, DateTime, String, Integer,func, Enum, ForeignKey
from sqlalchemy.orm import declarative_base
import uuid


Base = declarative_base()


# class Payment(Base):
#     __tablename__ = "payments"

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     plate_number = Column(String(50), ForeignKey("users.plate_number"))
#     amount = Column(Integer, nullable=False)
#     payment_code = Column(String(100), unique=True)
#     status = Column(Enum("PENDING","PAID","FAILED"), default="PENDING")
#     created_at = Column(DateTime, server_default=func.now())
#     update_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plate_number = Column(String(50), ForeignKey("users.plate_number"))
    amount = Column(Integer, nullable=False)
    order_code = Column(String(100), unique=True, nullable=False)
    status = Column(Enum("PENDING", "PAID", "FAILED", name="payment_status"), nullable=False, default="PENDING")
    reference = Column(String(100))  # Mã giao dịch PayOS
    paid_at = Column(DateTime, nullable=True)

