"""Camera handling module for DataMatrix Scanner."""

import cv2
import numpy as np
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages webcam connections and capture operations."""
    
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_index: int = 0
        self.is_active: bool = False
        self.frame_width: int = 1280
        self.frame_height: int = 720
        self.fps: int = 30
        
    def enumerate_cameras(self) -> List[dict]:
        """Enumerate all available cameras on the system."""
        cameras = []
        for i in range(5):  # Check first 5 indices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        h, w = frame.shape[:2] if frame is not None else (0, 0)
                        cameras.append({
                            'index': i,
                            'name': f'Camera {i}',
                            'width': w,
                            'height': h,
                            'available': True
                        })
                        logger.info(f"Found camera at index {i}: {w}x{h}")
                    cap.release()
                else:
                    cap.release()
            except Exception as e:
                logger.debug(f"Camera index {i} not available: {e}")
        return cameras
    
    def connect(self, camera_index: int = 0, width: int = 1280, height: int = 720) -> bool:
        """Connect to specified camera."""
        try:
            if self.cap is not None:
                self.disconnect()
            
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                self.camera_index = camera_index
                self.frame_width = width
                self.frame_height = height
                
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                
                # Verify settings
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                
                self.frame_width = actual_width if actual_width > 0 else width
                self.frame_height = actual_height if actual_height > 0 else height
                self.fps = actual_fps if actual_fps > 0 else 30
                
                self.is_active = True
                logger.info(f"Connected to camera {camera_index}: {self.frame_width}x{self.frame_height} @ {self.fps}fps")
                return True
            else:
                logger.error(f"Failed to open camera {camera_index}")
                return False
                
        except Exception as e:
            logger.error(f"Camera connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from current camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_active = False
        logger.info("Camera disconnected")
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame from camera."""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def get_frame_with_detection_box(self, bbox: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Get frame with optional detection box overlay."""
        frame = self.read_frame()
        if frame is None:
            return None
        
        if bbox is not None:
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        return frame
    
    def set_brightness(self, value: int):
        """Set camera brightness (0-100)."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value / 100.0)
    
    def set_contrast(self, value: int):
        """Set camera contrast (0-100)."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_CONTRAST, value / 100.0)
    
    def set_exposure(self, value: int):
        """Set camera exposure (0-100)."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_EXPOSURE, value / 100.0)
    
    def release(self):
        """Release camera resources."""
        self.disconnect()
