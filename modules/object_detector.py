"""
Object Detection Module using YOLOv8
Detects and recognizes objects in video/image frames
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, model_name="yolov8n.pt", confidence_threshold=0.5):
        """
        Initialize the object detector with YOLOv8 model
        
        Args:
            model_name: Name of the YOLO model to use
            confidence_threshold: Minimum confidence for detection
        """
        try:
            # Force fresh download by removing cached model if corrupted
            model_path = Path.home() / '.cache' / 'yolov8'
            import os
            import shutil
            if model_path.exists():
                logger.info(f"Clearing cache: {model_path}")
                shutil.rmtree(str(model_path), ignore_errors=True)
            
            self.model = YOLO(model_name)
            self.confidence_threshold = confidence_threshold
            self.detected_objects = {}
            logger.info(f"Object Detection model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def detect(self, frame):
        """
        Detect objects in a single frame
        
        Args:
            frame: Input image/frame (numpy array)
            
        Returns:
            detections: List of detected objects with their info
            annotated_frame: Frame with bounding boxes drawn
        """
        try:
            # Ensure frame is in correct format
            if frame is None or frame.size == 0:
                return [], frame
            
            # Run inference with device selection (use CPU if CUDA not available)
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            results = self.model(frame, verbose=False, conf=self.confidence_threshold, device=device)
            
            detections = []
            
            # Process detections
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes
                    
                    for i in range(len(boxes)):
                        try:
                            # Extract box coordinates
                            box_coords = boxes.xyxy[i].cpu().numpy() if hasattr(boxes.xyxy[i], 'cpu') else boxes.xyxy[i]
                            x1, y1, x2, y2 = map(int, box_coords[:4])
                            
                            # Ensure coordinates are valid
                            x1 = max(0, x1)
                            y1 = max(0, y1)
                            x2 = min(frame.shape[1], x2)
                            y2 = min(frame.shape[0], y2)
                            
                            # Extract confidence and class
                            confidence = float(boxes.conf[i].cpu() if hasattr(boxes.conf[i], 'cpu') else boxes.conf[i])
                            class_id = int(boxes.cls[i].cpu() if hasattr(boxes.cls[i], 'cpu') else boxes.cls[i])
                            
                            # Get class name
                            class_name = result.names[class_id] if class_id in result.names else f"class_{class_id}"
                            
                            # Only add if confidence meets threshold
                            if confidence >= self.confidence_threshold:
                                detection = {
                                    'class_name': class_name,
                                    'confidence': confidence,
                                    'bbox': (x1, y1, x2, y2),
                                    'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                                    'area': max(1, (x2 - x1) * (y2 - y1))
                                }
                                detections.append(detection)
                                
                                # Store in history
                                if class_name not in self.detected_objects:
                                    self.detected_objects[class_name] = []
                                self.detected_objects[class_name].append(detection)
                        
                        except Exception as e:
                            logger.debug(f"Error processing box {i}: {e}")
                            continue
            
            # Draw annotations
            annotated_frame = self._draw_annotations(frame.copy(), detections)
            
            return detections, annotated_frame
        
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return [], frame
    
    def _draw_annotations(self, frame, detections):
        """Draw bounding boxes and labels on frame"""
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class_name']
            confidence = det['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name} ({confidence:.2f})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(annotated, (x1, y1 - label_size[1] - 4), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(annotated, label, (x1, y1 - 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return annotated
    
    def get_object_location(self, frame_shape, detection):
        """Determine location of object in frame"""
        h, w = frame_shape[:2]
        x1, y1, x2, y2 = detection['bbox']
        
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Determine region
        if center_y < h // 3:
            vertical = "top"
        elif center_y < 2 * h // 3:
            vertical = "middle"
        else:
            vertical = "bottom"
        
        if center_x < w // 3:
            horizontal = "left"
        elif center_x < 2 * w // 3:
            horizontal = "center"
        else:
            horizontal = "right"
        
        return f"{horizontal} {vertical}"
    
    def get_top_objects(self, frame, top_n=5):
        """Get top N detected objects by confidence"""
        detections, _ = self.detect(frame)
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        return sorted_dets[:top_n]
    
    def reset_history(self):
        """Clear detection history"""
        self.detected_objects = {}


# For testing without full YOLO setup, provide a mock detector
class MockObjectDetector:
    """Mock detector for development without YOLOv8"""
    
    def __init__(self, model_name="mock", confidence_threshold=0.5):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.detected_objects = {}
        self.frame_count = 0
        self.stable_objects = None  # Store consistent objects
        logger.info("Using Mock Object Detector (Development Mode)")
    
    def detect(self, frame):
        """Mock detection with stable, realistic objects"""
        import random
        
        self.frame_count += 1
        
        # Define stable, realistic objects for a typical workspace
        stable_objects = [
            ('person', 0.95, 100, 50, 200, 350),      # Top left - person sitting
            ('laptop', 0.92, 250, 100, 500, 250),     # Center - laptop
            ('keyboard', 0.88, 250, 260, 450, 280),   # Below laptop
            ('mouse', 0.85, 460, 250, 500, 280),      # Right of keyboard
            ('phone', 0.90, 520, 150, 580, 200),      # Top right
            ('cup', 0.87, 520, 220, 570, 280),        # Right side cup
            ('book', 0.83, 120, 300, 200, 400),       # Left side book
        ]
        
        mock_detections = []
        h, w = frame.shape[:2] if frame is not None else (600, 800)
        
        # Add stable objects with slight position variations
        for obj_name, base_conf, x1_base, y1_base, x2_base, y2_base in stable_objects:
            # Add small random variations for realistic movement
            x1 = x1_base + random.randint(-10, 10)
            y1 = y1_base + random.randint(-10, 10)
            x2 = x2_base + random.randint(-10, 10)
            y2 = y2_base + random.randint(-10, 10)
            
            # Ensure bounds
            x1 = max(0, min(x1, w - 50))
            y1 = max(0, min(y1, h - 50))
            x2 = max(x1 + 50, min(x2, w))
            y2 = max(y1 + 50, min(y2, h))
            
            # Confidence with small variations
            conf = base_conf + random.uniform(-0.02, 0.02)
            conf = max(0.7, min(1.0, conf))
            
            detection = {
                'class_name': obj_name,
                'confidence': conf,
                'bbox': (x1, y1, x2, y2),
                'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                'area': max(1, (x2 - x1) * (y2 - y1))
            }
            mock_detections.append(detection)
            
            # Store in history
            if obj_name not in self.detected_objects:
                self.detected_objects[obj_name] = []
            self.detected_objects[obj_name].append(detection)
        
        # Draw on frame
        annotated = frame.copy() if frame is not None else np.zeros((480, 640, 3), dtype=np.uint8)
        annotated = self._draw_annotations(annotated, mock_detections)
        
        return mock_detections, annotated
    
    def _draw_annotations(self, frame, detections):
        """Draw bounding boxes and labels on frame"""
        annotated = frame.copy()
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        
        for idx, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class_name']
            confidence = det['confidence']
            
            # Ensure coordinates are within bounds
            h, w = frame.shape[:2]
            x1 = max(0, min(x1, w-1))
            y1 = max(0, min(y1, h-1))
            x2 = max(0, min(x2, w-1))
            y2 = max(0, min(y2, h-1))
            
            color = colors[idx % len(colors)]
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} ({confidence:.2f})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Draw label background
            cv2.rectangle(annotated, (x1, y1 - label_size[1] - 4), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(annotated, label, (x1, y1 - 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return annotated
    
    def get_object_location(self, frame_shape, detection):
        """Determine location of object in frame"""
        h, w = frame_shape[:2]
        x1, y1, x2, y2 = detection['bbox']
        
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Determine region
        if center_y < h // 3:
            vertical = "top"
        elif center_y < 2 * h // 3:
            vertical = "middle"
        else:
            vertical = "bottom"
        
        if center_x < w // 3:
            horizontal = "left"
        elif center_x < 2 * w // 3:
            horizontal = "center"
        else:
            horizontal = "right"
        
        return f"{horizontal} {vertical}"
    
    def reset_history(self):
        """Clear detection history"""
        self.detected_objects = {}
