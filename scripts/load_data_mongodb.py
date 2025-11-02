"""
Script to load hotel booking data into MongoDB
This script processes the CSV file and populates MongoDB collections
"""

import csv
from pymongo import MongoClient
from typing import Dict
import sys
import os
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST'),
    'port': os.getenv('MONGO_PORT'),
    'database': os.getenv('MONGO_DATABASE')
}


def clean_value(value: str):
    """Clean and handle NULL/empty values"""
    if value == 'NULL' or value == '' or value is None:
        return None
    return value.strip()


def insert_hotel(client, hotel_name: str, hotels_collection) -> int:
    """Insert or get hotel and return its ID"""
    hotel = hotels_collection.find_one({"hotel_name": hotel_name})
    
    if not hotel:
        result = hotels_collection.insert_one({
            "hotel_name": hotel_name,
            "metadata": {
                "created_at": client.datetime.utcnow() if hasattr(client, 'datetime') else None
            }
        })
        return result.inserted_id
    else:
        return hotel["_id"]


def insert_guest(client, country: str, is_repeated_guest: str, 
                 customer_type: str, guests_collection) -> int:
    """Insert or get guest and return its ID"""
    is_repeated = True if is_repeated_guest == '1' else False
    
    guest = guests_collection.find_one({
        "country": country,
        "is_repeated_guest": is_repeated,
        "customer_type": customer_type
    })
    
    if not guest:
        result = guests_collection.insert_one({
            "country": country,
            "is_repeated_guest": is_repeated,
            "customer_type": customer_type,
            "metadata": {
                "created_at": client.datetime.utcnow() if hasattr(client, 'datetime') else None
            }
        })
        return result.inserted_id
    else:
        return guest["_id"]


def load_bookings_data(file_path: str):
    """
    Load bookings data from CSV into MongoDB
    Uses denormalized document structure for fast queries
    """
    client = None
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'])
        db = client[MONGO_CONFIG['database']]
        
        print(f"Connected to MongoDB database: {MONGO_CONFIG['database']}")
        
        # Create collections
        hotels_collection = db['hotels']
        guests_collection = db['guests']
        bookings_collection = db['bookings']
        
        # Create indexes for better performance
        hotels_collection.create_index("hotel_name", unique=True)
        guests_collection.create_index([("country", 1), ("is_repeated_guest", 1), ("customer_type", 1)])
        bookings_collection.create_index("booking_details.lead_time")
        bookings_collection.create_index("status.is_canceled")
        bookings_collection.create_index("status.reservation_status")
        
        total_inserted = 0
        
        # Read CSV file
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Get or create hotel
                    hotel_name = clean_value(row['hotel'])
                    hotel_id = insert_hotel(client, hotel_name, hotels_collection)
                    
                    # Get or create guest
                    country = clean_value(row['country']) or 'UNK'
                    is_repeated = clean_value(row['is_repeated_guest'])
                    customer_type = clean_value(row['customer_type'])
                    guest_id = insert_guest(client, country, is_repeated, customer_type, guests_collection)
                    
                    # Build booking document (denormalized)
                    booking_doc = {
                        "hotel": {
                            "hotel_id": str(hotel_id),
                            "hotel_name": hotel_name
                        },
                        "guest": {
                            "guest_id": str(guest_id),
                            "country": country,
                            "is_repeated_guest": True if is_repeated == '1' else False
                        },
                        "booking_details": {
                            "lead_time": int(clean_value(row['lead_time']) or 0),
                            "arrival_date": {
                                "year": int(clean_value(row['arrival_date_year']) or 0),
                                "month": clean_value(row['arrival_date_month']),
                                "week": int(clean_value(row['arrival_date_week_number']) or 0),
                                "day": int(clean_value(row['arrival_date_day_of_month']) or 0)
                            },
                            "stays": {
                                "weekend_nights": int(clean_value(row['stays_in_weekend_nights']) or 0),
                                "week_nights": int(clean_value(row['stays_in_week_nights']) or 0)
                            },
                            "guests": {
                                "adults": int(clean_value(row['adults']) or 0),
                                "children": int(clean_value(row['children']) or 0),
                                "babies": int(clean_value(row['babies']) or 0)
                            },
                            "meal": clean_value(row['meal']),
                            "market_segment": clean_value(row['market_segment']),
                            "distribution_channel": clean_value(row['distribution_channel']),
                            "room": {
                                "reserved": clean_value(row['reserved_room_type']),
                                "assigned": clean_value(row['assigned_room_type'])
                            },
                            "booking_changes": int(clean_value(row['booking_changes']) or 0),
                            "deposit_type": clean_value(row['deposit_type']),
                            "agent": int(clean_value(row['agent']) or 0) if clean_value(row['agent']) else None,
                            "company": int(clean_value(row['company']) or 0) if clean_value(row['company']) else None,
                            "days_in_waiting_list": int(clean_value(row['days_in_waiting_list']) or 0),
                            "adr": float(clean_value(row['adr']) or 0),
                            "required_car_parking_spaces": int(clean_value(row['required_car_parking_spaces']) or 0),
                            "total_of_special_requests": int(clean_value(row['total_of_special_requests']) or 0)
                        },
                        "status": {
                            "is_canceled": True if clean_value(row['is_canceled']) == '1' else False,
                            "reservation_status": clean_value(row['reservation_status']),
                            "reservation_status_date": clean_value(row['reservation_status_date'])
                        },
                        "history": {
                            "previous_cancellations": int(clean_value(row['previous_cancellations']) or 0),
                            "previous_bookings_not_canceled": int(clean_value(row['previous_bookings_not_canceled']) or 0)
                        },
                        "metadata": {
                            "created_at": None  # Can be set to datetime if needed
                        }
                    }
                    
                    # Insert booking
                    bookings_collection.insert_one(booking_doc)
                    total_inserted += 1
                    
                    # Progress update
                    if total_inserted % 1000 == 0:
                        print(f"Inserted {total_inserted} bookings so far...")
                        
                except Exception as e:
                    print(f"Error processing row {row_num}: {e}")
                    continue
        
        print(f"\nData loading completed!")
        print(f"Total bookings inserted: {total_inserted}")
        
        # Display statistics
        print(f"\nCollection Statistics:")
        print(f"Total hotels: {hotels_collection.count_documents({})}")
        print(f"Total guests: {guests_collection.count_documents({})}")
        print(f"Total bookings: {bookings_collection.count_documents({})}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    finally:
        if client:
            client.close()
            print("\nMongoDB connection closed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_data_mongodb.py <csv_file_path>")
        print("Example: python load_data_mongodb.py hotel_bookings.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    load_bookings_data(csv_file)
