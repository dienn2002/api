import os

from payos import PayOS

PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY")

PAYOS_BASE_URL = "https://api-merchant.payos.vn"


if not PAYOS_CLIENT_ID or not PAYOS_API_KEY or not PAYOS_CHECKSUM_KEY:
    raise RuntimeError(
        "Thiếu cấu hình PayOS. Vui lòng kiểm tra các biến môi trường PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY"
    )

payos_client = PayOS(
    client_id=PAYOS_CLIENT_ID,
    api_key=PAYOS_API_KEY,
    checksum_key=PAYOS_CHECKSUM_KEY
)