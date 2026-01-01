"""
Business rules for order calculations
This file centralizes all pricing logic to prevent manipulation from client-side

Configuration values are in config_rules.py for easy modification
"""

# Import configuration from the human-readable config file
from .config_rules import (
    TAX_RATE, TAX_ENABLED,
    SHIPPING_TIERS, SHIPPING_ENABLED,
    COD_ENABLED, COD_FIXED_CHARGE, COD_MAX_ORDER_VALUE, COD_USE_PERCENTAGE, COD_PERCENTAGE,
    COUPONS
)


def calculate_tax(subtotal: float) -> float:
    """Calculate tax amount based on subtotal"""
    if not TAX_ENABLED:
        return 0.0
    return round(subtotal * (TAX_RATE / 100), 2)


def calculate_shipping(subtotal: float, state: str = None) -> float:
    """Calculate shipping charges based on subtotal using tiered rates"""
    if not SHIPPING_ENABLED:
        return 0.0
    
    # Find the applicable shipping tier
    for tier in SHIPPING_TIERS:
        min_value = tier['cart_min']
        max_value = tier['cart_max']
        shipping_charge = tier['shipping_charge']
        
        if max_value is None:
            # Last tier (unlimited max)
            if subtotal >= min_value:
                return shipping_charge
        else:
            # Regular tier with both min and max
            if min_value <= subtotal < max_value:
                return shipping_charge
    
    # Default fallback (should not reach here if tiers are configured correctly)
    return 0.0


def calculate_cod_charges(subtotal: float, payment_method: str) -> float:
    """Calculate COD charges if payment method is COD"""
    if payment_method.lower() != "cod" or not COD_ENABLED:
        return 0.0
    
    # Check if order value exceeds COD limit
    if subtotal > COD_MAX_ORDER_VALUE:
        raise ValueError(f"COD not available for orders above ₹{COD_MAX_ORDER_VALUE}")
    
    if COD_USE_PERCENTAGE:
        return round(subtotal * (COD_PERCENTAGE / 100), 2)
    else:
        return COD_FIXED_CHARGE


def apply_coupon(subtotal: float, coupon_code: str = None) -> float:
    """Calculate discount amount based on coupon code"""
    if not coupon_code or coupon_code not in COUPONS:
        return 0.0
    
    coupon = COUPONS[coupon_code]
    
    # Check if coupon is active
    if not coupon.get("active", True):
        raise ValueError(f"Coupon {coupon_code} is not active")
    
    # Check minimum order value
    if subtotal < coupon.get("min_order_value", 0):
        raise ValueError(f"Minimum order value of ₹{coupon['min_order_value']} required for {coupon_code}")
    
    # Calculate discount
    if coupon["type"] == "percentage":
        discount = round(subtotal * (coupon["value"] / 100), 2)
    else:  # fixed
        discount = coupon["value"]
    
    return discount


def calculate_order_totals(subtotal: float, payment_method: str, coupon_code: str = None, state: str = None):
    """
    Calculate all order totals based on business rules
    Returns a dictionary with breakdown of all charges
    """
    # Apply discount
    discount_amount = apply_coupon(subtotal, coupon_code)
    amount_after_discount = subtotal - discount_amount
    
    # Calculate tax on discounted amount
    tax_amount = calculate_tax(amount_after_discount)
    
    # Calculate shipping on subtotal (before discount)
    shipping_amount = calculate_shipping(subtotal, state)
    
    # Calculate COD charges on subtotal
    cod_charges = calculate_cod_charges(subtotal, payment_method)
    
    # Calculate final total
    total_amount = amount_after_discount + tax_amount + shipping_amount + cod_charges
    
    return {
        "subtotal": round(subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "tax_amount": round(tax_amount, 2),
        "shipping_amount": round(shipping_amount, 2),
        "cod_charges": round(cod_charges, 2),
        "total_amount": round(total_amount, 2)
    }
