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
