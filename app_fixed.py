"""
Memory Aid - Real-Time Object Detection System
Shows REAL webcam feed with actual YOLOv8 object detection
NO MOCK DATA - NO REMINDERS - JUST DETECTION
"""

import cv2
import sys
import logging
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIDENCE_THRESHOLD, YOLO_MODEL
from database.db_manager import DatabaseManager
from modules.object_detector import ObjectDetector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


class MemoryAidSystem:
    def __init__(self):
        logger.info("Initializing Memory Aid System...")
        
        # Database
        self.db_manager = DatabaseManager()
        logger.info("✓ Database initialized")
        
        # Real YOLOv8 detector ONLY
        try:
            logger.info("Loading YOLOv8 model...")
            self.detector = ObjectDetector()
            logger.info("✓ YOLOv8 model loaded successfully!")
        except Exception as e:
            logger.error(f"FATAL: Cannot load YOLOv8: {e}")
            raise
        
        # Webcam
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Cannot access webcam - check camera is connected")
            logger.info("✓ Webcam ready")
        except Exception as e:
            logger.error(f"FATAL: {e}")
            raise
        
        self.frame_count = 0
        self.fps_time = datetime.now()
        self.fps = 0

    def run(self):
        """Main loop - show webcam with real object detection only"""
        logger.info("=" * 70)
        logger.info("REAL-TIME OBJECT DETECTION - PRESS 'Q' TO EXIT")
        logger.info("=" * 70)
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.info("Video stream ended")
                    break
                
                # Resize for faster processing
                frame = cv2.resize(frame, (1024, 768))
                
                # REAL object detection
                try:
                    detections, annotated_frame = self.detector.detect(frame)
                except Exception as e:
                    logger.error(f"Detection error: {e}")
                    annotated_frame = frame
                    detections = []
                
                # Log detections to database
                for det in detections:
                    try:
                        location = self.detector.get_object_location(frame.shape, det)
                        self.db_manager.log_object_detection(
                            det['class_name'], 
                            det['confidence'], 
                            location=location
                        )
                    except:
                        pass
                
                # Calculate FPS
                self.frame_count += 1
                elapsed = (datetime.now() - self.fps_time).total_seconds()
                if elapsed > 1:
                    self.fps = self.frame_count / elapsed
                    self.frame_count = 0
                    self.fps_time = datetime.now()
                
                # Draw info on frame
                cv2.putText(annotated_frame, f"FPS: {self.fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Objects: {len(detections)}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(annotated_frame, "REAL YOLOv8 Detection", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Display
                if annotated_frame is not None:
                    cv2.imshow('Memory Aid - Real Detection', annotated_frame)
                
                # Log every 10 frames
                if self.frame_count % 10 == 0 and self.frame_count > 0:
                    obj_names = ', '.join([d['class_name'] for d in detections])
                    logger.info(f"Frame {self.frame_count:>4} | FPS: {self.fps:>5.1f} | Objects: {len(detections):>2} | {obj_names}")
                
                # Check for quit
                key = cv2.waitKey(30) & 0xFF
                if key == ord('q') or key == ord('Q') or key == 27:
                    logger.info("User quit")
                    break
        
        except KeyboardInterrupt:
            logger.info("Interrupted")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        logger.info("Cleaning up...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Done")


if __name__ == "__main__":
    try:
        system = MemoryAidSystem()
        system.run()
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        exit(1)
