"""
Script to load hotel booking data into MySQL database
This script processes the CSV file and populates the normalized tables
"""

import csv
import pymysql
from typing import Dict, Set
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
    'autocommit': False
}


def clean_value(value: str) -> str:
    """Clean and handle NULL/empty values"""
    if value == 'NULL' or value == '' or value is None:
        return None
    return value.strip()


def get_or_create_hotel(cursor, hotel_name: str, hotel_map: Dict[str, int]) -> int:
    """Get hotel_id or create new hotel and return its ID"""
    if hotel_name in hotel_map:
        return hotel_map[hotel_name]
    
    # Check if hotel exists in database
    cursor.execute("SELECT hotel_id FROM hotels WHERE hotel_name = %s", (hotel_name,))
    result = cursor.fetchone()
    
    if result:
        hotel_id = result[0]
    else:
        # Insert new hotel
        cursor.execute("INSERT INTO hotels (hotel_name) VALUES (%s)", (hotel_name,))
        hotel_id = cursor.lastrowid
    
    hotel_map[hotel_name] = hotel_id
    return hotel_id


def get_or_create_guest(cursor, country: str, is_repeated_guest: str, 
                         customer_type: str, guest_map: Dict[str, int]) -> int:
    """Get guest_id or create new guest and return its ID"""
    is_repeated = True if is_repeated_guest == '1' else False
    key = f"{country}_{is_repeated}_{customer_type}"
    
    if key in guest_map:
        return guest_map[key]
    
    # Check if guest exists in database
    cursor.execute(
        """SELECT guest_id FROM guests 
           WHERE country = %s AND is_repeated_guest = %s AND customer_type = %s 
           LIMIT 1""",
        (country, is_repeated, customer_type)
    )
    result = cursor.fetchone()
    
    if result:
        guest_id = result[0]
    else:
        # Insert new guest
        cursor.execute(
            """INSERT INTO guests (country, is_repeated_guest, customer_type) 
               VALUES (%s, %s, %s)""",
            (country, is_repeated, customer_type)
        )
        guest_id = cursor.lastrowid
    
    guest_map[key] = guest_id
    return guest_id


def load_bookings_data(file_path: str, batch_size: int = 1000):
    """
    Load bookings data from CSV into MySQL database
    Uses batch processing for efficiency
    """
    connection = None
    
    try:
        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Connected to MySQL database")
        
        hotel_map = {}
        guest_map = {}
        batch_count = 0
        total_inserted = 0
        
        # Read CSV file
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Get or create hotel
                    hotel_name = clean_value(row['hotel'])
                    hotel_id = get_or_create_hotel(cursor, hotel_name, hotel_map)
                    
                    # Get or create guest
                    country = clean_value(row['country']) or 'UNK'
                    is_repeated = clean_value(row['is_repeated_guest'])
                    customer_type = clean_value(row['customer_type'])
                    guest_id = get_or_create_guest(cursor, country, is_repeated, 
                                                   customer_type, guest_map)
                    
                    # Insert booking
                    insert_query = """
                        INSERT INTO bookings (
                            hotel_id, guest_id, lead_time, arrival_date_year,
                            arrival_date_month, arrival_date_week_number,
                            arrival_date_day_of_month, stays_in_weekend_nights,
                            stays_in_week_nights, adults, children, babies,
                            meal, market_segment, distribution_channel,
                            previous_cancellations, previous_bookings_not_canceled,
                            deposit_type, agent, company, days_in_waiting_list,
                            adr, required_car_parking_spaces, total_of_special_requests,
                            is_canceled, reservation_status, reservation_status_date
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    
                    booking_values = (
                        hotel_id,
                        guest_id,
                        int(clean_value(row['lead_time']) or 0),
                        int(clean_value(row['arrival_date_year']) or 0),
                        clean_value(row['arrival_date_month']),
                        int(clean_value(row['arrival_date_week_number']) or 0),
                        int(clean_value(row['arrival_date_day_of_month']) or 0),
                        int(clean_value(row['stays_in_weekend_nights']) or 0),
                        int(clean_value(row['stays_in_week_nights']) or 0),
                        int(clean_value(row['adults']) or 0),
                        int(clean_value(row['children']) or 0),
                        int(clean_value(row['babies']) or 0),
                        clean_value(row['meal']),
                        clean_value(row['market_segment']),
                        clean_value(row['distribution_channel']),
                        int(clean_value(row['previous_cancellations']) or 0),
                        int(clean_value(row['previous_bookings_not_canceled']) or 0),
                        clean_value(row['reserved_room_type']),
                        clean_value(row['assigned_room_type']),
                        int(clean_value(row['booking_changes']) or 0),
                        clean_value(row['deposit_type']),
                        int(clean_value(row['agent']) or 0) if clean_value(row['agent']) else None,
                        int(clean_value(row['company']) or 0) if clean_value(row['company']) else None,
                        int(clean_value(row['days_in_waiting_list']) or 0),
                        float(clean_value(row['adr']) or 0),
                        int(clean_value(row['required_car_parking_spaces']) or 0),
                        int(clean_value(row['total_of_special_requests']) or 0),
                        True if clean_value(row['is_canceled']) == '1' else False,
                        clean_value(row['reservation_status']),
                        clean_value(row['reservation_status_date'])
                    )
                    
                    cursor.execute(insert_query, booking_values)
                    batch_count += 1
                    total_inserted += 1
                    
                    # Commit in batches
                    if batch_count >= batch_size:
                        connection.commit()
                        print(f"Inserted {total_inserted} records so far...")
                        batch_count = 0
                        
                except Exception as e:
                    print(f"Error processing row {row_num}: {e}")
                    connection.rollback()
                    continue
            
            # Final commit
            if batch_count > 0:
                connection.commit()
        
        print(f"\nData loading completed!")
        print(f"Total bookings inserted: {total_inserted}")
        
        # Display statistics
        cursor.execute("SELECT COUNT(*) FROM hotels")
        print(f"Total unique hotels: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM guests")
        print(f"Total unique guests: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM bookings")
        print(f"Total bookings: {cursor.fetchone()[0]}")
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
        
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_data_mysql.py <csv_file_path>")
        print("Example: python load_data_mysql.py hotel_bookings.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    load_bookings_data(csv_file)
