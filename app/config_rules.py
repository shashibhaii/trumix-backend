# ==========================================
# TRUMIX BUSINESS RULES CONFIGURATION
# ==========================================
# This file contains all pricing and calculation rules
# Modify values here to change business logic
# ==========================================

# ------------------------------------------
# 1. TAX CONFIGURATION
# ------------------------------------------
TAX_RATE = 18  # Tax percentage (18% GST for India)
TAX_ENABLED = False  # Set to False to disable tax

# ------------------------------------------
# 2. SHIPPING CHARGES (Tiered by Cart Value)
# ------------------------------------------
# How shipping works:
# - Cart value determines shipping charges
# - Higher cart value = Lower shipping charges
# - Format: [Cart Min, Cart Max, Shipping Charge]

SHIPPING_TIERS = [
    {
        "cart_min": 0,
        "cart_max": 100,
        "shipping_charge": 90,
        "description": "Cart up to ₹100"
    },
    {
        "cart_min": 100,
        "cart_max": 200,
        "shipping_charge": 60,
        "description": "Cart ₹100-200"
    },
    {
        "cart_min": 200,
        "cart_max": 300,
        "shipping_charge": 30,
        "description": "Cart ₹200-300"
    },
    {
        "cart_min": 300,
        "cart_max": None,  # None means unlimited
        "shipping_charge": 0,
        "description": "Cart above ₹300 - FREE SHIPPING"
    }
]

SHIPPING_ENABLED = True  # Set to False to disable shipping

# ------------------------------------------
# 3. COD (Cash on Delivery) CHARGES
# ------------------------------------------
COD_ENABLED = True
COD_FIXED_CHARGE = 40  # Fixed COD handling fee in ₹
COD_MAX_ORDER_VALUE = 50000  # Maximum cart value for COD (in ₹)

# Alternative: Use percentage-based COD charge
COD_USE_PERCENTAGE = False  # Set to True to use percentage instead of fixed
COD_PERCENTAGE = 2  # Percentage of order value (if enabled)

# ------------------------------------------
# 4. DISCOUNT COUPONS
# ------------------------------------------
# Format for each coupon:
# "COUPON_CODE": {
#     "type": "percentage" or "fixed",
#     "value": discount value,
#     "min_order_value": minimum cart value required,
#     "active": True/False
# }

COUPONS = {
    # "WELCOME10": {
    #     "type": "percentage",
    #     "value": 10,  # 10% off
    #     "min_order_value": 200,
    #     "active": True,
    #     "description": "Welcome offer - 10% off on orders above ₹200"
    # },
    "FLAT50": {
        "type": "fixed",
        "value": 50,  # ₹50 off
        "min_order_value": 300,
        "active": True,
        "description": "Flat ₹50 off on orders above ₹300"
    }
    # "NEWYEAR2026": {
    #     "type": "percentage",
    #     "value": 15,  # 15% off
    #     "min_order_value": 500,
    #     "active": True,
    #     "description": "New Year special - 15% off on orders above ₹500"
    # }
}

# ==========================================
# NOTES FOR MODIFICATION:
# ==========================================
# 1. Shipping Tiers: Add/remove tiers as needed. Keep them in ascending order.
# 2. Coupons: Add new coupons by copying an existing one and modifying values.
# 3. Set "active": False to temporarily disable a coupon without deleting it.
# 4. After modifying this file, restart the server for changes to take effect.
# ==========================================
