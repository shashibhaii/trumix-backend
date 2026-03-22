from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from .. import models, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)

@router.get("/sales")
def get_sales_report(period: str = "monthly", db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Determine date range based on period
    now = datetime.now()
    if period == "weekly":
        start_date = now - timedelta(days=7)
        date_format = "%Y-%m-%d"
    elif period == "daily":
        start_date = now - timedelta(days=1)
        date_format = "%H:00"
    elif period == "yearly":
        start_date = now - timedelta(days=365)
        date_format = "%Y-%m"
    else: # monthly default
        start_date = now - timedelta(days=30)
        date_format = "%Y-%m-%d"

    # Query daily revenue
    sales_query = db.query(
        func.date_format(models.Order.created_at, date_format).label("label"),
        func.sum(models.Order.total_amount).label("revenue"),
        func.count(models.Order.id).label("orders")
    ).filter(
        models.Order.created_at >= start_date,
        models.Order.payment_status == models.PaymentStatus.Completed
    ).group_by("label").order_by("label").all()

    labels = [s.label for s in sales_query]
    revenue = [float(s.revenue) for s in sales_query]
    orders = [s.orders for s in sales_query]

    # Overall KPIs
    total_revenue = db.query(func.sum(models.Order.total_amount)).filter(models.Order.payment_status == models.PaymentStatus.Completed).scalar() or 0
    total_orders = db.query(func.count(models.Order.id)).count()
    total_customers = db.query(func.count(models.User.id)).filter(models.User.role == models.UserRole.user).scalar() or 0
    
    # Calculate Average Order Value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return {
        "success": True,
        "data": {
            "labels": labels,
            "revenue": revenue,
            "orders": orders,
            "kpis": {
                "totalRevenue": round(total_revenue, 2),
                "totalOrders": total_orders,
                "totalCustomers": total_customers,
                "avgOrderValue": round(float(avg_order_value), 2)
            }
        }
    }

@router.get("/top-products")
def get_top_products(limit: int = 5, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    top_products = db.query(
        models.Product.name,
        func.sum(models.OrderItem.quantity).label("quantity"),
        func.sum(models.OrderItem.price * models.OrderItem.quantity).label("revenue")
    ).join(models.OrderItem, models.Product.id == models.OrderItem.product_id)\
     .group_by(models.Product.name)\
     .order_by(desc("revenue"))\
     .limit(limit).all()

    return {
        "success": True,
        "data": [
            {"name": p.name, "revenue": float(p.revenue), "quantity": p.quantity}
            for p in top_products
        ]
    }

@router.get("/category-distribution")
def get_category_distribution(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    results = db.query(
        models.Category.name,
        func.sum(models.OrderItem.price * models.OrderItem.quantity).label("revenue")
    ).join(models.Product, models.Category.id == models.Product.category_id)\
     .join(models.OrderItem, models.Product.id == models.OrderItem.product_id)\
     .group_by(models.Category.name).all()

    return {
        "success": True,
        "data": [
            {"name": r.name, "value": float(r.revenue)} for r in results
        ]
    }
