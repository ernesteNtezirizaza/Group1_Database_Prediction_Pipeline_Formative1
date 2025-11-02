"""
Prediction Script for Hotel Booking Cancellations
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
