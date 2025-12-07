from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database
from .auth import get_current_user
import json

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"]
)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Calculate total and validate items
    total_amount = 0
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
        total_amount += price * quantity
        
        order_items.append({
            "product_id": product.id,
            "variant_id": variant_id,
            "quantity": quantity,
            "price": price
        })
        
    # Apply coupon if any (mock logic)
    if order_in.couponCode == "WELCOME10":
        total_amount = total_amount * 0.9
        
    # Create Order
    new_order = models.Order(
        user_id=current_user.id,
        customer_name=current_user.name,
        customer_email=current_user.email,
        customer_phone=current_user.phone,
        customer_address=json.dumps(order_in.shippingAddress),
        total_amount=total_amount,
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
    
    return {
        "success": True,
        "message": "Order created",
        "data": {
            "orderId": new_order.id,
            "totalAmount": total_amount,
            "status": new_order.status,
            "paymentIntentClientSecret": "pi_mock_secret" # Mock payment intent
        }
    }

@router.get("/", response_model=schemas.OrderListAPIResponse)
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
    
    return {
        "success": True,
        "data": orders
    }

@router.get("/{id}", response_model=schemas.OrderDetailAPIResponse)
def get_order(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check permission
    if current_user.role != models.UserRole.admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
        
    return {
        "success": True,
        "data": order
    }

@router.patch("/{id}/status", response_model=schemas.OrderResponse)
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
