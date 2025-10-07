from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, date as date_type
from enum import Enum as PyEnum
import uuid
from sqlalchemy import Column, String, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

class Gender(str, PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class UserRole(str, PyEnum):
    ADMIN = "admin"
    CLINICIAN = "clinician"
    PATIENT = "patient"
    RESEARCHER = "researcher"

class PatientStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    HIGH_RISK = "high_risk"

class CardiacBiomarkerType(str, PyEnum):
    RESTING_HR = "resting_heart_rate"
    HRV_RMSSD = "hrv_rmssd"
    HRV_SDNN = "hrv_sdnn"
    HR_RECOVERY = "heart_rate_recovery"
    ACTIVITY_LEVEL = "activity_level"
    SLEEP_DURATION = "sleep_duration"
    WEIGHT_TREND = "weight_trend"
    SYMPTOM_REPORT = "symptom_report"

class AlertType(str, PyEnum):
    HIGH_HEART_RATE = "high_heart_rate"
    LOW_HRV = "low_hrv"
    SYMPTOM_DETERIORATION = "symptom_deterioration"
    MISSING_DATA = "missing_data"
    WEIGHT_INCREASE = "weight_increase"

# User model for authentication and roles
class User(SQLModel, table=True):
    """User accounts for platform access"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Authentication
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    role: UserRole = Field(default=UserRole.CLINICIAN)
    is_active: bool = Field(default=True)
    
    # Profile
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    specialization: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships
    clinician_patients: List["ClinicianPatient"] = Relationship(back_populates="clinician")
    created_patients: List["Patient"] = Relationship(back_populates="created_by")
    clinical_notes: List["ClinicalNote"] = Relationship(back_populates="clinician")

# Consolidated Patient model with clinical fields
class Patient(SQLModel, table=True):
    """Enhanced patient model with clinical management"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        index=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Patient demographics
    first_name: str = Field(max_length=100, index=True)
    last_name: str = Field(max_length=100, index=True)
    date_of_birth: date_type
    gender: str = Field(max_length=20)
    
    # Contact information
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    emergency_contact: Optional[str] = Field(default=None)
    emergency_phone: Optional[str] = Field(default=None)
    
    # Clinical information
    primary_condition: Optional[str] = Field(default=None, max_length=255)
    secondary_conditions: Optional[str] = Field(default=None)
    medications: Optional[str] = Field(default=None)
    allergies: Optional[str] = Field(default=None)
    baseline_heart_rate: Optional[float] = Field(default=None)
    baseline_hrv: Optional[float] = Field(default=None)
    
    # Management fields
    status: PatientStatus = Field(default=PatientStatus.ACTIVE)
    risk_level: Optional[str] = Field(default=None)  # low, medium, high
    last_review_date: Optional[date_type] = Field(default=None)
    next_appointment: Optional[date_type] = Field(default=None)
    clinical_notes: Optional[str] = Field(default=None)
    
    # Relationships
    created_by_id: Optional[str] = Field(default=None, foreign_key="user.id")
    created_by: Optional[User] = Relationship(back_populates="created_patients")
    clinician_relationships: List["ClinicianPatient"] = Relationship(back_populates="patient")
    wearable_data: List["WearableData"] = Relationship(back_populates="patient")
    symptom_reports: List["SymptomReport"] = Relationship(back_populates="patient")
    biomarkers: List["CalculatedBiomarker"] = Relationship(back_populates="patient")
    clinical_notes_list: List["ClinicalNote"] = Relationship(back_populates="patient")
    alerts: List["PatientAlert"] = Relationship(back_populates="patient")

class ClinicianPatient(SQLModel, table=True):
    """Many-to-many relationship between clinicians and patients"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    clinician_id: str = Field(foreign_key="user.id")
    patient_id: str = Field(foreign_key="patient.id")
    assigned_date: datetime = Field(default_factory=datetime.utcnow)
    is_primary: bool = Field(default=True)
    notes: Optional[str] = Field(default=None)
    
    # Relationships
    clinician: User = Relationship(back_populates="clinician_patients")
    patient: Patient = Relationship(back_populates="clinician_relationships")

class WearableData(SQLModel, table=True):
    """Wearable device data table"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    timestamp: datetime = Field(index=True)
    patient_id: str = Field(foreign_key="patient.id", index=True)
    
    # Wearable metrics
    heart_rate: Optional[float] = Field(default=None, ge=0, le=300)
    hrv_rmssd: Optional[float] = Field(default=None, ge=0)
    hrv_sdnn: Optional[float] = Field(default=None, ge=0)
    steps: Optional[int] = Field(default=None, ge=0)
    calories: Optional[float] = Field(default=None, ge=0)
    sleep_minutes: Optional[float] = Field(default=None, ge=0)
    spo2: Optional[float] = Field(default=None, ge=0, le=100)
    stress_level: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Metadata
    source: str = Field(default="wearable", max_length=50)
    device_type: Optional[str] = Field(default=None, max_length=100)
    data_quality: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Relationship
    patient: Patient = Relationship(back_populates="wearable_data")

class SymptomReport(SQLModel, table=True):
    """Patient-reported symptoms table"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    report_date: date_type = Field(index=True)
    patient_id: str = Field(foreign_key="patient.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Symptom scores (0-10 scale)
    shortness_of_breath: int = Field(default=0, ge=0, le=10)
    fatigue_level: int = Field(default=0, ge=0, le=10)
    chest_discomfort: bool = Field(default=False)
    swelling_feet: bool = Field(default=False)
    dizziness: bool = Field(default=False)
    palpitations: bool = Field(default=False)
    
    # Clinical measurements
    weight_kg: Optional[float] = Field(default=None, ge=0)
    systolic_bp: Optional[int] = Field(default=None, ge=0, le=300)
    diastolic_bp: Optional[int] = Field(default=None, ge=0, le=200)
    temperature: Optional[float] = Field(default=None, ge=30, le=45)
    
    # Medication adherence
    medication_taken: bool = Field(default=True)
    medication_notes: Optional[str] = Field(default=None)
    
    # Additional notes
    notes: Optional[str] = Field(default=None)
    
    # Relationship
    patient: Patient = Relationship(back_populates="symptom_reports")

class CalculatedBiomarker(SQLModel, table=True):
    """Calculated biomarker values table"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    patient_id: str = Field(foreign_key="patient.id", index=True)
    
    # Biomarker data
    biomarker_type: CardiacBiomarkerType = Field(index=True)
    value: float = Field()
    unit: str = Field(default="", max_length=20)
    confidence: float = Field(default=1.0, ge=0, le=1)
    
    # Metadata
    calculation_method: Optional[str] = Field(default=None, max_length=100)
    source_data_ids: Optional[str] = Field(default=None)
    biomarker_metadata: Optional[str] = Field(default=None)
    
    # Relationship
    patient: Patient = Relationship(back_populates="biomarkers")

class ClinicalNote(SQLModel, table=True):
    """Clinical notes for patient encounters"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    patient_id: str = Field(foreign_key="patient.id")
    clinician_id: str = Field(foreign_key="user.id")
    
    # Note content
    note_type: str = Field(default="progress", max_length=50)
    subjective: Optional[str] = Field(default=None)
    objective: Optional[str] = Field(default=None)
    assessment: Optional[str] = Field(default=None)
    plan: Optional[str] = Field(default=None)
    vital_signs: Optional[str] = Field(default=None)
    
    # Relationships
    patient: Patient = Relationship(back_populates="clinical_notes_list")
    clinician: User = Relationship(back_populates="clinical_notes")

class PatientAlert(SQLModel, table=True):
    """Alert system for patient monitoring"""
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    patient_id: str = Field(foreign_key="patient.id")
    
    # Alert details
    alert_type: AlertType
    severity: str = Field(default="medium")
    title: str = Field(max_length=255)
    description: str
    is_resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by: Optional[str] = Field(default=None)
    resolution_notes: Optional[str] = Field(default=None)
    
    # Alert data
    trigger_value: Optional[float] = Field(default=None)
    normal_range: Optional[str] = Field(default=None)
    relevant_data_ids: Optional[str] = Field(default=None)
    
    # Relationship
    patient: Patient = Relationship(back_populates="alerts")