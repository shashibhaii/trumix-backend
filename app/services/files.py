import os
from fastapi import UploadFile, HTTPException


def _get_cloudinary():
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )
    return cloudinary


async def save_image(file: UploadFile) -> str:
    """Upload image to Cloudinary and return the CDN URL."""
    try:
        cld = _get_cloudinary()

        await file.seek(0)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty image file")

        result = cld.uploader.upload(
            content,
            folder="trumix/products",
            resource_type="image",
            transformation=[{"quality": "auto", "fetch_format": "auto"}],
        )
        return result["secure_url"]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
