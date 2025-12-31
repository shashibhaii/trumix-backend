"""
Script to check what products exist in the database
"""
from app.database import SessionLocal
from app import models

def check_products():
    db = SessionLocal()
    try:
        products = db.query(models.Product).all()
        
        if not products:
            print("No products found in the database!")
            print("\nYou can seed products by running: python seed_products.py")
        else:
            print(f"Found {len(products)} products:\n")
            print("ID  | Name                          | Price    | Stock | Category ID")
            print("-" * 80)
            for product in products:
                print(f"{product.id:<3} | {product.name:<29} | ${product.price:<7.2f} | {product.stock:<5} | {product.category_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_products()
