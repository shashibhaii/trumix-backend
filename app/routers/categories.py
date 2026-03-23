from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from .auth import get_current_user

import time
from typing import List, Optional, Dict, Any

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"]
)

# In-memory cache for categories
_categories_cache = {
    "data": None,
    "expiry": 0
}
CACHE_TTL = 300  # 5 minutes

@router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories():
    current_time = time.time()
    if _categories_cache["data"] is not None and current_time < _categories_cache["expiry"]:
        return _categories_cache["data"]
    
    # Cache miss: get DB manually to avoid overhead for cached requests
    db = next(database.get_db())
    try:
        categories = db.query(models.Category).all()
        
        # Update cache
        _categories_cache["data"] = categories
        _categories_cache["expiry"] = current_time + CACHE_TTL
        
        return categories
    finally:
        db.close()

@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = models.Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    # Invalidate cache
    _categories_cache["data"] = None
    
    return new_category

@router.put("/{id}", response_model=schemas.CategoryResponse)
def update_category(id: int, category: schemas.CategoryCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_category = db.query(models.Category).filter(models.Category.id == id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_category.name = category.name
    db_category.description = category.description
    db.commit()
    db.refresh(db_category)
    
    # Invalidate cache
    _categories_cache["data"] = None
    
    return db_category

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_category = db.query(models.Category).filter(models.Category.id == id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    
    # Invalidate cache
    _categories_cache["data"] = None
    
    return None
