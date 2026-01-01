"""
Add financial breakdown columns to orders table
Run this script to add subtotal, discount_amount, tax_amount, shipping_amount, and cod_charges
"""
from app.database import SessionLocal, engine
from sqlalchemy import text

def add_order_financial_fields():
    db = SessionLocal()
    try:
        # Check if columns already exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='orders' AND column_name='subtotal'
        """))
        
        if result.fetchone() is None:
            print("Adding financial breakdown columns to orders table...")
            
            # Add the columns with default values
            db.execute(text("""
                ALTER TABLE orders 
                ADD COLUMN subtotal FLOAT DEFAULT 0.0
            """))
            
            db.execute(text("""
                ALTER TABLE orders 
                ADD COLUMN discount_amount FLOAT DEFAULT 0.0
            """))
            
            db.execute(text("""
                ALTER TABLE orders 
                ADD COLUMN tax_amount FLOAT DEFAULT 0.0
            """))
            
            db.execute(text("""
                ALTER TABLE orders 
                ADD COLUMN shipping_amount FLOAT DEFAULT 0.0
            """))
            
            db.execute(text("""
                ALTER TABLE orders 
                ADD COLUMN cod_charges FLOAT DEFAULT 0.0
            """))
            
            # For existing orders, copy total_amount to subtotal as a reasonable default
            db.execute(text("""
                UPDATE orders 
                SET subtotal = total_amount 
                WHERE subtotal = 0.0
            """))
            
            db.commit()
            print("✓ Successfully added financial breakdown columns")
            print("  - subtotal")
            print("  - discount_amount")
            print("  - tax_amount")
            print("  - shipping_amount")
            print("  - cod_charges")
        else:
            print("Financial breakdown columns already exist")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_order_financial_fields()
