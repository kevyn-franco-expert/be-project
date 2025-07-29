import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_user_crud():
    """Test user CRUD operations"""
    print("Testing User CRUD operations...")
    
    # Create user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Create User: {response.status_code} - {response.json()}")
    
    # Get all users
    response = requests.get(f"{BASE_URL}/users")
    users = response.json()
    print(f"Get All Users: {response.status_code} - Found {len(users)} users")
    
    if users:
        user_id = users[0]['id']
        
        # Get specific user
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"Get User {user_id}: {response.status_code}")
        
        # Update user
        updated_data = {
            "name": "Updated Test User",
            "email": "updated@example.com",
            "phone": "0987654321"
        }
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=updated_data)
        print(f"Update User {user_id}: {response.status_code} - {response.json()}")

def test_vehicle_availability():
    """Test vehicle availability endpoint"""
    print("\nTesting Vehicle Availability...")
    
    # Get current date and future dates
    today = datetime.now()
    pickup_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    return_date = (today + timedelta(days=3)).strftime('%Y-%m-%d')
    
    # Check availability for all vehicles
    params = {
        "pickup_date": pickup_date,
        "return_date": return_date
    }
    response = requests.get(f"{BASE_URL}/vehicles/availability", params=params)
    vehicles = response.json()
    print(f"Check Availability: {response.status_code} - Found {len(vehicles)} available vehicles")
    
    # Check availability for specific vehicle type
    params["type"] = "suv"
    response = requests.get(f"{BASE_URL}/vehicles/availability", params=params)
    suvs = response.json()
    print(f"Check SUV Availability: {response.status_code} - Found {len(suvs)} available SUVs")

def test_booking_creation():
    """Test booking creation"""
    print("\nTesting Booking Creation...")
    
    # First, get available users and vehicles
    users_response = requests.get(f"{BASE_URL}/users")
    users = users_response.json()
    
    today = datetime.now()
    pickup_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    return_date = (today + timedelta(days=3)).strftime('%Y-%m-%d')
    
    availability_response = requests.get(f"{BASE_URL}/vehicles/availability", 
                                       params={"pickup_date": pickup_date, "return_date": return_date})
    vehicles = availability_response.json()
    
    if users and vehicles:
        booking_data = {
            "user_id": users[0]['id'],
            "vehicle_id": vehicles[0]['id'],
            "pickup_date": pickup_date,
            "return_date": return_date
        }
        
        response = requests.post(f"{BASE_URL}/bookings", json=booking_data)
        print(f"Create Booking: {response.status_code} - {response.json()}")
    else:
        print("Cannot test booking - no users or vehicles available")

def test_daily_report():
    """Test daily report endpoint"""
    print("\nTesting Daily Report...")
    
    # Get report for today
    today = datetime.now().strftime('%Y-%m-%d')
    response = requests.get(f"{BASE_URL}/reports/daily", params={"date": today})
    bookings = response.json()
    print(f"Daily Report for {today}: {response.status_code} - Found {len(bookings)} bookings")
    
    # Get report with vehicle type filter
    response = requests.get(f"{BASE_URL}/reports/daily", 
                          params={"date": today, "vehicle_type": "suv"})
    suv_bookings = response.json()
    print(f"SUV Bookings for {today}: {response.status_code} - Found {len(suv_bookings)} SUV bookings")

def test_error_handling():
    """Test error handling"""
    print("\nTesting Error Handling...")
    
    # Test invalid user creation
    invalid_user = {"name": "Test"}  # Missing required fields
    response = requests.post(f"{BASE_URL}/users", json=invalid_user)
    print(f"Invalid User Creation: {response.status_code} - {response.json()}")
    
    # Test invalid date format
    response = requests.get(f"{BASE_URL}/vehicles/availability", 
                          params={"pickup_date": "invalid-date", "return_date": "2024-01-20"})
    print(f"Invalid Date Format: {response.status_code} - {response.json()}")
    
    # Test non-existent user
    response = requests.get(f"{BASE_URL}/users/99999")
    print(f"Non-existent User: {response.status_code} - {response.json()}")

def main():
    """Run all tests"""
    print("Starting API Tests...")
    print("=" * 50)
    
    try:
        test_user_crud()
        test_vehicle_availability()
        test_booking_creation()
        test_daily_report()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()