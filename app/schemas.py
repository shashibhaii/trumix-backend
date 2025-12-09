from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import UserRole, OrderStatus, OfferType, OfferStatus, WholesaleInquiryStatus
import json

# Address Schemas
class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    
    class Config:
        orm_mode = True

# Auth Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    name: str
    password: str
    phone: Optional[str] = None

class UserLogin(UserBase):
    password: str

class OTPRequest(BaseModel):
    phone: str

class OTPLogin(BaseModel):
    phone: str
    otp: str

class UserResponse(UserBase):
    id: int
    name: str
    role: UserRole
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    addresses: List[AddressResponse] = []
    
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    totalSales: dict
    totalOrders: dict
    totalProducts: dict
    totalCustomers: dict

# Variant Schemas
class VariantBase(BaseModel):
    name: str
    price: float
    stock: int

class VariantCreate(VariantBase):
    pass

class VariantResponse(VariantBase):
    id: int
    
    class Config:
        orm_mode = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    price: float
    sale_price: Optional[float] = None
    stock: int
    category_id: int
    image_url: Optional[str] = None
    images: Optional[List[str]] = []
    attributes: Optional[Dict[str, Any]] = {}

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    rating: float
    review_count: int
    variants: List[VariantResponse] = []
    
    @field_validator('images', mode='before')
    def parse_images(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    @field_validator('attributes', mode='before')
    def parse_attributes(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    class Config:
        orm_mode = True

class PaginationMeta(BaseModel):
    total: int
    page: int
    pages: int

class ProductListData(BaseModel):
    products: List[ProductResponse]
    pagination: PaginationMeta

class ProductListAPIResponse(BaseModel):
    success: bool
    data: ProductListData

class ProductDetailAPIResponse(BaseModel):
    success: bool
    data: ProductResponse

# Order Schemas
class OrderItemResponse(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    price: float
    product_name: str 
    variant_name: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    items: List[dict] # {product_id, variant_id, quantity}
    shippingAddress: dict # {street, city, ...}
    paymentMethod: str
    couponCode: Optional[str] = None

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

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

# Cart Schemas
class CartItemBase(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    product: ProductResponse
    variant: Optional[VariantResponse] = None
    
    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse] = []
    subtotal: float
    tax: float
    total: float
    
    class Config:
        orm_mode = True

class CartAPIResponse(BaseModel):
    success: bool
    data: CartResponse

class OrderListAPIResponse(BaseModel):
    success: bool
    data: List[OrderResponse]

class OrderDetailAPIResponse(BaseModel):
    success: bool
    data: OrderResponse

# Wholesale & Contact
class WholesaleInquiryCreate(BaseModel):
    companyName: str
    contactPerson: str
    email: EmailStr
    phone: str
    businessType: Optional[str] = None
    gstId: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    message: str
    estimatedVolume: Optional[str] = None

class WholesaleInquiryResponse(BaseModel):
    id: int
    company_name: str
    contact_person: str
    email: str
    phone: str
    business_type: Optional[str] = None
    gst_id: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    message: str
    estimated_volume: Optional[str] = None
    status: WholesaleInquiryStatus
    created_at: datetime

    class Config:
        orm_mode = True

class WholesaleInquiryUpdate(BaseModel):
    status: WholesaleInquiryStatus

class ContactSubmissionCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
