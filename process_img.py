import cv2
import re
import base64

import numpy as np


# Khởi tạo model YOLO và PaddleOCR 1 lần
 
def get_plate_number_by_img(img: np.ndarray, yolo_model: any, ocr: any):
    """
    Nhận diện biển số từ ảnh OpenCV (np.ndarray)
    Trả về biển số sạch (A-Z, 0-9) hoặc None nếu không đọc được
    """
    if img is None or img.size == 0:
        print("[ERROR] Ảnh đầu vào không hợp lệ")
        return None

    try:
        # Detect biển số bằng YOLO
        results = yolo_model(img)

        if not results: 
            print("[INFO] YOLO không phát hiện gì.")
            return None
        
        for plate in results:

            # if not plate.boxes:
            if not plate.boxes or len(plate.boxes) == 0:
                print("[INFO] Plate boxes rỗng, bỏ qua.")
                continue

            for bbox in plate.boxes:
                if not hasattr(bbox, 'xyxy') or len(bbox.xyxy) == 0:
                    print("[INFO] bbox.xyxy trống, bỏ qua.")
                    continue

                x1, y1, x2, y2 = map(int, bbox.xyxy[0])

                # Crop vùng biển số từ ảnh gốc, giữ tỉ lệ
                plate_img = img[y1:y2, x1:x2]
                if plate_img is None or plate_img.size == 0:
                    print("[INFO] Crop plate_img rỗng, bỏ qua.")
                    continue

                # OCR đọc biển số, cls=True để tự xoay nếu nghiêng
                ocr_result = ocr.ocr(plate_img)

                plate_text = ""
                if ocr_result and len(ocr_result) > 0:
                    for line in ocr_result[0]:
                        plate_text += line[1][0] + " "
                else:
                    print("[INFO] OCR không đọc được gì, bỏ qua.")
                    continue

                # Lọc ký tự: giữ chữ và số
                clean_plate_text = re.sub(r'[^A-Z0-9]', '', plate_text.upper().strip())

                if clean_plate_text:
                    print(f"[DEBUG] Biển số đọc được: {clean_plate_text}")
                    return clean_plate_text
                else:
                    print("[INFO] Sau khi lọc ký tự, không còn gì.")

        print("[INFO] Không detect được biển số nào.")
        return None

    except Exception as e:
        print("[ERROR] Lỗi OCR:", e)
        return None


# Test nhanh biển số
# if __name__ == "__main__":
#     test_img_path = r"D:\api_v2\image\test_1.jpg"
#     img = cv2.imread(test_img_path)
#     plate = get_plate_number_by_img(img)
#     if plate:
#         print("Biển số đọc được:", plate)
#     else:
#         print("Không đọc được biển số")


# đọc khuôn mặt
# Load model 1 lần

# arcface_model = DeepFace.build_model("ArcFace")
# face_detector = MTCNN()

# def get_compare_face(face_ui_np: np.ndarray, face_db_base64: str, tolerance: float = 0.45):
#     """
#     So sánh ảnh khuôn mặt UI (numpy array) với ảnh trong DB (base64)
#     Trả về: is_match (bool), confidence (float)
#     """
#     try:

#         # Decode base64 từ DB → numpy array
   
#         db_bytes = base64.b64decode(face_db_base64)
#         db_np = cv2.imdecode(np.frombuffer(db_bytes, np.uint8), cv2.IMREAD_COLOR)
#         db_rgb = cv2.cvtColor(db_np, cv2.COLOR_BGR2RGB)
#         ui_rgb = cv2.cvtColor(face_ui_np, cv2.COLOR_BGR2RGB)

     
#         # Detect + crop + align
 
#         def detect_crop_align(img_rgb):
#             faces = face_detector.detect_faces(img_rgb)
#             if len(faces) == 0:
#                 return None
#             x, y, w, h = faces[0]['box']
#             x, y = max(0, x), max(0, y)
#             face_crop = img_rgb[y:y+h, x:x+w]
#             face_aligned = cv2.resize(face_crop, (112, 112))  # chuẩn ArcFace
#             return face_aligned

#         face_ui = detect_crop_align(ui_rgb)
#         face_db = detect_crop_align(db_rgb)

#         if face_ui is None or face_db is None:
#             print("Không phát hiện khuôn mặt trong một trong hai ảnh")
#             return False, 0.0
        
        
#         # Lấy embedding bằng ArcFace
     
#         def get_embedding(face_aligned):
#             emb = DeepFace.represent(
#                 img_path=face_aligned,
#                 model_name="ArcFace",
#                 enforce_detection=False
#             )[0]["embedding"]
#             return np.array(emb)

#         emb_ui = get_embedding(face_ui)
#         emb_db = get_embedding(face_db)

   
#         # Tính cosine similarity(độ tương đồng)
    
#         cosine_sim = np.dot(emb_ui, emb_db) / (np.linalg.norm(emb_ui) * np.linalg.norm(emb_db))
#         confidence = round(float(cosine_sim), 2)
#         is_match = cosine_sim >= (1 - tolerance)

#         return is_match, confidence

#     except Exception as e:
#         print("Lỗi trong get_compare_face:", e)
#         return False, 0.0








