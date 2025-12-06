from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get("/sales")
def get_sales_report(period: str = "monthly", db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Mock data for charts
    return {
        "success": True,
        "data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "revenue": [12000, 15000, 8000, 18000, 20000, 22000],
            "orders": [12, 15, 8, 18, 20, 22]
        }
    }

@router.get("/top-products")
def get_top_products(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Mock data
    return {
        "success": True,
        "data": [
            {"name": "Masala Chai", "revenue": 50000, "quantity": 100},
            {"name": "Green Tea", "revenue": 30000, "quantity": 60},
            {"name": "Earl Grey", "revenue": 20000, "quantity": 40}
        ]
    }
