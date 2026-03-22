"""
PhonePe Payments Router
Handles payment callbacks, status checks, and refunds.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import uuid4
from .. import models, schemas, database
from .auth import get_current_user
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import secrets
import json

security = HTTPBasic()

def verify_phonepe_webhook(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify Basic Auth credentials for PhonePe webhook."""
    correct_username = os.getenv("PHONEPE_WEBHOOK_USER", "phonepe_secret_user")
    correct_password = os.getenv("PHONEPE_WEBHOOK_PASS", "phonepe_secret_pass")
    
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect webhook credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Payments"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
    }
)


@router.post(
    "/callback",
    summary="PhonePe payment callback (server-to-server)",
    description="""
    Called by PhonePe servers after a payment is completed, failed, or cancelled.
    This endpoint is **unauthenticated** — it's called by PhonePe, not by users.
    
    The callback updates the order's payment_status and order status accordingly:
    - Payment COMPLETED → payment_status = Completed, order status = Processing
    - Payment FAILED → payment_status = Failed, order status stays Pending
    """
)
async def phonepe_callback(
    request: Request, 
    db: Session = Depends(database.get_db),
    _auth: str = Depends(verify_phonepe_webhook)
):
    """Handle PhonePe server-to-server callback."""
    from ..services import phonepe_service
    
    try:
        # Parse the callback body
        body = await request.json()
        print(f"[PHONEPE CALLBACK] Received: {body}")
        
        # The callback typically contains the merchantOrderId
        # We need to verify the payment status with PhonePe
        merchant_order_id = body.get("merchantOrderId") or body.get("merchant_order_id")
        
        if not merchant_order_id:
            # Try to extract from nested data
            data = body.get("data", {})
            merchant_order_id = data.get("merchantOrderId") or data.get("merchant_order_id")
        
        if not merchant_order_id:
            print("[PHONEPE CALLBACK] No merchantOrderId found in callback")
            return {"success": False, "message": "Missing merchantOrderId"}
        
        # Verify the payment status with PhonePe SDK
        try:
            status_result = phonepe_service.check_payment_status(merchant_order_id)
            payment_state = status_result.get("state", "UNKNOWN")
        except Exception as e:
            print(f"[PHONEPE CALLBACK] Error checking status: {e}")
            payment_state = "UNKNOWN"
        
        # Find the order by merchant_order_id
        order = db.query(models.Order).filter(
            models.Order.merchant_order_id == merchant_order_id
        ).first()
        
        if not order:
            print(f"[PHONEPE CALLBACK] Order not found for merchant_order_id: {merchant_order_id}")
            return {"success": False, "message": "Order not found"}
        
        # Update order based on payment state
        if payment_state == "COMPLETED":
            order.payment_status = models.PaymentStatus.Completed
            order.status = models.OrderStatus.Processing
            print(f"[PHONEPE CALLBACK] Order {order.id} payment COMPLETED")
            
            # Send order confirmation email
            try:
                from ..services.email_service import dispatch_order_placed
                order_dict = {
                    'id': order.id,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at,
                    'payment_method': order.payment_method,
                    'items': [
                        {
                            'name': item.product.name if item.product else "Unknown Product",
                            'quantity': item.quantity,
                            'price': item.price
                        }
                        for item in order.items
                    ]
                }
                dispatch_order_placed(order.customer_email, order.customer_name, order_dict)
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send order confirmation after payment: {str(e)}")
                
        elif payment_state == "FAILED":
            order.payment_status = models.PaymentStatus.Failed
            print(f"[PHONEPE CALLBACK] Order {order.id} payment FAILED")
        else:
            print(f"[PHONEPE CALLBACK] Order {order.id} payment state: {payment_state}")
        
        db.commit()
        
        return {"success": True, "message": f"Payment status updated to {payment_state}"}
        
    except Exception as e:
        print(f"[PHONEPE CALLBACK] Error processing callback: {str(e)}")
        return {"success": False, "message": str(e)}


@router.get(
    "/status/{order_id}",
    response_model=schemas.PaymentStatusResponse,
    summary="Check payment status",
    description="""
    Check the current payment status of an order.
    For PhonePe orders, this queries PhonePe's API for the latest status.
    
    **Authorization:** Users can check their own orders, admins can check any order.
    """
)
def check_payment_status(
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    from ..services import phonepe_service
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permission
    if current_user.role != models.UserRole.admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    # For PhonePe orders, check live status
    if order.payment_method == "phonepe" and order.merchant_order_id:
        try:
            status_result = phonepe_service.check_payment_status(order.merchant_order_id)
            payment_state = status_result.get("state", "UNKNOWN")
            
            # Update local order if status changed
            if payment_state == "COMPLETED" and order.payment_status != models.PaymentStatus.Completed:
                order.payment_status = models.PaymentStatus.Completed
                order.status = models.OrderStatus.Processing
                db.commit()
            elif payment_state == "FAILED" and order.payment_status != models.PaymentStatus.Failed:
                order.payment_status = models.PaymentStatus.Failed
                db.commit()
        except Exception as e:
            print(f"[PAYMENT STATUS] Error checking PhonePe status: {e}")
            status_result = {}
    else:
        status_result = {}
    
    return {
        "orderId": order.id,
        "merchantOrderId": order.merchant_order_id,
        "paymentMethod": order.payment_method or "cod",
        "paymentStatus": order.payment_status.value if order.payment_status else "Pending",
        "orderStatus": order.status.value if order.status else "Pending",
        "totalAmount": order.total_amount,
        # Extended fields
        "phonepeState": status_result.get("state"),
        "amountPaise": status_result.get("amount"),
        "errorCode": status_result.get("errorCode"),
        "detailedErrorCode": status_result.get("detailedErrorCode"),
        "paymentDetails": status_result.get("paymentDetails", [])
    }


@router.get(
    "/status/public/{merchant_order_id}",
    summary="Public payment status check (no auth required)",
    description="""
    Check payment status using the merchantOrderId (a random UUID-based string).
    This endpoint is **public** — no authentication required.
    
    Used by the payment status page after PhonePe redirect, where the user
    may be a guest (not logged in). The merchantOrderId is non-guessable
    (e.g., TRUMIX-25-39a765de), so it's safe to expose without auth.
    """
)
def check_payment_status_public(
    merchant_order_id: str,
    db: Session = Depends(database.get_db),
):
    from ..services import phonepe_service
    
    order = db.query(models.Order).filter(
        models.Order.merchant_order_id == merchant_order_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check live status with PhonePe
    if order.payment_method == "phonepe" and order.merchant_order_id:
        try:
            status_result = phonepe_service.check_payment_status(order.merchant_order_id)
            payment_state = status_result.get("state", "UNKNOWN")
            
            if payment_state == "COMPLETED" and order.payment_status != models.PaymentStatus.Completed:
                order.payment_status = models.PaymentStatus.Completed
                order.status = models.OrderStatus.Processing
                db.commit()
            elif payment_state == "FAILED" and order.payment_status != models.PaymentStatus.Failed:
                order.payment_status = models.PaymentStatus.Failed
                db.commit()
        except Exception as e:
            print(f"[PAYMENT STATUS PUBLIC] Error checking PhonePe status: {e}")
    
    return {
        "orderId": order.id,
        "paymentMethod": order.payment_method or "cod",
        "paymentStatus": order.payment_status.value if order.payment_status else "Pending",
        "orderStatus": order.status.value if order.status else "Pending",
        "totalAmount": order.total_amount
    }


@router.post(
    "/refund/{order_id}",
    summary="Initiate refund (Admin only)",
    description="""
    Initiate a refund for a completed PhonePe payment.
    
    **Admin only.** The order must have been paid via PhonePe with status = Completed.
    """
)
def initiate_refund(
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    from ..services import phonepe_service
    
    # Only admin can initiate refunds
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin can initiate refunds")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.payment_method != "phonepe":
        raise HTTPException(status_code=400, detail="Refunds only available for PhonePe payments")
    
    if order.payment_status != models.PaymentStatus.Completed:
        raise HTTPException(status_code=400, detail="Can only refund completed payments")
    
    # Generate unique refund ID
    refund_id = f"REFUND-{order.id}-{str(uuid4())[:8]}"
    amount_paise = int(order.total_amount * 100)
    
    try:
        result = phonepe_service.initiate_refund(
            merchant_order_id=order.merchant_order_id,
            refund_id=refund_id,
            amount_paise=amount_paise
        )
        
        order.payment_status = models.PaymentStatus.Refunded
        order.status = models.OrderStatus.Cancelled
        db.commit()
        
        return {
            "success": True,
            "message": "Refund initiated successfully",
            "data": {
                "orderId": order.id,
                "refundId": refund_id,
                "amount": order.total_amount,
                "state": result.get("state", "INITIATED")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refund failed: {str(e)}")
