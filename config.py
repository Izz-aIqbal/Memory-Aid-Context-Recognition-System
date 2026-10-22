"""
Configuration settings for Memory Aid with Context Recognition
"""

# Object Detection Settings
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4
YOLO_MODEL = "yolov8n.pt"  # nano model for faster inference

# Activity Recognition Settings
ACTIVITY_DETECTION_ENABLED = True
MOTION_THRESHOLD = 10
FRAME_BUFFER_SIZE = 30

# Reminder Settings
REMINDER_COOLDOWN = 600  # seconds (10 minutes - increased to reduce spam)
VOICE_ENABLED = False  # Disable voice to reduce spam in testing
TEXT_ENABLED = True
NOTIFICATION_DURATION = 5  # seconds

# Database Settings
DB_PATH = "memory_aid/database/memory_aid.db"
LOG_RETENTION_DAYS = 30

# Common Objects to Detect
IMPORTANT_OBJECTS = [
    "person", "keys", "phone", "wallet", "laptop", "backpack",
    "book", "glasses", "watch", "wallet", "door", "table",
    "chair", "car", "cup", "bottle", "mouse", "keyboard"
]

# Activity Labels
ACTIVITIES = {
    0: "sitting",
    1: "standing",
    2: "walking",
    3: "running",
    4: "reading",
    5: "working",
    6: "eating",
    7: "sleeping"
}

# Reminder Templates
REMINDER_TEMPLATES = {
    "object_location": "You left your {object} on the {location}",
    "activity_time": "It's time to {activity}",
    "activity_reminder": "You're currently {activity}. Don't forget!",
    "object_missing": "Your {object} hasn't been detected for {minutes} minutes",
}

# UI Settings
STREAMLIT_CONFIG = {
    "page_title": "Memory Aid with Context Recognition",
    "page_icon": "🧠",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
