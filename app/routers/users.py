from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

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
