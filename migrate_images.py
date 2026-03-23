import os
import base64
import uuid
import re
from sqlalchemy.orm import Session
from app import models, database

UPLOAD_DIR = "static/uploads"
BASE_URL = os.getenv("BASE_URL", "https://api.trumix.co.in")

def save_b64_to_file(b64_string: str) -> str:
    """
    Parses a data URI, saves the binary data to a file, and returns the public URL.
    """
    try:
        if not b64_string or not b64_string.startswith("data:"):
            return b64_string
            
        # Extract metadata and data
        header, encoded = b64_string.split(",", 1)
        
        # Get extension from header (e.g., data:image/png;base64)
        match = re.search(r'data:image/(\w+);base64', header)
        extension = match.group(1) if match else "jpg"
        if extension == "jpeg": extension = "jpg"
        
        # Unique filename
        filename = f"migrated_{uuid.uuid4()}.{extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Decode and save
        data = base64.b64decode(encoded)
        with open(filepath, "wb") as f:
            f.write(data)
            
        return f"{BASE_URL}/static/uploads/{filename}"
    except Exception as e:
        print(f"Error migrating image: {e}")
        return b64_string

def migrate():
    # Ensure directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    db = next(database.get_db())
    try:
        # Migrate Products
        products = db.query(models.Product).all()
        print(f"Checking {len(products)} products...")
        p_count = 0
        for p in products:
            if p.image_url and p.image_url.startswith("data:"):
                print(f" Migrating product: {p.name}")
                p.image_url = save_b64_to_file(p.image_url)
                p_count += 1
        
        # Migrate Categories
        categories = db.query(models.Category).all()
        print(f"Checking {len(categories)} categories...")
        c_count = 0
        for c in categories:
            if c.image_url and c.image_url.startswith("data:"):
                print(f" Migrating category: {c.name}")
                c.image_url = save_b64_to_file(c.image_url)
                c_count += 1
        
        db.commit()
        print(f"Migration complete! Migrated {p_count} products and {c_count} categories.")
        
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
