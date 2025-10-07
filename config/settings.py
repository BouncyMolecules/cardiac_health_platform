import os
from typing import Dict, Any, List, Tuple

class Settings:
    # App Configuration
    APP_NAME = "Cardiac Health Platform"
    VERSION = "1.0.0"
    
    # Data Storage
    DATA_PATH = "./data"
    RAW_DATA_PATH = os.path.join(DATA_PATH, "raw")
    PROCESSED_DATA_PATH = os.path.join(DATA_PATH, "processed")
    
    # Biomarker Thresholds (FIXED - using lists of tuples)
    BIOMARKER_THRESHOLDS = {
        "resting_heart_rate": {
            "normal": [(60, 100)],
            "warning": [(50, 60), (100, 120)],  # Multiple ranges in a list
            "critical": [(0, 50), (120, 300)]
        },
        "hrv_rmssd": {
            "normal": [(30, 100)],
            "low": [(0, 30)],
            "high": [(100, 300)]
        },
        "heart_rate_recovery": {
            "good": [(18, 50)],
            "poor": [(0, 18)]
        }
    }
    
    # Streamlit Config
    STREAMLIT_CONFIG = {
        "page_title": "Cardiac Health Dashboard",
        "page_icon": "❤️",
        "layout": "wide"
    }

settings = Settings()