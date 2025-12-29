from persistences.entitys.payment import Payment

class PaymentRepository:

    def __init__(self, session):
        self.session = session

    def get_by_order_code(self, order_code: str):
        return self.session.query(Payment).filter_by(order_code=str(order_code)).first()


    def create_payment(self, plate_number: str, amount: int, order_code: str):
        payment = Payment(
            plate_number=plate_number,
            amount=amount,
            order_code=order_code,
            status="PENDING"
        )
        self.session.add(payment)
        self.session.commit()
        return payment
    
    def update_payment_status(self, payment, reference: str, paid_at: str):
        print(f"[Repository] Cập nhật thanh toán {payment.order_code} to PAID")
        payment.status = "PAID"
        payment.reference = reference
        payment.paid_at = paid_at
        self.session.commit()
        print(f"[Repository] Cập nhật toán {payment.order_code} thành công")




