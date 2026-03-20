import base64
from fastapi import UploadFile, HTTPException


async def save_image_to_db(file: UploadFile, db=None) -> str:
    """
    Reads an uploaded image file, encodes it as base64,
    and returns a data URI string (data:content_type;base64,<data>).
    """
    try:
        await file.seek(0)
        content = await file.read()

        b64_data = base64.b64encode(content).decode("utf-8")
        content_type = file.content_type or "image/jpeg"

        # Return data URI — frontend can render this directly in <img src="...">
        return f"data:{content_type};base64,{b64_data}"

    except Exception as e:
        print(f"Error encoding image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")
