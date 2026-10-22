"""
Memory Aid with Context Recognition
An intelligent AI-powered system for remembering tasks, 
locating objects, and managing daily routines.
"""

__version__ = "1.0.0"
__author__ = "AI Project Team"
__description__ = "Memory Aid with Context Recognition using Object Detection and Activity Recognition"

from .database.db_manager import DatabaseManager
from .modules.object_detector import ObjectDetector, MockObjectDetector
from .modules.activity_recognizer import ActivityRecognizer, MockActivityRecognizer
from .modules.reminder_engine import ReminderEngine, MockReminderEngine

__all__ = [
    'DatabaseManager',
    'ObjectDetector',
    'MockObjectDetector',
    'ActivityRecognizer',
    'MockActivityRecognizer',
    'ReminderEngine',
    'MockReminderEngine'
]
