"""
Quick test to get all products via API
"""
import requests

BASE_URL = "http://localhost:8000"

# Get all products
response = requests.get(f"{BASE_URL}/api/v1/products/?page=1&limit=100")

if response.status_code == 200:
    data = response.json()
    products = data['data']['products']
    
    print(f"Found {len(products)} products:\n")
    print("Valid Product IDs to use in orders:")
    print("-" * 60)
    for product in products:
        print(f"ID {product['id']}: {product['name']} - ${product['price']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
