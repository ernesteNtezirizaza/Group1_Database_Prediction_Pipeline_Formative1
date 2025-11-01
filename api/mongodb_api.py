"""
MongoDB API endpoints for Hotel Booking System
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

router = APIRouter()

# MongoDB configuration
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST', 'localhost'),
    'port': int(os.getenv('MONGO_PORT', 27017)),
    'database': os.getenv('MONGO_DATABASE', 'hotel_booking_db')
}

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'])
mongo_db = mongo_client[MONGO_CONFIG['database']]

# =====================================================
# PYDANTIC MODELS
# =====================================================

class GuestCreate(BaseModel):
    country: str = Field(..., max_length=3, description="Country code (ISO 3-letter)")
    is_repeated_guest: bool = Field(default=False, description="Is this a repeated guest?")
    customer_type: str = Field(..., description="Customer type (Transient, Contract, etc.)")


class HotelCreate(BaseModel):
    hotel_name: str = Field(..., max_length=50, description="Name of the hotel")


class BookingCreate(BaseModel):
    hotel_id: str
    guest_id: str
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


# =====================================================
# GUEST CRUD OPERATIONS
# =====================================================

@router.post("/guests", status_code=201)
async def create_guest_mongo(guest: GuestCreate):
    """Create a new guest in MongoDB"""
    try:
        # Check if MongoDB is connected
        mongo_client.server_info()
        
        guest_collection = mongo_db['guests']
        
        # Check if guest already exists
        existing = guest_collection.find_one({
            "country": guest.country,
            "is_repeated_guest": guest.is_repeated_guest,
            "customer_type": guest.customer_type
        })
        
        if existing:
            return {
                "guest_id": str(existing["_id"]),
                **guest.dict(),
                "message": "Guest already exists"
            }
        
        # Insert new guest
        guest_doc = {
            **guest.dict(),
            "metadata": {
                "created_at": datetime.now().isoformat()
            }
        }
        result = guest_collection.insert_one(guest_doc)
        
        return {
            "guest_id": str(result.inserted_id),
            **guest.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.get("/guests/{guest_id}")
async def get_guest_mongo(guest_id: str):
    """Get a specific guest by ID from MongoDB"""
    try:
        mongo_client.server_info()
        guest_collection = mongo_db['guests']
        
        try:
            guest = guest_collection.find_one({"_id": ObjectId(guest_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid guest ID format")
        
        if not guest:
            raise HTTPException(status_code=404, detail="Guest not found")
        
        guest["guest_id"] = str(guest["_id"])
        del guest["_id"]
        return guest
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.get("/guests")
async def get_all_guests_mongo(skip: int = 0, limit: int = 100):
    """Get all guests from MongoDB with pagination"""
    try:
        mongo_client.server_info()
        guest_collection = mongo_db['guests']
        
        guests = guest_collection.find().skip(skip).limit(limit)
        
        result = []
        for guest in guests:
            guest["guest_id"] = str(guest["_id"])
            del guest["_id"]
            result.append(guest)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.put("/guests/{guest_id}")
async def update_guest_mongo(guest_id: str, guest: GuestCreate):
    """Update a guest in MongoDB"""
    try:
        mongo_client.server_info()
        guest_collection = mongo_db['guests']
        
        try:
            result = guest_collection.update_one(
                {"_id": ObjectId(guest_id)},
                {"$set": guest.dict()}
            )
        except:
            raise HTTPException(status_code=400, detail="Invalid guest ID format")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Guest not found")
        
        # Return updated guest
        updated = guest_collection.find_one({"_id": ObjectId(guest_id)})
        updated["guest_id"] = str(updated["_id"])
        del updated["_id"]
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.delete("/guests/{guest_id}", status_code=204)
async def delete_guest_mongo(guest_id: str):
    """Delete a guest from MongoDB"""
    try:
        mongo_client.server_info()
        guest_collection = mongo_db['guests']
        
        try:
            result = guest_collection.delete_one({"_id": ObjectId(guest_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid guest ID format")
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Guest not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")

# =====================================================
# HOTEL CRUD OPERATIONS
# =====================================================

@router.post("/hotels", status_code=201)
async def create_hotel_mongo(hotel: HotelCreate):
    """Create a new hotel in MongoDB"""
    try:
        mongo_client.server_info()
        hotel_collection = mongo_db['hotels']
        
        # Check if hotel already exists
        existing = hotel_collection.find_one({"hotel_name": hotel.hotel_name})
        
        if existing:
            return {
                "hotel_id": str(existing["_id"]),
                **hotel.dict(),
                "message": "Hotel already exists"
            }
        
        # Insert new hotel
        hotel_doc = {
            **hotel.dict(),
            "metadata": {
                "created_at": datetime.now().isoformat()
            }
        }
        result = hotel_collection.insert_one(hotel_doc)
        
        return {
            "hotel_id": str(result.inserted_id),
            **hotel.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.get("/hotels/{hotel_id}")
async def get_hotel_mongo(hotel_id: str):
    """Get a specific hotel by ID from MongoDB"""
    try:
        mongo_client.server_info()
        hotel_collection = mongo_db['hotels']
        
        try:
            hotel = hotel_collection.find_one({"_id": ObjectId(hotel_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid hotel ID format")
        
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        hotel["hotel_id"] = str(hotel["_id"])
        del hotel["_id"]
        return hotel
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.get("/hotels")
async def get_all_hotels_mongo():
    """Get all hotels from MongoDB"""
    try:
        mongo_client.server_info()
        hotel_collection = mongo_db['hotels']
        
        hotels = hotel_collection.find()
        
        result = []
        for hotel in hotels:
            hotel["hotel_id"] = str(hotel["_id"])
            del hotel["_id"]
            result.append(hotel)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.put("/hotels/{hotel_id}")
async def update_hotel_mongo(hotel_id: str, hotel: HotelCreate):
    """Update a hotel in MongoDB"""
    try:
        mongo_client.server_info()
        hotel_collection = mongo_db['hotels']
        
        try:
            result = hotel_collection.update_one(
                {"_id": ObjectId(hotel_id)},
                {"$set": hotel.dict()}
            )
        except:
            raise HTTPException(status_code=400, detail="Invalid hotel ID format")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        # Return updated hotel
        updated = hotel_collection.find_one({"_id": ObjectId(hotel_id)})
        updated["hotel_id"] = str(updated["_id"])
        del updated["_id"]
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.delete("/hotels/{hotel_id}", status_code=204)
async def delete_hotel_mongo(hotel_id: str):
    """Delete a hotel from MongoDB"""
    try:
        mongo_client.server_info()
        hotel_collection = mongo_db['hotels']
        
        try:
            result = hotel_collection.delete_one({"_id": ObjectId(hotel_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid hotel ID format")
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")

# =====================================================
# BOOKING CRUD OPERATIONS
# =====================================================

@router.post("/bookings", status_code=201)
async def create_booking_mongo(booking: BookingCreate):
    """Create a new booking in MongoDB"""
    try:
        mongo_client.server_info()
        booking_collection = mongo_db['bookings']
        
        # Get hotel and guest info from their IDs
        hotel_collection = mongo_db['hotels']
        guest_collection = mongo_db['guests']
        
        hotel = hotel_collection.find_one({"_id": ObjectId(booking.hotel_id)})
        guest = guest_collection.find_one({"_id": ObjectId(booking.guest_id)})
        
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        if not guest:
            raise HTTPException(status_code=404, detail="Guest not found")
        
        # Create denormalized booking document
        booking_doc = {
            "hotel": {
                "hotel_id": str(hotel["_id"]),
                "hotel_name": hotel["hotel_name"]
            },
            "guest": {
                "guest_id": str(guest["_id"]),
                "country": guest["country"],
                "is_repeated_guest": guest["is_repeated_guest"]
            },
            "booking_details": {
                "lead_time": booking.lead_time,
                "arrival_date": {
                    "year": booking.arrival_date_year,
                    "month": booking.arrival_date_month,
                    "week": booking.arrival_date_week_number,
                    "day": booking.arrival_date_day_of_month
                },
                "stays": {
                    "weekend_nights": booking.stays_in_weekend_nights,
                    "week_nights": booking.stays_in_week_nights
                },
                "guests": {
                    "adults": booking.adults,
                    "children": booking.children,
                    "babies": booking.babies
                },
                "meal": booking.meal,
                "market_segment": booking.market_segment,
                "distribution_channel": booking.distribution_channel,
                "room": {
                    "reserved": booking.reserved_room_type,
                    "assigned": booking.assigned_room_type
                },
                "booking_changes": booking.booking_changes,
                "deposit_type": booking.deposit_type,
                "agent": booking.agent,
                "company": booking.company,
                "days_in_waiting_list": booking.days_in_waiting_list,
                "adr": booking.adr,
                "required_car_parking_spaces": booking.required_car_parking_spaces,
                "total_of_special_requests": booking.total_of_special_requests
            },
            "status": {
                "is_canceled": booking.is_canceled,
                "reservation_status": booking.reservation_status,
                "reservation_status_date": booking.reservation_status_date
            },
            "history": {
                "previous_cancellations": booking.previous_cancellations,
                "previous_bookings_not_canceled": booking.previous_bookings_not_canceled
            },
            "metadata": {
                "created_at": datetime.now().isoformat()
            }
        }
        
        result = booking_collection.insert_one(booking_doc)
        
        booking_doc["booking_id"] = str(result.inserted_id)
        del booking_doc["_id"]
        
        return booking_doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")


@router.get("/bookings/{booking_id}")
async def get_booking_mongo(booking_id: str):
    """Get a specific booking by ID from MongoDB"""
    try:
        mongo_client.server_info()
        booking_collection = mongo_db['bookings']
        
        try:
            booking = booking_collection.find_one({"_id": ObjectId(booking_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid booking ID format")
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        booking["booking_id"] = str(booking["_id"])
        del booking["_id"]
        return booking
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}")