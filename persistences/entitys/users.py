from sqlalchemy import Column, DateTime, Uuid, String, Text, Integer,func,Column, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    plate_number = Column(String(50), primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String, unique=True, nullable=False)
    face_image = Column(Text, nullable=True)
    plate_image = Column(Text, nullable=True)
    status = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

