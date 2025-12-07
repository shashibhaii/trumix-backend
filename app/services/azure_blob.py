import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import UploadFile, HTTPException
import uuid

# Configuration
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "product-images")

def get_blob_service_client():
    if not AZURE_CONNECTION_STRING:
        print("Warning: AZURE_STORAGE_CONNECTION_STRING not set.")
        return None
    return BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

async def upload_image_to_blob(file: UploadFile) -> str:
    """
    Uploads an image file to Azure Blob Storage and returns the public URL.
    """
    blob_service_client = get_blob_service_client()
    if not blob_service_client:
        # Fallback or error if not configured
        # For now, let's raise an error to prompt configuration
        raise HTTPException(status_code=500, detail="Azure Storage not configured")

    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Get container client
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        
        # Create container if not exists
        # Create container if not exists
        if not container_client.exists():
            try:
                container_client.create_container(public_access="blob")
            except Exception as e:
                # If public access is not permitted, try creating without it
                # Note: Images won't be publicly accessible via URL unless account settings are changed
                print(f"Warning: Could not enable public access for container: {e}")
                container_client.create_container()

        # Upload blob
        blob_client = container_client.get_blob_client(unique_filename)
        
        # Reset file pointer to beginning
        await file.seek(0)
        content = await file.read()
        
        # Set content type
        content_settings = ContentSettings(content_type=file.content_type)
        
        blob_client.upload_blob(content, content_settings=content_settings, overwrite=True)
        
        # Return URL
        return blob_client.url
        
    except Exception as e:
        print(f"Error uploading to Azure Blob: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
