from app.database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        # Update Users table
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_expiry TIMESTAMP"))
            print("Updated users table.")
        except Exception as e:
            print(f"Error updating users table: {e}")

        # Update Products table
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS slug VARCHAR"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS sale_price FLOAT"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS images TEXT"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0.0"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS attributes TEXT"))
            
            # Add unique constraint to slug if needed, but might fail if duplicates exist.
            # conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_products_slug ON products (slug)"))
            print("Updated products table.")
        except Exception as e:
            print(f"Error updating products table: {e}")
            
        # Update Categories table
        try:
            conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS slug VARCHAR"))
            conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS image_url VARCHAR"))
            print("Updated categories table.")
        except Exception as e:
            print(f"Error updating categories table: {e}")

        # Update Orders table
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
            print("Updated orders table.")
        except Exception as e:
            print(f"Error updating orders table: {e}")

        # Update Wholesale Inquiries table
        try:
            conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS business_type VARCHAR"))
            conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS gst_id VARCHAR"))
            conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS address TEXT"))
            conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS website VARCHAR"))
            
            # Try to create enum type if not exists
            try:
                conn.execute(text("CREATE TYPE wholesaleinquirystatus AS ENUM ('Pending', 'Approved', 'Rejected')"))
            except Exception:
                pass 
            
            conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS status wholesaleinquirystatus DEFAULT 'Pending'"))
            print("Updated wholesale_inquiries table.")
        except Exception as e:
            print(f"Error updating wholesale_inquiries table: {e}")

        # Commit changes
        conn.commit()

if __name__ == "__main__":
    print("Starting schema update...")
    update_schema()
    print("Schema update complete.")
