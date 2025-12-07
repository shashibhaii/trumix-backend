from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def seed_products():
    db = SessionLocal()
    try:
        # 1. Define Categories
        categories_data = [
            {"name": "Instant Premixes", "slug": "instant-premixes", "description": "Quick and delicious instant tea and coffee premixes."},
            {"name": "Desi Cookies", "slug": "desi-cookies", "description": "Traditional authentic cookies."}
        ]
        
        category_map = {}
        
        print("Seeding Categories...")
        for cat_data in categories_data:
            category = db.query(models.Category).filter(models.Category.name == cat_data["name"]).first()
            if not category:
                category = models.Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"]
                )
                db.add(category)
                db.commit()
                db.refresh(category)
                print(f"Created category: {category.name}")
            else:
                print(f"Category already exists: {category.name}")
            category_map[category.name] = category

        # 2. Define Products
        # Instant Premixes (Sachets) - Assuming MRP is the price
        premixes = [
            {"name": "Cardamom Tea", "price": 10.00, "retailer_price": 8.00},
            {"name": "Ginger Tea", "price": 10.00, "retailer_price": 8.00},
            {"name": "Lemongrass Tea", "price": 10.00, "retailer_price": 8.00},
            {"name": "Masala Tea", "price": 10.00, "retailer_price": 8.00},
            {"name": "Espresso", "price": 15.00, "retailer_price": 12.00},
            {"name": "Cappucino", "price": 15.00, "retailer_price": 12.00},
            {"name": "Mocha", "price": 15.00, "retailer_price": 12.00},
            {"name": "Hazelnut", "price": 15.00, "retailer_price": 12.00},
        ]

        print("\nSeeding Instant Premixes...")
        premix_cat = category_map["Instant Premixes"]
        for p_data in premixes:
            product = db.query(models.Product).filter(models.Product.name == p_data["name"]).first()
            if not product:
                # Generate a simple slug
                slug = p_data["name"].lower().replace(" ", "-")
                product = models.Product(
                    name=p_data["name"],
                    slug=slug,
                    description=f"Instant {p_data['name']} Premix Sachet",
                    price=p_data["price"],
                    category_id=premix_cat.id,
                    stock=100, # Default stock
                    # Storing retailer price in attributes for now as it's not a main field
                    attributes=f'{{"retailer_price": {p_data["retailer_price"]}, "unit": "Sachet"}}'
                )
                db.add(product)
                print(f"Created product: {product.name}")
            else:
                print(f"Product already exists: {product.name}")

        # Desi Cookies (Variants)
        cookies = [
            {
                "name": "Classic Thekua", 
                "variants": [
                    {"name": "1 KG", "price": 399.00, "retailer_price": 320.00},
                    {"name": "500 Gms", "price": 229.00, "retailer_price": 184.00},
                    {"name": "250 Gms", "price": 119.00, "retailer_price": 96.00},
                ]
            },
            {
                "name": "Jaggery Thekua", 
                "variants": [
                    {"name": "1 KG", "price": 499.00, "retailer_price": 399.00},
                    {"name": "500 Gms", "price": 289.00, "retailer_price": 232.00},
                    {"name": "250 Gms", "price": 149.00, "retailer_price": 120.00},
                ]
            },
            {
                "name": "Desi Ghee Thekua", 
                "variants": [
                    {"name": "1 KG", "price": 599.00, "retailer_price": 480.00},
                    {"name": "500 Gms", "price": 349.00, "retailer_price": 280.00},
                    {"name": "250 Gms", "price": 199.00, "retailer_price": 160.00},
                ]
            },
            {
                "name": "Pista Thekua", 
                "variants": [
                    {"name": "1 KG", "price": 799.00, "retailer_price": 640.00},
                    {"name": "500 Gms", "price": 449.00, "retailer_price": 360.00},
                    {"name": "250 Gms", "price": 249.00, "retailer_price": 199.00},
                ]
            },
        ]

        print("\nSeeding Desi Cookies...")
        cookie_cat = category_map["Desi Cookies"]
        for c_data in cookies:
            product = db.query(models.Product).filter(models.Product.name == c_data["name"]).first()
            
            # Use the lowest variant price as the base product price
            base_price = min(v["price"] for v in c_data["variants"])
            
            if not product:
                slug = c_data["name"].lower().replace(" ", "-")
                product = models.Product(
                    name=c_data["name"],
                    slug=slug,
                    description=f"Authentic {c_data['name']}",
                    price=base_price,
                    category_id=cookie_cat.id,
                    stock=100
                )
                db.add(product)
                db.commit() # Commit to get ID
                db.refresh(product)
                print(f"Created product: {product.name}")
            else:
                print(f"Product already exists: {product.name}")

            # Handle Variants
            for v_data in c_data["variants"]:
                variant_name = f"{v_data['name']}"
                # Check if variant exists
                variant = db.query(models.Variant).filter(
                    models.Variant.product_id == product.id,
                    models.Variant.name == variant_name
                ).first()
                
                if not variant:
                    variant = models.Variant(
                        product_id=product.id,
                        name=variant_name,
                        price=v_data["price"],
                        stock=50 # Default stock per variant
                    )
                    db.add(variant)
                    print(f"  - Created variant: {variant_name} - MRP: {v_data['price']}")
                else:
                    print(f"  - Variant already exists: {variant_name}")

        db.commit()
        print("\nSeeding complete!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_products()
