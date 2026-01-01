# Shipping Rules Configuration

All business rules are now in an easy-to-modify format!

## Where to Modify Rules

**File**: `app/config_rules.py`

This file contains ALL configuration in a human-readable format.

## Current Shipping Tiers

| Cart Value Range | Shipping Charge |
|-----------------|----------------|
| ₹0 - ₹100 | ₹90 |
| ₹100 - ₹200 | ₹60 |
| ₹200 - ₹300 | ₹30 |
| Above ₹300 | **FREE** |

## How to Modify Shipping Rules

Open `app/config_rules.py` and edit the `SHIPPING_TIERS` section:

```python
SHIPPING_TIERS = [
    {
        "cart_min": 0,
        "cart_max": 100,
        "shipping_charge": 90,
        "description": "Cart up to ₹100"
    },
    # Add more tiers or modify existing ones
]
```

### Examples:

**Add a new tier:**
```python
{
    "cart_min": 500,
    "cart_max": 1000,
    "shipping_charge": 0,
    "description": "Premium range - Free shipping"
}
```

**Change existing charges:**
Just modify the `shipping_charge` value!

## Other Rules You Can Modify

1. **Tax Rate**: Change `TAX_RATE = 18` (percentage)
2. **COD Charges**: Change `COD_FIXED_CHARGE = 40` (₹)
3. **Coupons**: Add/edit in the `COUPONS` dictionary
4. **COD Limit**: Change `COD_MAX_ORDER_VALUE = 50000` (₹)

## After Making Changes

**Restart the server** for changes to take effect:
```bash
# The dev server will auto-reload if you're using --reload flag
# Otherwise, restart manually
```

## Testing Shipping Calculation

Cart examples with current rules:
- ₹80 cart → ₹90 shipping
- ₹150 cart → ₹60 shipping
- ₹250 cart → ₹30 shipping
- ₹350 cart → FREE shipping (₹0)
