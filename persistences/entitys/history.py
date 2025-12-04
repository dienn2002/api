import uuid
from sqlalchemy import Column, DateTime, String, Text, Integer, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class History(Base):
    __tablename__ = "history"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    plate_number = Column(String(50), index = True, nullable = False)
    face_image = Column(Text, nullable=True)
    plate_image = Column(Text, nullable=True)
    status = Column(Text, nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
