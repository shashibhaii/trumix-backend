import base64
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from .. import models


async def save_image_to_db(file: UploadFile, db: Session) -> str:
    """
    Reads an uploaded image file, encodes it as base64, 
    saves it to the ProductImage table, and returns the serving URL.
    """
    try:
        # Read file content
        await file.seek(0)
        content = await file.read()

        # Encode to base64
        b64_data = base64.b64encode(content).decode("utf-8")

        # Save to DB
        image = models.ProductImage(
            filename=file.filename or "unknown",
            content_type=file.content_type or "image/jpeg",
            data=b64_data,
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        # Return URL that the images router will serve
        return f"/api/v1/images/{image.id}"

    except Exception as e:
        db.rollback()
        print(f"Error saving image to DB: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
