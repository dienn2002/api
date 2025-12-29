from sqlalchemy import Column, DateTime, Uuid, String, Text, Integer,func,Column, Enum
from pydantic import BaseModel, Field
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


class PaymentRequest(BaseModel):
    plate_number: str
    
    
class PaymentResponse(BaseResponse):
    is_success: bool
    payment_code: Optional[str] = None
    amount: Optional[int] = None
    qr_code: Optional[str] = None
    checkout_url : Optional[str] = None
    message: Optional[str] = None

class LastestInOutResponse(BaseModel):
    is_success: bool
    plate_number: str
    time_in: Optional[str] = None
    time_out: Optional[str] = None
    tong_thoi_gian : int = 0
    so_tien: int = 0
    error_message: Optional[str] = None  
    error_code: Optional[str] = None


class CreatePaymentRequest(BaseModel):
    plate_number: str 
   
Base.metadata.create_all(bind=engine)
