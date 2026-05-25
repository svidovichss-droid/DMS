"""Camera preview panel."""

import cv2
import numpy as np
from PIL import Image, ImageTk
import customtkinter as ctk
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CameraPanel(ctk.CTkFrame):
    """Camera preview panel with detection overlay."""
    
    def __init__(self, parent, colors: dict):
        super().__init__(parent, fg_color=colors['panel_bg'], corner_radius=8)
        
        self.colors = colors
        self.current_image: Optional[ImageTk.PhotoImage] = None
        self.detection_box: Optional[Tuple[int, int, int, int]] = None
        self.detection_text: str = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup panel components."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="КАМЕРА",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['accent']
        )
        title.pack(anchor='nw', padx=10, pady=(8, 4))
        
        # Camera frame container
        self.frame_container = ctk.CTkFrame(self, fg_color='#000000', corner_radius=6)
        self.frame_container.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        
        # Camera label
        self.camera_label = ctk.CTkLabel(
            self.frame_container,
            text="Нет сигнала",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        self.camera_label.pack(fill='both', expand=True)
        
        # Crosshair overlay canvas
        self.crosshair_canvas = ctk.CTkCanvas(
            self.frame_container,
            bg='#000000',
            highlightthickness=0
        )
        self.crosshair_canvas.pack(fill='both', expand=True)
        self.crosshair_canvas.lower()  # Put behind label
        
        # Detection info frame
        self.info_frame = ctk.CTkFrame(self, height=60, fg_color=self.colors['secondary_bg'])
        self.info_frame.pack(fill='x', padx=8, pady=(0, 8))
        self.info_frame.pack_propagate(False)
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Ожидание Data Matrix...",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.info_label.pack(side='left', padx=10)
        
        # FPS counter
        self.fps_label = ctk.CTkLabel(
            self.info_frame,
            text="0 FPS",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        self.fps_label.pack(side='right', padx=10)
    
    def update_frame(self, frame: np.ndarray):
        """Update camera preview with new frame."""
        if frame is None:
            return
        
        try:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get canvas size
            canvas_w = self.crosshair_canvas.winfo_width()
            canvas_h = self.crosshair_canvas.winfo_height()
            
            if canvas_w < 10 or canvas_h < 10:
                canvas_w, canvas_h = 640, 480
            
            # Resize to fit canvas while maintaining aspect ratio
            h, w = rgb_frame.shape[:2]
            scale = min(canvas_w / w, canvas_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            resized = cv2.resize(rgb_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Create PIL image
            img = Image.fromarray(resized)
            self.current_image = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.crosshair_canvas.delete('all')
            x_offset = (canvas_w - new_w) // 2
            y_offset = (canvas_h - new_h) // 2
            
            self.crosshair_canvas.create_image(x_offset, y_offset, anchor='nw', image=self.current_image)
            
            # Draw crosshairs
            center_x = x_offset + new_w // 2
            center_y = y_offset + new_h // 2
            
            # Horizontal line
            self.crosshair_canvas.create_line(
                x_offset, center_y, x_offset + new_w, center_y,
                fill='#00d9ff', width=1, dash=(4, 4)
            )
            
            # Vertical line
            self.crosshair_canvas.create_line(
                center_x, y_offset, center_x, y_offset + new_h,
                fill='#00d9ff', width=1, dash=(4, 4)
            )
            
            # Draw detection box if present
            if self.detection_box:
                self._draw_detection_box(x_offset, y_offset, scale)
            
            # Hide placeholder text
            self.camera_label.configure(text="")
            
        except Exception as e:
            logger.error(f"Frame update error: {e}")
    
    def show_detection(self, bbox: Tuple[int, int, int, int], code_data: str):
        """Show detection overlay."""
        self.detection_box = bbox
        self.detection_text = code_data
        
        # Update info label
        display_text = code_data[:25] + "..." if len(code_data) > 25 else code_data
        self.info_label.configure(
            text=f"✓ {display_text}",
            text_color=self.colors['success']
        )
    
    def _draw_detection_box(self, offset_x: int, offset_y: int, scale: float):
        """Draw detection bounding box on canvas."""
        if not self.detection_box:
            return
        
        x, y, w, h = self.detection_box
        
        # Scale and offset coordinates
        x1 = int(x * scale) + offset_x
        y1 = int(y * scale) + offset_y
        x2 = int((x + w) * scale) + offset_x
        y2 = int((y + h) * scale) + offset_y
        
        # Draw rectangle
        self.crosshair_canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=self.colors['success'],
            width=2
        )
        
        # Draw corner markers
        corner_size = 10
        corners = [
            (x1, y1, x1 + corner_size, y1),  # Top-left horizontal
            (x1, y1, x1, y1 + corner_size),  # Top-left vertical
            (x2 - corner_size, y1, x2, y1),  # Top-right horizontal
            (x2, y1, x2, y1 + corner_size),  # Top-right vertical
            (x1, y2 - corner_size, x1, y2),  # Bottom-left vertical
            (x1, y2, x1 + corner_size, y2),  # Bottom-left horizontal
            (x2, y2 - corner_size, x2, y2),  # Bottom-right vertical
            (x2 - corner_size, y2, x2, y2),  # Bottom-right horizontal
        ]
        
        for x1c, y1c, x2c, y2c in corners:
            self.crosshair_canvas.create_line(x1c, y1c, x2c, y2c, fill=self.colors['success'], width=3)
    
    def clear_detection(self):
        """Clear detection overlay."""
        self.detection_box = None
        self.detection_text = ""
        self.info_label.configure(
            text="Ожидание Data Matrix...",
            text_color=self.colors['text_secondary']
        )
    
    def update_fps(self, fps: float):
        """Update FPS display."""
        self.fps_label.configure(text=f"{fps:.0f} FPS")
    
    def show_no_signal(self):
        """Show no signal message."""
        self.camera_label.configure(text="Нет сигнала с камеры", text_color=self.colors['error'])
        self.crosshair_canvas.delete('all')