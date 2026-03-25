from app.database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        print("Checking orders table columns...")
        result = conn.execute(text("SHOW COLUMNS FROM orders"))
        columns = [row[0] for row in result.fetchall()]
        
        to_add = {
            "tracking_id": "VARCHAR(100)",
            "tracking_url": "VARCHAR(500)",
            "shipping_provider": "VARCHAR(100)"
        }
        
        for col, col_type in to_add.items():
            if col not in columns:
                print(f"Adding column {col}...")
                try:
                    conn.execute(text(f"ALTER TABLE orders ADD COLUMN {col} {col_type} NULL"))
                    print(f"Successfully added {col}.")
                except Exception as e:
                    print(f"Error adding {col}: {e}")
            else:
                print(f"Column {col} already exists.")

        # Commit changes
        conn.commit()

if __name__ == "__main__":
    print("Starting tracking fields migration for MySQL...")
    update_schema()
    print("Migration complete.")
