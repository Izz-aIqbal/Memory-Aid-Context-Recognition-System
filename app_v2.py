"""
Memory Aid - Real-Time Object Detection System v2
Shows REAL webcam feed with actual YOLOv8 object detection
NO MOCK DATA - DEBUGGING MODE
"""

import cv2
import sys
import logging
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

# Import the improved detector
from modules.object_detector_v2 import ObjectDetector
from database.db_manager import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


class MemoryAidSystem:
    def __init__(self):
        logger.info("=" * 70)
        logger.info("MEMORY AID - REAL OBJECT DETECTION v2")
        logger.info("=" * 70)
        
        # Database
        self.db_manager = DatabaseManager()
        logger.info("✓ Database initialized")
        
        # Real YOLOv8 detector ONLY - with CPU optimization
        try:
            logger.info("Loading YOLOv8 model with CPU optimization...")
            self.detector = ObjectDetector(confidence_threshold=0.3)  # Lower threshold
            logger.info("✓ YOLOv8 model ready!")
        except Exception as e:
            logger.error(f"FATAL: Cannot load YOLOv8: {e}")
            raise
        
        # Webcam
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Cannot access webcam - check camera is connected")
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Single frame buffer
            
            logger.info("✓ Webcam initialized (640x480 @ 30fps)")
        except Exception as e:
            logger.error(f"FATAL: {e}")
            raise
        
        self.frame_count = 0
        self.detection_count = 0
        self.fps_time = datetime.now()
        self.fps = 0

    def run(self):
        """Main loop - show webcam with real object detection"""
        logger.info("=" * 70)
        logger.info("STARTING DETECTION")
        logger.info("Show phone, pen, or other objects to camera")
        logger.info("Press 'Q' or ESC to exit")
        logger.info("=" * 70)
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.info("Video stream ended")
                    break
                
                if frame is None or frame.size == 0:
                    logger.warning("Empty frame received")
                    continue
                
                # Resize for consistent processing
                frame = cv2.resize(frame, (640, 480))
                
                # REAL object detection
                try:
                    detections, annotated_frame = self.detector.detect(frame)
                    self.detection_count += len(detections)
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
                    except Exception as e:
                        logger.debug(f"DB logging error: {e}")
                
                # Calculate FPS
                self.frame_count += 1
                elapsed = (datetime.now() - self.fps_time).total_seconds()
                if elapsed > 1:
                    self.fps = self.frame_count / elapsed
                    self.frame_count = 0
                    self.fps_time = datetime.now()
                
                # Draw info on frame
                try:
                    cv2.putText(annotated_frame, f"FPS: {self.fps:.1f}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f"Detected: {len(detections)}", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, "YOLOv8 Real-Time", (10, 110),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Show detected objects
                    if detections:
                        obj_text = " | ".join([f"{d['class_name']} {d['confidence']:.0%}" for d in detections[:3]])
                        cv2.putText(annotated_frame, obj_text, (10, 480 - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                except Exception as e:
                    logger.debug(f"Draw error: {e}")
                
                # Display
                if annotated_frame is not None:
                    cv2.imshow('Memory Aid - Real Detection', annotated_frame)
                
                # Log every 30 frames
                if self.frame_count % 30 == 0 and self.frame_count > 0:
                    if detections:
                        obj_names = ', '.join([f"{d['class_name']}" for d in detections])
                        logger.info(f"✓ Frame {self.frame_count:>3} | FPS: {self.fps:>5.1f} | Objects: {len(detections):>2} → {obj_names}")
                    else:
                        logger.info(f"⊘ Frame {self.frame_count:>3} | FPS: {self.fps:>5.1f} | No objects detected")
                
                # Check for quit
                key = cv2.waitKey(1) & 0xFF
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
        logger.info(f"Total detections: {self.detection_count}")
        logger.info("Done")


if __name__ == "__main__":
    try:
        system = MemoryAidSystem()
        system.run()
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        exit(1)
