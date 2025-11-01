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
