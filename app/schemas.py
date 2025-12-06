from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import UserRole, OrderStatus, OfferType, OfferStatus

# Auth Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    name: str
    password: str
    secret_key: Optional[str] = None # For admin registration

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    name: str
    role: UserRole
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    totalSales: dict
    totalOrders: dict
    totalProducts: dict
    totalCustomers: dict

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str] = None
    
    class Config:
        orm_mode = True

# Order Schemas
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float
    product_name: str 

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        orm_mode = True

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True

# Offer Schemas
class OfferBase(BaseModel):
    code: str
    type: OfferType
    value: float
    min_order_value: float = 0
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    usage_limit: Optional[int] = None
    status: OfferStatus = OfferStatus.Active

class OfferCreate(OfferBase):
    pass

class OfferResponse(OfferBase):
    id: int
    
    class Config:
        orm_mode = True

class OfferValidate(BaseModel):
    code: str
    cart_value: float
