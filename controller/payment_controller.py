from fastapi import APIRouter, Request, HTTPException
from persistences.dto.app_dto import PaymentResponse, PaymentRequest, CreatePaymentRequest
from services.payment_service import PaymentService
from fastapi.responses import JSONResponse
from configs.db_config import SessionLocal

router = APIRouter(prefix="/payment", tags=["Payment"])

payment_service = PaymentService()


@router.post("/create")
def create_payment(req: CreatePaymentRequest):
    return payment_service.create_payment(req.plate_number)

@router.get("/return")
def payment_return(orderCode: str = None, status: str = None, cancel: str = None):
    if cancel == "true":
        return {"is_success": False, "message": "Thanh toán đã hủy", "order_code": orderCode}

    if status == "PAID":
        return {"is_success": True, "message": "Mời xe ra", "order_code": orderCode}

    return {"is_success": False, "message": f"Thanh toán thất bại ({status})", "order_code": orderCode}


@router.get("/cancel")
def payment_cancel():
    return {"message": "Đã hủy thanh toán"}

@router.post("/webhook")
async def payos_webhook(request: Request):
    payload = await request.json()
    signature = request.headers.get("x-payos-signature")

    if not signature:
        return {"message": "No signature, ignore"}

    if not payment_service.verify_webhook_signature(payload, signature):
        return {"message": "Invalid signature, ignore"}

    status = payload.get("data", {}).get("status")
    if status != "SUCCESS":
        return {"message": f"Payment status {status}, ignore"}

    # Chỉ khi webhook hợp lệ và SUCCESS
    print("Webhook verified and payment SUCCESS!")
    print("PAYLOAD: ", payload)

    try:
        payment_service.handle_payment_success(payload["data"])
        print("Payment successfully updated in DB")
    except Exception as e:
        print("Error handling payment:", e)
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "ok"}



# @router.get("/status/{order_code}")
# async def get_payment_status(order_code: str):
#     payment = payment_service.get_payment_by_order_code(order_code)
#     if not payment:
#         return JSONResponse(
#             status_code=404,
#             content={"is_success": False, "message": "Payment not found"}
#         )

#     return {
#         "is_success": True,
#         "order_code": payment.order_code,
#         "status": payment.status,  # PENDING / PAID / FAILED
#         "amount": payment.amount,
#         "plate_number": payment.plate_number
#     }
