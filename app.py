"""
Main Application - Memory Aid with Context Recognition
Integrates object detection, activity recognition, and reminder system
"""

import cv2
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    CONFIDENCE_THRESHOLD, NMS_THRESHOLD, YOLO_MODEL,
    ACTIVITY_DETECTION_ENABLED, MOTION_THRESHOLD, FRAME_BUFFER_SIZE,
    REMINDER_COOLDOWN, VOICE_ENABLED, TEXT_ENABLED
)
from database.db_manager import DatabaseManager
from modules.object_detector import ObjectDetector, MockObjectDetector
from modules.activity_recognizer import ActivityRecognizer, MockActivityRecognizer
from modules.reminder_engine import ReminderEngine, MockReminderEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryAidSystem:
    """
    Main Memory Aid System
    Combines object detection, activity recognition, and reminders
    """
    
    def __init__(self, use_mock=False, use_webcam=True, video_path=None):
        """
        Initialize the Memory Aid System
        
        Args:
            use_mock: Use mock models for testing
            use_webcam: Use webcam as input source
            video_path: Path to video file (alternative to webcam)
        """
        logger.info("Initializing Memory Aid System...")
        
        # Database
        self.db_manager = DatabaseManager()
        logger.info("✓ Database initialized")
        
        # Models - Always try to use real YOLOv8 first
        # Initialize detector - REAL detection only
        try:
            logger.info("Loading YOLOv8 object detection model (REAL MODE)...")
            self.detector = ObjectDetector()
            logger.info("✓ Real YOLOv8 model loaded - NO MOCK DATA")
        except Exception as e:
            logger.error(f"ERROR: Real detection failed: {e}")
            logger.error("STOPPING: Cannot run with mock data - need real YOLOv8")
            raise RuntimeError("Real detection required")
        
        # Activity recognizer
        if use_mock:
            self.activity_recognizer = MockActivityRecognizer()
        else:
            self.activity_recognizer = ActivityRecognizer(motion_threshold=MOTION_THRESHOLD)
        logger.info("✓ Activity recognizer initialized")
        
        # Reminder engine
        if use_mock:
            self.reminder_engine = MockReminderEngine(self.db_manager, voice_enabled=VOICE_ENABLED)
        else:
            self.reminder_engine = ReminderEngine(self.db_manager, voice_enabled=VOICE_ENABLED)
        logger.info("✓ Reminder engine initialized")
        
        # Video input
        self.use_webcam = use_webcam
        self.video_path = video_path
        self.cap = None
        self.initialize_video_source()
        
        # Frame tracking
        self.frame_count = 0
        self.fps_start_time = datetime.now()
        self.current_fps = 0
        
        # Reminder display system
        self.active_reminders = []  # List of active reminders to display
        self.reminder_display_time = {}  # Track when reminders were shown
        self.reminder_duration = 5  # Show reminders for 5 seconds
        
        logger.info("✓ Memory Aid System initialized successfully!")
    
    def initialize_video_source(self):
        """Initialize video input (webcam or file)"""
        try:
            if self.use_webcam:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Cannot open webcam")
                logger.info("✓ Webcam initialized")
            elif self.video_path:
                self.cap = cv2.VideoCapture(self.video_path)
                if not self.cap.isOpened():
                    raise Exception(f"Cannot open video file: {self.video_path}")
                logger.info(f"✓ Video file loaded: {self.video_path}")
        except Exception as e:
            logger.error(f"Error initializing video source: {e}")
            raise
    
    def process_frame(self, frame):
        """
        Process a single frame through the entire pipeline
        
        Args:
            frame: Input frame from camera
            
        Returns:
            annotated_frame: Frame with annotations
            results: Detection and activity results
        """
        if frame is None or frame.size == 0:
            return frame, {}
        
        try:
            # Object detection
            detections, annotated_frame = self.detector.detect(frame)
            
            # Activity recognition
            activity = "idle"
            activity_conf = 0.5
            
            if ACTIVITY_DETECTION_ENABLED:
                motion_level, _ = self.activity_recognizer.detect_motion(frame)
                activity, activity_conf = self.activity_recognizer.recognize_activity(
                    frame, detections, motion_level
                )
                
                # Log activity
                self.db_manager.log_activity(activity, activity_conf)
            
            # Process detections and generate reminders
            current_time = datetime.now()
            for detection in detections:
                obj_name = detection['class_name']
                confidence = detection['confidence']
                
                # Log object detection
                location = self.detector.get_object_location(frame.shape, detection)
                self.db_manager.log_object_detection(obj_name, confidence, location=location)
                
                # Generate reminders for important objects (lowered threshold to 0.5)
                if confidence > 0.5:  # Lowered from 0.95 to show more reminders
                    important_objects = ['keys', 'phone', 'wallet', 'glasses', 'watch', 'laptop', 'bag', 'backpack', 
                                       'person', 'book', 'cup', 'bottle', 'mouse', 'keyboard']
                    if any(obj.lower() in obj_name.lower() for obj in important_objects):
                        reminder = self.reminder_engine.generate_object_reminder(
                            obj_name, location, detections
                        )
                        if reminder:
                            self.reminder_engine.send_reminder(reminder)
                            # Add to active reminders for on-screen display
                            reminder_key = f"{reminder['type']}_{obj_name}"
                            if reminder_key not in self.reminder_display_time:
                                self.active_reminders.append(reminder)
                                self.reminder_display_time[reminder_key] = current_time
                                logger.info(f"📢 Reminder added: {reminder['message']}")
            
            # Clean up old reminders (older than display duration)
            reminders_to_keep = []
            keys_to_remove = []
            
            for key, display_time in self.reminder_display_time.items():
                elapsed = (current_time - display_time).total_seconds()
                if elapsed >= self.reminder_duration:
                    keys_to_remove.append(key)
            
            # Remove expired reminder keys
            for key in keys_to_remove:
                del self.reminder_display_time[key]
            
            # Keep only active reminders
            for r in self.active_reminders:
                # Try to find matching key
                found = False
                for key in self.reminder_display_time.keys():
                    if r.get('type') in key and (current_time - self.reminder_display_time[key]).total_seconds() < self.reminder_duration:
                        found = True
                        break
                if found:
                    reminders_to_keep.append(r)
            
            self.active_reminders = reminders_to_keep[:5]  # Keep max 5 reminders
            
            # Generate activity reminders - DISABLED to reduce spam
            # activity_reminder_types = ['sitting', 'standing', 'working', 'reading', 'walking', 'running']
            # if activity in activity_reminder_types:
            #     reminder = self.reminder_engine.generate_activity_reminder(activity)
            #     if reminder:
            #         self.reminder_engine.send_reminder(reminder)
            
            # Draw additional info on frame
            annotated_frame = self._draw_info(
                annotated_frame, detections, activity, activity_conf
            )
            
            return annotated_frame, {
                'detections': detections,
                'detection_count': len(detections),
                'activity': activity,
                'activity_confidence': activity_conf,
                'frame_count': self.frame_count
            }
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame, {}
    
    def _draw_info(self, frame, detections, activity, activity_conf):
        """Draw information on frame"""
        h, w = frame.shape[:2]
        
        # FPS
        elapsed = (datetime.now() - self.fps_start_time).total_seconds()
        if elapsed > 1:
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = datetime.now()
        
        # Background panel for info (semi-transparent)
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (400, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # FPS
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Object count
        cv2.putText(frame, f"Objects Detected: {len(detections)}", (10, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Show detected objects list
        if detections:
            y_offset = 90
            unique_objects = {}
            for det in detections:
                obj_name = det['class_name']
                conf = det['confidence']
                if obj_name not in unique_objects or conf > unique_objects[obj_name]:
                    unique_objects[obj_name] = conf
            
            for idx, (obj_name, conf) in enumerate(list(unique_objects.items())[:5]):  # Show top 5
                text = f"  - {obj_name} ({conf:.2f})"
                cv2.putText(frame, text, (10, y_offset + idx * 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        else:
            cv2.putText(frame, "No objects detected", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
        
        # Activity
        cv2.putText(frame, f"Activity: {activity} ({activity_conf:.2f})",
                   (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (w-300, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw reminders on screen (right side)
        if self.active_reminders:
            reminder_y = 60
            reminder_panel_width = 450
            reminder_panel_height = min(150, len(self.active_reminders) * 40 + 20)
            
            # Reminder panel background
            overlay2 = frame.copy()
            cv2.rectangle(overlay2, (w - reminder_panel_width - 10, 50), 
                          (w - 10, 50 + reminder_panel_height), (0, 0, 255), -1)
            cv2.addWeighted(overlay2, 0.7, frame, 0.3, 0, frame)
            
            # Reminder title
            cv2.putText(frame, "ACTIVE REMINDERS:", (w - reminder_panel_width, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show reminders
            for idx, reminder in enumerate(self.active_reminders[:3]):  # Show max 3 reminders
                message = reminder.get('message', '')
                # Truncate long messages
                if len(message) > 50:
                    message = message[:47] + "..."
                
                y_pos = 100 + idx * 35
                cv2.putText(frame, f"  {idx+1}. {message}", 
                           (w - reminder_panel_width + 5, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        return frame
    
    def run(self, display=True, max_frames=None):
        """
        Run the main system loop
        
        Args:
            display: Show video output
            max_frames: Maximum frames to process (None for infinite)
        """
        if self.cap is None:
            logger.error("Video source not initialized")
            return
        
        logger.info("Starting main loop... Press 'Q' to quit")
        logger.info("=" * 60)
        logger.info("Video window should appear now with real detections...")
        
        frame_count = 0
        detection_history = []
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.info("Video stream ended")
                    break
                
                if frame is None or frame.size == 0:
                    continue
                
                # Resize frame for faster processing
                frame = cv2.resize(frame, (1024, 768))
                h, w = frame.shape[:2]
                
                # Process frame
                self.frame_count += 1
                annotated_frame, results = self.process_frame(frame)
                
                # Update FPS counter
                elapsed = (datetime.now() - self.fps_start_time).total_seconds()
                if elapsed > 1:
                    self.current_fps = self.frame_count / elapsed
                    self.frame_count = 0
                    self.fps_start_time = datetime.now()
                
                # Ensure annotated_frame is valid before displaying
                if annotated_frame is not None and annotated_frame.size > 0:
                    # Display
                    if display:
                        try:
                            cv2.imshow('Memory Aid - Real-Time Object Detection', annotated_frame)
                        except Exception as e:
                            logger.error(f"Display error: {e}")
                    
                    # Check for quit command (non-blocking)
                    key = cv2.waitKey(30) & 0xFF
                    if key == ord('q') or key == ord('Q') or key == 27:  # 'q', 'Q', or ESC
                        logger.info("User quit")
                        break
                frame_count += 1
                
                # Log detection info every 10 frames
                if frame_count % 10 == 0:
                    det_count = results.get('detection_count', 0)
                    activity = results.get('activity', 'unknown')
                    conf = results.get('activity_confidence', 0)
                    
                    logger.info(f"Frame {frame_count} | FPS: {self.current_fps:.1f} | "
                              f"Objects: {det_count} | Activity: {activity} ({conf:.2f})")
                    
                    # Show detected objects
                    detections = results.get('detections', [])
                    if detections:
                        obj_names = [d['class_name'] for d in detections]
                        logger.info(f"  → Detected: {', '.join(obj_names)}")
                
                # Periodic detailed logging
                if frame_count % 100 == 0:
                    logger.info("-" * 60)
                    db_stats = self.db_manager.get_statistics(hours=1)
                    logger.info(f"Statistics (last hour):")
                    logger.info(f"  Unique Objects: {len(db_stats['objects'])}")
                    logger.info(f"  Unique Activities: {len(db_stats['activities'])}")
                    logger.info(f"  Reminders Sent: {db_stats['reminders_sent']}")
                    logger.info("-" * 60)
                
                # Max frames limit
                if max_frames and frame_count >= max_frames:
                    logger.info(f"Reached max frames limit: {max_frames}")
                    break
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Cleanup complete")
    
    def run_headless(self, duration_minutes=None):
        """
        Run system without display (for server/headless mode)
        
        Args:
            duration_minutes: How long to run (None for infinite)
        """
        logger.info("Running in headless mode...")
        
        if self.cap is None:
            logger.error("Video source not initialized")
            return
        
        frame_count = 0
        start_time = datetime.now()
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.resize(frame, (640, 480))
                _, results = self.process_frame(frame)
                
                frame_count += 1
                
                if frame_count % 50 == 0:
                    logger.info(f"Processed {frame_count} frames")
                
                # Check duration
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        logger.info(f"Duration limit reached: {duration_minutes} minutes")
                        break
        
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Memory Aid with Context Recognition')
    parser.add_argument('--mock', action='store_true', help='Use mock models')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--headless', action='store_true', help='Run without display')
    parser.add_argument('--duration', type=int, help='Run duration in minutes')
    parser.add_argument('--no-voice', action='store_true', help='Disable voice reminders')
    
    args = parser.parse_args()
    
    try:
        # Initialize system
        use_webcam = not args.video
        system = MemoryAidSystem(
            use_mock=args.mock,
            use_webcam=use_webcam,
            video_path=args.video
        )
        
        # Run
        if args.headless:
            system.run_headless(duration_minutes=args.duration)
        else:
            system.run(display=True, max_frames=None)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
