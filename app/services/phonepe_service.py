"""
PhonePe Payment Gateway Service
Wraps the official PhonePe Python SDK for Standard Checkout integration.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# PhonePe Configuration
PHONEPE_CLIENT_ID = os.getenv("PHONEPE_CLIENT_ID", "")
PHONEPE_CLIENT_SECRET = os.getenv("PHONEPE_CLIENT_SECRET", "")
PHONEPE_CLIENT_VERSION = int(os.getenv("PHONEPE_CLIENT_VERSION", "1"))
PHONEPE_ENV = os.getenv("PHONEPE_ENV", "SANDBOX")
PHONEPE_REDIRECT_URL = os.getenv("PHONEPE_REDIRECT_URL", "https://trumix.co.in/payment/status")
PHONEPE_CALLBACK_URL = os.getenv("PHONEPE_CALLBACK_URL", "")


def _get_env():
    """Get PhonePe environment enum."""
    from phonepe.sdk.pg.env import Env
    if PHONEPE_ENV.upper() == "PRODUCTION":
        return Env.PRODUCTION
    return Env.SANDBOX


def _get_client():
    """
    Get or create the StandardCheckoutClient singleton.
    The SDK manages the singleton internally via get_instance().
    """
    from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient

    if not PHONEPE_CLIENT_ID or not PHONEPE_CLIENT_SECRET:
        raise ValueError(
            "PhonePe credentials not configured. "
            "Set PHONEPE_CLIENT_ID and PHONEPE_CLIENT_SECRET in .env"
        )

    return StandardCheckoutClient.get_instance(
        client_id=PHONEPE_CLIENT_ID,
        client_secret=PHONEPE_CLIENT_SECRET,
        client_version=PHONEPE_CLIENT_VERSION,
        env=_get_env()
    )


def initiate_payment(merchant_order_id: str, amount_paise: int, redirect_url: str = None):
    """
    Initiate a PhonePe Standard Checkout payment.
    
    Args:
        merchant_order_id: Unique order ID for this transaction
        amount_paise: Amount in paise (₹1 = 100 paise)
        redirect_url: URL to redirect user after payment (optional, uses default)
    
    Returns:
        dict with checkout_url, phonepe_order_id, and state
    """
    from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest

    client = _get_client()
    
    if redirect_url is None:
        redirect_url = PHONEPE_REDIRECT_URL

    pay_request = StandardCheckoutPayRequest.build_request(
        merchant_order_id=merchant_order_id,
        amount=amount_paise,
        redirect_url=redirect_url
    )

    logger.info(f"Initiating PhonePe payment: order={merchant_order_id}, amount={amount_paise} paise")
    
    pay_response = client.pay(pay_request)
    
    result = {
        "checkout_url": pay_response.redirect_url,
        "phonepe_order_id": getattr(pay_response, "order_id", None),
        "state": getattr(pay_response, "state", "PENDING"),
    }
    
    logger.info(f"PhonePe payment initiated: {result}")
    return result


def check_payment_status(merchant_order_id: str):
    """
    Check the status of a payment order with full details.
    
    Args:
        merchant_order_id: The merchant order ID used during payment initiation
    
    Returns:
        dict with full order details from PhonePe
    """
    client = _get_client()
    
    logger.info(f"Checking PhonePe payment status (detailed): order={merchant_order_id}")
    
    # details=True to get paymentDetails, errorCode, etc.
    status_response = client.get_order_status(merchant_order_id=merchant_order_id, details=True)
    logger.info(f"RAW PhonePe status response for {merchant_order_id}: {status_response.__dict__ if hasattr(status_response, '__dict__') else status_response}")
    
    # Map SDK object to dict
    result = {
        "order_id": getattr(status_response, "order_id", None),
        "state": getattr(status_response, "state", "UNKNOWN"),
        "amount": getattr(status_response, "amount", None),
        "errorCode": getattr(status_response, "error_code", None),
        "detailedErrorCode": getattr(status_response, "detailed_error_code", None),
        "paymentDetails": [],
        "refundDetails": []
    }
    
    # Add payment attempts if available
    payment_details = getattr(status_response, "payment_details", getattr(status_response, "paymentDetails", []))
    if payment_details:
        for detail in payment_details:
            result["paymentDetails"].append({
                "transactionId": getattr(detail, "transaction_id", getattr(detail, "transactionId", None)),
                "paymentMode": getattr(detail, "payment_mode", getattr(detail, "paymentMode", None)),
                "amount": getattr(detail, "amount", None),
                "state": getattr(detail, "state", None),
                "errorCode": getattr(detail, "error_code", getattr(detail, "errorCode", None)),
                "detailedErrorCode": getattr(detail, "detailed_error_code", getattr(detail, "detailedErrorCode", None)),
                "instrument type": getattr(detail, "instrument_type", getattr(detail, "instrumentType", None))
            })
            
    # Add refund details if available (Check both camelCase and snake_case)
    refund_details = getattr(status_response, "refund_details", getattr(status_response, "refundDetails", []))
    if refund_details:
        logger.info(f"Found refund details: {len(refund_details)} items")
        for refund in refund_details:
            r_data = {
                "refundId": getattr(refund, "refund_id", getattr(refund, "refundId", None)),
                "merchantRefundId": getattr(refund, "merchant_refund_id", getattr(refund, "merchantRefundId", None)),
                "amount": getattr(refund, "amount", None),
                "state": getattr(refund, "state", None),
                "errorCode": getattr(refund, "error_code", getattr(refund, "errorCode", None)),
                "detailedErrorCode": getattr(refund, "detailed_error_code", getattr(refund, "detailedErrorCode", None))
            }
            result["refundDetails"].append(r_data)
    else:
        logger.info("No refund details found in status_response")
    
    # Also check payment_details for refund state
    payment_details = getattr(status_response, "payment_details", getattr(status_response, "paymentDetails", []))
    if payment_details:
        for detail in payment_details:
            d_state = getattr(detail, "state", None)
            if d_state == "REFUNDED" or d_state == "REFUND_SUCCESS":
                 logger.info(f"Transaction {getattr(detail, 'transaction_id', 'unknown')} has refund state: {d_state}")

    logger.debug(f"PhonePe payment status (final mapped) result: {result}")
    return result


def initiate_refund(merchant_order_id: str, refund_id: str, amount_paise: int):
    """
    Initiate a refund for a completed payment.
    
    Args:
        merchant_order_id: Original merchant order ID
        refund_id: Unique refund ID for tracking
        amount_paise: Refund amount in paise
    
    Returns:
        dict with refund details
    """
    from phonepe.sdk.pg.common.models.request.refund_request import RefundRequest
    
    client = _get_client()
    
    logger.info(
        f"Initiating PhonePe refund: order={merchant_order_id}, "
        f"refund_id={refund_id}, amount={amount_paise} paise"
    )
    
    refund_request = RefundRequest(
        merchant_refund_id=refund_id,
        amount=amount_paise,
        original_merchant_order_id=merchant_order_id
    )
    
    refund_response = client.refund(refund_request)
    
    result = {
        "refund_id": getattr(refund_response, "refund_id", refund_id),
        "state": getattr(refund_response, "state", "UNKNOWN"),
    }
    
    logger.info(f"PhonePe refund initiated: {result}")
    return result
