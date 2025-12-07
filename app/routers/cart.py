from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/cart",
    tags=["Cart"]
)

def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.get("/", response_model=schemas.CartAPIResponse)
def get_cart(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)
    
    # Calculate totals
    subtotal = 0
    # We can rely on Pydantic to serialize the items if we just pass the cart object
    # BUT, we need to calculate subtotal/tax/total which are not in the DB model directly (or are they?)
    # The Cart model doesn't have subtotal/tax/total fields stored.
    # The CartResponse schema expects them.
    # So we need to construct a dict that matches CartResponse schema.
    
    items_data = []
    
    for item in cart.items:
        # Determine price (use sale price if available, otherwise regular price)
        price = item.product.sale_price if item.product.sale_price else item.product.price
        # If variant, use variant price
        if item.variant:
            price = item.variant.price
            
        item_total = price * item.quantity
        subtotal += item_total
        
        # We need to construct CartItemResponse compatible dict
        # CartItemResponse has: id, product, variant, quantity
        # 'product' field expects ProductResponse. 'item.product' is ORM object.
        # Pydantic's from_orm (orm_mode) handles nested ORM objects IF we pass the ORM object.
        # But here we are constructing a dict.
        # If we pass item.product (ORM) to 'product' field in dict, Pydantic should handle it.
        
        items_data.append({
            "id": item.id,
            "product_id": item.product_id,
            "variant_id": item.variant_id,
            "product": item.product, 
            "variant": item.variant,
            "quantity": item.quantity,
        })
        
    tax = subtotal * 0.05 
    total = subtotal + tax
    
    # Construct the response matching CartResponse
    cart_response = {
        "id": cart.id,
        "items": items_data,
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }
    
    return {
        "success": True,
        "data": cart_response
    }

@router.post("/items", response_model=schemas.CartAPIResponse)
def add_to_cart(
    item_in: schemas.CartItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # ... (logic remains same)
    cart = get_or_create_cart(db, current_user.id)
    
    # Check if item already exists in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == item_in.product_id,
        models.CartItem.variant_id == item_in.variant_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item_in.quantity
        if existing_item.quantity <= 0:
            db.delete(existing_item)
    else:
        if item_in.quantity > 0:
            new_item = models.CartItem(
                cart_id=cart.id,
                product_id=item_in.product_id,
                variant_id=item_in.variant_id,
                quantity=item_in.quantity
            )
            db.add(new_item)
            
    db.commit()
    
    # Return updated cart
    return get_cart(db, current_user)

@router.delete("/items/{item_id}", response_model=schemas.CartAPIResponse)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)
    
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    db.delete(item)
    db.commit()
    
    return get_cart(db, current_user)
