import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import sys
import os
import uuid

# Add new imports
from database.clinical_service import ClinicalService
from data_models.database_models import Patient, Gender, CardiacBiomarkerType, PatientStatus, AlertType, ClinicalNote, UserRole

def show_clinician_dashboard():
    st.header("👨‍⚕️ Clinician Dashboard")
    
    clinical_service = ClinicalService()
    db_service = DatabaseService()
    
    # For demo purposes, we'll use a mock clinician ID
    # In a real app, this would come from authentication
    clinician_id = "demo_clinician_001"
    
    # Get dashboard statistics
    stats = clinical_service.get_clinician_dashboard_stats(clinician_id)
    
    # Overview metrics
    st.subheader("Practice Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", stats["total_patients"])
    
    with col2:
        st.metric("Active Alerts", stats["active_alerts"])
    
    with col3:
        st.metric("High Risk Patients", stats["high_risk_patients"])
    
    with col4:
        st.metric("Recent Data Points", f"{stats['recent_data_points']:,}")
    
    # Patient status distribution
    st.subheader("Patient Status Distribution")
    
    if stats["status_counts"]:
        status_data = pd.DataFrame({
            'Status': list(stats["status_counts"].keys()),
            'Count': list(stats["status_counts"].values())
        })
        
        fig = px.pie(status_data, values='Count', names='Status', 
                    title="Patient Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No patient data available")
    
    # Recent alerts
    st.subheader("🚨 Recent Alerts")
    
    active_alerts = clinical_service.get_active_alerts(clinician_id)
    
    if active_alerts:
        for alert in active_alerts[:5]:  # Show last 5 alerts
            patient = db_service.get_patient(alert.patient_id)
            patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown Patient"
            
            # Color code by severity
            if alert.severity == "critical":
                st.error(f"**{alert.severity.upper()}**: {alert.title} - {patient_name}")
            elif alert.severity == "high":
                st.warning(f"**{alert.severity.upper()}**: {alert.title} - {patient_name}")
            else:
                st.info(f"**{alert.severity.upper()}**: {alert.title} - {patient_name}")
            
            st.caption(f"Triggered: {alert.created_at.strftime('%Y-%m-%d %H:%M')}")
            st.write(alert.description)
            
            if st.button(f"Resolve Alert", key=f"resolve_{alert.id}"):
                clinical_service.resolve_alert(alert.id, "demo_clinician", "Resolved via dashboard")
                st.rerun()
            
            st.divider()
    else:
        st.success("No active alerts! All patients are stable.")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View All Patients", use_container_width=True):
            st.session_state['redirect_to'] = "Patient Management"
            st.rerun()
    
    with col2:
        if st.button("🔄 Review Alerts", use_container_width=True):
            st.session_state['redirect_to'] = "Alert Management"
            st.rerun()
    
    with col3:
        if st.button("📊 Patient Analytics", use_container_width=True):
            st.session_state['redirect_to'] = "Advanced Visualizations"
            st.rerun()

def show_patient_management_enhanced():
    st.header("👥 Patient Management")
    
    clinical_service = ClinicalService()
    db_service = DatabaseService()
    
    # For demo - in real app, this would come from auth
    clinician_id = "demo_clinician_001"
    
    tab1, tab2, tab3, tab4 = st.tabs(["My Patients", "Add Patient", "Patient Details", "Clinical Notes"])
    
    with tab1:
        st.subheader("My Patient List")
        
        # Search and filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("Search Patients", placeholder="Name, condition, email...")
        
        with col2:
            status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive", "High Risk"])
        
        with col3:
            risk_filter = st.selectbox("Risk Level", ["All", "Low", "Medium", "High"])
        
        # Get patients
        if search_query:
            patients = clinical_service.search_patients(search_query, clinician_id)
        else:
            patients = clinical_service.get_patients_by_clinician(clinician_id, include_inactive=True)
        
        # Apply filters
        if status_filter != "All":
            patients = [p for p in patients if p.status.value == status_filter.lower().replace(" ", "_")]
        
        if risk_filter != "All":
            patients = [p for p in patients if p.risk_level == risk_filter.lower()]
        
        if patients:
            # Display patients in an enhanced table
            patient_data = []
            for patient in patients:
                # Get latest data for quick stats
                wearable_data = db_service.get_patient_wearable_data(patient.id, days=1)
                latest_hr = None
                if wearable_data and wearable_data[0].heart_rate:
                    latest_hr = wearable_data[0].heart_rate
                
                patient_data.append({
                    "ID": patient.id[:8] + "...",
                    "Name": f"{patient.first_name} {patient.last_name}",
                    "Age": calculate_age(patient.date_of_birth),
                    "Condition": patient.primary_condition or "Not specified",
                    "Status": patient.status.value,
                    "Risk": patient.risk_level or "Not assessed",
                    "Last HR": f"{latest_hr} bpm" if latest_hr else "No data",
                    "Last Review": patient.last_review_date.strftime("%Y-%m-%d") if patient.last_review_date else "Never",
                    "Next Appointment": patient.next_appointment.strftime("%Y-%m-%d") if patient.next_appointment else "Not scheduled"
                })
            
            df = pd.DataFrame(patient_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Bulk actions
            st.subheader("Quick Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Generate Reports", use_container_width=True):
                    st.info("Patient reports generation started...")
            
            with col2:
                if st.button("📧 Send Reminders", use_container_width=True):
                    st.info("Reminder emails sent to patients.")
            
            with col3:
                if st.button("🔄 Update Status", use_container_width=True):
                    st.info("Status update workflow started...")
        
        else:
            st.info("No patients found matching your criteria.")
    
    with tab2:
        st.subheader("Add New Patient")
        
        # Use the existing patient form but enhance it
        show_patient_management()  # This will show the existing form
    
    with tab3:
        st.subheader("Patient Details & Management")
        
        patients = clinical_service.get_patients_by_clinician(clinician_id, include_inactive=True)
        if patients:
            patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
            selected_patient = st.selectbox("Select Patient", patient_options, key="enhanced_patient_details")
            
            if selected_patient:
                patient_id = selected_patient.split("(")[-1].rstrip(")")
                patient = db_service.get_patient(patient_id)
                
                if patient:
                    # Enhanced patient details with management options
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Patient Information")
                        
                        # Editable patient details
                        with st.form("edit_patient_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_status = st.selectbox("Status", 
                                                         [s.value for s in PatientStatus],
                                                         index=[s.value for s in PatientStatus].index(patient.status.value))
                                new_risk = st.selectbox("Risk Level", 
                                                      ["low", "medium", "high", "critical"],
                                                      index=["low", "medium", "high", "critical"].index(patient.risk_level) if patient.risk_level else 0)
                                new_condition = st.text_input("Primary Condition", value=patient.primary_condition or "")
                            
                            with col2:
                                new_review = st.date_input("Last Review Date", value=patient.last_review_date)
                                new_appointment = st.date_input("Next Appointment", value=patient.next_appointment)
                                clinical_notes = st.text_area("Clinical Notes", value=patient.clinical_notes or "")
                            
                            if st.form_submit_button("Update Patient"):
                                patient.status = PatientStatus(new_status)
                                patient.risk_level = new_risk
                                patient.primary_condition = new_condition
                                patient.last_review_date = new_review
                                patient.next_appointment = new_appointment
                                patient.clinical_notes = clinical_notes
                                patient.updated_at = datetime.utcnow()
                                
                                clinical_service.session.commit()
                                st.success("Patient updated successfully!")
                                st.rerun()
                    
                    with col2:
                        st.subheader("Quick Actions")
                        
                        if st.button("📊 View Dashboard", use_container_width=True):
                            st.session_state['selected_patient'] = patient_id
                            st.session_state['redirect_to'] = "Dashboard"
                            st.rerun()
                        
                        if st.button("📈 View Analytics", use_container_width=True):
                            st.session_state['selected_patient'] = patient_id
                            st.session_state['redirect_to'] = "Advanced Visualizations"
                            st.rerun()
                        
                        if st.button("🩺 Add Clinical Note", use_container_width=True):
                            st.session_state['selected_patient'] = patient_id
                            st.session_state['redirect_to'] = "Clinical Notes"
                            st.rerun()
                        
                        if st.button("📋 Generate Report", use_container_width=True):
                            report = clinical_service.generate_patient_report(patient_id)
                            st.success(f"Report generated for {patient.first_name} {patient.last_name}")
                            
                            # Show report summary
                            st.write("**Report Summary:**")
                            st.write(f"- Monitoring Period: {report['summary']['monitoring_period_days']} days")
                            st.write(f"- Data Points: {report['summary']['data_points']}")
                            st.write(f"- Symptom Reports: {report['summary']['symptom_reports']}")
                            st.write(f"- Average Heart Rate: {report['summary']['average_heart_rate'] or 'No data'}")
    
    with tab4:
        st.subheader("Clinical Notes")
        
        patients = clinical_service.get_patients_by_clinician(clinician_id)
        if patients:
            patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
            selected_patient = st.selectbox("Select Patient", patient_options, key="clinical_notes")
            
            if selected_patient:
                patient_id = selected_patient.split("(")[-1].rstrip(")")
                patient = db_service.get_patient(patient_id)
                
                # Add new clinical note
                st.subheader("Add New Clinical Note")
                
                with st.form("clinical_note_form"):
                    note_type = st.selectbox("Note Type", ["progress", "assessment", "plan", "telemedicine"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        subjective = st.text_area("Subjective", placeholder="Patient's reported symptoms and concerns...")
                    with col2:
                        objective = st.text_area("Objective", placeholder="Clinical findings, vital signs...")
                    
                    assessment = st.text_area("Assessment", placeholder="Clinical assessment and diagnosis...")
                    plan = st.text_area("Plan", placeholder="Treatment plan and recommendations...")
                    
                    if st.form_submit_button("Save Clinical Note"):
                        note_data = {
                            "patient_id": patient_id,
                            "clinician_id": clinician_id,
                            "note_type": note_type,
                            "subjective": subjective,
                            "objective": objective,
                            "assessment": assessment,
                            "plan": plan
                        }
                        
                        clinical_service.add_clinical_note(note_data)
                        st.success("Clinical note saved successfully!")
                        st.rerun()
                
                # Show existing notes
                st.subheader("Previous Clinical Notes")
                notes = clinical_service.get_patient_notes(patient_id)
                
                if notes:
                    for note in notes:
                        with st.expander(f"{note.note_type.title()} Note - {note.created_at.strftime('%Y-%m-%d %H:%M')}"):
                            if note.subjective:
                                st.write("**Subjective:**", note.subjective)
                            if note.objective:
                                st.write("**Objective:**", note.objective)
                            if note.assessment:
                                st.write("**Assessment:**", note.assessment)
                            if note.plan:
                                st.write("**Plan:**", note.plan)
                else:
                    st.info("No clinical notes found for this patient.")

def show_alert_management():
    st.header("🚨 Alert Management")
    
    clinical_service = ClinicalService()
    db_service = DatabaseService()
    
    clinician_id = "demo_clinician_001"
    
    tab1, tab2 = st.tabs(["Active Alerts", "Alert History"])
    
    with tab1:
        st.subheader("Active Alerts")
        
        active_alerts = clinical_service.get_active_alerts(clinician_id)
        
        if active_alerts:
            for alert in active_alerts:
                patient = db_service.get_patient(alert.patient_id)
                patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown Patient"
                
                # Create expandable alert card
                with st.expander(f"🔴 {alert.severity.upper()}: {alert.title} - {patient_name}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Patient:** {patient_name}")
                        st.write(f"**Description:** {alert.description}")
                        st.write(f"**Triggered:** {alert.created_at.strftime('%Y-%m-%d %H:%M')}")
                        
                        if alert.trigger_value:
                            st.write(f"**Trigger Value:** {alert.trigger_value}")
                        if alert.normal_range:
                            st.write(f"**Normal Range:** {alert.normal_range}")
                    
                    with col2:
                        # Resolution form
                        with st.form(f"resolve_alert_{alert.id}"):
                            resolution_notes = st.text_area("Resolution Notes", key=f"notes_{alert.id}")
                            if st.form_submit_button("✅ Resolve Alert"):
                                clinical_service.resolve_alert(alert.id, clinician_id, resolution_notes)
                                st.success("Alert resolved!")
                                st.rerun()
        else:
            st.success("🎉 No active alerts! All patients are stable.")
    
    with tab2:
        st.subheader("Alert History")
        
        # For demo - get some resolved alerts
        st.info("Alert history feature will show resolved alerts and trends over time.")
        
        # This would typically show a table of resolved alerts with filters
        st.write("Future enhancement: Alert analytics and resolution patterns")


# Add new import
from visualizations.advanced_viz import AdvancedVisualizations
from visualizations.viz_utils import *

# ... existing imports ...

def show_advanced_visualizations():
    st.header("📊 Advanced Visualizations")
    
    db_service = DatabaseService()
    patients = db_service.get_all_patients()
    viz = AdvancedVisualizations()
    
    if not patients:
        st.info("No patients found. Please add patients first.")
        return
    
    patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
    selected_patient = st.selectbox("Select Patient", patient_options, key="advanced_viz")
    
    if selected_patient:
        patient_id = selected_patient.split("(")[-1].rstrip(")")
        patient = db_service.get_patient(patient_id)
        
        if patient:
            st.subheader(f"Advanced Analytics for {patient.first_name} {patient.last_name}")
            
            # Visualization type selector
            viz_type = st.selectbox(
                "Choose Visualization Type",
                [
                    "HRV Comprehensive Analysis",
                    "Calendar Heatmaps", 
                    "Correlation Matrix",
                    "Biomarker Comparison",
                    "Sleep Analysis",
                    "Risk Assessment",
                    "Real-time Monitoring"
                ]
            )
            
            if viz_type == "HRV Comprehensive Analysis":
                show_hrv_analysis(viz, db_service, patient)
            elif viz_type == "Calendar Heatmaps":
                show_calendar_heatmaps(viz, db_service, patient)
            elif viz_type == "Correlation Matrix":
                show_correlation_matrix(viz, db_service, patient)
            elif viz_type == "Biomarker Comparison":
                show_biomarker_comparison(viz, db_service, patient)
            elif viz_type == "Sleep Analysis":
                show_sleep_analysis(viz, db_service, patient)
            elif viz_type == "Risk Assessment":
                show_risk_assessment(viz, db_service, patient)
            elif viz_type == "Real-time Monitoring":
                show_real_time_monitoring(viz, patient)

def show_hrv_analysis(viz, db_service, patient):
    st.subheader("❤️ Heart Rate Variability Analysis")

 # Get HRV data
    wearable_data = db_service.get_patient_wearable_data(patient.id, days=90)
    hrv_data = prepare_hrv_data(wearable_data)
    
    if hrv_data.empty:
        st.info("Not enough HRV data available for comprehensive analysis.")
        return
    
# Create comprehensive HRV visualization
    fig = viz.create_heart_rate_variability_chart(hrv_data, f"{patient.first_name} {patient.last_name}")
    if fig:
        st.plotly_chart(fig, use_container_width=True)

# Additional HRV insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_hrv = hrv_data['hrv'].mean()
        st.metric("Average HRV", f"{avg_hrv:.1f} ms")
    
    with col2:
        hrv_std = hrv_data['hrv'].std()
        st.metric("HRV Variability", f"{hrv_std:.1f} ms")
    
    with col3:
        trend = "Improving" if hrv_data['hrv'].iloc[-1] > hrv_data['hrv'].iloc[0] else "Declining"
        st.metric("30-Day Trend", trend)

def show_calendar_heatmaps(viz, db_service, patient):
    st.subheader("📅 Activity Calendar Heatmaps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        year = st.selectbox("Select Year", [2024, 2023, 2022], key="heatmap_year")
    
    with col2:
        metric = st.selectbox("Select Metric", ["steps", "heart_rate", "sleep_minutes"], key="heatmap_metric")
    
    # Get data for the selected year
    wearable_data = db_service.get_patient_wearable_data(patient.id, days=365)
    
    if not wearable_data:
        st.info("No data available for calendar heatmap.")
        return
    
    # Prepare data
    heatmap_data = []
    for data in wearable_data:
        if getattr(data, metric, None) is not None:
            heatmap_data.append({
                'date': data.timestamp.date(),
                metric: getattr(data, metric)
            })
    
    df = pd.DataFrame(heatmap_data)
    
    if df.empty:
        st.info(f"No {metric} data available for {year}.")
        return
    
    # Create calendar heatmap
    fig = viz.create_calendar_heatmap(df, metric, year)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

def show_correlation_matrix(viz, db_service, patient):
    st.subheader("🔗 Health Metrics Correlation Matrix")
    
    # Get comprehensive data
    wearable_data = db_service.get_patient_wearable_data(patient.id, days=90)
    
    if not wearable_data:
        st.info("Not enough data for correlation analysis.")
        return
    
    # Prepare correlation data
    corr_data = []
    for data in wearable_data:
        corr_data.append({
            'heart_rate': data.heart_rate,
            'steps': data.steps or 0,
            'calories': data.calories or 0,
            'sleep': data.sleep_minutes or 0,
            'hrv': data.hrv_rmssd or 0
        })
    
    df = pd.DataFrame(corr_data).dropna()
    
    if len(df) < 10:
        st.info("Need at least 10 data points for meaningful correlation analysis.")
        return
    
    # Create correlation matrix
    fig = viz.create_correlation_matrix(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation guide
        st.info("""
        **Correlation Interpretation:**
        - 🔵 +1.0: Perfect positive correlation
        - ⚪ 0.0: No correlation  
        - 🔴 -1.0: Perfect negative correlation
        """)

def show_biomarker_comparison(viz, db_service, patient):
    st.subheader("📈 Multi-Biomarker Trend Comparison")
    
    # Get biomarker data
    biomarkers = db_service.get_patient_biomarkers(patient.id, days=60)
    
    if not biomarkers:
        st.info("No biomarker data available for comparison.")
        return
    
    # Prepare biomarker data
    biomarker_data = prepare_biomarker_data(biomarkers)
    
    if not biomarker_data:
        st.info("Not enough biomarker data for comparison.")
        return
    
    # Create comparison visualization
    fig = viz.create_biomarker_trend_comparison(biomarker_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

def show_sleep_analysis(viz, db_service, patient):
    st.subheader("😴 Comprehensive Sleep Analysis")
    
    # Get sleep data from wearable
    wearable_data = db_service.get_patient_wearable_data(patient.id, days=60)
    
    if not wearable_data:
        st.info("No sleep data available.")
        return
    
    # Prepare sleep data
    sleep_data = []
    for data in wearable_data:
        if data.sleep_minutes:
            sleep_data.append({
                'date': data.timestamp.date(),
                'duration': data.sleep_minutes,
                'efficiency': min(100, (data.sleep_minutes or 0) / 480 * 100)
            })
    
    df = pd.DataFrame(sleep_data)
    
    if df.empty:
        st.info("No sleep duration data available.")
        return
    
    # Create sleep analysis dashboard
    fig = viz.create_sleep_analysis_dashboard(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

def show_risk_assessment(viz, db_service, patient):
    st.subheader("⚠️ Cardiac Risk Assessment")
    
    # Get patient data for risk assessment
    wearable_data = db_service.get_patient_wearable_data(patient.id, days=30)
    
    if not wearable_data:
        st.info("Not enough data for risk assessment.")
        return
    
    # Prepare risk assessment data
    risk_data = []
    for data in wearable_data:
        risk_data.append({
            'date': data.timestamp.date(),
            'heart_rate': data.heart_rate,
            'hrv': data.hrv_rmssd or 0
        })
    
    df = pd.DataFrame(risk_data).dropna()
    
    if df.empty:
        st.info("No data available for risk assessment.")
        return
    
    # Define risk thresholds
    thresholds = {
        'heart_rate': {'normal': [60, 100]},
        'hrv': {'normal': [20, 100]}
    }
    
    # Create risk assessment chart
    fig = viz.create_risk_assessment_chart(df, thresholds)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

def show_real_time_monitoring(viz, patient):
    st.subheader("🔄 Real-time Health Monitoring")
    
    st.info("This is a demonstration of real-time monitoring capabilities.")
    
    # Generate sample real-time data
    real_time_data = generate_sample_real_time_data(24)
    
    # Create real-time dashboard
    fig = viz.create_real_time_monitoring_dashboard(real_time_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Simulated alerts
    st.subheader("📢 Health Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.warning("**Elevated Heart Rate**\n\nAverage resting HR increased by 12% in the last 7 days.")
    
    with col2:
        st.error("**Low HRV Alert**\n\nHRV below normal range for 3 consecutive days.")

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from data_models.database_models import Patient, Gender, CardiacBiomarkerType
from config.database import create_db_and_tables
from database.database_service import DatabaseService

# Page configuration
st.set_page_config(**settings.STREAMLIT_CONFIG)

def main():
    create_db_and_tables()
    
    st.title("❤️ Cardiac Health Platform")
    
    # Sidebar navigation - UPDATED
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        [
            "Clinician Dashboard", 
            "Patient Management", 
            "Wearable Data", 
            "Biomarker Analysis", 
            "Advanced Visualizations", 
            "Alert Management",
            "Data Insights"
        ]
    )
    
    if page == "Clinician Dashboard":
        show_clinician_dashboard()
    elif page == "Patient Management":
        show_patient_management_enhanced()
    elif page == "Wearable Data":
        show_wearable_data()
    elif page == "Biomarker Analysis":
        show_biomarker_analysis()
    elif page == "Advanced Visualizations":
        show_advanced_visualizations()
    elif page == "Alert Management":
        show_alert_management()
    elif page == "Data Insights":
        show_data_insights()
   

def show_dashboard():
    st.header("Cardiac Health Dashboard")
    
    db_service = DatabaseService()
    patients = db_service.get_all_patients()
    
    if not patients:
        st.info("No patients found. Please add patients in the Patient Management section.")
        return
    
    # Patient selector for dashboard
    patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
    selected_patient = st.selectbox("Select Patient", patient_options, key="dashboard_patient")
    
    if selected_patient:
        patient_id = selected_patient.split("(")[-1].rstrip(")")
        patient = db_service.get_patient(patient_id)
        
        if patient:
            # Display patient info
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Patient", f"{patient.first_name} {patient.last_name}")
            with col2:
                age = calculate_age(patient.date_of_birth)
                st.metric("Age", f"{age} years")
            with col3:
                st.metric("Condition", patient.primary_condition or "Not specified")
            with col4:
                st.metric("Patient Since", patient.created_at.strftime("%Y-%m-%d"))
            
            # Get health summary
            summary = db_service.get_patient_health_summary(patient_id)
            
            # Health metrics
            st.subheader("📊 Health Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                latest_hr = summary['latest_heart_rate']
                hr_status = "normal" if latest_hr and 60 <= latest_hr <= 100 else "warning"
                st.metric("Resting HR", 
                         f"{latest_hr} bpm" if latest_hr else "No data", 
                         delta=None,
                         delta_color="normal" if hr_status == "normal" else "off")
            
            with col2:
                recent_activity = summary['recent_activity']
                activity_status = "normal" if recent_activity and recent_activity >= 5000 else "warning"
                st.metric("Avg Steps", 
                         f"{recent_activity:.0f}" if recent_activity else "No data",
                         delta_color="normal" if activity_status == "normal" else "off")
            
            with col3:
                data_points = summary['data_points_count']
                st.metric("Data Points", data_points)
            
            with col4:
                sob = summary['latest_symptoms'].shortness_of_breath if summary['latest_symptoms'] else "No data"
                sob_status = "normal" if isinstance(sob, str) or sob <= 3 else "warning"
                st.metric("SOB Level", 
                         sob,
                         delta_color="normal" if sob_status == "normal" else "off")
            
            # Recent data charts
            st.subheader("📈 Recent Trends")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Heart rate trend
                biomarkers = db_service.get_patient_biomarkers(
                    patient_id, 
                    CardiacBiomarkerType.RESTING_HR, 
                    days=14
                )
                
                if biomarkers:
                    hr_data = pd.DataFrame([{
                        'date': b.timestamp.date(),
                        'heart_rate': b.value
                    } for b in biomarkers])
                    
                    fig = px.line(hr_data, x='date', y='heart_rate',
                                title="Resting Heart Rate (14 days)",
                                labels={'heart_rate': 'Heart Rate (bpm)', 'date': 'Date'})
                    
                    # Add normal range
                    fig.add_hrect(y0=60, y1=100, line_width=0, fillcolor="green", opacity=0.1,
                                annotation_text="Normal Range", annotation_position="top left")
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No heart rate data available")
            
            with col2:
                # Activity trend
                wearable_data = db_service.get_patient_wearable_data(patient_id, days=7)
                
                if wearable_data:
                    # Group by date and sum steps
                    steps_by_date = {}
                    for data in wearable_data:
                        date_key = data.timestamp.date()
                        if date_key not in steps_by_date:
                            steps_by_date[date_key] = 0
                        steps_by_date[date_key] += data.steps or 0
                    
                    activity_data = pd.DataFrame([
                        {'date': date, 'steps': steps} 
                        for date, steps in steps_by_date.items()
                    ])
                    
                    if not activity_data.empty:
                        fig = px.bar(activity_data, x='date', y='steps',
                                    title="Daily Steps (7 days)",
                                    labels={'steps': 'Steps', 'date': 'Date'})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No step data available")
                else:
                    st.info("No activity data available")
            
            # Latest symptoms
            st.subheader("🩺 Recent Symptoms")
            latest_symptoms = db_service.get_patient_symptom_reports(patient_id, days=7)
            
            if latest_symptoms:
                symptoms_df = pd.DataFrame([{
                    'date': report.report_date,  # FIXED: report.date → report.report_date
                    'sob': report.shortness_of_breath,
                    'fatigue': report.fatigue_level,
                    'chest_pain': report.chest_discomfort,
                    'swelling': report.swelling_feet,
                    'weight': report.weight_kg
                } for report in latest_symptoms])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Symptom scores
                    fig = px.line(symptoms_df, x='date', y=['sob', 'fatigue'],
                                title="Symptom Scores (0-10 scale)",
                                labels={'value': 'Score', 'variable': 'Symptom'})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Weight trend
                    if symptoms_df['weight'].notna().any():
                        fig = px.line(symptoms_df.dropna(subset=['weight']), 
                                    x='date', y='weight',
                                    title="Weight Trend (kg)")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No weight data available")
            else:
                st.info("No recent symptom reports")

def show_patient_management():
    st.header("👥 Patient Management")
    
    db_service = DatabaseService()
    
    tab1, tab2, tab3 = st.tabs(["Add Patient", "View Patients", "Patient Details"])
    
    with tab1:
        st.subheader("Add New Patient")
        
        with st.form("patient_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*")
                last_name = st.text_input("Last Name*")
                date_of_birth = st.date_input("Date of Birth*", 
                                            max_value=date.today(),
                                            value=date(1980, 1, 1))
                gender = st.selectbox("Gender", [g.value for g in Gender])
            
            with col2:
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                primary_condition = st.selectbox(
                    "Primary Cardiac Condition",
                    ["", "Hypertension", "Heart Failure", "Coronary Artery Disease", 
                     "Arrhythmia", "Cardiomyopathy", "Other"]
                )
                medications = st.text_area("Current Medications", placeholder="List medications separated by commas")
                allergies = st.text_area("Allergies", placeholder="List allergies separated by commas")
            
            submitted = st.form_submit_button("Create Patient")
            
            if submitted:
                if first_name and last_name:
                    patient_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": date_of_birth,
                        "gender": gender,
                        "email": email or None,
                        "phone": phone or None,
                        "primary_condition": primary_condition or None,
                        "medications": medications or None,
                        "allergies": allergies or None
                    }
                    
                    try:
                        patient = db_service.create_patient(patient_data)
                        st.success(f"Patient {patient.first_name} {patient.last_name} created successfully!")
                        
                        # Show quick actions
                        st.info(f"**Next steps:** Add wearable data and symptom reports for {first_name} in the respective sections.")
                        
                    except Exception as e:
                        st.error(f"Error creating patient: {e}")
                else:
                    st.error("Please fill in required fields (First Name, Last Name)")
    
    with tab2:
        st.subheader("All Patients")
        
        patients = db_service.get_all_patients()
        
        if patients:
            # Display patients in a nice table
            patient_data = []
            for patient in patients:
                patient_data.append({
                    "ID": patient.id[:8] + "...",  # Shorten ID for display
                    "Name": f"{patient.first_name} {patient.last_name}",
                    "Age": calculate_age(patient.date_of_birth),
                    "Gender": patient.gender,
                    "Condition": patient.primary_condition or "Not specified",
                    "Contact": patient.email or patient.phone or "N/A",
                    "Created": patient.created_at.strftime("%Y-%m-%d")
                })
            
            df = pd.DataFrame(patient_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Export Patients as CSV",
                data=csv,
                file_name=f"patients_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No patients found. Add your first patient above.")
    
    with tab3:
        st.subheader("Patient Details")
        
        patients = db_service.get_all_patients()
        if patients:
            patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
            selected_patient = st.selectbox("Select Patient", patient_options, key="patient_details")
            
            if selected_patient:
                patient_id = selected_patient.split("(")[-1].rstrip(")")
                patient = db_service.get_patient(patient_id)
                
                if patient:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Demographic Information")
                        st.write(f"**Name:** {patient.first_name} {patient.last_name}")
                        st.write(f"**Date of Birth:** {patient.date_of_birth} (Age: {calculate_age(patient.date_of_birth)})")
                        st.write(f"**Gender:** {patient.gender}")
                        st.write(f"**Email:** {patient.email or 'Not provided'}")
                        st.write(f"**Phone:** {patient.phone or 'Not provided'}")
                    
                    with col2:
                        st.subheader("Medical Information")
                        st.write(f"**Primary Condition:** {patient.primary_condition or 'Not specified'}")
                        st.write(f"**Medications:** {patient.medications or 'None listed'}")
                        st.write(f"**Allergies:** {patient.allergies or 'None listed'}")
                        st.write(f"**Patient Since:** {patient.created_at.strftime('%Y-%m-%d')}")
                    
                    # Quick stats
                    st.subheader("Health Data Summary")
                    summary = db_service.get_patient_health_summary(patient_id)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Resting HR", 
                                 f"{summary['latest_heart_rate']} bpm" if summary['latest_heart_rate'] else "No data")
                    with col2:
                        st.metric("Recent Activity", f"{summary['recent_activity']:.0f} steps/day")
                    with col3:
                        st.metric("Data Points", summary['data_points_count'])
                    with col4:
                        latest_report = summary['latest_symptoms']
                        if latest_report:
                            st.metric("Last Symptom Report", latest_report.report_date.strftime("%Y-%m-%d"))  # FIXED: report.date → report.report_date
                        else:
                            st.metric("Last Symptom Report", "No reports")
                    
                    # Action buttons
                    st.subheader("Quick Actions")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📊 View Full Analytics", key="view_analytics"):
                            st.session_state['redirect_to'] = "Biomarker Analysis"
                            st.rerun()
                    
                    with col2:
                        if st.button("⌚ Add Wearable Data", key="add_wearable"):
                            st.session_state['redirect_to'] = "Wearable Data"
                            st.rerun()
                    
                    with col3:
                        if st.button("🩺 Add Symptom Report", key="add_symptoms"):
                            st.session_state['redirect_to'] = "Symptom Report"
                            st.rerun()

def show_wearable_data():
    st.header("📊 Wearable Data")
    
    db_service = DatabaseService()
    patients = db_service.get_all_patients()
    
    if not patients:
        st.info("No patients found. Please add patients in the Patient Management section first.")
        return
    
    tab1, tab2, tab3 = st.tabs(["Fitbit Integration", "Manual Upload", "View Data"])
    
    with tab1:
        show_fitbit_integration(db_service, patients)
    
    with tab2:
        show_manual_upload(db_service, patients)
    
    with tab3:
        show_wearable_data_view(db_service, patients)

def show_fitbit_integration(db_service, patients):
    st.header("🔗 Fitbit Integration")
    
    # Initialize Fitbit services
    fitbit_auth = FitbitAuth()
    fitbit_service = FitbitDataService()
    
    # Handle OAuth callback if returning from Fitbit
    query_params = st.experimental_get_query_params()
    if 'code' in query_params and not fitbit_auth.is_authenticated():
        with st.spinner("Completing Fitbit authentication..."):
            code = query_params['code'][0]
            token = fitbit_auth.fetch_token(fitbit_config.AUTHORIZE_URL + '?code=' + code)
            if token:
                st.success("✅ Fitbit account connected successfully!")
                st.experimental_set_query_params()  # Clear URL parameters
                st.rerun()
    
    if not fitbit_auth.is_authenticated():
        st.info("Connect your Fitbit account to sync real health data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Connect Your Fitbit")
            st.write("1. Click the button below")
            st.write("2. Authorize our app in Fitbit") 
            st.write("3. You'll be redirected back here")
            
            # Patient selector
            patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
            selected_patient = st.selectbox("Select Patient for Fitbit Data", patient_options, key="fitbit_patient_auth")
            
            if st.button("🔗 Connect Fitbit Account", type="primary"):
                if selected_patient:
                    patient_id = selected_patient.split("(")[-1].rstrip(")")
                    st.session_state['fitbit_patient_id'] = patient_id
                    
                    auth_url = fitbit_auth.get_authorization_url()
                    st.markdown(f"**Please visit this URL to authorize:**")
                    st.markdown(f"[{auth_url}]({auth_url})")
                    st.info("After authorizing, you'll be redirected back to this app with your data")
                else:
                    st.error("Please select a patient first")
        
        with col2:
            st.subheader("What Data We Access")
            st.write("✅ Heart rate (resting & intraday)")
            st.write("✅ Heart Rate Variability (HRV)")
            st.write("✅ Sleep stages and quality") 
            st.write("✅ Activity and steps")
            st.write("✅ Calories burned")
            st.write("✅ Weight trends")
    
    else:
        st.success("✅ Fitbit account connected!")
        
        # Show which patient this is connected to
        patient_id = st.session_state.get('fitbit_patient_id')
        patient = db_service.get_patient(patient_id) if patient_id else None
        
        if patient:
            st.write(f"**Connected for:** {patient.first_name} {patient.last_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sync Options")
            sync_days = st.slider("Days of data to sync", 1, 30, 7)
            
            if st.button("🔄 Sync Real Fitbit Data", type="primary"):
                if patient_id:
                    with st.spinner("Syncing real data from Fitbit..."):
                        sync_real_fitbit_data(fitbit_service, db_service, patient_id, sync_days)
                else:
                    st.error("No patient selected for Fitbit data")
            
            if st.button("🔄 Sync Today's Data", type="secondary"):
                if patient_id:
                    with st.spinner("Syncing today's data..."):
                        sync_real_fitbit_data(fitbit_service, db_service, patient_id, 1)
                else:
                    st.error("No patient selected for Fitbit data")
        
        with col2:
            st.subheader("Account Actions")
            
            # Show basic profile info
            profile = fitbit_service.get_profile()
            if profile and 'user' in profile:
                user = profile['user']
                st.write(f"**Fitbit User:** {user.get('displayName', 'N/A')}")
                st.write(f"**Member since:** {user.get('memberSince', 'N/A')}")
            
            if st.button("🚪 Disconnect Fitbit", type="secondary"):
                fitbit_auth.revoke_access()
                st.session_state.pop('fitbit_patient_id', None)
                st.success("Disconnected from Fitbit")
                st.rerun()
        
        # Show recently synced data preview
        st.subheader("Recently Synced Data")
        if patient_id:
            wearable_data = db_service.get_patient_wearable_data(patient_id, days=1)
            if wearable_data:
                # Show latest heart rate data
                hr_data = [d for d in wearable_data if d.heart_rate]
                if hr_data:
                    latest_hr = hr_data[0].heart_rate
                    st.metric("Latest Heart Rate", f"{latest_hr} bpm")
                
                # Show activity summary
                steps_today = sum(d.steps or 0 for d in wearable_data)
                st.metric("Steps Today", f"{steps_today:,}")
            else:
                st.info("No Fitbit data synced yet. Click 'Sync Real Fitbit Data' above.")

def sync_real_fitbit_data(fitbit_service, db_service, patient_id, days):
    """Sync real data from Fitbit API"""
    try:
        saved_count = 0
        
        # Sync data for each day
        for day_offset in range(days):
            date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')
            
            # Get heart rate data
            hr_data = fitbit_service.get_heart_rate_intraday(date)
            if hr_data is not None and not hr_data.empty:
                for _, row in hr_data.iterrows():
                    wearable_data = {
                        "patient_id": patient_id,
                        "timestamp": row['datetime'],
                        "heart_rate": row['value'],
                        "source": "fitbit"
                    }
                    db_service.add_wearable_data(wearable_data)
                    saved_count += 1
            
            # Get resting heart rate
            resting_hr = fitbit_service.get_resting_heart_rate(date)
            if resting_hr:
                biomarker = {
                    "patient_id": patient_id,
                    "biomarker_type": CardiacBiomarkerType.RESTING_HR,
                    "value": resting_hr,
                    "timestamp": datetime.now(),
                    "unit": "bpm",
                    "source": "fitbit"
                }
                db_service.add_biomarker(biomarker)
            
            # Get activity summary
            activity = fitbit_service.get_activity_summary(date)
            if activity and 'summary' in activity:
                summary = activity['summary']
                if summary.get('steps', 0) > 0:
                    wearable_data = {
                        "patient_id": patient_id,
                        "timestamp": datetime.strptime(date, '%Y-%m-%d'),
                        "steps": summary.get('steps', 0),
                        "calories": summary.get('caloriesOut', 0),
                        "source": "fitbit"
                    }
                    db_service.add_wearable_data(wearable_data)
                    saved_count += 1
        
        st.success(f"✅ Successfully synced {saved_count} data points from Fitbit!")
        
    except Exception as e:
        st.error(f"Error syncing Fitbit data: {e}")

def show_manual_upload(db_service, patients):
    st.header("📁 Manual Data Upload")
    
    patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
    selected_patient = st.selectbox("Select Patient", patient_options, key="manual_upload")
    
    if selected_patient:
        patient_id = selected_patient.split("(")[-1].rstrip(")")
        
        tab1, tab2 = st.tabs(["Single Entry", "CSV Upload"])
        
        with tab1:
            st.subheader("Manual Data Entry")
            
            with st.form("manual_wearable_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    timestamp = st.datetime_input("Timestamp", datetime.now())
                    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=72)
                    steps = st.number_input("Steps", min_value=0, value=5000)
                    calories = st.number_input("Calories", min_value=0, value=2000)
                
                with col2:
                    hrv_rmssd = st.number_input("HRV RMSSD (ms)", min_value=0, value=42)
                    sleep_minutes = st.number_input("Sleep (minutes)", min_value=0, max_value=1440, value=480)
                    spo2 = st.slider("Blood Oxygen (%)", 80, 100, 98)
                    source = st.selectbox("Data Source", ["manual", "other_device"])
                
                notes = st.text_area("Notes (optional)")
                
                submitted = st.form_submit_button("Save Wearable Data")
                if submitted:
                    wearable_data = {
                        "patient_id": patient_id,
                        "timestamp": timestamp,
                        "heart_rate": heart_rate,
                        "hrv_rmssd": hrv_rmssd,
                        "steps": steps,
                        "calories": calories,
                        "sleep_minutes": sleep_minutes,
                        "spo2": spo2,
                        "source": source
                    }
                    
                    try:
                        db_service.add_wearable_data(wearable_data)
                        st.success("Wearable data saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving data: {e}")
        
        with tab2:
            st.subheader("CSV Upload")
            st.write("Upload data exported from your wearable device or health app")
            
            uploaded_file = st.file_uploader("Choose CSV file", type='csv', key="wearable_csv")
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success("File uploaded successfully!")
                    
                    st.write("**Data Preview:**")
                    st.dataframe(df.head())
                    
                    st.write("**Data Summary:**")
                    st.write(f"- Rows: {len(df)}")
                    st.write(f"- Columns: {list(df.columns)}")
                    
                    # Column mapping
                    st.subheader("Column Mapping")
                    st.write("Map your CSV columns to our database fields:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        timestamp_col = st.selectbox("Timestamp Column", df.columns, index=0)
                        hr_col = st.selectbox("Heart Rate Column", [""] + list(df.columns))
                        steps_col = st.selectbox("Steps Column", [""] + list(df.columns))
                    
                    with col2:
                        hrv_col = st.selectbox("HRV Column", [""] + list(df.columns))
                        calories_col = st.selectbox("Calories Column", [""] + list(df.columns))
                        sleep_col = st.selectbox("Sleep Column", [""] + list(df.columns))
                    
                    if st.button("Process and Save Data"):
                        with st.spinner("Processing data..."):
                            saved_count = 0
                            for _, row in df.iterrows():
                                try:
                                    # Convert timestamp
                                    timestamp = pd.to_datetime(row[timestamp_col])
                                    
                                    wearable_data = {
                                        "patient_id": patient_id,
                                        "timestamp": timestamp,
                                        "heart_rate": float(row[hr_col]) if hr_col and pd.notna(row[hr_col]) else None,
                                        "hrv_rmssd": float(row[hrv_col]) if hrv_col and pd.notna(row[hrv_col]) else None,
                                        "steps": int(row[steps_col]) if steps_col and pd.notna(row[steps_col]) else None,
                                        "calories": float(row[calories_col]) if calories_col and pd.notna(row[calories_col]) else None,
                                        "sleep_minutes": float(row[sleep_col]) if sleep_col and pd.notna(row[sleep_col]) else None,
                                        "source": "csv_upload"
                                    }
                                    
                                    db_service.add_wearable_data(wearable_data)
                                    saved_count += 1
                                
                                except Exception as e:
                                    st.warning(f"Could not process row {_}: {e}")
                                    continue
                            
                            st.success(f"Successfully saved {saved_count} out of {len(df)} records!")
                            
                except Exception as e:
                    st.error(f"Error reading file: {e}")

def show_wearable_data_view(db_service, patients):
    st.header("📋 View Wearable Data")
    
    patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
    selected_patient = st.selectbox("Select Patient", patient_options, key="view_wearable")
    
    if selected_patient:
        patient_id = selected_patient.split("(")[-1].rstrip(")")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Get data
        wearable_data = db_service.get_patient_wearable_data(patient_id, days=365)  # Get more and filter
        filtered_data = [
            d for d in wearable_data 
            if start_date <= d.timestamp.date() <= end_date
        ]
        
        if filtered_data:
            st.write(f"**Found {len(filtered_data)} data points**")
            
            # Convert to DataFrame for display
            data_df = pd.DataFrame([{
                'Timestamp': d.timestamp,
                'Heart Rate': d.heart_rate,
                'HRV RMSSD': d.hrv_rmssd,
                'Steps': d.steps,
                'Calories': d.calories,
                'Sleep (min)': d.sleep_minutes,
                'SpO2': d.spo2,
                'Source': d.source
            } for d in filtered_data])
            
            st.dataframe(data_df, use_container_width=True)
            
            # Export option
            csv = data_df.to_csv(index=False)
            st.download_button(
                label="Export Data as CSV",
                data=csv,
                file_name=f"wearable_data_{patient_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Summary statistics
            st.subheader("Summary Statistics")
            if not data_df.empty:
                summary_stats = data_df.describe()
                st.dataframe(summary_stats)
        else:
            st.info("No wearable data found for the selected patient and date range.")

def show_biomarker_analysis():
    st.header("Biomarker Analysis")
    
    db_service = DatabaseService()
    patients = db_service.get_all_patients()
    
    if not patients:
        st.info("No patients found. Please add patients in the Patient Management section.")
        return
    
    patient_options = [f"{p.first_name} {p.last_name} ({p.id})" for p in patients]
    selected_patient = st.selectbox("Select Patient", patient_options, key="biomarker_analysis")
    
    if selected_patient:
        patient_id = selected_patient.split("(")[-1].rstrip(")")
        
        st.info("Advanced biomarker analysis and trend detection will appear here")
        
        # Placeholder for biomarker analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("HRV Analysis")
            
            biomarkers = db_service.get_patient_biomarkers(
                patient_id, 
                CardiacBiomarkerType.HRV_RMSSD, 
                days=30
            )
            
            if biomarkers:
                hrv_data = pd.DataFrame([{
                    'Date': b.timestamp.date(),
                    'HRV_RMSSD': b.value
                } for b in biomarkers])
                
                fig = px.line(hrv_data, x='Date', y='HRV_RMSSD', 
                             title="HRV RMSSD Trend (30 days)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No HRV data available")
        
        with col2:
            st.subheader("Resting Heart Rate Trend")
            
            biomarkers = db_service.get_patient_biomarkers(
                patient_id, 
                CardiacBiomarkerType.RESTING_HR, 
                days=30
            )
            
            if biomarkers:
                rhr_data = pd.DataFrame([{
                    'Date': b.timestamp.date(),
                    'Resting_HR': b.value
                } for b in biomarkers])
                
                fig = px.line(rhr_data, x='Date', y='Resting_HR', 
                             title="Resting Heart Rate Trend (30 days)")
                
                # Add normal range
                fig.add_hrect(y0=60, y1=100, line_width=0, fillcolor="green", opacity=0.2,
                            annotation_text="Normal Range", annotation_position="top left")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No resting heart rate data available")

def show_data_insights():
    st.header("📊 Data Insights")
    
    db_service = DatabaseService()
    patients = db_service.get_all_patients()
    
    if not patients:
        st.info("No patients found. Please add patients in the Patient Management section.")
        return
    
    st.info("Advanced analytics and machine learning insights will appear here")
    
    # Patient overview stats
    st.subheader("Practice Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(patients))
    
    with col2:
        active_patients = sum(1 for p in patients if p.created_at.date() >= datetime.now().date() - timedelta(days=30))
        st.metric("Active Patients (30d)", active_patients)
    
    with col3:
        total_data_points = 0
        for patient in patients:
            wearable_data = db_service.get_patient_wearable_data(patient.id, days=365)
            total_data_points += len(wearable_data)
        st.metric("Total Data Points", total_data_points)
    
    with col4:
        avg_age = sum(calculate_age(p.date_of_birth) for p in patients) / len(patients) if patients else 0
        st.metric("Average Age", f"{avg_age:.1f} years")
    
    # Conditions distribution
    st.subheader("Patient Conditions Distribution")
    conditions = [p.primary_condition or "Not specified" for p in patients]
    condition_counts = pd.Series(conditions).value_counts()
    
    if not condition_counts.empty:
        fig = px.pie(values=condition_counts.values, names=condition_counts.index,
                    title="Primary Cardiac Conditions")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No condition data available")

def calculate_age(dob: date) -> int:
    """Calculate age from date of birth"""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# Handle page redirects
if 'redirect_to' in st.session_state:
    page = st.session_state.pop('redirect_to')
    st.success(f"Redirecting to {page}...")
    # Note: Streamlit doesn't have built-in redirects, so we show a message
    # In a real app, you might use query parameters or other navigation methods

if __name__ == "__main__":
    main()