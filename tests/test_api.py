"""
Test script for API endpoints
Run this after starting the FastAPI server to verify all endpoints work
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://group1-database-prediction-pipeline.onrender.com"

def test_health_check():
    """Test health check endpoint"""
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(" Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f" Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Health check error: {e}")
        return False


def test_create_hotel():
    """Test creating a hotel"""
    print("\n2. Testing Create Hotel (POST)...")
    try:
        hotel_data = {
            "hotel_name": "Test Hotel API"
        }
        response = requests.post(f"{BASE_URL}/api/v1/hotels", json=hotel_data)
        if response.status_code == 201:
            print(" Hotel created successfully")
            hotel = response.json()
            print(f"   Hotel ID: {hotel.get('hotel_id')}")
            return hotel
        else:
            print(f" Failed to create hotel: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f" Error creating hotel: {e}")
        return None


def test_get_hotels():
    """Test getting all hotels"""
    print("\n3. Testing Get All Hotels (GET)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/hotels")
        if response.status_code == 200:
            hotels = response.json()
            print(f" Retrieved {len(hotels)} hotels")
            return hotels
        else:
            print(f" Failed to get hotels: {response.status_code}")
            return None
    except Exception as e:
        print(f" Error getting hotels: {e}")
        return None


def test_create_guest():
    """Test creating a guest"""
    print("\n4. Testing Create Guest (POST)...")
    try:
        guest_data = {
            "country": "TST",
            "is_repeated_guest": False,
            "customer_type": "Transient"
        }
        response = requests.post(f"{BASE_URL}/api/v1/guests", json=guest_data)
        if response.status_code == 201:
            print(" Guest created successfully")
            guest = response.json()
            print(f"   Guest ID: {guest.get('guest_id')}")
            return guest
        else:
            print(f" Failed to create guest: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f" Error creating guest: {e}")
        return None


def test_create_booking(hotel_id, guest_id):
    """Test creating a booking"""
    print("\n5. Testing Create Booking (POST)...")
    try:
        booking_data = {
            "hotel_id": hotel_id,
            "guest_id": guest_id,
            "lead_time": 30,
            "arrival_date_year": 2024,
            "arrival_date_month": "December",
            "arrival_date_week_number": 50,
            "arrival_date_day_of_month": 15,
            "stays_in_weekend_nights": 2,
            "stays_in_week_nights": 3,
            "adults": 2,
            "children": 0,
            "babies": 0,
            "meal": "BB",
            "market_segment": "Online TA",
            "distribution_channel": "TA/TO",
            "previous_cancellations": 0,
            "previous_bookings_not_canceled": 0,
            "reserved_room_type": "A",
            "assigned_room_type": "A",
            "booking_changes": 0,
            "deposit_type": "No Deposit",
            "agent": None,
            "company": None,
            "days_in_waiting_list": 0,
            "adr": 100.50,
            "required_car_parking_spaces": 0,
            "total_of_special_requests": 1,
            "is_canceled": False,
            "reservation_status": "Check-Out",
            "reservation_status_date": "2024-12-20"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bookings", json=booking_data)
        if response.status_code == 201:
            print(" Booking created successfully")
            booking = response.json()
            print(f"   Booking ID: {booking.get('booking_id')}")
            return booking
        else:
            print(f" Failed to create booking: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f" Error creating booking: {e}")
        return None


def test_get_bookings():
    """Test getting bookings"""
    print("\n6. Testing Get All Bookings (GET)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/bookings?limit=5")
        if response.status_code == 200:
            bookings = response.json()
            print(f" Retrieved {len(bookings)} bookings")
            return bookings
        else:
            print(f" Failed to get bookings: {response.status_code}")
            return None
    except Exception as e:
        print(f" Error getting bookings: {e}")
        return None


def test_update_booking(booking_id):
    """Test updating a booking"""
    print("\n7. Testing Update Booking (PUT)...")
    try:
        update_data = {
            "reservation_status": "Canceled",
            "is_canceled": True
        }
        response = requests.put(
            f"{BASE_URL}/api/v1/bookings/{booking_id}",
            json=update_data
        )
        if response.status_code == 200:
            print(" Booking updated successfully")
            booking = response.json()
            print(f"   New status: {booking.get('reservation_status')}")
            return booking
        else:
            print(f" Failed to update booking: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f" Error updating booking: {e}")
        return None


def test_get_statistics():
    """Test statistics endpoint"""
    print("\n8. Testing Get Statistics (GET)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/statistics")
        if response.status_code == 200:
            print(" Statistics retrieved successfully")
            stats = response.json()
            print(f"   Total bookings: {stats.get('total_bookings', 'N/A')}")
            print(f"   Cancellation rate: {stats.get('cancellation_rate', 'N/A')}%")
            print(f"   Average ADR: {stats.get('avg_adr', 'N/A')}")
            return stats
        else:
            print(f" Failed to get statistics: {response.status_code}")
            return None
    except Exception as e:
        print(f" Error getting statistics: {e}")
        return None


def test_get_logs():
    """Test booking logs endpoint"""
    print("\n9. Testing Get Booking Logs (GET)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/bookings/logs?limit=5")
        if response.status_code == 200:
            logs = response.json()
            print(f" Retrieved {len(logs)} log entries")
            return logs
        else:
            print(f" Failed to get logs: {response.status_code}")
            return None
    except Exception as e:
        print(f" Error getting logs: {e}")
        return None


def test_delete_booking(booking_id):
    """Test deleting a booking"""
    print("\n10. Testing Delete Booking (DELETE)...")
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/bookings/{booking_id}")
        if response.status_code == 204:
            print("✅ Booking deleted successfully")
            return True
        else:
            print(f" Failed to delete booking: {response.status_code}")
            return False
    except Exception as e:
        print(f" Error deleting booking: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Endpoint Testing")
    print("=" * 60)
    print("Make sure the FastAPI server is running on https://group1-database-prediction-pipeline.onrender.com")
    
    tests_passed = 0
    tests_total = 10
    
    # Test health check
    if test_health_check():
        tests_passed += 1
    else:
        print("\n Server is not running or not accessible")
        return
    
    # Test CRUD operations
    hotel = test_create_hotel()
    if hotel:
        tests_passed += 1
    
    hotels = test_get_hotels()
    if hotels:
        tests_passed += 1
    
    guest = test_create_guest()
    if guest:
        tests_passed += 1
    
    hotel_id = hotel.get('hotel_id') if hotel else 1
    guest_id = guest.get('guest_id') if guest else 1
    
    booking = test_create_booking(hotel_id, guest_id)
    if booking:
        tests_passed += 1
    
    bookings = test_get_bookings()
    if bookings:
        tests_passed += 1
    
    booking_id = booking.get('booking_id') if booking else None
    if booking_id:
        updated_booking = test_update_booking(booking_id)
        if updated_booking:
            tests_passed += 1
    
    stats = test_get_statistics()
    if stats:
        tests_passed += 1
    
    logs = test_get_logs()
    if logs is not None:
        tests_passed += 1
    
    if booking_id:
        if test_delete_booking(booking_id):
            tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    if tests_passed == tests_total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
