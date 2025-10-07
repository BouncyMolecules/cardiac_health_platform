import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import streamlit as st

class AdvancedVisualizations:
    def __init__(self):
        self.color_scale = px.colors.sequential.Viridis
    
    def create_calendar_heatmap(self, data: pd.DataFrame, metric: str, year: int):
        """Create calendar heatmap without external dependencies"""
        if data.empty:
            return None
            
        # Ensure we have data for the specified year
        data['date'] = pd.to_datetime(data['date'])
        yearly_data = data[data['date'].dt.year == year].copy()
        
        if yearly_data.empty:
            return None
        
        # Create a complete date range for the year
        start_date = pd.Timestamp(f'{year}-01-01')
        end_date = pd.Timestamp(f'{year}-12-31')
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create a DataFrame with all dates
        calendar_df = pd.DataFrame({'date': all_dates})
        calendar_df['day'] = calendar_df['date'].dt.day
        calendar_df['month'] = calendar_df['date'].dt.month
        calendar_df['weekday'] = calendar_df['date'].dt.weekday
        calendar_df['week'] = calendar_df['date'].dt.isocalendar().week
        
        # Merge with actual data
        calendar_df = calendar_df.merge(yearly_data, on='date', how='left')
        
        # Pivot for heatmap
        heatmap_data = calendar_df.pivot_table(
            values=metric, 
            index='week', 
            columns='weekday', 
            aggfunc='mean'
        )
        
        # Create custom text for hover
        text_data = calendar_df.pivot_table(
            values='date', 
            index='week', 
            columns='weekday', 
            aggfunc='first'
        )
        
        # Create the heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            y=[f'Week {int(w)}' for w in heatmap_data.index],
            colorscale='Viridis',
            hoverinfo='text',
            text=[[f"Date: {text_data.iloc[i, j].strftime('%Y-%m-%d') if pd.notna(text_data.iloc[i, j]) else 'No data'}<br>{metric}: {heatmap_data.iloc[i, j]:.1f}" 
                   for j in range(len(heatmap_data.columns))] 
                  for i in range(len(heatmap_data))]
        ))
        
        fig.update_layout(
            title=f'{metric.title()} Calendar Heatmap - {year}',
            height=400,
            xaxis_title='Day of Week',
            yaxis_title='Week of Year'
        )
        
        return fig

    def create_heart_rate_variability_chart(self, hrv_data: pd.DataFrame, patient_name: str):
        """Create advanced HRV analysis with multiple components"""
        if hrv_data.empty:
            return None
            
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'HRV Trend Over Time', 
                'HRV Distribution',
                'Daily Pattern',
                'HRV vs Activity'
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}]
            ]
        )
        
        # 1. HRV Trend
        fig.add_trace(
            go.Scatter(x=hrv_data['date'], y=hrv_data['hrv'], 
                      mode='lines+markers', name='HRV',
                      line=dict(color='#2E86AB', width=3)),
            row=1, col=1
        )
        
        # Add rolling average
        hrv_data['rolling_avg'] = hrv_data['hrv'].rolling(window=7).mean()
        fig.add_trace(
            go.Scatter(x=hrv_data['date'], y=hrv_data['rolling_avg'],
                      mode='lines', name='7-Day Average',
                      line=dict(color='#A23B72', width=2, dash='dash')),
            row=1, col=1
        )
        
        # 2. Distribution
        fig.add_trace(
            go.Histogram(x=hrv_data['hrv'], name='HRV Distribution',
                        marker_color='#F18F01', nbinsx=20),
            row=1, col=2
        )
        
        # 3. Daily pattern (if we have time data)
        if 'hour' in hrv_data.columns:
            daily_avg = hrv_data.groupby('hour')['hrv'].mean()
            fig.add_trace(
                go.Scatter(x=daily_avg.index, y=daily_avg.values,
                          mode='lines', name='Daily Pattern',
                          line=dict(color='#C73E1D', width=3)),
                row=2, col=1
            )
        
        # 4. HRV vs Activity (if activity data available)
        if 'activity' in hrv_data.columns:
            fig.add_trace(
                go.Scatter(x=hrv_data['activity'], y=hrv_data['hrv'],
                          mode='markers', name='HRV vs Activity',
                          marker=dict(color=hrv_data['hrv'], 
                                    colorscale='Viridis',
                                    size=8,
                                    showscale=True)),
                row=2, col=2
            )
        
        fig.update_layout(
            title=f'Comprehensive HRV Analysis for {patient_name}',
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def create_correlation_matrix(self, metrics_data: pd.DataFrame):
        """Create correlation matrix between different health metrics"""
        # Select only numeric columns
        numeric_data = metrics_data.select_dtypes(include=[np.number])
        
        if numeric_data.empty or len(numeric_data.columns) < 2:
            return None
            
        # Calculate correlation matrix
        corr_matrix = numeric_data.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            zmin=-1, 
            zmax=1
        )
        
        fig.update_layout(
            title='Correlation Matrix: Health Metrics Relationships',
            height=600
        )
        
        return fig
    
    def create_biomarker_trend_comparison(self, biomarkers_data: Dict[str, pd.DataFrame]):
        """Compare multiple biomarker trends in one visualization"""
        if not biomarkers_data:
            return None
            
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3
        color_idx = 0
        
        for biomarker_name, data in biomarkers_data.items():
            if not data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data['value'],
                        name=biomarker_name,
                        line=dict(color=colors[color_idx % len(colors)], width=3),
                        mode='lines+markers'
                    )
                )
                color_idx += 1
        
        fig.update_layout(
            title='Multi-Biomarker Trend Comparison',
            xaxis_title='Date',
            yaxis_title='Value',
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_sleep_analysis_dashboard(self, sleep_data: pd.DataFrame):
        """Comprehensive sleep analysis visualization"""
        if sleep_data.empty:
            return None
            
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Sleep Duration Trend',
                'Sleep Stage Distribution',
                'Sleep Efficiency',
                'Sleep vs Activity Correlation'
            ),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # 1. Sleep duration trend
        fig.add_trace(
            go.Scatter(x=sleep_data['date'], y=sleep_data['duration'],
                      mode='lines+markers', name='Sleep Duration',
                      line=dict(color='#4B3F72', width=3)),
            row=1, col=1
        )
        
        # 2. Sleep stage distribution (if available)
        if all(stage in sleep_data.columns for stage in ['deep', 'light', 'rem', 'awake']):
            stage_totals = sleep_data[['deep', 'light', 'rem', 'awake']].sum()
            fig.add_trace(
                go.Pie(labels=stage_totals.index, values=stage_totals.values,
                      name='Sleep Stages'),
                row=1, col=2
            )
        
        # 3. Sleep efficiency
        if 'efficiency' in sleep_data.columns:
            fig.add_trace(
                go.Bar(x=sleep_data['date'], y=sleep_data['efficiency'],
                      name='Sleep Efficiency',
                      marker_color=sleep_data['efficiency'],
                      colorscale='Viridis'),
                row=2, col=1
            )
        
        # 4. Sleep vs Activity correlation
        if 'activity' in sleep_data.columns:
            fig.add_trace(
                go.Scatter(x=sleep_data['activity'], y=sleep_data['duration'],
                          mode='markers', name='Sleep vs Activity',
                          marker=dict(size=8, color=sleep_data['efficiency'],
                                    colorscale='Viridis', showscale=True)),
                row=2, col=2
            )
        
        fig.update_layout(
            title='Comprehensive Sleep Analysis Dashboard',
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def create_risk_assessment_chart(self, patient_data: pd.DataFrame, thresholds: Dict):
        """Create risk assessment visualization based on biomarker thresholds"""
        if patient_data.empty:
            return None
            
        fig = go.Figure()
        
        # Add normal range
        for metric, ranges in thresholds.items():
            if metric in patient_data.columns:
                normal_range = ranges.get('normal', [])
                if len(normal_range) == 2:
                    fig.add_trace(
                        go.Scatter(
                            x=patient_data['date'],
                            y=[normal_range[1]] * len(patient_data),
                            fill=None,
                            mode='lines',
                            line=dict(color='green', width=0),
                            showlegend=False,
                            name=f'{metric} Upper Normal'
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=patient_data['date'],
                            y=[normal_range[0]] * len(patient_data),
                            fill='tonexty',
                            mode='lines',
                            line=dict(color='green', width=0),
                            fillcolor='rgba(0,255,0,0.2)',
                            name=f'{metric} Normal Range'
                        )
                    )
                
                # Add patient data
                fig.add_trace(
                    go.Scatter(
                        x=patient_data['date'],
                        y=patient_data[metric],
                        mode='lines+markers',
                        name=metric,
                        line=dict(width=3)
                    )
                )
        
        fig.update_layout(
            title='Cardiac Risk Assessment',
            xaxis_title='Date',
            yaxis_title='Value',
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def create_real_time_monitoring_dashboard(self, real_time_data: pd.DataFrame):
        """Create real-time monitoring dashboard"""
        if real_time_data.empty:
            return None
            
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Real-time Heart Rate',
                'HRV Live Monitoring',
                'Activity Level',
                'Stress Indicator'
            )
        )
        
        # Real-time heart rate with anomaly detection
        hr_data = real_time_data[real_time_data['metric'] == 'heart_rate']
        if not hr_data.empty:
            fig.add_trace(
                go.Scatter(x=hr_data['timestamp'], y=hr_data['value'],
                          mode='lines', name='Heart Rate',
                          line=dict(color='red', width=2)),
                row=1, col=1
            )
        
        # HRV monitoring
        hrv_data = real_time_data[real_time_data['metric'] == 'hrv']
        if not hrv_data.empty:
            fig.add_trace(
                go.Scatter(x=hrv_data['timestamp'], y=hrv_data['value'],
                          mode='lines', name='HRV',
                          line=dict(color='blue', width=2)),
                row=1, col=2
            )
        
        # Activity
        activity_data = real_time_data[real_time_data['metric'] == 'activity']
        if not activity_data.empty:
            fig.add_trace(
                go.Bar(x=activity_data['timestamp'], y=activity_data['value'],
                      name='Activity', marker_color='orange'),
                row=2, col=1
            )
        
        # Stress indicator (calculated)
        if 'stress' in real_time_data['metric'].values:
            stress_data = real_time_data[real_time_data['metric'] == 'stress']
            fig.add_trace(
                go.Scatter(x=stress_data['timestamp'], y=stress_data['value'],
                          mode='lines', name='Stress Level',
                          line=dict(color='purple', width=2)),
                row=2, col=2
            )
        
        fig.update_layout(
            title='Real-time Health Monitoring Dashboard',
            height=600,
            showlegend=True,
            template='plotly_dark'
        )
        
        return fig

    def create_weekly_activity_pattern(self, activity_data: pd.DataFrame):
        """Create weekly activity pattern visualization"""
        if activity_data.empty:
            return None
        
        # Extract day of week and hour
        activity_data['day_of_week'] = activity_data['timestamp'].dt.day_name()
        activity_data['hour'] = activity_data['timestamp'].dt.hour
        
        # Pivot for heatmap
        weekly_pattern = activity_data.pivot_table(
            values='value',
            index='hour',
            columns='day_of_week',
            aggfunc='mean'
        )
        
        # Reorder columns to start with Monday
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_pattern = weekly_pattern.reindex(columns=days_order)
        
        fig = px.imshow(
            weekly_pattern,
            labels=dict(x="Day of Week", y="Hour of Day", color="Activity Level"),
            x=weekly_pattern.columns,
            y=[f"{h:02d}:00" for h in weekly_pattern.index],
            color_continuous_scale='Viridis',
            aspect="auto"
        )
        
        fig.update_layout(
            title='Weekly Activity Pattern Heatmap',
            height=500
        )
        
        return fig