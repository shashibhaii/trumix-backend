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
        recipients = db.query(models.User).all()
    elif request.recipient_type == "selected" and request.selected_emails:
        recipients = db.query(models.User).filter(
            models.User.email.in_(request.selected_emails)
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

    # Create campaign record
    campaign = models.Campaign(
        subject=request.subject,
        content=request.content,
        cta_url=request.cta_url,
        cta_text=request.cta_text,
        recipient_count=len(recipients),
        sent_by_id=current_user.id
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Queue emails and save recipients
    count = 0
    for user in recipients:
        # Save recipient record
        recipient = models.CampaignRecipient(
            campaign_id=campaign.id,
            email=user.email,
            user_id=user.id,
            status="Sent"
        )
        db.add(recipient)
        
        # Dispatch email
        background_tasks.add_task(
            email_service.dispatch_marketing_email,
            to_email=user.email,
            subject=request.subject,
            content=request.content,
            user_name=user.name,
            cta_url=request.cta_url,
            cta_text=request.cta_text
        )
        count += 1
    
    db.commit()

    return {
        "message": f"Marketing campaign '{request.subject}' successfully queued for {count} recipients.",
        "campaign_id": campaign.id,
        "recipient_count": count
    }

@router.get("/history", response_model=List[schemas.CampaignResponse])
async def get_campaign_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get history of all marketing campaigns."""
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return db.query(models.Campaign).order_by(models.Campaign.created_at.desc()).all()

@router.get("/history/{campaign_id}", response_model=schemas.CampaignDetailResponse)
async def get_campaign_detail(
    campaign_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get detailed history of a specific marketing campaign."""
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    return campaign

@router.get("/stats")
async def get_marketing_stats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get basic stats for marketing (total active users etc.)"""
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    total_users = db.query(models.User).count()
    # In a more advanced version, we'd track email campaign history
    return {
        "total_active_users": total_users,
    }
