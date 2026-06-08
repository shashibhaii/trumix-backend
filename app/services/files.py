import os
import httpx
from fastapi import UploadFile, HTTPException


async def save_image(file: UploadFile) -> str:
    """Upload image to Cloudinary via REST API and return the CDN URL."""
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise HTTPException(status_code=500, detail="Cloudinary credentials not configured")

    try:
        await file.seek(0)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty image file")

        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                url,
                data={
                    "upload_preset": None,
                    "folder": "trumix/products",
                    "api_key": api_key,
                },
                files={"file": (file.filename or "image.jpg", content, file.content_type or "image/jpeg")},
                auth=(api_key, api_secret),
            )

        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {resp.text}")

        return resp.json()["secure_url"]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
