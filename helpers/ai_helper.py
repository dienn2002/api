from ultralytics import YOLO
from paddleocr import PaddleOCR
from constants.constant import YOLO_PATH     
import numpy as np
import re
from utils.common_utils import decode_base64_to_cv2

class AIHelper:
    _yolo_model = None
    _ocr_model = None

    @classmethod
    def load_models(cls):
        if cls._yolo_model is None:
            try:
                cls._yolo_model = YOLO(YOLO_PATH)
                print(f"[INFO] YOLO model loaded from {YOLO_PATH}")
            except Exception as e:
                print(f"[ERROR] Failed to load YOLO model: {e}")

        if cls._ocr_model is None:
            try:
                cls._ocr_model = PaddleOCR(use_angle_cls=True, lang='en', show_log=False) 
                print("[INFO] OCR model loaded.")
            except Exception as e:
                print(f"[ERROR] Failed to load OCR model: {e}")

    @classmethod
    def get_plate_number_by_img(cls, img: np.ndarray):
        if cls._yolo_model is None or cls._ocr_model is None:
            cls.load_models()

        if img is None or img.size == 0:
            return None

        try:
            results = cls._yolo_model(img)

            if not results: 
                return None
            
            for plate in results:
                if not plate.boxes or len(plate.boxes) == 0:
                    continue

                for bbox in plate.boxes:
                    if not hasattr(bbox, 'xyxy') or len(bbox.xyxy) == 0:
                        continue

                    x1, y1, x2, y2 = map(int, bbox.xyxy[0])

                    plate_img = img[y1:y2, x1:x2]
                    if plate_img is None or plate_img.size == 0:
                        continue

                    ocr_result = cls._ocr_model.ocr(plate_img, cls=True)

                    plate_text = ""
                    if ocr_result and isinstance(ocr_result, list) and len(ocr_result) > 0 and ocr_result[0] is not None:
                        for line in ocr_result[0]:
                            plate_text += line[1][0] + " "
                    else:
                        continue

                    clean_plate_text = re.sub(r'[^A-Z0-9]', '', plate_text.upper().strip())

                    if clean_plate_text:
                        return clean_plate_text
            
            return None

        except Exception as e:
            print(f"[ERROR] Processing error: {e}")
            return None
    
    @classmethod
    def retrieve_plate_number_from_base64(cls, base64_str: str) -> str | None:
        img = decode_base64_to_cv2(base64_str)
        if img is None:
            return None
        return cls.get_plate_number_by_img(img)    
        