
from constants.constant import IN, OUT
from sqlalchemy import func
from configs.db_config import session_scope
from persistences.entitys.history import History
import base64
import cv2
import numpy as np
from datetime import datetime

def get_max_count_for_plate(plate_number: str, status: str) -> int:
    try:
        with session_scope() as db:
            max_count = (
                db.query(func.max(History.count))
                .filter(History.plate_number == plate_number, History.status == status)
                .scalar()
            )
            return max_count or 0
    except Exception as e:
        print(f"[get_max_count_for_plate] Error: {e}")
        return 0

def decode_base64_to_cv2(base64_str: str):
    img_bytes = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def encode_cv2_to_base64(img) -> str:
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

def format_db_time(dt):
    if not dt:
        print("[format_db_time] Warning: Received None as datetime input")
        return None
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"[format_db_time] Error: {e}")
        return None
    
def validate_type_request(request_type: str):
    return request_type and request_type.upper() in [IN, OUT]
