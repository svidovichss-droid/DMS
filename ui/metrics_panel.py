"""Quality metrics panel."""

import customtkinter as ctk
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MetricsPanel(ctk.CTkFrame):
    """Panel for displaying ISO quality metrics."""
    
    def __init__(self, parent, colors: dict):
        super().__init__(parent, fg_color=colors['panel_bg'], corner_radius=8)
        
        self.colors = colors
        self.metric_widgets = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup panel components."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="ПАРАМЕТРЫ КАЧЕСТВА",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['accent']
        )
        title.pack(anchor='nw', padx=10, pady=(8, 4))
        
        # Grade display
        grade_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary_bg'], corner_radius=6)
        grade_frame.pack(fill='x', padx=8, pady=(0, 10))
        
        self.grade_label = ctk.CTkLabel(
            grade_frame,
            text="-",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.grade_label.pack(pady=(10, 0))
        
        self.score_label = ctk.CTkLabel(
            grade_frame,
            text="Оценка: --",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        self.score_label.pack(pady=(0, 10))
        
        # Metrics list
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        
        metrics = [
            ('sc', 'SC', 'Контраст символа', 0.80, True),
            ('ed', 'ED', 'Чёткость краёв', 0.50, True),
            ('an', 'AN', 'Осевая неравномерность', 0.08, False),
            ('gn', 'GN', 'Сеточная неравномерность', 0.08, False),
            ('uect', 'UEC', 'Неисп. коррекция ошибок', 0.50, True),
            ('fpd', 'FPD', 'Повреждение шаблона', 0.60, True),
        ]
        
        for key, code, name, threshold, min_is_good in metrics:
            self._create_metric_row(metrics_frame, key, code, name, threshold, min_is_good)
    
    def _create_metric_row(self, parent, key: str, code: str, name: str, 
                          threshold: float, min_is_good: bool):
        """Create a single metric row."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill='x', pady=3)
        
        # Code label
        code_label = ctk.CTkLabel(
            row,
            text=code,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text'],
            width=40
        )
        code_label.pack(side='left')
        
        # Value and progress bar container
        value_frame = ctk.CTkFrame(row, fg_color="transparent")
        value_frame.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        # Progress bar
        progress = ctk.CTkProgressBar(
            value_frame,
            height=8,
            progress_color=self.colors['accent'],
            fg_color=self.colors['secondary_bg']
        )
        progress.set(0)
        progress.pack(fill='x')
        
        # Value label
        value_label = ctk.CTkLabel(
            value_frame,
            text="--",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor='w'
        )
        value_label.pack(anchor='w')
        
        # Status indicator
        status_label = ctk.CTkLabel(
            row,
            text="—",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_secondary'],
            width=25
        )
        status_label.pack(side='right')
        
        # Store widgets
        self.metric_widgets[key] = {
            'progress': progress,
            'value': value_label,
            'status': status_label,
            'threshold': threshold,
            'min_is_good': min_is_good
        }
    
    def update_metrics(self, metrics):
        """Update metrics display with new values."""
        if metrics is None:
            self.reset()
            return
        
        metric_map = {
            'sc': metrics.symbol_contrast,
            'ed': metrics.edge_determinacy,
            'an': metrics.axial_non_uniformity,
            'gn': metrics.grid_non_uniformity,
            'uect': metrics.unused_error_correction,
            'fpd': metrics.fixed_pattern_damage
        }
        
        for key, value in metric_map.items():
            if key in self.metric_widgets:
                self._update_single_metric(key, value)
    
    def _update_single_metric(self, key: str, value: float):
        """Update a single metric display."""
        if key not in self.metric_widgets:
            return
        
        widgets = self.metric_widgets[key]
        
        # Normalize value to 0-1 range for progress bar
        # For non-uniformity metrics, lower is better, so invert
        if widgets['min_is_good']:
            normalized = min(1.0, value)
            threshold = widgets['threshold']
            # Scale: threshold maps to 0.7, max value maps to 1.0
            display_value = min(1.0, 0.3 + (value / max(0.01, threshold)) * 0.7)
        else:
            # For max values (like non-uniformity), lower is better
            threshold = widgets['threshold']
            if threshold > 0:
                inverted = max(0, 1 - value / (threshold * 2))
                display_value = 0.3 + inverted * 0.7
            else:
                display_value = 0.5
        
        # Update progress bar
        widgets['progress'].set(display_value)
        
        # Update value label
        widgets['value'].configure(text=f"{value:.2f}")
        
        # Determine pass/fail
        if widgets['min_is_good']:
            passed = value >= widgets['threshold']
        else:
            passed = value <= widgets['threshold']
        
        # Update colors
        if passed:
            color = self.colors['success']
            status = "✓"
        else:
            color = self.colors['error']
            status = "✗"
        
        widgets['progress'].configure(progress_color=color)
        widgets['value'].configure(text_color=color)
        widgets['status'].configure(text=status, text_color=color)
    
    def update_grade(self, grade: str, score: float):
        """Update overall grade display."""
        grade_colors = {
            'A': self.colors['grade_a'],
            'B': self.colors['grade_b'],
            'C': self.colors['grade_c'],
            'D': self.colors['grade_d'],
            'F': self.colors['grade_f']
        }
        
        color = grade_colors.get(grade, self.colors['text_secondary'])
        
        self.grade_label.configure(text=grade, text_color=color)
        self.score_label.configure(text=f"Оценка: {score:.1f}/5.0", text_color=color)
    
    def reset(self):
        """Reset all metrics to default state."""
        self.grade_label.configure(text="-", text_color=self.colors['text_secondary'])
        self.score_label.configure(text="Оценка: --", text_color=self.colors['text_secondary'])
        
        for key, widgets in self.metric_widgets.items():
            widgets['progress'].set(0)
            widgets['value'].configure(text="--", text_color=self.colors['text_secondary'])
            widgets['status'].configure(text="—", text_color=self.colors['text_secondary'])
            widgets['progress'].configure(progress_color=self.colors['accent'])