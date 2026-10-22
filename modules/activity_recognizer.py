"""
Activity Recognition Module
Infers user activities based on motion and frame analysis
"""

import cv2
import numpy as np
import logging
from collections import deque
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityRecognizer:
    def __init__(self, activity_labels=None, motion_threshold=10):
        """
        Initialize activity recognizer
        
        Args:
            activity_labels: Dictionary of activity labels
            motion_threshold: Threshold for motion detection
        """
        self.activity_labels = activity_labels or {
            0: "sitting",
            1: "standing",
            2: "walking",
            3: "running",
            4: "reading",
            5: "working",
            6: "eating",
            7: "sleeping"
        }
        self.motion_threshold = motion_threshold
        self.prev_frame = None
        self.activity_history = deque(maxlen=30)
        self.current_activity = None
        self.activity_confidence = 0
        self.activity_start_time = None
    
    def detect_motion(self, frame):
        """
        Detect motion between frames
        
        Args:
            frame: Current frame
            
        Returns:
            motion_level: Level of motion detected
            motion_mask: Binary mask showing motion areas
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return 0, None
        
        # Calculate frame difference
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        _, motion_mask = cv2.threshold(frame_diff, self.motion_threshold, 255, cv2.THRESH_BINARY)
        
        # Count motion pixels
        motion_level = cv2.countNonZero(motion_mask)
        
        self.prev_frame = gray
        
        return motion_level, motion_mask
    
    def estimate_pose(self, frame, detections):
        """
        Estimate pose/posture from detected objects
        Based on person detection and bounding box analysis
        
        Args:
            frame: Input frame
            detections: Object detections from detector
            
        Returns:
            posture: Estimated posture (standing, sitting, etc.)
        """
        h, w = frame.shape[:2]
        
        # Find person detections
        people = [d for d in detections if d['class_name'] == 'person']
        
        if not people:
            return "unknown", 0.5
        
        person = people[0]
        x1, y1, x2, y2 = person['bbox']
        person_height = y2 - y1
        person_width = x2 - x1
        
        # Aspect ratio analysis
        aspect_ratio = person_height / (person_width + 1e-6)
        
        # Position analysis
        center_y = (y1 + y2) // 2
        
        confidence = person['confidence']
        
        # Simple heuristic-based posture estimation
        if aspect_ratio > 1.8:  # Tall and narrow = standing
            posture = "standing"
        elif aspect_ratio > 1.2:  # Medium = walking
            posture = "walking"
        else:  # Wide = sitting
            posture = "sitting"
        
        return posture, confidence
    
    def recognize_activity(self, frame, detections, motion_level):
        """
        Recognize activity based on multiple factors
        
        Args:
            frame: Input frame
            detections: Object detections
            motion_level: Level of motion detected
            
        Returns:
            activity: Recognized activity
            confidence: Confidence score
        """
        posture, posture_conf = self.estimate_pose(frame, detections)
        
        # Simple activity inference
        if motion_level > 5000:
            activity = "running"
            confidence = min(1.0, motion_level / 10000)
        elif motion_level > 2000:
            activity = "walking"
            confidence = min(1.0, motion_level / 5000)
        elif posture == "standing":
            activity = "standing"
            confidence = posture_conf
        elif posture == "sitting":
            # Check if reading or working
            if self._has_readable_object(detections):
                activity = "reading"
            else:
                activity = "working"
            confidence = posture_conf
        else:
            activity = "idle"
            confidence = 0.5
        
        # Store in history
        self.activity_history.append({
            'activity': activity,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
        
        # Update current activity (using majority voting)
        self.current_activity = activity
        self.activity_confidence = confidence
        
        if self.activity_start_time is None:
            self.activity_start_time = datetime.now()
        
        return activity, confidence
    
    def _has_readable_object(self, detections):
        """Check if frame contains readable objects"""
        readable_items = ['book', 'laptop', 'phone', 'tablet', 'monitor', 'screen']
        return any(d['class_name'].lower() in readable_items for d in detections)
    
    def get_activity_duration(self):
        """Get duration of current activity"""
        if self.activity_start_time:
            duration = (datetime.now() - self.activity_start_time).total_seconds()
            return duration
        return 0
    
    def get_activity_summary(self):
        """Get summary of recent activities"""
        if not self.activity_history:
            return []
        
        summary = {}
        for record in self.activity_history:
            activity = record['activity']
            if activity not in summary:
                summary[activity] = 0
            summary[activity] += 1
        
        return sorted(summary.items(), key=lambda x: x[1], reverse=True)
    
    def reset(self):
        """Reset activity tracking"""
        self.prev_frame = None
        self.activity_history.clear()
        self.current_activity = None
        self.activity_confidence = 0
        self.activity_start_time = None


# Mock Activity Recognizer for development
class MockActivityRecognizer:
    """Mock recognizer for development without complex ML models"""
    
    def __init__(self, activity_labels=None, motion_threshold=10):
        self.activity_labels = activity_labels or {
            0: "sitting", 1: "standing", 2: "walking"
        }
        self.current_activity = "sitting"
        self.activity_confidence = 0.85
        self.frame_count = 0
        self.activity_cycle = ["sitting", "working", "reading"]
        self.activity_index = 0
    
    def detect_motion(self, frame):
        """Simulate motion detection"""
        self.frame_count += 1
        # Vary motion based on activity
        if self.current_activity == "sitting":
            motion = 500 + (self.frame_count % 200)  # Low motion
        elif self.current_activity == "working":
            motion = 2000 + (self.frame_count % 500)  # Medium motion
        else:
            motion = 3000 + (self.frame_count % 800)  # Higher motion
        return motion, None
    
    def recognize_activity(self, frame, detections, motion_level):
        """Recognize activity with realistic patterns"""
        # Cycle through activities every 50 frames
        if self.frame_count % 50 == 0:
            self.activity_index = (self.activity_index + 1) % len(self.activity_cycle)
            self.current_activity = self.activity_cycle[self.activity_index]
        
        # Confidence slightly varies but stays stable
        confidence = 0.82 + (abs((self.frame_count % 30) - 15) / 150)
        
        return self.current_activity, min(0.95, confidence)
    
    def get_activity_duration(self):
        """Get activity duration"""
        return (self.frame_count // 50) * 5 + 5
    
    def get_activity_summary(self):
        """Get activity summary"""
        return [("sitting", 15), ("working", 10), ("reading", 8)]
    
    def reset(self):
        """Reset activity tracking"""
        self.frame_count = 0
        self.activity_index = 0
        self.current_activity = "sitting"
