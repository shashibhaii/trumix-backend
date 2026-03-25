import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "test_admin@example.com"
ADMIN_PASSWORD = "admin123"

def login_admin():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_order_tracking():
    token = login_admin()
    if not token:
        print("Login failed")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get an order
    response = requests.get(f"{BASE_URL}/api/v1/orders/", headers=headers)
    orders = response.json()["data"]["orders"]
    if not orders:
        print("No orders found to test")
        return
    
    order = orders[0]
    order_id = order["id"]
    print(f"Testing with Order ID: {order_id}")

    # 2. Update status to Shipped with tracking info
    tracking_data = {
        "status": "Shipped",
        "tracking_id": "AWB123456",
        "tracking_url": "https://track.blue/123",
        "shipping_provider": "BlueDart"
    }
    
    print(f"Updating order {order_id} to Shipped...")
    response = requests.patch(
        f"{BASE_URL}/api/v1/orders/{order_id}/status",
        json=tracking_data,
        headers=headers
    )
    
    if response.status_code == 200:
        updated_order = response.json()
        print("✓ Successfully updated status and tracking info")
        print(f"  Tracking ID: {updated_order.get('tracking_id')}")
        print(f"  Provider: {updated_order.get('shipping_provider')}")
    else:
        print(f"✗ Failed to update: {response.status_code} - {response.text}")
        return

    # 3. Get the order again to verify persistence
    print(f"Verifying persistence for order {order_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}", headers=headers)
    verified_order = response.json()["data"]
    
    if (verified_order.get("tracking_id") == tracking_data["tracking_id"] and 
        verified_order.get("shipping_provider") == tracking_data["shipping_provider"]):
        print("✓ Persistence verified!")
    else:
        print("✗ Persistence check failed")
        print(f"  Expected: {tracking_data['tracking_id']}, Got: {verified_order.get('tracking_id')}")

if __name__ == "__main__":
    test_order_tracking()
