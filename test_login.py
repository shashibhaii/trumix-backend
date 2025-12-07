import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_login():
    # 1. Register an admin user (if not exists)
    register_payload = {
        "email": "admin@test.com",
        "password": "adminpassword",
        "name": "Admin User",
        "secret_key": "admin_secret_key" # Assuming default env var
    }
    
    print("Attempting to register admin...")
    try:
        resp = requests.post(f"{BASE_URL}/register", json=register_payload)
        if resp.status_code == 200:
            print("Admin registered successfully.")
        elif resp.status_code == 400 and "already registered" in resp.text:
            print("Admin already exists.")
        else:
            print(f"Registration failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Registration error: {e}")

    # 2. Try JSON Login
    print("\nAttempting JSON login...")
    login_payload = {
        "email": "admin@test.com",
        "password": "adminpassword"
    }
    try:
        resp = requests.post(f"{BASE_URL}/login", json=login_payload)
        if resp.status_code == 200:
            print("JSON Login successful.")
            print(resp.json())
        else:
            print(f"JSON Login failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"JSON Login error: {e}")

    # 3. Try Form Login (OAuth2 style) -> Should hit /token now
    print("\nAttempting Form login (username=email) on /token...")
    form_payload = {
        "username": "admin@test.com",
        "password": "adminpassword"
    }
    try:
        resp = requests.post(f"{BASE_URL}/token", data=form_payload)
        if resp.status_code == 200:
            print("Form Login successful.")
        else:
            print(f"Form Login failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Form Login error: {e}")

if __name__ == "__main__":
    test_login()
