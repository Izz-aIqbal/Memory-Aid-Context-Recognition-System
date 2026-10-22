"""
Reminder Engine
Generates and manages intelligent context-aware reminders
"""

import logging
from datetime import datetime, timedelta
import pyttsx3
from queue import Queue
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReminderEngine:
    def __init__(self, db_manager, voice_enabled=True):
        """
        Initialize the reminder engine
        
        Args:
            db_manager: Database manager instance
            voice_enabled: Whether to use text-to-speech
        """
        self.db_manager = db_manager
        self.voice_enabled = voice_enabled
        self.reminder_queue = Queue()
        self.last_reminders = {}  # Track last reminder time for each object/activity
        self.reminder_cooldown = 30  # 30 seconds (reduced from 5 minutes for testing)
        self.tts_engine = None
        
        if self.voice_enabled:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
            except Exception as e:
                logger.warning(f"TTS initialization failed: {e}")
                self.voice_enabled = False
    
    def generate_object_reminder(self, object_name, location, detections):
        """
        Generate reminder for detected objects
        
        Args:
            object_name: Name of the object
            location: Location in frame (e.g., "left top")
            detections: All current detections
        """
        # Check cooldown
        key = f"object_{object_name}"
        if not self._check_cooldown(key):
            return None
        
        message = f"You left your {object_name} on the {location}"
        
        reminder_id = self.db_manager.add_reminder(
            reminder_type="object",
            message=message,
            object_name=object_name
        )
        
        return {
            'id': reminder_id,
            'type': 'object',
            'message': message,
            'timestamp': datetime.now()
        }
    
    def generate_activity_reminder(self, activity_name, duration=None):
        """
        Generate reminder based on activity
        
        Args:
            activity_name: Current activity
            duration: How long activity has been ongoing
        """
        key = f"activity_{activity_name}"
        if not self._check_cooldown(key):
            return None
        
        # Generate contextual reminders based on activity
        reminders = {
            "reading": "You've been reading for a while. Take a break and rest your eyes!",
            "working": "Don't forget to take a break and stretch!",
            "sitting": "You've been sitting for too long. Time to move around!",
            "standing": "You've been standing. Find a comfortable place to sit.",
            "eating": "Don't forget to drink water!",
            "sleeping": "Good rest! Time to wake up when ready.",
        }
        
        message = reminders.get(activity_name, f"You're currently {activity_name}")
        
        reminder_id = self.db_manager.add_reminder(
            reminder_type="activity",
            message=message,
            activity_name=activity_name
        )
        
        return {
            'id': reminder_id,
            'type': 'activity',
            'message': message,
            'timestamp': datetime.now()
        }
    
    def generate_task_reminder(self, task_name, task_id):
        """
        Generate reminder for pending tasks
        
        Args:
            task_name: Name of the task
            task_id: ID of the task
        """
        key = f"task_{task_id}"
        if not self._check_cooldown(key):
            return None
        
        message = f"Reminder: {task_name}"
        
        reminder_id = self.db_manager.add_reminder(
            reminder_type="task",
            message=message
        )
        
        return {
            'id': reminder_id,
            'type': 'task',
            'message': message,
            'timestamp': datetime.now()
        }
    
    def send_reminder(self, reminder):
        """
        Send a reminder (text and/or voice)
        
        Args:
            reminder: Reminder dictionary
        """
        if reminder is None:
            return
        
        message = reminder.get('message', '')
        reminder_id = reminder.get('id')
        
        try:
            # Text notification
            logger.info(f"🔔 REMINDER: {message}")
            
            # Voice notification
            if self.voice_enabled and self.tts_engine:
                try:
                    self._speak_async(message)
                except Exception as e:
                    logger.warning(f"TTS failed: {e}")
            
            # Mark as sent in database
            if reminder_id:
                self.db_manager.mark_reminder_sent(reminder_id)
        
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def _speak_async(self, message):
        """Speak message in a separate thread"""
        def speak():
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"Speech error: {e}")
        
        thread = threading.Thread(target=speak, daemon=True)
        thread.start()
    
    def _check_cooldown(self, key):
        """Check if reminder is on cooldown"""
        if key not in self.last_reminders:
            self.last_reminders[key] = datetime.now()
            return True
        
        last_time = self.last_reminders[key]
        if (datetime.now() - last_time).total_seconds() > self.reminder_cooldown:
            self.last_reminders[key] = datetime.now()
            return True
        
        return False
    
    def get_pending_reminders(self):
        """Get all pending reminders from database"""
        return self.db_manager.get_pending_reminders()
    
    def dismiss_all_reminders(self):
        """Dismiss all pending reminders"""
        self.last_reminders.clear()
        logger.info("All reminders dismissed")


# Mock Reminder Engine for development
class MockReminderEngine:
    """Mock reminder engine for testing without TTS"""
    
    def __init__(self, db_manager, voice_enabled=True):
        self.db_manager = db_manager
        self.voice_enabled = voice_enabled
        self.last_reminders = {}
        self.reminder_cooldown = 300
    
    def generate_object_reminder(self, object_name, location, detections):
        message = f"You left your {object_name} on the {location}"
        return {
            'id': 1,
            'type': 'object',
            'message': message,
            'timestamp': datetime.now()
        }
    
    def generate_activity_reminder(self, activity_name, duration=None):
        return {
            'id': 2,
            'type': 'activity',
            'message': f"You're {activity_name}",
            'timestamp': datetime.now()
        }
    
    def send_reminder(self, reminder):
        if reminder:
            logger.info(f"[REMINDER] {reminder['message']}")
    
    def get_pending_reminders(self):
        return []
