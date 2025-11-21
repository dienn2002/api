from sqlalchemy import Column, DateTime, Uuid, String, Text, Integer,func,Column, Enum
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
import uuid
from typing import Optional

from db_config import engine

Base = declarative_base()

from enum import Enum as PyEnum


class StatusEnum(PyEnum):
    IN = "IN"
    OUT = "OUT"

class User(Base):
    __tablename__ = "users"

    plate_number = Column(String(50), primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    face_image = Column(Text, nullable=True)
    plate_image = Column(Text, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


#  lưu ảnh real time - khi vô / ra
class History(Base):
    __tablename__ = "history"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    plate_number = Column(String(50), index = True, nullable = False)
    face_image = Column(Text, nullable=True)
    plate_image = Column(Text, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ApprovalRequest(BaseModel):
    plate_number: str
    face_image: str
    plate_image: str
    approval_type: str

class AccessControlRequest(BaseModel):
    plate_image: str
    type: str

class BaseResponse(BaseModel):
    is_success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class AccessControlResponse(BaseResponse):
    plate_number: Optional[str] = None
    face_image: Optional[str] = None





# Ensure metadata is in sync when the module is imported.
Base.metadata.create_all(bind=engine)

