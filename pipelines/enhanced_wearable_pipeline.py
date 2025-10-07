import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_models import WearableData, CalculatedBiomarker, CardiacBiomarkerType
from wearable_integration.fitbit_data import FitbitDataService

class EnhancedWearablePipeline:
    def __init__(self):
        self.fitbit_service = FitbitDataService()
    
    def sync_fitbit_data(self, days: int = 7):
        """Sync data from Fitbit for specified number of days"""
        all_data = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Get heart rate data
            hr_data = self.fitbit_service.get_heart_rate_intraday(date)
            if hr_data is not None:
                for _, row in hr_data.iterrows():
                    wearable_data = WearableData(
                        user_id="fitbit_user",
                        timestamp=row['datetime'],
                        heart_rate=row['value'],
                        source="fitbit"
                    )
                    all_data.append(wearable_data)
            
            # Get resting heart rate
            resting_hr = self.fitbit_service.get_resting_heart_rate(date)
            if resting_hr:
                biomarker = CalculatedBiomarker(
                    user_id="fitbit_user",
                    biomarker_type=CardiacBiomarkerType.RESTING_HR,
                    value=resting_hr,
                    timestamp=datetime.strptime(date, '%Y-%m-%d'),
                    metadata={"source": "fitbit"}
                )
                all_data.append(biomarker)
        
        return all_data
    
    def calculate_hrv_from_heart_rate(self, heart_rate_data: pd.DataFrame):
        """Calculate HRV from heart rate data (simplified)"""
        if heart_rate_data.empty:
            return None
            
        # Calculate RMSSD approximation from heart rate variability
        hr_values = heart_rate_data['heart_rate'].values
        differences = np.diff(hr_values)
        rmssd = np.sqrt(np.mean(differences**2))
        
        return rmssd