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
