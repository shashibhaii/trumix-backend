from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database

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
