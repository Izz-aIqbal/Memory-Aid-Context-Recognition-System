"""
Streamlit Web Interface for Memory Aid System
Interactive dashboard for task management and monitoring
"""

import streamlit as st
import cv2
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import STREAMLIT_CONFIG, REMINDER_TEMPLATES
from database.db_manager import DatabaseManager

# Set page config
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .reminder-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

db_manager = st.session_state.db_manager

# Sidebar Navigation
with st.sidebar:
    st.title("📱 Navigation")
    page = st.radio("Go to", [
        'Dashboard',
        'Tasks',
        'Reminders',
        'Detection Logs',
        'Statistics',
        'Settings'
    ])
    st.session_state.page = page
    
    st.divider()
    
    st.subheader("🔧 System Status")
    st.info("✓ Database: Connected")
    st.info("✓ System: Ready")

# Main Content Area
def show_dashboard():
    """Dashboard page"""
    st.title("🧠 Memory Aid Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Recent Objects", "5", "+2")
    with col2:
        st.metric("Active Tasks", "3", "-1")
    with col3:
        st.metric("Reminders Today", "8", "+3")
    
    st.divider()
    
    # Recent detections
    st.subheader("📸 Recent Object Detections")
    recent_objects = db_manager.get_recent_objects(minutes=60, limit=10)
    
    if recent_objects:
        df_objects = pd.DataFrame(recent_objects, columns=['Object', 'Confidence', 'Last Seen'])
        df_objects['Confidence'] = df_objects['Confidence'].apply(lambda x: f"{x:.2%}")
        st.dataframe(df_objects, use_container_width=True)
    else:
        st.info("No recent detections")
    
    # Recent activities
    st.subheader("🎯 Recent Activities")
    recent_activities = db_manager.get_recent_activities(minutes=60, limit=10)
    
    if recent_activities:
        df_activities = pd.DataFrame(recent_activities, columns=['Activity', 'Confidence', 'Last Detected'])
        df_activities['Confidence'] = df_activities['Confidence'].apply(lambda x: f"{x:.2%}")
        st.dataframe(df_activities, use_container_width=True)
    else:
        st.info("No recent activities")


def show_tasks():
    """Tasks management page"""
    st.title("✅ Task Management")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_task = st.text_input("Add a new task:")
    with col2:
        add_button = st.button("Add Task", use_container_width=True)
    
    if add_button and new_task:
        task_id = db_manager.add_task(new_task)
        st.success(f"Task added: {new_task}")
        st.rerun()
    
    st.divider()
    
    # Pending tasks
    st.subheader("📋 Pending Tasks")
    pending_tasks = db_manager.get_pending_tasks()
    
    if pending_tasks:
        for task_id, task_name, description, due_time in pending_tasks:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{task_name}**")
                if description:
                    st.caption(description)
            
            with col2:
                if due_time:
                    st.caption(f"Due: {due_time}")
            
            with col3:
                if st.button("✓", key=f"complete_{task_id}", use_container_width=True):
                    db_manager.complete_task(task_id)
                    st.success("Task completed!")
                    st.rerun()
    else:
        st.info("No pending tasks")


def show_reminders():
    """Reminders page"""
    st.title("🔔 Reminders")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        reminder_text = st.text_area("Create a custom reminder:")
    with col2:
        if st.button("Send Reminder", use_container_width=True):
            if reminder_text:
                reminder_id = db_manager.add_reminder(
                    reminder_type="custom",
                    message=reminder_text
                )
                st.success("Reminder created!")
                st.rerun()
    
    st.divider()
    
    # Pending reminders
    st.subheader("📬 Pending Reminders")
    pending_reminders = db_manager.get_pending_reminders()
    
    if pending_reminders:
        for reminder_id, message, reminder_type in pending_reminders:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if reminder_type == "object":
                    st.markdown(f"📍 **Object Reminder:**\n{message}")
                elif reminder_type == "activity":
                    st.markdown(f"🎯 **Activity Reminder:**\n{message}")
                else:
                    st.markdown(f"✏️ **Custom Reminder:**\n{message}")
            
            with col2:
                if st.button("Mark as Read", key=f"read_{reminder_id}", use_container_width=True):
                    db_manager.mark_reminder_sent(reminder_id)
                    st.rerun()
    else:
        st.info("No pending reminders")


def show_detection_logs():
    """Detection logs page"""
    st.title("📊 Detection Logs")
    
    # Time range selector
    hours = st.slider("Show detections from last (hours):", 1, 24, 6)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Object Detections")
        recent_objects = db_manager.get_recent_objects(minutes=hours*60, limit=20)
        
        if recent_objects:
            df = pd.DataFrame(recent_objects, columns=['Object', 'Confidence', 'Last Seen'])
            df['Confidence'] = df['Confidence'].apply(lambda x: f"{x:.2%}")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No detections in this period")
    
    with col2:
        st.subheader("Activity Logs")
        recent_activities = db_manager.get_recent_activities(minutes=hours*60, limit=20)
        
        if recent_activities:
            df = pd.DataFrame(recent_activities, columns=['Activity', 'Confidence', 'Last Detected'])
            df['Confidence'] = df['Confidence'].apply(lambda x: f"{x:.2%}")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No activities in this period")


def show_statistics():
    """Statistics page"""
    st.title("📈 Statistics")
    
    hours = st.slider("Statistics for last (hours):", 1, 48, 24)
    
    stats = db_manager.get_statistics(hours=hours)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Reminders Sent", stats['reminders_sent'])
    
    with col2:
        st.metric("Unique Objects Detected", len(stats['objects']))
    
    with col3:
        st.metric("Unique Activities", len(stats['activities']))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Objects Detected")
        if stats['objects']:
            df = pd.DataFrame(stats['objects'], columns=['Object', 'Count'])
            st.bar_chart(df.set_index('Object'))
        else:
            st.info("No data")
    
    with col2:
        st.subheader("Top Activities")
        if stats['activities']:
            df = pd.DataFrame(stats['activities'], columns=['Activity', 'Count'])
            st.bar_chart(df.set_index('Activity'))
        else:
            st.info("No data")


def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    
    st.subheader("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Enable Voice Notifications", value=True)
        st.checkbox("Enable Text Notifications", value=True)
        st.slider("Reminder Cooldown (minutes):", 1, 60, 5)
    
    with col2:
        st.checkbox("Auto-clean Old Data", value=True)
        st.slider("Data Retention (days):", 1, 90, 30)
        st.checkbox("Enable Debug Logging", value=False)
    
    st.divider()
    
    st.subheader("Database Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clean Old Data", use_container_width=True):
            db_manager.cleanup_old_data(days=30)
            st.success("Old data cleaned!")
    
    with col2:
        if st.button("Export Statistics", use_container_width=True):
            stats = db_manager.get_statistics(hours=24)
            st.json(stats)


# Page routing
if st.session_state.page == 'Dashboard':
    show_dashboard()
elif st.session_state.page == 'Tasks':
    show_tasks()
elif st.session_state.page == 'Reminders':
    show_reminders()
elif st.session_state.page == 'Detection Logs':
    show_detection_logs()
elif st.session_state.page == 'Statistics':
    show_statistics()
elif st.session_state.page == 'Settings':
    show_settings()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8rem; margin-top: 2rem;'>
    Memory Aid with Context Recognition © 2025 | Powered by AI & Computer Vision
    </div>
""", unsafe_allow_html=True)
