"""Main window for DataMatrix Quality Scanner."""

import customtkinter as ctk
from typing import Optional, Callable
import cv2
import numpy as np
from PIL import Image, ImageTk
import logging

from ui.camera_panel import CameraPanel
from ui.metrics_panel import MetricsPanel
from ui.log_panel import LogPanel

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """Main application window."""
    
    def __init__(self, config, on_scan_callback: Optional[Callable] = None):
        super().__init__()
        
        self.config = config
        self.on_scan_callback = on_scan_callback
        
        # Window settings
        self.title("DataMatrix Quality Scanner - ISO 15415")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Color scheme - Industrial Dark Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.colors = {
            'primary_bg': '#1a1a2e',
            'secondary_bg': '#16213e',
            'panel_bg': '#0f3460',
            'accent': '#00d9ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff4757',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'grade_a': '#00ff88',
            'grade_b': '#00d9ff',
            'grade_c': '#ffaa00',
            'grade_d': '#ff6b35',
            'grade_f': '#ff4757'
        }
        
        self.current_frame: Optional[np.ndarray] = None
        self.alarm_active = False
        self.is_scanning = False
        
        self._setup_ui()
        self._configure_grid()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Setup UI components."""
        # Header frame
        self.header_frame = ctk.CTkFrame(self, height=60, fg_color=self.colors['secondary_bg'])
        self.header_frame.pack(side='top', fill='x', padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)
        
        self._setup_header()
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color=self.colors['primary_bg'])
        self.content_frame.pack(side='top', fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Camera
        self.camera_panel = CameraPanel(self.content_frame, self.colors)
        self.camera_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=0)
        
        # Right panel - Metrics
        self.metrics_panel = MetricsPanel(self.content_frame, self.colors)
        self.metrics_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=0)
        
        # Bottom panel - Log
        self.log_panel = LogPanel(self.content_frame, self.colors)
        self.log_panel.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=0, pady=(10, 0))
        
        # Footer frame
        self.footer_frame = ctk.CTkFrame(self, height=50, fg_color=self.colors['secondary_bg'])
        self.footer_frame.pack(side='bottom', fill='x', padx=10, pady=(5, 10))
        self.footer_frame.pack_propagate(False)
        
        self._setup_footer()
    
    def _setup_header(self):
        """Setup header components."""
        # Title
        title_label = ctk.CTkLabel(
            self.header_frame,
            text="DataMatrix Quality Scanner",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['accent']
        )
        title_label.pack(side='left', padx=15)
        
        # ISO badge
        iso_label = ctk.CTkLabel(
            self.header_frame,
            text="ISO 15415",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_secondary'],
            fg_color=self.colors['panel_bg'],
            corner_radius=4,
            padx=10,
            pady=2
        )
        iso_label.pack(side='left', padx=5)
        
        # Connection status
        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="● OFFLINE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['error']
        )
        self.status_label.pack(side='right', padx=15)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.header_frame,
            text="⚙ Настройки",
            width=100,
            height=32,
            command=self._on_settings_click
        )
        self.settings_btn.pack(side='right', padx=5)
        
        # Language label
        lang_label = ctk.CTkLabel(
            self.header_frame,
            text="RU",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        lang_label.pack(side='right', padx=(15, 5))
    
    def _setup_footer(self):
        """Setup footer components."""
        # Statistics frame
        stats_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        stats_frame.pack(side='left', padx=15)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Сканирований: 0 | Успешно: 0 | Брак: 0",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.stats_label.pack(side='left')
        
        # Control buttons
        btn_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        btn_frame.pack(side='right', padx=15)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Старт",
            width=100,
            height=32,
            fg_color=self.colors['success'],
            command=self._on_start_click
        )
        self.start_btn.pack(side='left', padx=3)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="■ Стоп",
            width=100,
            height=32,
            fg_color=self.colors['error'],
            state='disabled',
            command=self._on_stop_click
        )
        self.stop_btn.pack(side='left', padx=3)
        
        self.export_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Экспорт",
            width=100,
            height=32,
            command=self._on_export_click
        )
        self.export_btn.pack(side='left', padx=3)
    
    def _configure_grid(self):
        """Configure grid weights for responsive layout."""
        self.content_frame.columnconfigure(0, weight=3)
        self.content_frame.columnconfigure(1, weight=2)
        self.content_frame.rowconfigure(0, weight=2)
        self.content_frame.rowconfigure(1, weight=1)
    
    def update_frame(self, frame: np.ndarray):
        """Update camera preview frame."""
        self.current_frame = frame
        self.camera_panel.update_frame(frame)
    
    def show_detection(self, bbox, code_data: str):
        """Show detection overlay on camera preview."""
        self.camera_panel.show_detection(bbox, code_data)
    
    def update_metrics(self, metrics):
        """Update quality metrics display."""
        self.metrics_panel.update_metrics(metrics)
    
    def update_grade(self, grade: str, score: float):
        """Update grade display."""
        self.metrics_panel.update_grade(grade, score)
        self.trigger_alarm(grade == 'F')
    
    def add_log_entry(self, timestamp: str, code: str, grade: str, passed: bool):
        """Add entry to scan log."""
        self.log_panel.add_entry(timestamp, code, grade, passed)
    
    def update_statistics(self, total: int, passed: int, failed: int):
        """Update statistics display."""
        self.stats_label.configure(
            text=f"Сканирований: {total} | Успешно: {passed} | Брак: {failed}"
        )
    
    def set_camera_status(self, connected: bool, camera_name: str = ""):
        """Update camera connection status."""
        if connected:
            self.status_label.configure(
                text=f"● {camera_name}",
                text_color=self.colors['success']
            )
        else:
            self.status_label.configure(
                text="● OFFLINE",
                text_color=self.colors['error']
            )
    
    def set_scanning_state(self, is_scanning: bool):
        """Update UI for scanning state."""
        self.is_scanning = is_scanning
        if is_scanning:
            self.start_btn.configure(state='disabled', fg_color=self.colors['text_secondary'])
            self.stop_btn.configure(state='normal')
        else:
            self.start_btn.configure(state='normal', fg_color=self.colors['success'])
            self.stop_btn.configure(state='disabled')
    
    def trigger_alarm(self, is_failure: bool):
        """Trigger visual alarm effect."""
        if is_failure:
            self.alarm_active = True
            self.header_frame.configure(fg_color=self.colors['error'])
            self.after(500, self._reset_alarm)
    
    def _reset_alarm(self):
        """Reset alarm visual effect."""
        self.alarm_active = False
        self.header_frame.configure(fg_color=self.colors['secondary_bg'])
    
    def _on_start_click(self):
        """Handle start button click."""
        self.set_scanning_state(True)
        if self.on_scan_callback:
            self.on_scan_callback('start')
    
    def _on_stop_click(self):
        """Handle stop button click."""
        self.set_scanning_state(False)
        if self.on_scan_callback:
            self.on_scan_callback('stop')
    
    def _on_settings_click(self):
        """Handle settings button click."""
        logger.info("Settings dialog requested")
    
    def _on_export_click(self):
        """Handle export button click."""
        logger.info("Export dialog requested")
    
    def clear_detection(self):
        """Clear detection overlay."""
        self.camera_panel.clear_detection()
    
    def reset_metrics(self):
        """Reset metrics display to defaults."""
        self.metrics_panel.reset()
    
    def get_colors(self) -> dict:
        """Get application color scheme."""
        return self.colors