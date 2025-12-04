from sqlalchemy import Column, DateTime, Uuid, String, Text, Integer,func,Column, Enum
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
import uuid
from typing import Optional, List
from configs.db_config import engine

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


#  lưu ảnh real time - khi vô / ra
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

class ApprovalRequest(BaseModel):
    plate_number: str
    face_image: str
    plate_image: str
    approval_type: str
    

class AccessControlRequest(BaseModel):
    plate_image: str
    type: str
    

class CheckPlateNumber(BaseModel):
    plate_number: str
    request_type: str

class VerifyBackup(BaseModel):
    plate_number: str
    approval_type: str
    plate_image: str

class BaseResponse(BaseModel):
    is_success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class AccessControlResponse(BaseResponse):
    plate_number: Optional[str] = None
    face_image: Optional[str] = None
    update_time: Optional[str] = None
    count: Optional[int] = None
    full_name:  Optional[str] = None


class AddUser(BaseModel):
    plate_number: str
    full_name: str
    phone_number: str
    email: Optional[str] = None
    face_image: str
    plate_image: str

class UpdateUser(BaseModel):
    plate_number: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    face_image: Optional[str] = None
    plate_image: Optional[str] = None

class DeleteUser(BaseModel):
    plate_number: str

class SearchUser(BaseModel):
    plate_number: str


class UserResponse(BaseResponse): 
    full_name: Optional[str] = None
    plate_number: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[str] = None

# Response models
class HistoryItem(BaseModel):
    id: str
    plate_number: str
    status: str
    count: int
    created_at: str  # created_at

class UserItem(BaseModel):
    plate_number: str
    full_name: str
    email: Optional[str]
    phone_number: Optional[str]
    status: str
    face_image: Optional[str]
    plate_image: Optional[str]

class UserHistoryResponse(BaseModel):
    is_success: bool
    user: Optional[UserItem] = None
    history: List[HistoryItem] = []
    message: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    count: Optional[int] = None
    update_time: Optional[str] = None

# Ensure metadata is in sync when the module is imported.
Base.metadata.create_all(bind=engine)
