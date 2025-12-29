
from configs.db_config import session_scope, SessionLocal
from configs.payos_config import PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY, PAYOS_BASE_URL
from repository.payment_repository import PaymentRepository
from repository.history_repository import HistoryRepository
from persistences.entitys.payment import Payment
from persistences.dto.app_dto import  PaymentResponse

import requests
import time
import hmac
import hashlib

   
class PaymentService:
    FIXED_AMOUNT = 3000

    def _create_signature(self, payload: dict) -> str:
        data = {
            "amount": payload["amount"],
            "cancelUrl": payload["cancelUrl"],
            "description": payload["description"],
            "orderCode": payload["orderCode"],
            "returnUrl": payload["returnUrl"],
        }

        raw = "&".join(f"{k}={data[k]}" for k in sorted(data.keys()))

        signature = hmac.new(
            PAYOS_CHECKSUM_KEY.encode("utf-8"),
            raw.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return signature


    def create_payment(self, plate_number: str):
        order_code = int(time.time())  # unique

        payload = {
            "orderCode": order_code,
            "amount": self.FIXED_AMOUNT,
            "description": f"Xe {plate_number}",
            "returnUrl": "http://localhost:8000/smart-gate/v1/payment/return",
            "cancelUrl": "http://localhost:8000/smart-gate/v1/payment/cancel"
        }
        print("=== PAYOS REQUEST ===")
        print(payload)


        payload["signature"] = self._create_signature(payload)

        headers = {
            "x-client-id": PAYOS_CLIENT_ID,
            "x-api-key": PAYOS_API_KEY,
            "Content-Type": "application/json"
        }

        url = f"{PAYOS_BASE_URL}/v2/payment-requests"

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        payos_resp = response.json()

        print("PAYOS RAW RESPONSE =", payos_resp)

        if payos_resp.get("code") != "00":
            raise RuntimeError(payos_resp.get("desc", "PayOS error"))

        data = payos_resp["data"]

        return {
            "is_success": True,
            "amount": self.FIXED_AMOUNT,
            "orderCode": data["orderCode"],
            "checkoutUrl": data["checkoutUrl"],
            "qrCode": data["qrCode"]
            
        }

    
      # VERIFY WEBHOOK

    def verify_webhook_signature(self, data: dict, signature: str) -> bool:
        sorted_items = sorted(data.items())
        raw_data = "&".join(f"{k}={v}" for k, v in sorted_items)

        expected = hmac.new(
            PAYOS_CHECKSUM_KEY.encode(),
            raw_data.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    # ==========================
    # HANDLE PAYMENT SUCCESS
    # ==========================
    def handle_payment_success(self, data: dict):
        order_code = data["orderCode"]
        # reference = data["reference"]
        paid_time = data["transactionDateTime"]
        print(f"Xử lý thanh toán thành công cho order_code={order_code}, paid_time={paid_time}")

        with session_scope() as session:
            payment_repo = PaymentRepository(session)
            # history_repo = HistoryRepository(session)

            payment = payment_repo.get_by_order_code(order_code)
            if not payment:
                print("Không tìm thấy khoản thanh toán ở DB")
                raise RuntimeError("Payment not found")

            if payment.status == "PAID":
                print("Thanh toán đã TRẢ TIỀN, bỏ qua webhook trùng lặp")
                return  # chống webhook gửi lại

            print(f"Đang cập nhật thanh toán {order_code} status to PAID")
            payment_repo.update_payment_status(payment, reference=order_code, paid_at=paid_time)
            print(f"Đã cập nhật thanh toán {order_code} thành công")
            # history_repo.mark_paid_by_plate(payment.plate_number)


    # def get_payment_by_order_code(self, order_code: str):
    #     session = SessionLocal()
    #     try:
    #         return session.query(Payment).filter_by(order_code=order_code).first()
    #     finally:
    #         session.close()