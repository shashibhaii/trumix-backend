from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.get("/", response_model=List[schemas.OrderResponse])
def get_orders(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[models.OrderStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    if search:
        # Simple search by customer name or email
        query = query.filter(
            (models.Order.customer_name.contains(search)) | 
            (models.Order.customer_email.contains(search))
        )
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/{id}", response_model=schemas.OrderResponse)
def get_order(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/{id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    id: int, 
    status_update: schemas.OrderUpdateStatus, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order
