#!/usr/bin/env python3
"""
Test script for Medicine Delivery API
Run this after starting the server to test the endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_user_registration():
    """Test user registration"""
    print("Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "phone": "+1234567890",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("User registered successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.json()}")
    print()

def test_user_login():
    """Test user login"""
    print("Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Login successful!")
        token_data = response.json()
        print(f"Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_profile(token):
    """Test getting user profile"""
    if not token:
        print("No token available, skipping profile test")
        return
    
    print("Testing get profile...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Profile retrieved successfully!")
        profile = response.json()
        print(f"User: {profile['first_name']} {profile['last_name']}")
        print(f"Email: {profile['email']}")
        print(f"Phone: {profile['phone']}")
    else:
        print(f"Error: {response.json()}")
    print()

def test_update_profile(token):
    """Test updating user profile"""
    if not token:
        print("No token available, skipping profile update test")
        return
    
    print("Testing profile update...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "blood_group": "O+",
        "allergies": ["Penicillin", "Sulfa drugs"],
        "address_line1": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345"
    }
    
    response = requests.put(f"{BASE_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Profile updated successfully!")
        profile = response.json()
        print(f"Blood Group: {profile['blood_group']}")
        print(f"Address: {profile['address_line1']}, {profile['city']}")
    else:
        print(f"Error: {response.json()}")
    print()

def test_send_verification_code(token):
    """Test sending verification code"""
    if not token:
        print("No token available, skipping verification test")
        return
    
    print("Testing send verification code...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/auth/send-verification-code?phone=+1234567890", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Verification code sent successfully!")
        print("Check the console output for the verification code")
    else:
        print(f"Error: {response.json()}")
    print()

def main():
    """Run all tests"""
    print("=== Medicine Delivery API Test Suite ===\n")
    
    try:
        test_health_check()
        test_user_registration()
        token = test_user_login()
        test_get_profile(token)
        test_update_profile(token)
        test_send_verification_code(token)
        
        print("=== Test Suite Completed ===")
        print("Check the server console for verification codes")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 