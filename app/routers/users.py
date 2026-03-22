from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

@router.get("/customers", response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Query users with their order aggregate data
    customers = db.query(
        models.User.id,
        models.User.name,
        models.User.email,
        models.User.phone,
        models.User.created_at.label("joined_at"),
        func.count(models.Order.id).label("order_count"),
        func.sum(models.Order.total_amount).label("total_spent")
    ).outerjoin(models.Order, models.User.id == models.Order.user_id)\
     .filter(models.User.role == models.UserRole.user)\
     .group_by(models.User.id).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "joined_at": c.joined_at,
            "order_count": c.order_count,
            "total_spent": float(c.total_spent or 0)
        } for c in customers
    ]

@router.get("/customers/{user_id}", response_model=schemas.CustomerDetailResponse)
def get_customer_detail(user_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get orders
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()
    
    formatted_orders = []
    for order in orders:
        order_dict = {
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
            "payment_method": order.payment_method,
            "payment_status": order.payment_status.value if order.payment_status else "Pending",
            "phonepe_order_id": order.phonepe_order_id,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": []
        }
        for item in order.items:
            order_dict["items"].append({
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "price": item.price,
                "product_name": item.product.name if item.product else "Unknown Product",
                "variant_name": item.variant.name if item.variant else None,
                "product_image": item.product.image_url if item.product else None
            })
        formatted_orders.append(order_dict)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "joined_at": user.created_at,
        "addresses": user.addresses,
        "orders": formatted_orders,
        "total_spent": sum(o.total_amount for o in orders),
        "order_count": len(orders)
    }

@router.get("/profile", response_model=schemas.UserResponse)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=schemas.UserResponse)
def update_user_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if user_update.name:
        current_user.name = user_update.name
    if user_update.phone:
        current_user.phone = user_update.phone
    if user_update.avatar_url:
        current_user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/addresses", response_model=schemas.AddressResponse)
def create_address(
    address: schemas.AddressCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_address = models.Address(**address.dict(), user_id=current_user.id)
    if address.is_default:
        # Set all other addresses to not default
        db.query(models.Address).filter(models.Address.user_id == current_user.id).update({"is_default": False})
    
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

@router.get("/addresses", response_model=List[schemas.AddressResponse])
def get_addresses(
    current_user: models.User = Depends(get_current_user)
):
    return current_user.addresses

@router.put("/addresses/{address_id}", response_model=schemas.AddressResponse)
def update_address(
    address_id: int,
    address_update: schemas.AddressUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_address = db.query(models.Address).filter(models.Address.id == address_id, models.Address.user_id == current_user.id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    if address_update.is_default:
        # Set all other addresses to not default
        db.query(models.Address).filter(models.Address.user_id == current_user.id).update({"is_default": False})
    
    update_data = address_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)
    
    db.commit()
    db.refresh(db_address)
    return db_address

@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_address = db.query(models.Address).filter(models.Address.id == address_id, models.Address.user_id == current_user.id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(db_address)
    db.commit()
    return {"message": "Address deleted"}
