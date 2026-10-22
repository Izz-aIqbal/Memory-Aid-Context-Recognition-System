"""
Database Manager for Memory Aid System
Handles all SQLite database operations
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="memory_aid/database/memory_aid.db"):
        self.db_path = db_path
        # Create database directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Objects Detection Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS object_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                location TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frame_id INTEGER
            )
        """)
        
        # Activity Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER
            )
        """)
        
        # Reminders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_type TEXT NOT NULL,
                object_name TEXT,
                activity_name TEXT,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sent_at DATETIME,
                is_sent BOOLEAN DEFAULT 0,
                is_acknowledged BOOLEAN DEFAULT 0
            )
        """)
        
        # User Tasks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                description TEXT,
                due_time TIME,
                is_completed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        """)
        
        # System Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_object_detection(self, object_name, confidence, location=None, frame_id=None):
        """Log detected object"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO object_detections (object_name, confidence, location, frame_id)
            VALUES (?, ?, ?, ?)
        """, (object_name, confidence, location, frame_id))
        conn.commit()
        conn.close()
    
    def log_activity(self, activity_name, confidence, duration=None):
        """Log detected activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activity_log (activity_name, confidence, duration)
            VALUES (?, ?, ?)
        """, (activity_name, confidence, duration))
        conn.commit()
        conn.close()
    
    def add_reminder(self, reminder_type, message, object_name=None, activity_name=None):
        """Add a reminder to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (reminder_type, object_name, activity_name, message)
            VALUES (?, ?, ?, ?)
        """, (reminder_type, object_name, activity_name, message))
        conn.commit()
        reminder_id = cursor.lastrowid
        conn.close()
        return reminder_id
    
    def mark_reminder_sent(self, reminder_id):
        """Mark a reminder as sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders SET is_sent = 1, sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reminder_id,))
        conn.commit()
        conn.close()
    
    def get_pending_reminders(self):
        """Get all unsent reminders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, message, reminder_type FROM reminders
            WHERE is_sent = 0
            ORDER BY created_at ASC
        """)
        reminders = cursor.fetchall()
        conn.close()
        return reminders
    
    def get_recent_objects(self, minutes=5, limit=10):
        """Get recently detected objects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        cursor.execute("""
            SELECT DISTINCT object_name, MAX(confidence) as max_confidence, 
                   MAX(timestamp) as last_seen
            FROM object_detections
            WHERE timestamp > ?
            GROUP BY object_name
            ORDER BY last_seen DESC
            LIMIT ?
        """, (time_threshold, limit))
        objects = cursor.fetchall()
        conn.close()
        return objects
    
    def get_recent_activities(self, minutes=5, limit=5):
        """Get recently detected activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        time_threshold = datetime.now() - timedelta(minutes=minutes)
        cursor.execute("""
            SELECT activity_name, MAX(confidence) as max_confidence,
                   MAX(timestamp) as last_seen
            FROM activity_log
            WHERE timestamp > ?
            GROUP BY activity_name
            ORDER BY last_seen DESC
            LIMIT ?
        """, (time_threshold, limit))
        activities = cursor.fetchall()
        conn.close()
        return activities
    
    def add_task(self, task_name, description=None, due_time=None):
        """Add a new task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_tasks (task_name, description, due_time)
            VALUES (?, ?, ?)
        """, (task_name, description, due_time))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id
    
    def get_pending_tasks(self):
        """Get all incomplete tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, task_name, description, due_time
            FROM user_tasks
            WHERE is_completed = 0
            ORDER BY due_time ASC
        """)
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def complete_task(self, task_id):
        """Mark a task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_tasks
            SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id,))
        conn.commit()
        conn.close()
    
    def log_system_event(self, log_level, message):
        """Log a system event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_logs (log_level, message)
            VALUES (?, ?)
        """, (log_level, message))
        conn.commit()
        conn.close()
    
    def get_statistics(self, hours=24):
        """Get system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        # Most detected objects
        cursor.execute("""
            SELECT object_name, COUNT(*) as count
            FROM object_detections
            WHERE timestamp > ?
            GROUP BY object_name
            ORDER BY count DESC
            LIMIT 5
        """, (time_threshold,))
        objects = cursor.fetchall()
        
        # Most detected activities
        cursor.execute("""
            SELECT activity_name, COUNT(*) as count
            FROM activity_log
            WHERE timestamp > ?
            GROUP BY activity_name
            ORDER BY count DESC
            LIMIT 5
        """, (time_threshold,))
        activities = cursor.fetchall()
        
        # Reminders sent
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM reminders
            WHERE sent_at > ?
        """, (time_threshold,))
        reminders_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "objects": objects,
            "activities": activities,
            "reminders_sent": reminders_count
        }
    
    def cleanup_old_data(self, days=30):
        """Remove old data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("DELETE FROM object_detections WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM activity_log WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM system_logs WHERE timestamp < ?", (cutoff_date,))
        
        conn.commit()
        conn.close()
