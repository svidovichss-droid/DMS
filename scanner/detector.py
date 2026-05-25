"""Data Matrix detection and decoding module."""

import cv2
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
import logging
import pyzbar.pyzbar as pyzbar

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of Data Matrix detection."""
    data: str
    bbox: Tuple[int, int, int, int]
    quality: float
    timestamp: float
    rect: List[Tuple[int, int]]  # Rotated rectangle points


class DataMatrixDetector:
    """Detects and decodes Data Matrix codes in images."""
    
    def __init__(self):
        self.last_detected_data: Optional[str] = None
        self.last_detection_time: float = 0
        self.confidence_threshold: float = 0.5
        
    def detect(self, frame: np.ndarray) -> Optional[DetectionResult]:
        """
        Detect Data Matrix in the given frame.
        
        Args:
            frame: BGR image from camera
            
        Returns:
            DetectionResult if Data Matrix found, None otherwise
        """
        if frame is None:
            return None
        
        try:
            # Convert to grayscale for better detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast for better detection
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Try to detect Data Matrix using pyzbar
            decoded_objects = pyzbar.decode(enhanced, symbols=[pyzbar.ZBarSymbol.DATAMATRIX])
            
            if decoded_objects:
                obj = decoded_objects[0]
                
                # Extract detection info
                data = obj.data.decode('utf-8')
                rect = obj.rect
                polygon = obj.polygon
                
                # Create bounding box
                x, y = rect.left, rect.top
                w, h = rect.width, rect.height
                bbox = (x, y, w, h)
                
                # Calculate quality based on symbol size and position
                quality = self._calculate_detection_quality(frame, bbox, polygon)
                
                self.last_detected_data = data
                self.last_detection_time = cv2.getTickCount() / cv2.getTickFrequency()
                
                # Convert polygon to list of tuples
                polygon_points = [(point.x, point.y) for point in polygon]
                
                logger.debug(f"Detected Data Matrix: {data}, quality: {quality:.2f}")
                
                return DetectionResult(
                    data=data,
                    bbox=bbox,
                    quality=quality,
                    timestamp=self.last_detection_time,
                    rect=polygon_points
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return None
    
    def _calculate_detection_quality(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                                     polygon) -> float:
        """Calculate detection quality based on various factors."""
        h, w = frame.shape[:2]
        x, y, bw, bh = bbox
        
        # Size quality (prefer larger symbols)
        size_score = min(1.0, (bw * bh) / (w * h * 0.1))
        
        # Position quality (center is better)
        center_x, center_y = x + bw / 2, y + bh / 2
        dist_from_center = np.sqrt((center_x - w/2)**2 + (center_y - h/2)**2)
        max_dist = np.sqrt((w/2)**2 + (h/2)**2)
        position_score = 1.0 - (dist_from_center / max_dist)
        
        # Polygon quality (should have 4 corners for square Data Matrix)
        polygon_score = min(1.0, len(polygon) / 4.0)
        
        # Combined quality
        quality = (size_score * 0.3 + position_score * 0.4 + polygon_score * 0.3)
        
        return quality
    
    def preprocess_image(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess image for better detection."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Apply sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def is_duplicate(self, data: str, min_interval: float = 2.0) -> bool:
        """Check if detected code is a duplicate of recent detection."""
        if data == self.last_detected_data:
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            if current_time - self.last_detection_time < min_interval:
                return True
        return False
    
    def extract_region(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract and return the Data Matrix region."""
        x, y, w, h = bbox
        margin = max(w, h) // 4  # Add some margin
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(frame.shape[1], x + w + margin)
        y2 = min(frame.shape[0], y + h + margin)
        
        return frame[y1:y2, x1:x2]
    
    def draw_detection(self, frame: np.ndarray, result: DetectionResult) -> np.ndarray:
        """Draw detection visualization on frame."""
        output = frame.copy()
        
        # Draw bounding box
        x, y, w, h = result.bbox
        color = (0, 255, 0)  # Green
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
        
        # Draw polygon
        if result.rect:
            pts = np.array(result.rect, np.int32)
            cv2.polylines(output, [pts], True, (0, 255, 255), 2)
        
        # Draw data text
        text = f"{result.data[:20]}..." if len(result.data) > 20 else result.data
        cv2.putText(output, text, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return output
