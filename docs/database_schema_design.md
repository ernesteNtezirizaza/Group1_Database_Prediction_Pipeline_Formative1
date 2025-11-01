# Hotel Booking Database Schema Design

## ERD Diagram Overview
The database is designed with 4 main tables following 3NF normalization principles.

## Table Structures

### 1. **hotels** Table
Stores hotel information
- `hotel_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `hotel_name` (VARCHAR(50), NOT NULL, UNIQUE)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

### 2. **guests** Table
Stores guest/customer information
- `guest_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `country` (VARCHAR(3), NOT NULL)
- `is_repeated_guest` (BOOLEAN, DEFAULT FALSE)
- `customer_type` (VARCHAR(20), NOT NULL) - Transient, Contract, Group, Transient-Party
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

### 3. **bookings** Table
Main booking information
- `booking_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `hotel_id` (INT, FOREIGN KEY -> hotels.hotel_id)
- `guest_id` (INT, FOREIGN KEY -> guests.guest_id)
- `lead_time` (INT, NOT NULL)
- `arrival_date_year` (INT, NOT NULL)
- `arrival_date_month` (VARCHAR(20), NOT NULL)
- `arrival_date_week_number` (INT, NOT NULL)
- `arrival_date_day_of_month` (INT, NOT NULL)
- `stays_in_weekend_nights` (INT, DEFAULT 0)
- `stays_in_week_nights` (INT, DEFAULT 0)
- `adults` (INT, NOT NULL)
- `children` (INT, DEFAULT 0)
- `babies` (INT, DEFAULT 0)
- `meal` (VARCHAR(20), NOT NULL) - BB, HB, FB, SC, Undefined
- `market_segment` (VARCHAR(50), NOT NULL)
- `distribution_channel` (VARCHAR(50), NOT NULL)
- `previous_cancellations` (INT, DEFAULT 0)
- `previous_bookings_not_canceled` (INT, DEFAULT 0)
- `reserved_room_type` (VARCHAR(1), NOT NULL)
- `assigned_room_type` (VARCHAR(1), NOT NULL)
- `booking_changes` (INT, DEFAULT 0)
- `deposit_type` (VARCHAR(20), NOT NULL)
- `agent` (INT, NULL)
- `company` (INT, NULL)
- `days_in_waiting_list` (INT, DEFAULT 0)
- `adr` (DECIMAL(10,2), NOT NULL) - Average Daily Rate
- `required_car_parking_spaces` (INT, DEFAULT 0)
- `total_of_special_requests` (INT, DEFAULT 0)
- `is_canceled` (BOOLEAN, DEFAULT FALSE)
- `reservation_status` (VARCHAR(20), NOT NULL)
- `reservation_status_date` (DATE)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

### 4. **booking_logs** Table
Automated logging table for triggers
- `log_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `booking_id` (INT, FOREIGN KEY -> bookings.booking_id)
- `action` (VARCHAR(20), NOT NULL) - INSERT, UPDATE, DELETE
- `old_status` (VARCHAR(20), NULL)
- `new_status` (VARCHAR(20), NULL)
- `timestamp` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

## Stored Procedures

### 1. `sp_validate_booking`
Validates booking data before insertion
- Checks lead_time >= 0
- Checks adults > 0
- Checks valid reservation_status
- Returns error message if validation fails

### 2. `sp_get_booking_statistics`
Returns statistics for bookings
- Total bookings
- Cancellation rate
- Average ADR
- Most common country

## Triggers

### 1. `trg_booking_after_update`
Logs status changes in bookings
- Fires after UPDATE on bookings
- Records old_status and new_status in booking_logs

### 2. `trg_booking_after_insert`
Logs new bookings
- Fires after INSERT on bookings
- Records action in booking_logs

## Indexes
- Index on `hotels.hotel_name`
- Index on `bookings.hotel_id`
- Index on `bookings.guest_id`
- Index on `bookings.is_canceled`
- Index on `bookings.reservation_status`
- Index on `booking_logs.booking_id`

## MongoDB Collections Design

### Collection 1: **hotels**
```json
{
  "hotel_id": 1,
  "hotel_name": "Resort Hotel",
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Collection 2: **guests**
```json
{
  "guest_id": 1,
  "country": "PRT",
  "is_repeated_guest": false,
  "customer_type": "Transient",
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Collection 3: **bookings** (Denormalized for quick access)
```json
{
  "booking_id": 1,
  "hotel": {
    "hotel_id": 1,
    "hotel_name": "Resort Hotel"
  },
  "guest": {
    "guest_id": 1,
    "country": "PRT",
    "is_repeated_guest": false
  },
  "booking_details": {
    "lead_time": 342,
    "arrival_date": {
      "year": 2015,
      "month": "July",
      "week": 27,
      "day": 1
    },
    "stays": {
      "weekend_nights": 0,
      "week_nights": 0
    },
    "guests": {
      "adults": 2,
      "children": 0,
      "babies": 0
    },
    "meal": "BB",
    "market_segment": "Direct",
    "distribution_channel": "Direct",
    "room": {
      "reserved": "C",
      "assigned": "C"
    },
    "booking_changes": 3,
    "deposit_type": "No Deposit",
    "agent": null,
    "company": null,
    "days_in_waiting_list": 0,
    "adr": 0,
    "required_car_parking_spaces": 0,
    "total_of_special_requests": 0
  },
  "status": {
    "is_canceled": false,
    "reservation_status": "Check-Out",
    "reservation_status_date": "2015-07-01"
  },
  "history": {
    "previous_cancellations": 0,
    "previous_bookings_not_canceled": 0
  },
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Rationale for Design

1. **Normalization**: The schema follows 3NF by separating hotels, guests, and bookings into distinct tables to avoid data redundancy.

2. **Foreign Keys**: Proper relationships ensure referential integrity between tables.

3. **MongoDB Design**: Uses embedded documents for quick queries without joins while maintaining logical grouping.

4. **Automation**: Triggers and stored procedures handle validation and logging automatically.

5. **Indexing**: Strategic indexes improve query performance for common operations like searching by status or hotel.

6. **ML-Ready**: The schema preserves all features needed for machine learning predictions including booking patterns, guest history, and hotel characteristics.
