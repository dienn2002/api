
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
@api_v1.post("/access-control/request")
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
                        error_message = MessageError.STATUS_INVALID.message()
                    )

                else:
                    response = AccessControlResponse(
                        is_success = True,
                        plate_number = plate_number,
                        face_image = user.face_image
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
    
@api_v1.post("/access-control/success")
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
            count=get_next_count_for_plate(request_data.plate_number, request_data.approval_type), # thêm DK vao ra
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

app.include_router(api_v1)

def validate_type_request(request_type: str) -> bool:
    return request_type in (const.IN, const.OUT)
        

def get_next_count_for_plate(target_plate_number: str, status: str) -> int:
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
                # Nếu chưa có bản ghi nào với biển số này, bắt đầu từ 1
                next_count = 1
            else:
                # Tăng giá trị MAX tìm được lên 1
                next_count = max_count_result + 1
                
            return next_count

    except Exception as e:
        print(f"Lỗi khi truy vấn MAX count cho plate {target_plate_number}: {e}")
        # Trả về 1 hoặc raise lỗi nếu có vấn đề nghiêm trọng
        return 1
    
def retrievePlateNumber(plate_image: str) -> str:
    plate_np = cv2.imdecode(np.frombuffer(base64.b64decode(plate_image), np.uint8), cv2.IMREAD_COLOR)
    return get_plate_number_by_img(plate_np, yolo_model, ocr)



# đăng ký người dùng

@app.post("/register-user")
async def register_user(
    plate_number: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    image_face: UploadFile = File(...),
):
    try:
        # 1. Chuyển ảnh thô thành base64
        face_bytes = await image_face.read()
        face_base64 = base64.b64encode(face_bytes).decode("utf-8")

        # 2. Kiểm tra DB xem đã có plate_number hoặc email chưa
        with session_scope() as session:
            existing_user = session.query(User).filter(
                (User.plate_number == plate_number) | (User.email == email)
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Biển số hoặc email đã tồn tại")

            # 3. Tạo user mới
            user = User(
                plate_number=plate_number,
                full_name=full_name,
                email=email,
                face_image=face_base64,
                plate_image=None,
                status=const.OUT  #OUT lúc đăng ký (xe chưa đi vào cổng lần nào), đúng với trạng thái “chưa vào bãi”
            )
            session.add(user)

        return {"message": "Đăng ký thành công!", "plate_number": plate_number}  

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))