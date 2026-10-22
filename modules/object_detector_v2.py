"""
Object Detection Module using YOLOv8 - CPU OPTIMIZED
Real-time object detection with proper CPU inference
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
from pathlib import Path
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObjectDetector:
    def __init__(self, model_name="yolov8n.pt", confidence_threshold=0.3):
        """
        Initialize the object detector with YOLOv8 model
        
        Args:
            model_name: Name of the YOLO model to use
            confidence_threshold: Minimum confidence for detection (lowered to 0.3)
        """
        try:
            logger.info(f"Loading {model_name} on CPU...")
            
            # Force CPU inference - no GPU
            device = 'cpu'
            logger.info(f"Using device: {device}")
            
            # Load model
            self.model = YOLO(model_name)
            self.model.to(device)
            
            # Lower threshold to catch more objects
            self.confidence_threshold = confidence_threshold
            self.device = device
            self.detected_objects = {}
            
            logger.info(f"✓ YOLOv8 model loaded: {model_name}")
            logger.info(f"✓ Confidence threshold: {self.confidence_threshold}")
            
        except Exception as e:
            logger.error(f"FATAL: Cannot load model: {e}")
            raise

    def detect(self, frame):
        """
        Detect objects in a single frame
        
        Args:
            frame: Input image/frame (numpy array) BGR format
            
        Returns:
            detections: List of detected objects with their info
            annotated_frame: Frame with bounding boxes drawn
        """
        detections = []
        annotated_frame = frame.copy()
        
        if frame is None or frame.size == 0:
            return detections, annotated_frame
        
        try:
            # Run inference - IMPORTANT: device='cpu' to avoid GPU errors
            results = self.model(frame, verbose=False, conf=self.confidence_threshold, device='cpu')
            
            if results is None or len(results) == 0:
                return detections, annotated_frame
            
            result = results[0]
            
            # Check if boxes exist
            if result.boxes is None or len(result.boxes) == 0:
                return detections, annotated_frame
            
            boxes = result.boxes
            h, w = frame.shape[:2]
            
            # Process each detection
            for i in range(len(boxes)):
                try:
                    # Get box coordinates
                    box = boxes.xyxy[i].cpu().numpy() if hasattr(boxes.xyxy[i], 'cpu') else boxes.xyxy[i]
                    x1, y1, x2, y2 = map(int, box[:4])
                    
                    # Clamp coordinates to frame bounds
                    x1 = max(0, min(x1, w - 1))
                    y1 = max(0, min(y1, h - 1))
                    x2 = max(0, min(x2, w - 1))
                    y2 = max(0, min(y2, h - 1))
                    
                    # Ensure x1 < x2 and y1 < y2
                    if x1 >= x2 or y1 >= y2:
                        continue
                    
                    # Get class info
                    class_id = int(boxes.cls[i].item()) if hasattr(boxes.cls[i], 'item') else int(boxes.cls[i])
                    class_name = result.names[class_id] if hasattr(result, 'names') else f"class_{class_id}"
                    confidence = float(boxes.conf[i].item()) if hasattr(boxes.conf[i], 'item') else float(boxes.conf[i])
                    
                    # Create detection dict
                    detection = {
                        'class_name': class_name,
                        'confidence': confidence,
                        'bbox': (x1, y1, x2, y2),
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                        'area': max(1, (x2 - x1) * (y2 - y1))
                    }
                    detections.append(detection)
                    
                    # Draw on frame
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{class_name} {confidence:.2f}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
                    cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 4),
                                 (x1 + label_size[0], y1), (0, 255, 0), -1)
                    cv2.putText(annotated_frame, label, (x1, y1 - 2),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                
                except Exception as e:
                    logger.debug(f"Error processing box: {e}")
                    continue
            
            return detections, annotated_frame
        
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return [], frame

    def get_object_location(self, frame_shape, detection):
        """Determine location of object in frame"""
        h, w = frame_shape[:2]
        x1, y1, x2, y2 = detection['bbox']
        
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        vertical = "top" if center_y < h // 3 else ("middle" if center_y < 2 * h // 3 else "bottom")
        horizontal = "left" if center_x < w // 3 else ("center" if center_x < 2 * w // 3 else "right")
        
        return f"{horizontal} {vertical}"

    def reset_history(self):
        """Clear detection history"""
        self.detected_objects = {}
