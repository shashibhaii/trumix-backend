from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    # In a real app, calculate these from DB
    # For now, return mock data as per requirements or simple counts
    
    total_sales = 125000 # Mock
    total_orders = db.query(models.Order).count()
    total_products = db.query(models.Product).count()
    total_customers = db.query(models.User).count() # Assuming users are customers for now, or just mock it

    return {
        "totalSales": { "value": total_sales, "change": 12.5, "trend": "up" },
        "totalOrders": { "value": total_orders, "change": 8.2, "trend": "up" },
        "totalProducts": { "value": total_products, "change": 0, "trend": "neutral" },
        "totalCustomers": { "value": total_customers, "change": 15.3, "trend": "up" }
    }
