from sqlalchemy.orm import Session

from app.db.models import Order
from app.services.payment_service import PaymentService
from app.services.audit_service import log_event


payment_service = PaymentService()


def verify_payment(
    db: Session,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
):

    order = (
        db.query(Order)
        .filter(
            Order.razorpay_order_id
            == razorpay_order_id
        )
        .first()
    )

    if not order:
        raise ValueError(
            "Order not found"
        )

    if order.payment_status == "paid":
        return {
            "success": True,
            "already_paid": True,
            "order_id": order.id,
            "payment_id": order.payment_id
        }

    valid = payment_service.verify_payment_signature(
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature
    )

    if not valid:

        log_event(
            db=db,
            action="PAYMENT_VERIFICATION_FAILED",
            actor="SYSTEM",
            order_id=order.id,
            details={
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id
            }
        )

        raise ValueError(
            "Invalid payment signature"
        )

    order.payment_id = razorpay_payment_id
    order.payment_status = "paid"
    order.status = "paid"

    db.commit()
    db.refresh(order)

    log_event(
        db=db,
        action="PAYMENT_VERIFIED",
        actor="SYSTEM",
        order_id=order.id,
        details={
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "amount": float(order.total),
            "currency": order.currency
        }
    )

    return {
        "success": True,
        "already_paid": False,
        "order_id": order.id,
        "payment_id": order.payment_id,
        "payment_status": order.payment_status
    }