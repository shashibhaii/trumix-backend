from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/", response_model=List[schemas.ProductResponse]) # Simplified pagination for now
def get_products(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None, 
    category: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Product)
    if search:
        query = query.filter(models.Product.name.contains(search))
    if category:
        query = query.join(models.Category).filter(models.Category.name == category)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None), # Handle file upload
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Handle image upload here (save to disk)
    image_url = None
    if image:
        import shutil
        import os
        import uuid
        
        # Generate unique filename
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"static/images/{unique_filename}"
        
        # Ensure directory exists
        os.makedirs("static/images", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # Construct URL (assuming localhost for now, in prod use env var for base URL)
        # For now, we store the relative path or absolute URL. 
        # Let's store the relative path accessible via the static mount.
        image_url = f"/static/images/{unique_filename}"
    
    new_product = models.Product(
        name=name,
        category_id=category_id,
        price=price,
        stock=stock,
        description=description,
        image_url=image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{id}", response_model=schemas.ProductResponse)
def update_product(
    id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if name: product.name = name
    if category_id: product.category_id = category_id
    if price: product.price = price
    if stock: product.stock = stock
    if description: product.description = description
    if image:
        import shutil
        import os
        import uuid
        
        # Generate unique filename
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"static/images/{unique_filename}"
        
        os.makedirs("static/images", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        product.image_url = f"/static/images/{unique_filename}"
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return None
