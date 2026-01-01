from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database
from .auth import get_current_user
import json

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
    responses={
        404: {"description": "Order not found"},
        403: {"description": "Not authorized"},
    }
)

@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="""
    Create a new order with automatic server-side calculation of all financial values.
    
    **How it works:**
    1. Send items, shipping address, payment method, and optional coupon
    2. Server validates products and calculates:
       - Subtotal from product prices
       - Tax (18% GST)
       - Shipping (tiered: ₹90/₹60/₹30/FREE based on cart value)
       - COD charges (₹40 if COD selected)
       - Discount (applies valid coupon)
    3. Returns complete breakdown and order ID
    
    **Important:** All financial calculations are done server-side to prevent manipulation.
    """,
    response_description="Order created successfully with financial breakdown",
    responses={
        201: {
            "description": "Order created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Order created",
                        "data": {
                            "orderId": 5,
                            "subtotal": 298.00,
                            "discountAmount": 29.80,
                            "taxAmount": 48.28,
                            "shippingAmount": 60.00,
                            "codCharges": 40.00,
                            "totalAmount": 417.08,
                            "status": "Pending",
                            "paymentIntentClientSecret": "pi_mock_secret"
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid request or coupon error"},
        404: {"description": "Product not found"}
    }
)
def create_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Import business rules
    from ..business_rules import calculate_order_totals
    
    # Calculate subtotal from items and validate products exist
    subtotal = 0
    order_items = []
    
    for item in order_in.items:
        product = db.query(models.Product).filter(models.Product.id == item['productId']).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['productId']} not found")
            
        price = product.sale_price if product.sale_price else product.price
        variant_id = item.get('variantId')
        
        if variant_id:
            variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
            if not variant:
                raise HTTPException(status_code=404, detail=f"Variant {variant_id} not found")
            price = variant.price
            
        quantity = item['quantity']
        subtotal += price * quantity
        
        order_items.append({
            "product_id": product.id,
            "variant_id": variant_id,
            "quantity": quantity,
            "price": price
        })
    
    # Calculate all financial values using business rules (SERVER-SIDE)
    try:
        state = order_in.shippingAddress.get('state')
        financial_breakdown = calculate_order_totals(
            subtotal=subtotal,
            payment_method=order_in.paymentMethod,
            coupon_code=order_in.couponCode,
            state=state
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Use provided customer details or fall back to user profile
    customer_name = order_in.customerName or current_user.name
    customer_email = order_in.customerEmail or current_user.email
    customer_phone = order_in.customerPhone or current_user.phone
        
    # Create Order with calculated values
    new_order = models.Order(
        user_id=current_user.id,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_address=json.dumps(order_in.shippingAddress),
        subtotal=financial_breakdown['subtotal'],
        discount_amount=financial_breakdown['discount_amount'],
        tax_amount=financial_breakdown['tax_amount'],
        shipping_amount=financial_breakdown['shipping_amount'],
        cod_charges=financial_breakdown['cod_charges'],
        total_amount=financial_breakdown['total_amount'],
        status=models.OrderStatus.Pending
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create Order Items
    for item in order_items:
        new_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item['product_id'],
            variant_id=item['variant_id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.add(new_item)
        
    # Clear user's cart
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if cart:
        db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
        
    db.commit()
    
    # Send order confirmation email
    try:
        from ..services.email_service import send_order_confirmation
        from datetime import datetime
        
        email_data = {
            'customer_email': customer_email,
            'customer_name': customer_name,
            'order_id': new_order.id,
            'order_date': datetime.now().strftime("%B %d, %Y"),
            'items': [
                {
                    'name': item['product'].name if 'product' in item else db.query(models.Product).get(item['product_id']).name,
                    'variant_name': db.query(models.Variant).get(item['variant_id']).name if item['variant_id'] else None,
                    'quantity': item['quantity'],
                    'price': item['price']
                }
                for item in order_items
            ],
            'subtotal': financial_breakdown['subtotal'],
            'discount_amount': financial_breakdown['discount_amount'],
            'tax_amount': financial_breakdown['tax_amount'],
            'shipping_amount': financial_breakdown['shipping_amount'],
            'cod_charges': financial_breakdown['cod_charges'],
            'total_amount': financial_breakdown['total_amount'],
            'shipping_address': order_in.shippingAddress
        }
        send_order_confirmation(email_data)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send order confirmation: {str(e)}")
        # Don't fail the order if email fails
    
    return {
        "success": True,
        "message": "Order created",
        "data": {
            "orderId": new_order.id,
            "subtotal": financial_breakdown['subtotal'],
            "discountAmount": financial_breakdown['discount_amount'],
            "taxAmount": financial_breakdown['tax_amount'],
            "shippingAmount": financial_breakdown['shipping_amount'],
            "codCharges": financial_breakdown['cod_charges'],
            "totalAmount": financial_breakdown['total_amount'],
            "status": new_order.status,
            "paymentIntentClientSecret": "pi_mock_secret" # Mock payment intent
        }
    }

@router.get(
    "/",
    response_model=schemas.OrderListAPIResponse,
    summary="Get all orders",
    description="""
    Retrieve all orders with complete financial breakdown.
    
    **Admin users:** See all orders from all customers
    **Regular users:** See only their own orders
    
    **Response includes:**
    - Subtotal, discount, tax, shipping, COD charges
    - Complete item list with product names
    - Order status and timestamps
    
    **Filters available:**
    - status: Filter by order status (Pending, Processing, Shipped, Delivered, Cancelled)
    - skip/limit: Pagination parameters
    """
)
def get_orders(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[models.OrderStatus] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Order)
    
    # If not admin, only show own orders
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
        
    if status:
        query = query.filter(models.Order.status == status)
    
    orders = query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Format orders with proper item data
    formatted_orders = []
    for order in orders:
        order_data = {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "customer_address": order.customer_address,
            "subtotal": order.subtotal,
            "discount_amount": order.discount_amount,
            "tax_amount": order.tax_amount,
            "shipping_amount": order.shipping_amount,
            "cod_charges": order.cod_charges,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": []
        }
        
        # Format order items with product and variant names
        for item in order.items:
            item_data = {
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "price": item.price,
                "product_name": item.product.name if item.product else "Unknown Product",
                "variant_name": item.variant.name if item.variant else None
            }
            order_data["items"].append(item_data)
        
        formatted_orders.append(order_data)
    
    return {
        "success": True,
        "data": formatted_orders
    }

@router.get(
    "/{id}",
    response_model=schemas.OrderDetailAPIResponse,
    summary="Get order by ID",
    description="""
    Retrieve a specific order with complete details and financial breakdown.
    
    **Authorization:**
    - Admin users can view any order
    - Regular users can only view their own orders
    
    **Response includes full financial breakdown:**
    - Subtotal, discount amount, tax amount
    - Shipping charges, COD charges
    - Total amount and order status
    - Complete item list with product and variant names
    """
)
def get_order(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check permission
    if current_user.role != models.UserRole.admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    # Format order with proper item data
    order_data = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "customer_address": order.customer_address,
        "subtotal": order.subtotal,
        "discount_amount": order.discount_amount,
        "tax_amount": order.tax_amount,
        "shipping_amount": order.shipping_amount,
        "cod_charges": order.cod_charges,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": []
    }
    
    # Format order items with product and variant names
    for item in order.items:
        item_data = {
            "product_id": item.product_id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,
            "price": item.price,
            "product_name": item.product.name if item.product else "Unknown Product",
            "variant_name": item.variant.name if item.variant else None
        }
        order_data["items"].append(item_data)
        
    return {
        "success": True,
        "data": order_data
    }

@router.patch(
    "/{id}/status",
    response_model=schemas.OrderResponse,
    summary="Update order status (Admin only)",
    description="""
    Update the status of an order. **Admin users only.**
    
    **Available statuses:**
    - Pending
    - Processing
    - Shipped
    - Delivered
    - Cancelled
    
    **Use case:** Track order lifecycle from creation to delivery.
    """
)
def update_order_status(
    id: int, 
    status_update: schemas.OrderUpdateStatus, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only admin can update status
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order
