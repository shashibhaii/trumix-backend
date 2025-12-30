from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database
from .auth import get_current_user
from ..services.azure_blob import upload_image_to_blob

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)

@router.get("/", response_model=schemas.ProductListAPIResponse)
def get_products(
    page: int = 1, 
    limit: int = 10, 
    search: Optional[str] = None, 
    category: Optional[str] = None,
    category_id: Optional[int] = None,
    sort: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Product)
    
    if search:
        query = query.filter(models.Product.name.contains(search))
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    elif category:
        # Check if category is ID or slug
        if category.isdigit():
            query = query.filter(models.Product.category_id == int(category))
        else:
            query = query.join(models.Category).filter(models.Category.slug == category)
            
    # Sorting
    if sort == 'price_asc':
        query = query.order_by(models.Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(models.Product.price.desc())
    elif sort == 'newest':
        query = query.order_by(models.Product.id.desc())
    elif sort == 'order':
        query = query.order_by(models.Product.display_order.asc(), models.Product.id.desc())
    # elif sort == 'popular': # Need order stats for this
    #     pass
        
    total = query.count()
    skip = (page - 1) * limit
    products = query.offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "products": products,
            "pagination": {
                "total": total,
                "page": page,
                "pages": pages
            }
        }
    }

@router.get("/{id_or_slug}", response_model=schemas.ProductDetailAPIResponse)
def get_product_details(id_or_slug: str, db: Session = Depends(database.get_db)):
    query = db.query(models.Product)
    if id_or_slug.isdigit():
        product = query.filter(models.Product.id == int(id_or_slug)).first()
    else:
        product = query.filter(models.Product.slug == id_or_slug).first()
        
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return {
        "success": True,
        "data": product
    }

@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(None),
    display_order: int = Form(0),
    image: UploadFile = File(None), # Handle file upload
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    # Handle image upload
    image_url = None
    if image:
        # Use Azure Blob Storage
        image_url = await upload_image_to_blob(image)
    
    new_product = models.Product(
        name=name,
        category_id=category_id,
        price=price,
        stock=stock,
        description=description,
        image_url=image_url,
        display_order=display_order
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{id}", response_model=schemas.ProductResponse)
async def update_product(
    id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    display_order: Optional[int] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if name: product.name = name
    if category_id: product.category_id = category_id
    if price: product.price = price
    if stock: product.stock = stock
    if description: product.description = description
    if display_order is not None: product.display_order = display_order
    if image:
        # Use Azure Blob Storage
        product.image_url = await upload_image_to_blob(image)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return None
