from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/offers",
    tags=["Offers"]
)

@router.get("/", response_model=List[schemas.OfferResponse])
def get_offers(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    offers = db.query(models.Offer).all()
    return offers

@router.post("/", response_model=schemas.OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(offer: schemas.OfferCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_offer = db.query(models.Offer).filter(models.Offer.code == offer.code).first()
    if db_offer:
        raise HTTPException(status_code=400, detail="Offer code already exists")
    
    new_offer = models.Offer(**offer.dict())
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer

@router.post("/validate")
def validate_offer(validation: schemas.OfferValidate, db: Session = Depends(database.get_db)):
    offer = db.query(models.Offer).filter(models.Offer.code == validation.code).first()
    
    if not offer:
        return {"valid": False, "message": "Invalid coupon code"}
    
    if offer.status != models.OfferStatus.Active:
        return {"valid": False, "message": "Coupon is not active"}
        
    if offer.valid_from and offer.valid_from > datetime.utcnow():
        return {"valid": False, "message": "Coupon is not yet valid"}
        
    if offer.valid_until and offer.valid_until < datetime.utcnow():
        return {"valid": False, "message": "Coupon has expired"}
        
    if offer.usage_limit is not None and offer.usage_limit <= 0: # Simplified usage check
        return {"valid": False, "message": "Coupon usage limit reached"}
        
    if validation.cart_value < offer.min_order_value:
        return {"valid": False, "message": f"Minimum order value of {offer.min_order_value} required"}

    discount_amount = 0
    if offer.type == models.OfferType.Percentage:
        discount_amount = (offer.value / 100) * validation.cart_value
    elif offer.type == models.OfferType.Fixed:
        discount_amount = offer.value
    elif offer.type == models.OfferType.Shipping:
        discount_amount = 0 # Logic for free shipping would be handled by frontend/cart logic usually, or return specific flag
        
    return {
        "valid": True,
        "discountAmount": discount_amount,
        "message": "Coupon applied successfully"
    }
