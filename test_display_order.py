"""
Test script to verify display_order functionality
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin and get token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_get_products_with_order_sort(token):
    """Test getting products sorted by display_order"""
    print("\n--- Testing GET /api/v1/products?sort=order ---")
    response = requests.get(
        f"{BASE_URL}/api/v1/products?sort=order",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Successfully retrieved products sorted by display_order")
        print(f"Total products: {data['data']['pagination']['total']}")
        
        # Show first few products with their display_order
        products = data['data']['products']
        for product in products[:5]:
            print(f"  - {product['name']}: display_order={product.get('display_order', 'N/A')}")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")

def test_update_product_display_order(token, product_id, new_order):
    """Test updating a product's display_order"""
    print(f"\n--- Testing PUT /api/v1/products/{product_id} (updating display_order to {new_order}) ---")
    
    # Create form data
    data = {"display_order": str(new_order)}
    
    response = requests.put(
        f"{BASE_URL}/api/v1/products/{product_id}",
        data=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        product = response.json()
        print(f"✓ Successfully updated product display_order")
        print(f"  Product: {product['name']}")
        print(f"  New display_order: {product.get('display_order', 'N/A')}")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")

def main():
    print("Starting display_order functionality tests...")
    
    # Login
    print("\n1. Logging in as admin...")
    token = login_admin()
    if not token:
        print("Cannot proceed without authentication")
        return
    print("✓ Logged in successfully")
    
    # Test 1: Get products with order sort
    test_get_products_with_order_sort(token)
    
    # Test 2: Update a product's display_order (using product ID 1 as example)
    test_update_product_display_order(token, product_id=1, new_order=5)
    
    # Test 3: Verify the sort order again
    test_get_products_with_order_sort(token)
    
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    main()
