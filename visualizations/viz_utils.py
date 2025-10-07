import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

def prepare_hrv_data(wearable_data: List) -> pd.DataFrame:
    """Prepare HRV data for visualization"""
    if not wearable_data:
        return pd.DataFrame()
    
    data_points = []
    for data in wearable_data:
        if data.hrv_rmssd:
            data_points.append({
                'date': data.timestamp.date(),
                'hrv': data.hrv_rmssd,
                'heart_rate': data.heart_rate,
                'activity': data.steps or 0
            })
    
    return pd.DataFrame(data_points)

def prepare_sleep_data(sleep_reports: List) -> pd.DataFrame:
    """Prepare sleep data for visualization"""
    if not sleep_reports:
        return pd.DataFrame()
    
    data_points = []
    for report in sleep_reports:
        data_points.append({
            'date': report.report_date,
            'duration': report.sleep_minutes or 0,
            'efficiency': min(100, (report.sleep_minutes or 0) / 480 * 100),  # Assume 8h ideal
            'quality': report.sleep_quality or 0
        })
    
    return pd.DataFrame(data_points)

def prepare_biomarker_data(biomarkers: List) -> Dict[str, pd.DataFrame]:
    """Prepare biomarker data for comparison visualization"""
    biomarker_dict = {}
    
    for biomarker in biomarkers:
        if biomarker.biomarker_type not in biomarker_dict:
            biomarker_dict[biomarker.biomarker_type] = []
        
        biomarker_dict[biomarker.biomarker_type].append({
            'date': biomarker.timestamp.date(),
            'value': biomarker.value
        })
    
    # Convert to DataFrames
    return {name: pd.DataFrame(data) for name, data in biomarker_dict.items()}

def generate_sample_real_time_data(hours: int = 24) -> pd.DataFrame:
    """Generate sample real-time data for demonstration"""
    base_time = datetime.now()
    data_points = []
    
    for i in range(hours * 12):  # 5-minute intervals
        timestamp = base_time - timedelta(minutes=i * 5)
        
        # Simulate heart rate data
        base_hr = 65 + 10 * np.sin(i / 20) + np.random.normal(0, 3)
        data_points.append({
            'timestamp': timestamp,
            'metric': 'heart_rate',
            'value': max(40, min(120, base_hr))
        })
        
        # Simulate HRV data
        base_hrv = 45 + 15 * np.sin(i / 30) + np.random.normal(0, 5)
        data_points.append({
            'timestamp': timestamp,
            'metric': 'hrv',
            'value': max(10, min(100, base_hrv))
        })
        
        # Simulate activity data (every hour)
        if i % 12 == 0:
            data_points.append({
                'timestamp': timestamp,
                'metric': 'activity',
                'value': np.random.poisson(50)
            })
    
    return pd.DataFrame(data_points)