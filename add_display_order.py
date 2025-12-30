"""
Add display_order column to products table
Run this script to add the display_order column to existing products.
"""
from app.database import SessionLocal, engine
from sqlalchemy import text

def add_display_order_column():
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='products' AND column_name='display_order'
        """))
        
        if result.fetchone() is None:
            print("Adding display_order column to products table...")
            # Add the column with default value
            db.execute(text("""
                ALTER TABLE products 
                ADD COLUMN display_order INTEGER DEFAULT 0
            """))
            db.commit()
            print("✓ Successfully added display_order column")
        else:
            print("display_order column already exists")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_display_order_column()
