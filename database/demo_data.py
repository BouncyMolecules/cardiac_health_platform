from sqlmodel import Session, select
from datetime import datetime, timedelta, date
import random
from config.database import get_session
from data_models.database_models import *

def create_demo_clinical_data():
    """Create demo data for testing multi-patient features"""
    session = next(get_session())
    
    # Create demo clinician
    clinician = User(
        id="demo_clinician_001",
        username="dr_smith",
        email="dr.smith@cardiacclinic.com",
        hashed_password="demo_hash",
        role=UserRole.CLINICIAN,
        first_name="John",
        last_name="Smith",
        specialization="Cardiology"
    )
    
    try:
        session.add(clinician)
        session.commit()
    except:
        session.rollback()
        print("Clinician already exists")
    
    # Create demo patients if they don't exist
    demo_patients = [
        {
            "first_name": "Maria",
            "last_name": "Garcia",
            "date_of_birth": date(1965, 3, 15),
            "gender": "female",
            "primary_condition": "Heart Failure",
            "risk_level": "high",
            "status": PatientStatus.ACTIVE
        },
        {
            "first_name": "David",
            "last_name": "Chen",
            "date_of_birth": date(1978, 7, 22),
            "gender": "male", 
            "primary_condition": "Hypertension",
            "risk_level": "medium",
            "status": PatientStatus.ACTIVE
        },
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "date_of_birth": date(1952, 11, 8),
            "gender": "female",
            "primary_condition": "Arrhythmia",
            "risk_level": "low",
            "status": PatientStatus.ACTIVE
        }
    ]
    
    for patient_data in demo_patients:
        # Check if patient exists
        existing = session.exec(
            select(Patient).where(
                Patient.first_name == patient_data["first_name"],
                Patient.last_name == patient_data["last_name"]
            )
        ).first()
        
        if not existing:
            patient = Patient(**patient_data)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            
            # Assign to clinician
            assignment = ClinicianPatient(
                clinician_id="demo_clinician_001",
                patient_id=patient.id,
                is_primary=True
            )
            session.add(assignment)
            session.commit()
    
    # Create some demo alerts
    patients = session.exec(select(Patient)).all()
    
    for patient in patients[:2]:
        alert = PatientAlert(
            patient_id=patient.id,
            alert_type=AlertType.HIGH_HEART_RATE,
            severity="high",
            title="Elevated Resting Heart Rate",
            description=f"Patient's average resting heart rate has increased by 15% over the past week.",
            trigger_value=85,
            normal_range="60-100 bpm"
        )
        session.add(alert)
    
    session.commit()
    print("Demo clinical data created successfully!")

if __name__ == "__main__":
    create_demo_clinical_data()