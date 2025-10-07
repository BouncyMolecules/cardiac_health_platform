Cardiac Health Platform - Multimodal Digital Biomarker Analysis

A comprehensive multimodal platform for cardiac health monitoring and digital biomarker analysis. This professional healthcare application integrates wearable data, clinical notes, and patient management into a single, powerful platform.

🌟 Features

❤️ Cardiac Biomarker Tracking

Heart Rate Variability (HRV) analysis with RMSSD and SDNN
Resting Heart Rate monitoring with trend analysis
Activity Levels and step tracking
Sleep Quality and duration monitoring
Symptom Tracking with standardized scoring

📊 Multimodal Data Integration

Fitbit API Integration - Real-time wearable data synchronization
Manual Data Entry - Flexible patient-reported outcomes
Clinical Documentation - SOAP notes and progress tracking
Multi-patient Management - Complete clinical workflow support

🎯 Advanced Analytics
Interactive Visualizations with Plotly

Calendar Heatmaps for activity patterns

Correlation Analysis between health metrics

Risk Assessment with clinical thresholds

Real-time Monitoring dashboards

🏥 Clinical Features
Patient Management with status tracking

Clinical Notes system with templates
Alert System for abnormal readings
Multi-clinician Support with role-based access
Comprehensive Reporting and data export

🚀 Quick Start

Prerequisites:

Python 3.9+
Fitbit Developer Account (for wearable integration)
Streamlit


Installation:

Clone the repository

bash
git clone https://github.com/yourusername/cardiac-health-platform.git
cd cardiac-health-platform

Create virtual environment

bash
python -m venv cardiac_env
source cardiac_env/bin/activate  # Windows: cardiac_env\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Configure Fitbit Integration

Register at Fitbit Developer Portal
Create a new application
Set redirect URI to http://localhost:8501
Create .streamlit/secrets.toml:

toml
FITBIT_CLIENT_ID = "your_client_id"
FITBIT_CLIENT_SECRET = "your_client_secret"

Run the application

bash
streamlit run app.py

📁 Project Structure


cardiac_health_platform/
├── app.py                          # Main Streamlit application
├── database/
│   ├── database_service.py         # Database operations
│   ├── clinical_service.py         # Clinical management
│   └── demo_data.py               # Sample data generator
├── data_models/
│   └── database_models.py          # SQLModel data schemas
├── config/
│   ├── settings.py                 # Application settings
│   └── fitbit_config.py           # Fitbit API configuration
├── wearable_integration/
│   ├── fitbit_auth.py             # OAuth authentication
│   └── fitbit_data.py             # Fitbit API service
├── visualizations/
│   ├── advanced_viz.py            # Advanced charts
│   └── viz_utils.py               # Visualization utilities
└── requirements.txt               # Python dependencies

🎨 Key Components

Patient Management
Complete patient profiles with medical history
Status tracking (Active, Inactive, High Risk)
Risk level assessment and monitoring
Appointment scheduling and clinical notes

Wearable Integration

Real-time Fitbit data synchronization
Automatic biomarker calculation
Historical data analysis
Data quality assessment
Analytics Dashboard
Multi-panel HRV analysis
Activity pattern recognition
Sleep quality assessment
Trend detection and alerts

Clinical Workflow

SOAP note templates
Progress tracking
Alert management
Reporting and exports

🔧 Configuration
Environment Setup
The platform uses SQLite by default (easy setup) but can be configured for PostgreSQL:

python

# In config/database.py

DATABASE_URL = "postgresql://user:password@localhost/cardiac_health"
Custom Biomarker Thresholds
Modify clinical thresholds in config/settings.py:


BIOMARKER_THRESHOLDS = {
    "resting_heart_rate": {
        "normal": [(60, 100)],
        "warning": [(50, 60), (100, 120)],
        "critical": [(0, 50), (120, 300)]
    }
}

💡 Usage Examples

Adding a New Patient
Navigate to "Patient Management"
Fill in demographic and clinical information
Assign to a clinician
Start monitoring biomarkers

Syncing Fitbit Data

Go to "Wearable Data" → "Fitbit Integration"
Select patient and click "Connect Fitbit Account"
Authorize through Fitbit OAuth
Sync historical and real-time data

Clinical Documentation

Access "Clinical Notes" in patient management
Use SOAP template (Subjective, Objective, Assessment, Plan)
Document vital signs and symptoms
Track treatment plans

🛠️ Development

Adding New Biomarkers
Extend CardiacBiomarkerType in data models
Add calculation logic in pipelines
Create visualization components
Update threshold configurations

Custom Data Sources

The platform is designed to be extensible. To add new wearable devices:
Create new service class in wearable_integration/
Implement data fetching and parsing
Map to existing data models
Add UI components in app.py

API Endpoints
While primarily a Streamlit app, the architecture supports API development:


# Example future FastAPI integration

@app.get("/api/patients/{patient_id}/biomarkers")
def get_biomarkers(patient_id: str, days: int = 30):
    return clinical_service.get_patient_biomarkers(patient_id, days)
📈 Deployment

Local Development
bash
streamlit run app.py
Production Deployment
The app can be deployed on:

Hugging Face Spaces
Streamlit Community Cloud
Heroku (with PostgreSQL)
AWS/Azure with containerization

Docker Setup
dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]

Development Setup:

Fork the repository
Create a feature branch

Make your changes

Add tests
Submit a pull request
Areas for Contribution
New wearable device integrations
Additional biomarker algorithms
Enhanced visualization components
Clinical guideline implementations
Multi-language support

📊 Research Applications

This platform can be used or extended to support digital health research by providing:

Standardized data collection across modalities
Longitudinal tracking of cardiac biomarkers
Clinical validation frameworks
Export capabilities for analysis
Privacy-preserving data handling

🏛️ Compliance
HIPAA Considerations
Patient data encryption at rest
Access controls and audit logging
Secure API communications
Data minimization principles

Data Privacy

Local data processing options
Anonymous analytics modes
Patient consent management
Data export and deletion tools


🙏 Acknowledgments

Fitbit API for wearable data integration
Streamlit for the amazing web framework
SQLModel for modern database operations
Plotly for interactive visualizations

🚀 Future Roadmap
Apple HealthKit integration
Machine learning risk prediction
Mobile app companion

EHR system integrations

Clinical trial module

Patient portal features
