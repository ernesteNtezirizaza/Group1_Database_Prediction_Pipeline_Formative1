"""
Prediction Script for Hotel Booking Cancellations
Fetches latest booking data from API and makes predictions using ML model
"""

import requests
import pandas as pd
import numpy as np
import joblib
from typing import Dict, List, Optional
import json
from datetime import datetime
import os

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Model configuration
MODEL_PATH = 'cancellation_model.pkl'
PREPROCESSOR_PATH = 'feature_preprocessor.pkl'


class BookingPredictor:
    """
    Class to handle fetching booking data and making predictions
    """
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.model = None
        self.preprocessor = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained ML model and preprocessor"""
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                print(f"Model loaded from {MODEL_PATH}")
            
            if os.path.exists(PREPROCESSOR_PATH):
                self.preprocessor = joblib.load(PREPROCESSOR_PATH)
                print(f"Preprocessor loaded from {PREPROCESSOR_PATH}")
        except Exception as e:
            print(f"Warning: Could not load model files: {e}")
            print("Will create dummy model for demonstration")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a simple dummy model for demonstration"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        
        # Dummy model for demonstration
        print("Creating dummy model...")
        # This will be replaced with actual training in practice
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self.preprocessor = Pipeline([
            ('scaler', StandardScaler())
        ])
    
    def fetch_latest_bookings(self, limit: int = 10) -> List[Dict]:
        """
        Fetch the latest bookings from the API
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/bookings",
                params={"limit": limit}
            )
            response.raise_for_status()
            bookings = response.json()
            print(f"Fetched {len(bookings)} bookings from API")
            return bookings
        except requests.exceptions.RequestException as e:
            print(f"Error fetching bookings: {e}")
            return []

