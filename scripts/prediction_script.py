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
import pymysql
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Model configuration
MODEL_PATH = 'models/cancellation_model.pkl'
PREPROCESSOR_PATH = 'models/feature_preprocessor.pkl'


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
    
    def log_prediction_to_db(self, booking_id: int, prediction: Dict):
        """
        Log prediction result to both MySQL and MongoDB databases
        """
        try:
            # Log to MySQL
            self._log_to_mysql(booking_id, prediction)
            
            # Log to MongoDB
            self._log_to_mongodb(booking_id, prediction)
            
            print(f"\nPrediction logged for booking {booking_id}:")
            print(f"  Cancellation probability: {prediction.get('cancellation_probability', 0):.2%}")
            print(f"  Predicted outcome: {'Will Cancel' if prediction.get('predicted_canceled') else 'Will NOT Cancel'}")
            
        except Exception as e:
            print(f"Error logging prediction: {e}")
    
    def _log_to_mysql(self, booking_id: int, prediction: Dict):
        """Save prediction to MySQL database"""
        connection = None
        try:
            # MySQL configuration
            mysql_config = {
                'host': os.getenv('MYSQL_HOST'),
                'user': os.getenv('MYSQL_USER'),
                'password': os.getenv('MYSQL_PASSWORD'),
                'database': os.getenv('MYSQL_DATABASE'),
                'charset': 'utf8mb4',
                'autocommit': True
            }
            
            # Add port if provided
            if os.getenv('MYSQL_PORT'):
                mysql_config['port'] = int(os.getenv('MYSQL_PORT'))
            
            # Add SSL if required
            if os.getenv('MYSQL_SSL', '').lower() == 'true':
                mysql_config['ssl'] = {'check_hostname': False}
            
            connection = pymysql.connect(**mysql_config)
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO predictions (
                    booking_id, predicted_canceled, cancellation_probability,
                    not_cancelled_probability, features_used, model_version, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                booking_id,
                prediction.get('predicted_canceled', False),
                float(prediction.get('cancellation_probability', 0)),
                float(prediction.get('not_cancelled_probability', 0)),
                prediction.get('features_used', 0),
                prediction.get('model_version', None),
                prediction.get('note', None)
            )
            
            cursor.execute(insert_query, values)
            print(f"  ✓ Saved to MySQL (prediction_id: {cursor.lastrowid})")
            
        except Exception as e:
            print(f"  ✗ MySQL save failed: {e}")
        finally:
            if connection:
                connection.close()
    
    def _log_to_mongodb(self, booking_id: int, prediction: Dict):
        """Save prediction to MongoDB database"""
        try:
            # MongoDB configuration
            mongo_uri = os.getenv('MONGO_URI')
            if not mongo_uri:
                mongo_host = os.getenv('MONGO_HOST', 'localhost')
                mongo_port = int(os.getenv('MONGO_PORT', 27017))
                mongo_uri = f"mongodb://{mongo_host}:{mongo_port}"
            
            mongo_database = os.getenv('MONGO_DATABASE', 'hotel_booking_db')
            
            client = MongoClient(mongo_uri)
            db = client[mongo_database]
            predictions_collection = db['predictions']
            
            # Create prediction document
            prediction_doc = {
                'booking_id': booking_id,
                'predicted_canceled': prediction.get('predicted_canceled', False),
                'cancellation_probability': float(prediction.get('cancellation_probability', 0)),
                'not_cancelled_probability': float(prediction.get('not_cancelled_probability', 0)),
                'features_used': prediction.get('features_used', 0),
                'model_version': prediction.get('model_version', None),
                'metadata': {
                    'created_at': datetime.now(),
                    'notes': prediction.get('note', None)
                }
            }
            
            result = predictions_collection.insert_one(prediction_doc)
            print(f"  ✓ Saved to MongoDB (id: {result.inserted_id})")
            
            client.close()
            
        except Exception as e:
            print(f"  ✗ MongoDB save failed: {e}")
    
    def batch_predict(self, bookings: List[Dict]) -> List[Dict]:
        """
        Make predictions on multiple bookings
        """
        results = []
        for booking in bookings:
            prediction = self.predict(booking)
            results.append(prediction)
            
            # Log to database
            if 'booking_id' in prediction:
                self.log_prediction_to_db(prediction['booking_id'], prediction)
        
        return results
    
    def save_predictions(self, predictions: List[Dict], filename: str = None):
        """
        Save predictions to JSON file
        """
        if filename is None:
            filename = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        print(f"\nPredictions saved to {filename}")


def train_model_from_api_data(api_url: str = API_BASE_URL, output_path: str = MODEL_PATH):
    """
    Train a model using data from the API
    This function would be called to create the initial model
    """
    try:
        print("\nFetching training data from API...")
        response = requests.get(f"{api_url}/api/v1/bookings", params={"limit": 1000})
        response.raise_for_status()
        bookings = response.json()
        
        if len(bookings) == 0:
            print("No booking data available for training")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(bookings)
        
        # Prepare features and target
        predictor = BookingPredictor(api_url)
        
        X = []
        y = []
        for booking in bookings:
            try:
                features = predictor.prepare_features(booking)
                X.append(features[0])
                y.append(booking.get('is_canceled', False))
            except:
                continue
        
        if len(X) == 0:
            print("Could not prepare features for training")
            return
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        print("\nTraining model...")
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        
        model = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10))
        ])
        
        model.fit(X, y)
        
        # Save model
        joblib.dump(model, output_path)
        print(f"\nModel trained and saved to {output_path}")
        
        # Evaluate
        score = model.score(X, y)
        print(f"Model accuracy on training data: {score:.2%}")
        
    except Exception as e:
        print(f"Error training model: {e}")


def main():
    """
    Main function to run predictions
    """
    print("=" * 60)
    print("Hotel Booking Cancellation Prediction System")
    print("=" * 60)
    
    # Initialize predictor
    predictor = BookingPredictor()
    
    # Option 1: Train model if needed
    if not os.path.exists(MODEL_PATH):
        print("\nNo trained model found. Would you like to train one? (y/n)")
        # For automated execution, skip training
        # train_model_from_api_data()
        print("Skipping training for demo purposes")
    
    # Fetch latest bookings
    print("\nFetching latest bookings from API...")
    bookings = predictor.fetch_latest_bookings(limit=10)
    
    if not bookings:
        print("No bookings found. Please ensure the API is running and has data.")
        return
    
    # Make predictions
    print(f"\nMaking predictions for {len(bookings)} bookings...")
    predictions = predictor.batch_predict(bookings)
    
    # Display summary
    print("\n" + "=" * 60)
    print("Prediction Summary")
    print("=" * 60)
    
    total_cancellations = sum(1 for p in predictions if p.get('predicted_canceled'))
    avg_probability = np.mean([p.get('cancellation_probability', 0) for p in predictions])
    
    print(f"Total bookings analyzed: {len(predictions)}")
    print(f"Predicted cancellations: {total_cancellations}")
    print(f"Average cancellation probability: {avg_probability:.2%}")
    
    # Save predictions
    predictor.save_predictions(predictions)
    
    print("\nPrediction process completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
