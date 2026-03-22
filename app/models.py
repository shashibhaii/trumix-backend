from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    editor = "editor"
    user = "user"

class OrderStatus(str, enum.Enum):
    Pending = "Pending"
    Processing = "Processing"
    Shipped = "Shipped"
    Delivered = "Delivered"
    Cancelled = "Cancelled"

class PaymentStatus(str, enum.Enum):
    Pending = "Pending"
    Initiated = "Initiated"
    Completed = "Completed"
    Failed = "Failed"
    Refunded = "Refunded"

class OfferType(str, enum.Enum):
    Percentage = "Percentage"
    Fixed = "Fixed"
    Shipping = "Shipping"

class OfferStatus(str, enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Expired = "Expired"

class WholesaleInquiryStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.admin)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    otp = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    addresses = relationship("Address", back_populates="user")
    cart = relationship("Cart", uselist=False, back_populates="user")

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    street = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    sale_price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    image_url = Column(Text(length=2**24), nullable=True) # Base64 data URI
    images = Column(Text, nullable=True) # JSON string of list of images
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    attributes = Column(Text, nullable=True) # JSON string
    category_id = Column(Integer, ForeignKey("categories.id"))
    display_order = Column(Integer, default=0, nullable=True)
    
    category = relationship("Category", back_populates="products")
    variants = relationship("Variant", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

class Variant(Base):
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=True)
    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("Variant", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Link to user if logged in
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    customer_address = Column(Text, nullable=True) # JSON or formatted string
    
    # Financial breakdown
    subtotal = Column(Float, nullable=False)  # Sum of item prices
    discount_amount = Column(Float, default=0.0)  # Discount from coupons
    tax_amount = Column(Float, default=0.0)  # Tax charged
    shipping_amount = Column(Float, default=0.0)  # Shipping charges
    cod_charges = Column(Float, default=0.0)  # COD handling fee
    total_amount = Column(Float, nullable=False)  # Final total
    
    # Payment tracking
    payment_method = Column(String(50), default="cod")  # "cod" or "phonepe"
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.Pending)
    phonepe_order_id = Column(String(255), nullable=True)  # PhonePe's internal order ID
    merchant_order_id = Column(String(255), nullable=True, unique=True)  # Our unique ID sent to PhonePe
    
    status = Column(Enum(OrderStatus), default=OrderStatus.Pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False) # Price at time of purchase
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("Variant")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(Enum(OfferType), nullable=False)
    value = Column(Float, nullable=False)
    min_order_value = Column(Float, default=0)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    status = Column(Enum(OfferStatus), default=OfferStatus.Active)

class WholesaleInquiry(Base):
    __tablename__ = "wholesale_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    business_type = Column(String(100), nullable=True)
    gst_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    estimated_volume = Column(String(100), nullable=True)
    status = Column(Enum(WholesaleInquiryStatus), default=WholesaleInquiryStatus.Pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    data = Column(Text(length=2**24), nullable=False)  # MEDIUMTEXT for base64
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    cta_url = Column(String(500), nullable=True)
    cta_text = Column(String(100), nullable=True)
    recipient_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_by_id = Column(Integer, ForeignKey("users.id"))

    sent_by = relationship("User")
    recipients = relationship("CampaignRecipient", back_populates="campaign")

class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    email = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), default="Sent") # Sent, Delivered, Opened, etc.

    campaign = relationship("Campaign", back_populates="recipients")
    user = relationship("User")
