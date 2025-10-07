import os
import streamlit as st
from typing import Optional

class FitbitConfig:
    # Get credentials from Streamlit secrets instead of environment variables
    CLIENT_ID = st.secrets.get("FITBIT_CLIENT_ID", "YOUR_CLIENT_ID")
    CLIENT_SECRET = st.secrets.get("FITBIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
    REDIRECT_URI = 'http://localhost:8501'
    
    # API Endpoints
    API_BASE_URL = "https://api.fitbit.com"
    AUTHORIZE_URL = f"{API_BASE_URL}/oauth2/authorize"
    TOKEN_URL = f"{API_BASE_URL}/oauth2/token"
    
    # Scopes for cardiac data
    SCOPES = [
        "activity",
        "heartrate",
        "sleep",
        "profile",
        "weight"
    ]

fitbit_config = FitbitConfig()