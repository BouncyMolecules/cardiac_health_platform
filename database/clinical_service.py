from sqlmodel import Session, select, desc, and_, or_
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import json

from config.database import get_session
from data_models.database_models import *  # Now all models are here

class ClinicalService:
    def __init__(self):
        self.session = next(get_session())
    
    # Patient Management Methods
    def get_patients_by_clinician(self, clinician_id: str, include_inactive: bool = False) -> List[Patient]:
        """Get all patients assigned to a clinician"""
        statement = select(Patient).join(ClinicianPatient).where(
            ClinicianPatient.clinician_id == clinician_id
        )
        
        if not include_inactive:
            statement = statement.where(Patient.status == PatientStatus.ACTIVE)
        
        return self.session.exec(statement.order_by(desc(Patient.created_at))).all()
    
    def assign_patient_to_clinician(self, patient_id: str, clinician_id: str, is_primary: bool = True) -> ClinicianPatient:
        """Assign a patient to a clinician"""
        assignment = ClinicianPatient(
            clinician_id=clinician_id,
            patient_id=patient_id,
            is_primary=is_primary
        )
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment
    
    def update_patient_status(self, patient_id: str, status: PatientStatus, risk_level: Optional[str] = None) -> Patient:
        """Update patient status and risk level"""
        patient = self.session.get(Patient, patient_id)
        if patient:
            patient.status = status
            if risk_level:
                patient.risk_level = risk_level
            patient.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(patient)
        return patient
    
    def search_patients(self, query: str, clinician_id: Optional[str] = None) -> List[Patient]:
        """Search patients by name, condition, or other criteria"""
        search_term = f"%{query}%"
        
        if clinician_id:
            statement = select(Patient).join(ClinicianPatient).where(
                ClinicianPatient.clinician_id == clinician_id,
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.primary_condition.ilike(search_term),
                    Patient.email.ilike(search_term)
                )
            )
        else:
            statement = select(Patient).where(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.primary_condition.ilike(search_term),
                    Patient.email.ilike(search_term)
                )
            )
        
        return self.session.exec(statement.order_by(desc(Patient.created_at))).all()
    
    # Clinical Notes Methods
    def add_clinical_note(self, note_data: Dict[str, Any]) -> ClinicalNote:
        """Add a clinical note for a patient"""
        note = ClinicalNote(**note_data)
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note
    
    def get_patient_notes(self, patient_id: str, limit: int = 50) -> List[ClinicalNote]:
        """Get clinical notes for a patient"""
        statement = select(ClinicalNote).where(
            ClinicalNote.patient_id == patient_id
        ).order_by(desc(ClinicalNote.created_at)).limit(limit)
        
        return self.session.exec(statement).all()
    
    # Alert Management Methods
    def create_alert(self, alert_data: Dict[str, Any]) -> PatientAlert:
        """Create a new patient alert"""
        alert = PatientAlert(**alert_data)
        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        return alert
    
    def get_active_alerts(self, clinician_id: Optional[str] = None) -> List[PatientAlert]:
        """Get all active (unresolved) alerts"""
        if clinician_id:
            statement = select(PatientAlert).join(Patient).join(ClinicianPatient).where(
                ClinicianPatient.clinician_id == clinician_id,
                PatientAlert.is_resolved == False
            )
        else:
            statement = select(PatientAlert).where(
                PatientAlert.is_resolved == False
            )
        
        return self.session.exec(statement.order_by(desc(PatientAlert.created_at))).all()
    
    def resolve_alert(self, alert_id: str, resolved_by: str, notes: Optional[str] = None) -> PatientAlert:
        """Mark an alert as resolved"""
        alert = self.session.get(PatientAlert, alert_id)
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by
            alert.resolution_notes = notes
            self.session.commit()
            self.session.refresh(alert)
        return alert
    
    # Analytics for Multi-Patient Management
    def get_clinician_dashboard_stats(self, clinician_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for a clinician"""
        # Get assigned patients
        patients = self.get_patients_by_clinician(clinician_id)
        
        # Count by status
        status_counts = {}
        risk_counts = {}
        for patient in patients:
            status_counts[patient.status] = status_counts.get(patient.status, 0) + 1
            if patient.risk_level:
                risk_counts[patient.risk_level] = risk_counts.get(patient.risk_level, 0) + 1
        
        # Active alerts
        active_alerts = self.get_active_alerts(clinician_id)
        
        # Recent data activity
        recent_activity = 0
        week_ago = datetime.utcnow() - timedelta(days=7)
        for patient in patients:
            wearable_data = self.session.exec(
                select(WearableData).where(
                    WearableData.patient_id == patient.id,
                    WearableData.timestamp >= week_ago
                )
            ).all()
            recent_activity += len(wearable_data)
        
        return {
            "total_patients": len(patients),
            "status_counts": status_counts,
            "risk_counts": risk_counts,
            "active_alerts": len(active_alerts),
            "recent_data_points": recent_activity,
            "high_risk_patients": risk_counts.get("high", 0)
        }
    
    def generate_patient_report(self, patient_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive patient report"""
        patient = self.session.get(Patient, patient_id)
        if not patient:
            return {}
        
        # Get recent data
        start_date = datetime.utcnow() - timedelta(days=days)
        
        wearable_data = self.session.exec(
            select(WearableData).where(
                WearableData.patient_id == patient_id,
                WearableData.timestamp >= start_date
            )
        ).all()
        
        symptom_reports = self.session.exec(
            select(SymptomReport).where(
                SymptomReport.patient_id == patient_id,
                SymptomReport.report_date >= start_date.date()
            )
        ).all()
        
        biomarkers = self.session.exec(
            select(CalculatedBiomarker).where(
                CalculatedBiomarker.patient_id == patient_id,
                CalculatedBiomarker.timestamp >= start_date
            )
        ).all()
        
        clinical_notes = self.get_patient_notes(patient_id, limit=10)
        
        # Calculate metrics
        avg_heart_rate = None
        avg_hrv = None
        if wearable_data:
            hr_values = [d.heart_rate for d in wearable_data if d.heart_rate]
            hrv_values = [d.hrv_rmssd for d in wearable_data if d.hrv_rmssd]
            avg_heart_rate = sum(hr_values) / len(hr_values) if hr_values else None
            avg_hrv = sum(hrv_values) / len(hrv_values) if hrv_values else None
        
        return {
            "patient": patient,
            "summary": {
                "monitoring_period_days": days,
                "data_points": len(wearable_data),
                "symptom_reports": len(symptom_reports),
                "average_heart_rate": avg_heart_rate,
                "average_hrv": avg_hrv,
                "clinical_notes": len(clinical_notes)
            },
            "recent_notes": clinical_notes,
            "alerts": self.session.exec(
                select(PatientAlert).where(
                    PatientAlert.patient_id == patient_id,
                    PatientAlert.created_at >= start_date
                )
            ).all()
        }