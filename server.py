
import base64
import cv2, numpy as np

from fastapi import FastAPI, HTTPException, File, UploadFile, Form

from db_config import SessionLocal, session_scope
from models import *
from process_img import get_plate_number_by_img
from fastapi import APIRouter
from ultralytics import YOLO
from paddleocr import PaddleOCR
from sqlalchemy import func
from message_error import MessageError
import constant as const


# ___________Khởi tạo ứng dụng FastAPI_____________________
app = FastAPI(title="Hệ thống ra vào cổng thông minh")

api_v1 = APIRouter(prefix = "/smart-gate/v1")

yolo_model = YOLO(r"D:\api\model\best_final.pt")

ocr = PaddleOCR(use_angle_cls=True, lang='en')
# ______________KẾT NỐI DB______________________
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# ______________API______________________
@app.get("/")
def root():
    return {"message": "Hệ thống ra vào cổng thông minh."}


# @app.post("/access-control-in")
@api_v1.post("/access-control/request", response_model_exclude_none=True)
async def handle_request(request: AccessControlRequest):
    try:
        if not validate_type_request(request.type):
            return  AccessControlResponse(
                is_success = False,
                error_code = MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message = MessageError.TYPE_NOT_SUPPORTED.message()
            )

        plate_number = retrievePlateNumber(request.plate_image)

        if not plate_number:
            return AccessControlResponse(
                is_success = False,
                error_code = MessageError.DETECT_PLATE_NUMBER_ERROR.code(),
                error_message = MessageError.DETECT_PLATE_NUMBER_ERROR.message()
            )
        
        with session_scope() as session:
            user = (
                session.query(User)
                .filter_by(plate_number=plate_number)
                .order_by(User.created_at.desc())
                .first()
            )
    
            if user:
                if user.status == request.type.upper():
                    # Xe đang IN thi request OUT moi chap nhan - hieu khong -                   
                    response = AccessControlResponse(
                        is_success = False,
                        plate_number = plate_number,
                        face_image = user.face_image,
                        error_code = MessageError.STATUS_INVALID.code(),
                        error_message = MessageError.STATUS_INVALID.message(),
                        full_name = user.full_name
                    )

                else:
                    response = AccessControlResponse(
                        is_success = True,
                        plate_number = plate_number,
                        face_image = user.face_image,
                        update_time = format_db_time(user.update_at),
                        count = get_max_count_for_plate(plate_number, const.IN),
                        full_name = user.full_name
                    )
            
            else:
                response = AccessControlResponse(
                    is_success = False,
                    plate_number = plate_number,
                    error_code = MessageError.NOT_FOUND.code(),
                    error_message = MessageError.NOT_FOUND.message()
                )
        print("[HANDLE_REQUEST] - type: " + str(request.type) + " plate_number: " + plate_number + " response: " + str(response)[:50])
        return response
    
    except Exception as e:
        print(e)
        return  AccessControlResponse(
            is_success = False,
            error_code = MessageError.SERVER_ERROR.code(),
            error_message = MessageError.SERVER_ERROR.message()
        )
    
@api_v1.post("/access-control/verify-backup", response_model_exclude_none=True)
async def handle_approval_request(request_data: VerifyBackup):
    try:
        if not validate_type_request(request_data.approval_type):
            return  AccessControlResponse(
                is_success = False,
                error_code = MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message = MessageError.TYPE_NOT_SUPPORTED.message()
            )

        new_history = History(
            plate_number=request_data.plate_number,
            plate_image=request_data.plate_image,
            face_image="Xác nhận bởi Nhân Viên",
            status=request_data.approval_type,
            count=get_max_count_for_plate(request_data.plate_number, request_data.approval_type) + 1,
        )

        with session_scope() as session:
            session.add(new_history)
            print("[INSERT_HISTTORY] [BACKUP] [" + request_data.approval_type + "] successfully!")
        
            session.query(User).filter(
                User.plate_number == request_data.plate_number
            ).update(
                {
                    User.status: request_data.approval_type
                },
                synchronize_session='fetch'
            )

        return BaseResponse(is_success = True)
    
    except Exception as e:
        print("[handle_approval_request] error: " + e)
        return BaseResponse(is_success = False)
    
@api_v1.post("/access-control/success", response_model_exclude_none=True)
async def handle_approval_request(request_data: ApprovalRequest):
    try:
        if not validate_type_request(request_data.approval_type):
            return  AccessControlResponse(
                is_success = False,
                error_code = MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message = MessageError.TYPE_NOT_SUPPORTED.message()
            )

        new_history = History(
            plate_number=request_data.plate_number,
            face_image=request_data.face_image,
            plate_image=request_data.plate_image,
            status=request_data.approval_type,
            count=get_max_count_for_plate(request_data.plate_number, request_data.approval_type) + 1,
        )

        with session_scope() as session:
            session.add(new_history)
            print("[INSERT_HISTTORY] [" + request_data.approval_type + "] successfully!")
        
            session.query(User).filter(
                User.plate_number == request_data.plate_number
            ).update(
                {
                    User.status: request_data.approval_type
                },
                synchronize_session='fetch'
            )

        return BaseResponse(is_success = True)
    
    except Exception as e:
        print("[handle_approval_request] error: " + e)
        return BaseResponse(is_success = False)
    
@api_v1.post("/access-control/check-plate-number", response_model_exclude_none=True)
async def handle_check_plate_number(request_data: CheckPlateNumber):
    try:
        if not validate_type_request(request_data.request_type):
            return  AccessControlResponse(
                is_success = False,
                error_code = MessageError.TYPE_NOT_SUPPORTED.code(),
                    error_message = MessageError.TYPE_NOT_SUPPORTED.message()
                )

        with session_scope() as session:
            user = (
                session.query(User)
                .filter_by(plate_number=request_data.plate_number)
                .order_by(User.created_at.desc())
                .first()
            )
    
            if user:
                if user.status == request_data.request_type.upper():
                    # Xe đang IN thi request OUT moi chap nhan - hieu khong -                   
                    response = AccessControlResponse(
                        is_success = False,
                        plate_number = request_data.plate_number,
                        face_image = user.face_image,
                        error_code = MessageError.STATUS_INVALID.code(),
                        error_message = MessageError.STATUS_INVALID.message(),
                        full_name = user.full_name,
                    )

                else:
                    response = AccessControlResponse(
                        is_success = True,
                        plate_number = request_data.plate_number,
                        face_image = user.face_image,
                        update_time = format_db_time(user.update_at),
                        count = get_max_count_for_plate(request_data.plate_number, const.IN),
                        full_name = user.full_name
                    )
            
            else:
                response = AccessControlResponse(
                    is_success = False,
                    plate_number = request_data.plate_number,
                    error_code = MessageError.NOT_FOUND.code(),
                    error_message = MessageError.NOT_FOUND.message()
                )
        print("[CHECK_REQUEST] - type: " + str(request_data.request_type) + " plate_number: " + request_data.plate_number + " response: " + str(response)[:50])
        return response

    except Exception as e:
        print("[handle_check_plate_number] error: " + e)
        return BaseResponse(is_success = False)

# app.include_router(api_v1)

def validate_type_request(request_type: str) -> bool:
    return request_type in (const.IN, const.OUT)
        

def get_max_count_for_plate(target_plate_number: str, status: str) -> int:
    try:
        # Sử dụng Context Manager để lấy session
        with session_scope() as db:
            
            # 1. Thực hiện Truy vấn MAX có điều kiện lọc (Filter)
            max_count_result = (
                db.query(func.max(History.count))
                .filter(History.plate_number == target_plate_number, History.status == status) # <-- Lọc theo plate_number
                .scalar()
            )
            
            # 2. Xử lý giá trị
            if max_count_result is None:
                max_count_result = 0
                
            return max_count_result

    except Exception as e:
        print(f"Lỗi khi truy vấn MAX count cho plate {target_plate_number}: {e}")
        # Trả về 1 hoặc raise lỗi nếu có vấn đề nghiêm trọng
        return 0
    
def retrievePlateNumber(plate_image: str) -> str:
    plate_np = cv2.imdecode(np.frombuffer(base64.b64decode(plate_image), np.uint8), cv2.IMREAD_COLOR)
    return get_plate_number_by_img(plate_np, yolo_model, ocr)



# quan ly người dùng
@api_v1.post("/access-control/add_user", response_model_exclude_none=True)
async def add_user(request: AddUser):
    if not request.user:
        raise HTTPException(status_code=400, detail="Thiếu dữ liệu người dùng")
    try:
        with session_scope() as session:
            exists = session.query(User).filter(
                (User.email == request.user.email) |
                (User.phone_number == request.user.phone_number) |
                (User.plate_number == request.user.plate_number)
            ).first()
            if exists:
                raise HTTPException(status_code=400, detail="Email, số điện thoại hoặc biển số đã tồn tại")
            
            user = User(**request.user.dict(exclude={"id"}))
            session.add(user)
            session.commit()
            session.refresh(user)
            return {"is_success": True, "message": "Thêm người dùng thành công", "data": {"id": user.id}}
    except Exception as e:
        return {"is_success": False, "message": str(e), "data": None}
    

@api_v1.put("/access-control/update-user", response_model_exclude_none=True)
async def update_user(request: UpdateUser):
    if not request.user or not request.user.id:
        raise HTTPException(status_code=400, detail="Thiếu ID người dùng")
    try:
        with session_scope() as session:
            user = session.query(User).filter_by(id=request.user.id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
            for key, value in request.user.dict(exclude_unset=True, exclude={"id"}).items():
                setattr(user, key, value)
            session.commit()
            session.refresh(user)
            return {"is_success": True, "message": "Cập nhật thành công", "data": {"id": user.id}}
    except Exception as e:
        return {"is_success": False, "message": str(e), "data": None}


@api_v1.delete("/access-control/delete-user", response_model_exclude_none=True)
async def delete_user(request: DeleteUser):
    if not request.user or not request.user.id:
        raise HTTPException(status_code=400, detail="Thiếu ID người dùng")
    try:
        with session_scope() as session:
            user = session.query(User).filter_by(id=request.user.id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
            session.delete(user)
            session.commit()
            return {"is_success": True, "message": "Xóa thành công", "data": None}
    except Exception as e:
        return {"is_success": False, "message": str(e), "data": None}

@api_v1.post("/access-control/search-user-history", response_model=UserHistoryResponse)
def search_user_history(request_data: CheckPlateNumber):
    try:
        if not validate_type_request(request_data.request_type):
            return UserHistoryResponse(
                is_success=False,
                error_code=MessageError.TYPE_NOT_SUPPORTED.code(),
                error_message=MessageError.TYPE_NOT_SUPPORTED.message()
            )

        with session_scope() as session:
            # 1Lấy thông tin user
            user = (
                session.query(User)
                .filter_by(plate_number=request_data.plate_number)
                .order_by(User.created_at.desc())
                .first()
            )

            user_obj = None
            if user:
                user_obj = UserItem(
                    plate_number=user.plate_number,
                    full_name=user.full_name,
                    email=user.email,
                    phone_number=user.phone_number,
                    status=user.status,
                    face_image=user.face_image,
                    plate_image=user.plate_image
                )

            # Lấy lịch sử 20 bản ghi gần nhất
            histories = (
                session.query(History)
                .filter(History.plate_number == request_data.plate_number)
                .order_by(History.created_at.desc())
                .limit(20)
                .all()
            )

            history_list = [
                HistoryItem(
                    id=h.id,
                    plate_number=h.plate_number,
                    status=h.status,
                    count=h.count,
                    timestamp=format_db_time(h.created_at)
                ) for h in histories
            ]

            # 3Kiểm tra logic IN / OUT
            if user:
                if user.status == request_data.request_type.upper():
                    return UserHistoryResponse(
                        is_success=False,
                        user=user_obj,
                        history=history_list,
                        error_code=MessageError.STATUS_INVALID.code(),
                        error_message=MessageError.STATUS_INVALID.message()
                    )
                else:
                    return UserHistoryResponse(
                        is_success=True,
                        user=user_obj,
                        history=history_list,
                        update_time=format_db_time(user.update_at),
                        count=get_max_count_for_plate(request_data.plate_number, const.IN)
                    )
            else:
                return UserHistoryResponse(
                    is_success=False,
                    history=history_list,
                    error_code=MessageError.NOT_FOUND.code(),
                    error_message=MessageError.NOT_FOUND.message()
                )

    except Exception as e:
        return UserHistoryResponse(
            is_success=False,
            message=str(e)
        )


from datetime import datetime

def format_db_time(dt_value):
    if not dt_value:
        return None
    
    # 2. Nếu đúng là kiểu datetime thì format
    if isinstance(dt_value, datetime):
        return dt_value.strftime("%H:%M:%S %d/%m/%Y")
    
  
    return str(dt_value)

app.include_router(api_v1)