from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class FitbitHeartRateData(BaseModel):
    datetime: datetime
    heart_rate: int
    confidence: Optional[int] = None

class FitbitSleepData(BaseModel):
    date: str
    duration: int  # in minutes
    efficiency: int
    stages: Dict[str, int]  # deep, light, rem, wake
    resting_heart_rate: Optional[int] = None

class FitbitActivitySummary(BaseModel):
    steps: int
    calories_out: float
    active_minutes: int
    sedentary_minutes: int
    distance: float