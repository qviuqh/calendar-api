#!/usr/bin/env python3
"""
Test script cho Calendar API
Chạy script này sau khi server đã running
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Helper để print response đẹp"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}")

def main():
    print("🚀 Testing Calendar API...")
    
    # Test 1: Register
    print("\n1️⃣ Testing Registration...")
    register_data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "testpassword123"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response("Register", r)
    
    if r.status_code != 201:
        print("❌ Registration failed!")
        return
    
    # Test 2: Login
    print("\n2️⃣ Testing Login...")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Login", r)
    
    if r.status_code != 200:
        print("❌ Login failed!")
        return
    
    tokens = r.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 3: Get Me
    print("\n3️⃣ Testing Get Me...")
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("Get Me", r)
    
    # Test 4: Create Calendar
    print("\n4️⃣ Testing Create Calendar...")
    calendar_data = {
        "name": "My Test Calendar",
        "timezone": "Asia/Bangkok"
    }
    r = requests.post(f"{BASE_URL}/calendars", json=calendar_data, headers=headers)
    print_response("Create Calendar", r)
    
    if r.status_code != 201:
        print("❌ Create calendar failed!")
        return
    
    calendar_id = r.json()["id"]
    
    # Test 5: List Calendars
    print("\n5️⃣ Testing List Calendars...")
    r = requests.get(f"{BASE_URL}/calendars", headers=headers)
    print_response("List Calendars", r)
    
    # Test 6: Create Event
    print("\n6️⃣ Testing Create Event...")
    now = datetime.utcnow()
    event_data = {
        "calendar_id": calendar_id,
        "title": "Test Meeting",
        "description": "This is a test event",
        "start_at": (now + timedelta(days=1)).isoformat() + "Z",
        "end_at": (now + timedelta(days=1, hours=1)).isoformat() + "Z",
        "location": "Zoom",
        "is_all_day": False
    }
    r = requests.post(f"{BASE_URL}/events", json=event_data, headers=headers)
    print_response("Create Event", r)
    
    if r.status_code != 201:
        print("❌ Create event failed!")
        return
    
    event_id = r.json()["id"]
    
    # Test 7: Create Conflicting Event (should fail)
    print("\n7️⃣ Testing Conflict Detection...")
    conflict_event = event_data.copy()
    conflict_event["title"] = "Conflicting Event"
    # Same time as previous event
    r = requests.post(f"{BASE_URL}/events", json=conflict_event, headers=headers)
    print_response("Create Conflicting Event (should fail)", r)
    
    # Test 8: List Events
    print("\n8️⃣ Testing List Events...")
    r = requests.get(f"{BASE_URL}/events?calendar_id={calendar_id}", headers=headers)
    print_response("List Events", r)
    
    # Test 9: Get Specific Event
    print("\n9️⃣ Testing Get Event...")
    r = requests.get(f"{BASE_URL}/events/{event_id}", headers=headers)
    print_response("Get Event", r)
    
    # Test 10: Update Event
    print("\n🔟 Testing Update Event...")
    update_data = {
        "title": "Updated Meeting Title",
        "description": "Updated description"
    }
    r = requests.patch(f"{BASE_URL}/events/{event_id}", json=update_data, headers=headers)
    print_response("Update Event", r)
    
    # Test 11: Refresh Token
    print("\n1️⃣1️⃣ Testing Refresh Token...")
    r = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token})
    print_response("Refresh Token", r)
    
    # Test 12: Delete Event (soft delete)
    print("\n1️⃣2️⃣ Testing Delete Event...")
    r = requests.delete(f"{BASE_URL}/events/{event_id}", headers=headers)
    print_response("Delete Event", r)
    
    # Test 13: Logout
    print("\n1️⃣3️⃣ Testing Logout...")
    r = requests.post(f"{BASE_URL}/auth/logout", json={"refresh_token": refresh_token})
    print_response("Logout", r)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure server is running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
