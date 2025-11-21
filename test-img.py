
import cv2
import re
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR

yolo_model = YOLO(r"D:\api_v2\model\best_final.pt")
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
)
def get_plate_number_by_img(img: np.ndarray):
    # img = cv2.imread(test_img_path)
    
    if img is None or img.size == 0:
        print("Ảnh đầu vào không hợp lệ")
        return None

    try:
        # Detect biển số bằng YOLO
        results = yolo_model(img)

        for plate in results:
            if not plate.boxes:
                continue

        for bbox in plate.boxes:
            x1, y1, x2, y2 = map(int, bbox.xyxy[0])

            # Crop vùng biển số từ ảnh gốc, giữ tỉ lệ
            plate_img = img[y1:y2, x1:x2]
            if plate_img is None or plate_img.size == 0:
                continue

            # OCR đọc biển số, cls=True để tự xoay nếu nghiêng
            ocr_result = ocr.ocr(img)
            # ocr_result = ocr.predict(img)

            plate_text = ""
            if ocr_result and len(ocr_result) > 0:
                for line in ocr_result[0]:
                    plate_text += line[1][0] + " "

            # Lọc ký tự: giữ chữ và số
            clean_plate_text = re.sub(r'[^A-Z0-9]', '', plate_text.upper().strip())

            if clean_plate_text:
                return clean_plate_text

        return None

    except Exception as e:
        print("Lỗi OCR:", e)
        return None


# Test nhanh
if __name__ == "__main__":
    test_img_path = r"D:\api\image\test_3.jpg"
    img = cv2.imread(test_img_path)
    
    plate = get_plate_number_by_img(img)
    if plate:
        print("Biển số đọc được:", plate)
    else:
        print("Không đọc được biển số")
