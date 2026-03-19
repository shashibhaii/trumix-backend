import base64
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter(
    prefix="/api/v1/images",
    tags=["Images"],
)


@router.get("/{image_id}")
def get_image(image_id: int, db: Session = Depends(database.get_db)):
    """Serve an image from the database by decoding its base64 data."""
    image = db.query(models.ProductImage).filter(models.ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Decode base64 back to binary
    image_bytes = base64.b64decode(image.data)

    return Response(
        content=image_bytes,
        media_type=image.content_type,
        headers={"Cache-Control": "public, max-age=31536000"},  # Cache for 1 year
    )
