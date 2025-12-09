from app.database import engine
from sqlalchemy import text

def fix_users_schema():
    print("Attempting to fix users schema...")
    with engine.connect() as conn:
        try:
            # Add columns individually and commit after each to isolate failures
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp VARCHAR"))
                conn.commit()
                print("Added otp column")
            except Exception as e:
                print(f"Error adding otp column: {e}")
                conn.rollback()

            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_expiry TIMESTAMP"))
                conn.commit()
                print("Added otp_expiry column")
            except Exception as e:
                print(f"Error adding otp_expiry column: {e}")
                conn.rollback()
                
        except Exception as e:
            print(f"General Error: {e}")

if __name__ == "__main__":
    fix_users_schema()
