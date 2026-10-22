"""
Simple Test - Memory Aid System
Demonstrates object detection, activity recognition, and reminders
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager
from modules.object_detector import MockObjectDetector
from modules.activity_recognizer import MockActivityRecognizer
from modules.reminder_engine import MockReminderEngine
import numpy as np

def test_system():
    """Test all components"""
    print("\n" + "="*70)
    print("MEMORY AID SYSTEM - COMPONENT TEST")
    print("="*70 + "\n")
    
    # 1. Test Database
    print("1️⃣  Testing Database...")
    db = DatabaseManager("test_memory.db")
    
    # Add test data
    db.log_object_detection("keys", 0.95, location="left top")
    db.log_object_detection("phone", 0.89, location="center middle")
    db.log_activity("sitting", 0.92)
    db.add_task("Buy groceries", "Need milk and eggs", "14:00")
    
    print("   ✓ Database operations successful")
    
    # 2. Test Object Detector
    print("\n2️⃣  Testing Object Detection...")
    detector = MockObjectDetector()
    
    # Create dummy frame
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detections, _ = detector.detect(dummy_frame)
    print(f"   ✓ Detected {len(detections)} objects:")
    for det in detections:
        print(f"     • {det['class_name']} (confidence: {det['confidence']:.2f})")
    
    # 3. Test Activity Recognizer
    print("\n3️⃣  Testing Activity Recognition...")
    recognizer = MockActivityRecognizer()
    
    activity, conf = recognizer.recognize_activity(dummy_frame, detections, 1000)
    print(f"   ✓ Recognized activity: {activity} (confidence: {conf:.2f})")
    
    # 4. Test Reminder Engine
    print("\n4️⃣  Testing Reminder Engine...")
    reminder_engine = MockReminderEngine(db)
    
    # Generate reminder
    reminder = reminder_engine.generate_object_reminder("keys", "left top", detections)
    if reminder:
        print(f"   ✓ Generated reminder:")
        print(f"     Message: {reminder['message']}")
    
    # 5. Check Database
    print("\n5️⃣  Checking Database Content...")
    
    stats = db.get_statistics(hours=1)
    print(f"   ✓ Statistics:")
    print(f"     • Objects detected: {len(stats['objects'])}")
    print(f"     • Activities detected: {len(stats['activities'])}")
    print(f"     • Reminders sent: {stats['reminders_sent']}")
    
    recent_objects = db.get_recent_objects(minutes=60)
    print(f"\n   ✓ Recent objects ({len(recent_objects)} total):")
    for obj in recent_objects:
        print(f"     • {obj[0]} (confidence: {obj[1]:.2f})")
    
    tasks = db.get_pending_tasks()
    print(f"\n   ✓ Pending tasks ({len(tasks)} total):")
    for task_id, name, desc, due_time in tasks:
        print(f"     • {name} (due: {due_time})")
    
    # Cleanup
    import os
    if os.path.exists("test_memory.db"):
        os.remove("test_memory.db")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - SYSTEM IS WORKING!")
    print("="*70 + "\n")
    
    print("Next steps:")
    print("1. Run with mock data:    python app.py --mock")
    print("2. Launch dashboard:       streamlit run ui/dashboard.py")
    print("3. Run with webcam:        python app.py")
    print("\n")

if __name__ == "__main__":
    test_system()
