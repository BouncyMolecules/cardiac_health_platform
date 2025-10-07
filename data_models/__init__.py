from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class CardiacBiomarkerType(str, Enum):
    RESTING_HR = "resting_heart_rate"
    HRV_RMSSD = "hrv_rmssd"
    HRV_SDNN = "hrv_sdnn"
    HR_RECOVERY = "heart_rate_recovery"
    ACTIVITY_LEVEL = "activity_level"
    SLEEP_DURATION = "sleep_duration"
    WEIGHT_TREND = "weight_trend"
    SYMPTOM_REPORT = "symptom_report"

class WearableData(BaseModel):
    user_id: str
    timestamp: datetime
    heart_rate: Optional[float] = Field(..., ge=0, le=200)
    hrv_rmssd: Optional[float] = None
    hrv_sdnn: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[float] = None
    sleep_minutes: Optional[float] = None
    source: str = "wearable"  # fitbit, apple_watch, etc.

class SymptomReport(BaseModel):
    user_id: str
    date: date
    shortness_of_breath: int = Field(..., ge=0, le=10)  # 0-10 scale
    fatigue_level: int = Field(..., ge=0, le=10)
    chest_discomfort: bool = False
    swelling_feet: bool = False
    weight_kg: Optional[float] = None
    medication_taken: bool = True
    notes: Optional[str] = None

class CalculatedBiomarker(BaseModel):
    user_id: str
    biomarker_type: CardiacBiomarkerType
    value: float
    timestamp: datetime
    confidence: float = 1.0
    metadata: Dict[str, Any] = {}