from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    tags=["Wholesale & Contact"]
)

@router.post("/api/v1/wholesale/inquiry", response_model=dict)
def submit_wholesale_inquiry(
    inquiry: schemas.WholesaleInquiryCreate,
    db: Session = Depends(database.get_db)
):
    new_inquiry = models.WholesaleInquiry(
        company_name=inquiry.companyName,
        contact_person=inquiry.contactPerson,
        email=inquiry.email,
        phone=inquiry.phone,
        business_type=inquiry.businessType,
        gst_id=inquiry.gstId,
        address=inquiry.address,
        website=inquiry.website,
        message=inquiry.message,
        estimated_volume=inquiry.estimatedVolume
    )
    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    
    return {
        "success": True,
        "message": "Inquiry submitted successfully. We will contact you soon."
    }

@router.get("/api/v1/wholesale/inquiries", response_model=List[schemas.WholesaleInquiryResponse])
def get_wholesale_inquiries(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    inquiries = db.query(models.WholesaleInquiry).order_by(models.WholesaleInquiry.created_at.desc()).all()
    return inquiries

@router.put("/api/v1/wholesale/inquiries/{id}/status", response_model=schemas.WholesaleInquiryResponse)
def update_wholesale_inquiry_status(
    id: int,
    status_update: schemas.WholesaleInquiryUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    inquiry = db.query(models.WholesaleInquiry).filter(models.WholesaleInquiry.id == id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
        
    inquiry.status = status_update.status
    db.commit()
    db.refresh(inquiry)
    return inquiry

@router.post("/api/v1/contact", response_model=dict)
def submit_contact_form(
    contact: schemas.ContactSubmissionCreate,
    db: Session = Depends(database.get_db)
):
    new_submission = models.ContactSubmission(
        name=contact.name,
        email=contact.email,
        subject=contact.subject,
        message=contact.message
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return {
        "success": True,
        "message": "Message sent successfully."
    }
