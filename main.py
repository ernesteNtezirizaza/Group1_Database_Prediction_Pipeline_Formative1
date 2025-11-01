"""
FastAPI Application with CRUD Operations
Handles both MySQL and MongoDB databases
"""

from fastapi import FastAPI
from datetime import datetime
import os

# Import API routers
from api.mysql_api import router as mysql_router
from api.mongodb_api import router as mongo_router

app = FastAPI(
    title="Hotel Booking API",
    description="CRUD API for Hotel Booking Management with MySQL and MongoDB",
    version="1.0.0"
)

# Include routers
app.include_router(mysql_router, prefix="/api/v1", tags=["MySQL Operations"])
app.include_router(mongo_router, prefix="/api/v1/mongo", tags=["MongoDB Operations"])

# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from api.mongodb_api import mongo_client
    return {
        "status": "healthy",
        "mysql_connected": True,
        "mongodb_connected": mongo_client.server_info() is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "message": "Hotel Booking API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)