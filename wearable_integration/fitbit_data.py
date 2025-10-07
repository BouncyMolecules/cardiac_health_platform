import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import requests
from wearable_integration.fitbit_auth import FitbitAuth

class FitbitDataService:
    def __init__(self):
        self.auth = FitbitAuth()
        self.base_url = "https://api.fitbit.com/1/user/-"
    
    def make_api_call(self, endpoint):
        """Make API call to Fitbit with error handling"""
        headers = self.auth.get_headers()
        if not headers:
            st.error("Not authenticated with Fitbit")
            return None
            
        try:
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                st.error("Authentication expired. Please reconnect your Fitbit account.")
                return None
            elif response.status_code == 429:
                st.error("Rate limit exceeded. Please try again later.")
                return None
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Network error: {e}")
            return None
    
    def get_heart_rate_intraday(self, date: str = "today", detail_level: str = "1min"):
        """Get real intraday heart rate data from Fitbit"""
        endpoint = f"/activities/heart/date/{date}/1d/{detail_level}.json"
        data = self.make_api_call(endpoint)
        
        if data:
            return self._parse_heart_rate_data(data)
        return None
    
    def get_resting_heart_rate(self, date: str = "today"):
        """Get real resting heart rate from Fitbit"""
        endpoint = f"/activities/heart/date/{date}/1d.json"
        data = self.make_api_call(endpoint)
        
        if data and 'activities-heart' in data and len(data['activities-heart']) > 0:
            return data['activities-heart'][0]['value'].get('restingHeartRate')
        return None
    
    def get_sleep_data(self, date: str = "today"):
        """Get real sleep data from Fitbit"""
        endpoint = f"/sleep/date/{date}.json"
        return self.make_api_call(endpoint)
    
    def get_activity_summary(self, date: str = "today"):
        """Get real activity summary from Fitbit"""
        endpoint = f"/activities/date/{date}.json"
        return self.make_api_call(endpoint)
    
    def get_profile(self):
        """Get user profile from Fitbit"""
        endpoint = "/profile.json"
        return self.make_api_call(endpoint)
    
    def get_devices(self):
        """Get connected Fitbit devices"""
        endpoint = "/devices.json"
        return self.make_api_call(endpoint)
    
    def _parse_heart_rate_data(self, data):
        """Parse real Fitbit heart rate data"""
        try:
            if 'activities-heart-intraday' in data and 'dataset' in data['activities-heart-intraday']:
                intraday_data = data['activities-heart-intraday']['dataset']
                df = pd.DataFrame(intraday_data)
                
                if not df.empty and 'activities-heart' in data and len(data['activities-heart']) > 0:
                    date_str = data['activities-heart'][0]['dateTime']
                    df['datetime'] = pd.to_datetime(f"{date_str} " + df['time'])
                    return df
                    
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error parsing heart rate data: {e}")
            return pd.DataFrame()