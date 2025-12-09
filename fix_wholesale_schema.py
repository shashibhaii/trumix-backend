from app.database import engine
from sqlalchemy import text

def fix_wholesale_schema():
    print("Attempting to fix wholesale_inquiries schema...")
    with engine.connect() as conn:
        try:
            # Add columns individually and commit after each to isolate failures
            try:
                conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS business_type VARCHAR"))
                conn.commit()
                print("Added business_type")
            except Exception as e:
                print(f"Error adding business_type: {e}")
                conn.rollback()

            try:
                conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS gst_id VARCHAR"))
                conn.commit()
                print("Added gst_id")
            except Exception as e:
                print(f"Error adding gst_id: {e}")
                conn.rollback()

            try:
                conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS address TEXT"))
                conn.commit()
                print("Added address")
            except Exception as e:
                print(f"Error adding address: {e}")
                conn.rollback()

            try:
                conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS website VARCHAR"))
                conn.commit()
                print("Added website")
            except Exception as e:
                print(f"Error adding website: {e}")
                conn.rollback()

            # Status Enum
            try:
                conn.execute(text("CREATE TYPE wholesaleinquirystatus AS ENUM ('Pending', 'Approved', 'Rejected')"))
                conn.commit()
                print("Created wholesaleinquirystatus enum")
            except Exception as e:
                print(f"Enum creation skipped (likely exists): {e}")
                conn.rollback()

            try:
                conn.execute(text("ALTER TABLE wholesale_inquiries ADD COLUMN IF NOT EXISTS status wholesaleinquirystatus DEFAULT 'Pending'"))
                conn.commit()
                print("Added status column")
            except Exception as e:
                print(f"Error adding status column: {e}")
                conn.rollback()
                
        except Exception as e:
            print(f"General Error: {e}")

if __name__ == "__main__":
    fix_wholesale_schema()
