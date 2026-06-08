import os
import json
import uuid
import urllib.request
import urllib.error
from base64 import b64encode
from fastapi import UploadFile, HTTPException


async def save_image(file: UploadFile) -> str:
    """Upload image to Cloudinary via urllib (stdlib) and return the CDN URL."""
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
        boundary = uuid.uuid4().hex

        body = b""
        for name, value in [("folder", "trumix/products"), ("api_key", api_key)]:
            body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()

        filename = file.filename or "image.jpg"
        content_type = file.content_type or "image/jpeg"
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode()
        body += content
        body += f"\r\n--{boundary}--\r\n".encode()

        credentials = b64encode(f"{api_key}:{api_secret}".encode()).decode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Authorization": f"Basic {credentials}",
            },
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())

        return result["secure_url"]

    except HTTPException:
        raise
    except urllib.error.HTTPError as e:
        detail = e.read().decode() if e.fp else str(e)
        print(f"Cloudinary HTTP error: {detail}")
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {detail}")
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
