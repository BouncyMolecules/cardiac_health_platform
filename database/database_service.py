from sqlmodel import Session, select, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json

from config.database import get_session
from data_models.database_models import (
    Patient, WearableData, SymptomReport, CalculatedBiomarker, CardiacBiomarkerType
)

class DatabaseService:
    def __init__(self):
        self.session = next(get_session())
    
    # Patient CRUD Operations
    def create_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Create a new patient"""
        patient = Patient(**patient_data)
        self.session.add(patient)
        self.session.commit()
        self.session.refresh(patient)
        return patient
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        return self.session.get(Patient, patient_id)
    
    def get_all_patients(self) -> List[Patient]:
        """Get all patients"""
        statement = select(Patient).order_by(Patient.created_at.desc())
        return self.session.exec(statement).all()
    
    def update_patient(self, patient_id: str, update_data: Dict[str, Any]) -> Optional[Patient]:
        """Update patient data"""
        patient = self.get_patient(patient_id)
        if patient:
            for key, value in update_data.items():
                setattr(patient, key, value)
            self.session.commit()
            self.session.refresh(patient)
        return patient
    
    # Wearable Data Operations
    def add_wearable_data(self, wearable_data: Dict[str, Any]) -> WearableData:
        """Add wearable data record"""
        data = WearableData(**wearable_data)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def get_patient_wearable_data(
        self, 
        patient_id: str, 
        days: int = 7,
        metrics: Optional[List[str]] = None
    ) -> List[WearableData]:
        """Get wearable data for a patient"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        statement = select(WearableData).where(
            WearableData.patient_id == patient_id,
            WearableData.timestamp >= start_date
        ).order_by(WearableData.timestamp.desc())
        
        return self.session.exec(statement).all()
    
    # Symptom Report Operations
    def add_symptom_report(self, symptom_data: Dict[str, Any]) -> SymptomReport:
        """Add symptom report"""
        report = SymptomReport(**symptom_data)
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report
    
    def get_patient_symptom_reports(
        self, 
        patient_id: str, 
        days: int = 30
    ) -> List[SymptomReport]:
        """Get symptom reports for a patient"""
        start_date = date.today() - timedelta(days=days)
        
        statement = select(SymptomReport).where(
            SymptomReport.patient_id == patient_id,
            SymptomReport.report_date >= start_date  # CHANGED: from 'date' to 'report_date'
        ).order_by(desc(SymptomReport.report_date))  # CHANGED: from 'date' to 'report_date'
        
        return self.session.exec(statement).all()
    
    # Biomarker Operations
    def add_biomarker(self, biomarker_data: Dict[str, Any]) -> CalculatedBiomarker:
        """Add calculated biomarker"""
        biomarker = CalculatedBiomarker(**biomarker_data)
        self.session.add(biomarker)
        self.session.commit()
        self.session.refresh(biomarker)
        return biomarker
    
    def get_patient_biomarkers(
        self, 
        patient_id: str,
        biomarker_type: Optional[CardiacBiomarkerType] = None,
        days: int = 30
    ) -> List[CalculatedBiomarker]:
        """Get biomarkers for a patient"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        statement = select(CalculatedBiomarker).where(
            CalculatedBiomarker.patient_id == patient_id,
            CalculatedBiomarker.timestamp >= start_date
        )
        
        if biomarker_type:
            statement = statement.where(CalculatedBiomarker.biomarker_type == biomarker_type)
        
        statement = statement.order_by(desc(CalculatedBiomarker.timestamp))
        
        return self.session.exec(statement).all()
    
    # Analytics Queries
    def get_patient_health_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get health summary for dashboard"""
        # Latest resting heart rate
        latest_hr = self.session.exec(
            select(CalculatedBiomarker).where(
                CalculatedBiomarker.patient_id == patient_id,
                CalculatedBiomarker.biomarker_type == CardiacBiomarkerType.RESTING_HR
            ).order_by(desc(CalculatedBiomarker.timestamp)).limit(1)
        ).first()
        
        # Latest symptom report
        latest_symptoms = self.session.exec(
            select(SymptomReport).where(
                SymptomReport.patient_id == patient_id
            ).order_by(desc(SymptomReport.report_date)).limit(1)  # CHANGED: from 'date' to 'report_date'
        ).first()
        
        # Recent activity (last 7 days average steps)
        week_ago = datetime.utcnow() - timedelta(days=7)
        wearable_data = self.get_patient_wearable_data(patient_id, days=7)
        avg_steps = sum([d.steps or 0 for d in wearable_data]) / max(len(wearable_data), 1)
        
        return {
            "latest_heart_rate": latest_hr.value if latest_hr else None,
            "latest_symptoms": latest_symptoms,
            "recent_activity": avg_steps,
            "data_points_count": len(wearable_data)
        }