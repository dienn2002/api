import requests
import hmac
import hashlib
import json
import time


class PayOSService:

    def __init__(self, client_id, api_key, checksum_key):
        self.client_id = client_id
        self.api_key = api_key
        self.checksum_key = checksum_key
        self.base_url = "https://api.payos.vn"

    def create_signature(self, data: dict):
        raw = (
            f"amount={data['amount']}"
            f"&orderCode={data['orderCode']}"
            f"&description={data['description']}"
            f"&returnUrl={data['returnUrl']}"
            
        )

        return hmac.new(
            self.checksum_key.encode(),
            raw.encode(),
            hashlib.sha256
        ).hexdigest()


    # def create_payment(self, order_code: str, amount: int, return_url: str, cancel_url: str):
        
    #     payload = {
    #         "orderCode": order_code,
    #         "amount": amount,
    #         "description": f"Thanh toán gửi xe - Mã đơn {order_code}",
    #         "returnUrl": return_url,
    #         "cancelUrl": cancel_url,
    #     }

    #     payload["signature"] = self.create_signature(payload)

    #     headers = {
    #         "x-client-id": self.client_id,
    #         "x-api-key": self.api_key,
    #         "Content-Type": "application/json"
    #     }

    #     res = requests.post(
    #         f"{self.base_url}/v2/payment-requests",
    #         headers=headers,
    #         json=payload,
    #         timeout=10
    #     )

    #     try:
    #         res.raise_for_status()
    #         return res.json()
    #     except requests.HTTPError as e:
    #         return {"error": str(e), "status_code": res.status_code}
    def create_payment(self, amount: int, description: str):
        payload = {
            "orderCode": int(time.time()),
            "amount": amount,
            "description": description,
            "returnUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel"
        }

        payload["signature"] = create_signature(payload)

        headers = {
            "x-client-id": PAYOS_CLIENT_ID,
            "x-api-key": PAYOS_API_KEY,
            "Content-Type": "application/json"
        }

        res = requests.post(PAYOS_URL, json=payload, headers=headers)
        res.raise_for_status()

        return res.json()["data"]