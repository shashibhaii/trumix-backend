from app.database import engine
from sqlalchemy import text

def update_enum():
    # We need to run this outside of a transaction block usually for ALTER TYPE, 
    # but SQLAlchemy engine.connect() starts a transaction.
    # We can try using execution_options(isolation_level="AUTOCOMMIT")
    
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        try:
            # Check if 'user' already exists in the enum to avoid error
            # Postgres doesn't support "IF NOT EXISTS" for enum values directly in all versions easily without a query.
            # But we can just try to add it and catch the error if it exists.
            
            conn.execute(text("ALTER TYPE userrole ADD VALUE 'user'"))
            print("Successfully added 'user' to userrole enum.")
        except Exception as e:
            print(f"Error updating enum (might already exist): {e}")

if __name__ == "__main__":
    print("Starting enum update...")
    update_enum()
    print("Enum update complete.")
