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
    
    def prepare_features(self, booking: Dict) -> np.ndarray:
        """
        Prepare features from booking data for ML prediction
        """
        # Select important features for cancellation prediction
        features = [
            booking.get('lead_time', 0),
            booking.get('arrival_date_year', 2015),
            booking.get('stays_in_weekend_nights', 0),
            booking.get('stays_in_week_nights', 0),
            booking.get('adults', 0),
            booking.get('children', 0),
            booking.get('babies', 0),
            booking.get('previous_cancellations', 0),
            booking.get('previous_bookings_not_canceled', 0),
            booking.get('booking_changes', 0),
            booking.get('days_in_waiting_list', 0),
            booking.get('adr', 0),
            booking.get('required_car_parking_spaces', 0),
            booking.get('total_of_special_requests', 0),
        ]
        
        # Add categorical encodings
        # Meal types (BB, HB, FB, SC, Undefined)
        meal_map = {'BB': 0, 'HB': 1, 'FB': 2, 'SC': 3, 'Undefined': 4}
        meal = booking.get('meal', 'BB')
        features.append(meal_map.get(meal, 4))
        
        # Deposit type
        deposit_map = {'No Deposit': 0, 'Non Refund': 1, 'Refundable': 2}
        deposit = booking.get('deposit_type', 'No Deposit')
        features.append(deposit_map.get(deposit, 0))
        
        # Convert to numpy array
        feature_array = np.array(features).reshape(1, -1)
        
        # Handle missing values
        feature_array = np.nan_to_num(feature_array, nan=0.0, posinf=0.0, neginf=0.0)
        
        return feature_array
    
    def predict(self, booking: Dict) -> Dict:
        """
        Make prediction on a single booking
        """
        try:
            # Prepare features
            features = self.prepare_features(booking)
            
            # Preprocess if preprocessor exists
            if self.preprocessor:
                try:
                    features = self.preprocessor.transform(features)
                except:
                    # If preprocessing fails, use original features
                    pass
            
            # Make prediction
            if self.model:
                prediction = self.model.predict(features)[0]
                probability = self.model.predict_proba(features)[0]
                
                return {
                    'booking_id': booking.get('booking_id'),
                    'predicted_canceled': bool(prediction),
                    'cancellation_probability': float(max(probability)),
                    'not_cancelled_probability': float(min(probability)),
                    'features_used': len(features[0]),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return dummy prediction if no model
                return {
                    'booking_id': booking.get('booking_id'),
                    'predicted_canceled': False,
                    'cancellation_probability': 0.3,
                    'not_cancelled_probability': 0.7,
                    'features_used': len(features[0]),
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Dummy prediction - no trained model available'
                }
        except Exception as e:
            print(f"Error making prediction: {e}")
            return {
                'booking_id': booking.get('booking_id'),
                'error': str(e)
            }

