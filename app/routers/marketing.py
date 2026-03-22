from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import database, models, schemas
from .auth import get_current_user
from ..services import email_service

router = APIRouter(
    prefix="/api/v1/marketing",
    tags=["marketing"]
)

logger = logging.getLogger(__name__)

@router.post("/send-email", status_code=status.HTTP_202_ACCEPTED)
async def send_marketing_email(
    request: schemas.MarketingEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Send a marketing email to users.
    Only accessible by administrators.
    """
    if current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can send marketing emails"
        )

    recipients = []
    
    if request.recipient_type == "all":
        recipients = db.query(models.User).filter(models.User.is_active == True).all()
    elif request.recipient_type == "selected" and request.selected_emails:
        recipients = db.query(models.User).filter(
            models.User.email.in_(request.selected_emails),
            models.User.is_active == True
        ).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recipient selection"
        )

    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching active users found"
        )

    # Queue emails
    count = 0
    for user in recipients:
        background_tasks.add_task(
            email_service.dispatch_marketing_email,
            to_email=user.email,
            subject=request.subject,
            content=request.content,
            cta_url=request.cta_url,
            cta_text=request.cta_text
        )
        count += 1

    return {
        "message": f"Marketing email successfully queued for {count} recipients.",
        "recipient_count": count
    }

@router.get("/stats")
async def get_marketing_stats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get basic stats for marketing (total active users etc.)"""
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    total_users = db.query(models.User).filter(models.User.is_active == True).count()
    # In a more advanced version, we'd track email campaign history
    return {
        "total_active_users": total_users,
    }
