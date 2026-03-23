import os
import uuid
from fastapi import UploadFile, HTTPException
import shutil

UPLOAD_DIR = "static/uploads"
BASE_URL = os.getenv("BASE_URL", "https://api.trumix.co.in")

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_image_locally(file: UploadFile) -> str:
    """
    Saves an uploaded image file to the local static/uploads directory 
    and returns the public URL.
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        if not file_extension:
            file_extension = ".jpg"
            
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return URL
        # We use a relative path /static/uploads/... because the frontend can prepend the base URL
        # Or we can return the full URL if BASE_URL is configured
        return f"{BASE_URL}/static/uploads/{unique_filename}"
        
    except Exception as e:
        print(f"Error saving image locally: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save image locally: {str(e)}")
