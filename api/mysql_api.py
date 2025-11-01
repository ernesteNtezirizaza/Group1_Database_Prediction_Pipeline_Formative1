"""
MySQL API endpoints for Hotel Booking System
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import pymysql
from datetime import datetime
import os

router = APIRouter()

# Database configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'hotel_booking_db'),
    'charset': 'utf8mb4'
}

# =====================================================
# PYDANTIC MODELS
# =====================================================

class GuestCreate(BaseModel):
    country: str = Field(..., max_length=3, description="Country code (ISO 3-letter)")
    is_repeated_guest: bool = Field(default=False, description="Is this a repeated guest?")
    customer_type: str = Field(..., description="Customer type (Transient, Contract, etc.)")


class GuestResponse(GuestCreate):
    guest_id: int

    class Config:
        from_attributes = True


class HotelCreate(BaseModel):
    hotel_name: str = Field(..., max_length=50, description="Name of the hotel")


class HotelResponse(HotelCreate):
    hotel_id: int

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    hotel_id: int
    guest_id: int
    lead_time: int = Field(..., ge=0, description="Days between booking and arrival")
    arrival_date_year: int = Field(..., ge=2015, le=2020)
    arrival_date_month: str
    arrival_date_week_number: int = Field(..., ge=1, le=53)
    arrival_date_day_of_month: int = Field(..., ge=1, le=31)
    stays_in_weekend_nights: int = Field(default=0, ge=0)
    stays_in_week_nights: int = Field(default=0, ge=0)
    adults: int = Field(..., gt=0, description="Number of adults (must be > 0)")
    children: int = Field(default=0, ge=0)
    babies: int = Field(default=0, ge=0)
    meal: str
    market_segment: str
    distribution_channel: str
    previous_cancellations: int = Field(default=0, ge=0)
    previous_bookings_not_canceled: int = Field(default=0, ge=0)
    reserved_room_type: str = Field(..., max_length=1)
    assigned_room_type: str = Field(..., max_length=1)
    booking_changes: int = Field(default=0, ge=0)
    deposit_type: str
    agent: Optional[int] = None
    company: Optional[int] = None
    days_in_waiting_list: int = Field(default=0, ge=0)
    adr: float = Field(..., ge=0, description="Average Daily Rate")
    required_car_parking_spaces: int = Field(default=0, ge=0)
    total_of_special_requests: int = Field(default=0, ge=0)
    is_canceled: bool = Field(default=False)
    reservation_status: str
    reservation_status_date: Optional[str] = None


class BookingUpdate(BaseModel):
    reservation_status: Optional[str] = None
    is_canceled: Optional[bool] = None
    booking_changes: Optional[int] = None
    adr: Optional[float] = None


class BookingResponse(BookingCreate):
    booking_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# DATABASE DEPENDENCIES
# =====================================================

def get_mysql_connection():
    """Dependency to get MySQL connection"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        yield connection
    finally:
        connection.close()


# =====================================================
# GUEST CRUD OPERATIONS
# =====================================================

@router.post("/guests", response_model=GuestResponse, status_code=201)
async def create_guest(guest: GuestCreate, conn=Depends(get_mysql_connection)):
    """Create a new guest"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO guests (country, is_repeated_guest, customer_type)
               VALUES (%s, %s, %s)""",
            (guest.country, guest.is_repeated_guest, guest.customer_type)
        )
        conn.commit()
        guest_id = cursor.lastrowid
        return GuestResponse(guest_id=guest_id, **guest.dict())
    except pymysql.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()


@router.get("/guests/{guest_id}", response_model=GuestResponse)
async def get_guest(guest_id: int, conn=Depends(get_mysql_connection)):
    """Get a specific guest by ID"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT * FROM guests WHERE guest_id = %s",
            (guest_id,)
        )
        guest = cursor.fetchone()
        if not guest:
            raise HTTPException(status_code=404, detail="Guest not found")
        return GuestResponse(**guest)
    finally:
        cursor.close()


@router.get("/guests", response_model=List[GuestResponse])
async def get_all_guests(skip: int = 0, limit: int = 100, conn=Depends(get_mysql_connection)):
    """Get all guests with pagination"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT * FROM guests LIMIT %s OFFSET %s",
            (limit, skip)
        )
        guests = cursor.fetchall()
        return [GuestResponse(**g) for g in guests]
    finally:
        cursor.close()


@router.put("/guests/{guest_id}", response_model=GuestResponse)
async def update_guest(guest_id: int, guest: GuestCreate, conn=Depends(get_mysql_connection)):
    """Update a guest"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE guests SET country = %s, is_repeated_guest = %s, 
               customer_type = %s WHERE guest_id = %s""",
            (guest.country, guest.is_repeated_guest, guest.customer_type, guest_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Guest not found")
        conn.commit()
        return GuestResponse(guest_id=guest_id, **guest.dict())
    finally:
        cursor.close()


@router.delete("/guests/{guest_id}", status_code=204)
async def delete_guest(guest_id: int, conn=Depends(get_mysql_connection)):
    """Delete a guest"""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM guests WHERE guest_id = %s", (guest_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Guest not found")
        conn.commit()
        return None
    finally:
        cursor.close()

# =====================================================
# HOTEL CRUD OPERATIONS
# =====================================================

@router.post("/hotels", response_model=HotelResponse, status_code=201)
async def create_hotel(hotel: HotelCreate, conn=Depends(get_mysql_connection)):
    """Create a new hotel"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO hotels (hotel_name) VALUES (%s)",
            (hotel.hotel_name,)
        )
        conn.commit()
        hotel_id = cursor.lastrowid
        return HotelResponse(hotel_id=hotel_id, **hotel.dict())
    except pymysql.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()


@router.get("/hotels/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: int, conn=Depends(get_mysql_connection)):
    """Get a specific hotel by ID"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM hotels WHERE hotel_id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        return HotelResponse(**hotel)
    finally:
        cursor.close()


@router.get("/hotels", response_model=List[HotelResponse])
async def get_all_hotels(conn=Depends(get_mysql_connection)):
    """Get all hotels"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM hotels")
        hotels = cursor.fetchall()
        return [HotelResponse(**h) for h in hotels]
    finally:
        cursor.close()


@router.put("/hotels/{hotel_id}", response_model=HotelResponse)
async def update_hotel(hotel_id: int, hotel: HotelCreate, conn=Depends(get_mysql_connection)):
    """Update a hotel"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE hotels SET hotel_name = %s WHERE hotel_id = %s",
            (hotel.hotel_name, hotel_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Hotel not found")
        conn.commit()
        return HotelResponse(hotel_id=hotel_id, **hotel.dict())
    finally:
        cursor.close()


@router.delete("/hotels/{hotel_id}", status_code=204)
async def delete_hotel(hotel_id: int, conn=Depends(get_mysql_connection)):
    """Delete a hotel"""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM hotels WHERE hotel_id = %s", (hotel_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Hotel not found")
        conn.commit()
        return None
    finally:
        cursor.close()

# =====================================================
# BOOKING CRUD OPERATIONS
# =====================================================

@router.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(booking: BookingCreate, conn=Depends(get_mysql_connection)):
    """Create a new booking"""
    cursor = conn.cursor()
    try:
        # Validate booking using stored procedure
        cursor.execute(
            "CALL sp_validate_booking(%s, %s, %s, @is_valid, @error_message)",
            (booking.lead_time, booking.adults, booking.reservation_status)
        )
        cursor.execute("SELECT @is_valid, @error_message")
        result = cursor.fetchone()
        
        if not result or not result[0]:
            raise HTTPException(status_code=400, detail=result[1] if result else "Validation failed")
        
        # Insert booking
        insert_query = """
            INSERT INTO bookings (
                hotel_id, guest_id, lead_time, arrival_date_year, arrival_date_month,
                arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights,
                stays_in_week_nights, adults, children, babies, meal, market_segment,
                distribution_channel, previous_cancellations, previous_bookings_not_canceled,
                reserved_room_type, assigned_room_type, booking_changes, deposit_type,
                agent, company, days_in_waiting_list, adr, required_car_parking_spaces,
                total_of_special_requests, is_canceled, reservation_status, reservation_status_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        values = (
            booking.hotel_id, booking.guest_id, booking.lead_time, booking.arrival_date_year,
            booking.arrival_date_month, booking.arrival_date_week_number, booking.arrival_date_day_of_month,
            booking.stays_in_weekend_nights, booking.stays_in_week_nights, booking.adults, booking.children,
            booking.babies, booking.meal, booking.market_segment, booking.distribution_channel,
            booking.previous_cancellations, booking.previous_bookings_not_canceled, booking.reserved_room_type,
            booking.assigned_room_type, booking.booking_changes, booking.deposit_type, booking.agent,
            booking.company, booking.days_in_waiting_list, booking.adr, booking.required_car_parking_spaces,
            booking.total_of_special_requests, booking.is_canceled, booking.reservation_status,
            booking.reservation_status_date
        )
        
        cursor.execute(insert_query, values)
        conn.commit()
        booking_id = cursor.lastrowid
        
        # Get created booking
        cursor.execute(
            "SELECT * FROM bookings WHERE booking_id = %s",
            (booking_id,)
        )
        created_booking = cursor.fetchone()
        
        return BookingResponse(**created_booking)
    except pymysql.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database constraint error: {str(e)}")
    finally:
        cursor.close()


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, conn=Depends(get_mysql_connection)):
    """Get a specific booking by ID"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT * FROM bookings WHERE booking_id = %s",
            (booking_id,)
        )
        booking = cursor.fetchone()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return BookingResponse(**booking)
    finally:
        cursor.close()


@router.get("/bookings", response_model=List[BookingResponse])
async def get_all_bookings(skip: int = 0, limit: int = 100, 
                           is_canceled: Optional[bool] = None,
                           conn=Depends(get_mysql_connection)):
    """Get all bookings with pagination and optional filtering"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        if is_canceled is not None:
            cursor.execute(
                "SELECT * FROM bookings WHERE is_canceled = %s LIMIT %s OFFSET %s",
                (is_canceled, limit, skip)
            )
        else:
            cursor.execute(
                "SELECT * FROM bookings LIMIT %s OFFSET %s",
                (limit, skip)
            )
        bookings = cursor.fetchall()
        return [BookingResponse(**b) for b in bookings]
    finally:
        cursor.close()


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: int, booking_update: BookingUpdate, 
                        conn=Depends(get_mysql_connection)):
    """Update a booking (only allowed fields)"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Build update query dynamically
        updates = []
        values = []
        
        if booking_update.reservation_status is not None:
            updates.append("reservation_status = %s")
            values.append(booking_update.reservation_status)
        
        if booking_update.is_canceled is not None:
            updates.append("is_canceled = %s")
            values.append(booking_update.is_canceled)
        
        if booking_update.booking_changes is not None:
            updates.append("booking_changes = %s")
            values.append(booking_update.booking_changes)
        
        if booking_update.adr is not None:
            updates.append("adr = %s")
            values.append(booking_update.adr)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(booking_id)
        update_query = f"UPDATE bookings SET {', '.join(updates)} WHERE booking_id = %s"
        
        cursor.execute(update_query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Get updated booking
        cursor.execute(
            "SELECT * FROM bookings WHERE booking_id = %s",
            (booking_id,)
        )
        booking = cursor.fetchone()
        return BookingResponse(**booking)
    finally:
        cursor.close()


@router.delete("/bookings/{booking_id}", status_code=204)
async def delete_booking(booking_id: int, conn=Depends(get_mysql_connection)):
    """Delete a booking"""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Booking not found")
        conn.commit()
        return None
    finally:
        cursor.close()


# =====================================================
# STATISTICS ENDPOINTS
# =====================================================

@router.get("/statistics")
async def get_statistics(conn=Depends(get_mysql_connection)):
    """Get booking statistics using stored procedure"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "CALL sp_get_booking_statistics(@total, @cancellation_rate, @avg_adr, @country)"
        )
        cursor.execute(
            "SELECT @total as total_bookings, @cancellation_rate as cancellation_rate, "
            "@avg_adr as avg_adr, @country as most_common_country"
        )
        stats = cursor.fetchone()
        return stats
    finally:
        cursor.close()


@router.get("/bookings/logs")
async def get_booking_logs(skip: int = 0, limit: int = 100, conn=Depends(get_mysql_connection)):
    """Get booking change logs from triggers"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT * FROM booking_logs ORDER BY timestamp DESC LIMIT %s OFFSET %s",
            (limit, skip)
        )
        logs = cursor.fetchall()
        return logs
    finally:
        cursor.close()