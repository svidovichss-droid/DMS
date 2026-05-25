"""Scan log panel."""

import customtkinter as ctk
from tkinter import ttk
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LogPanel(ctk.CTkFrame):
    """Panel for displaying scan history log."""
    
    def __init__(self, parent, colors: dict, max_entries: int = 100):
        super().__init__(parent, fg_color=colors['panel_bg'], corner_radius=8)
        
        self.colors = colors
        self.max_entries = max_entries
        self.entries: List[dict] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup panel components."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill='x', padx=10, pady=(8, 4))
        
        title = ctk.CTkLabel(
            title_frame,
            text="ЖУРНАЛ СКАНИРОВАНИЙ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['accent']
        )
        title.pack(side='left')
        
        # Entry count
        self.count_label = ctk.CTkLabel(
            title_frame,
            text="0 записей",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        self.count_label.pack(side='right')
        
        # Table container
        table_frame = ctk.CTkFrame(self, fg_color=self.colors['secondary_bg'], corner_radius=6)
        table_frame.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        
        # Configure grid
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=3)
        table_frame.columnconfigure(2, weight=1)
        table_frame.columnconfigure(3, weight=1)
        
        # Header row
        headers = ['Время', 'Код Data Matrix', 'Оценка', 'Статус']
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=self.colors['accent']
            )
            label.grid(row=0, column=i, sticky='ew', padx=5, pady=3)
        
        # Scrollable frame for entries
        self.scroll_frame = ctk.CTkScrollableFrame(
            table_frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['panel_bg'],
            scrollbar_button_hover_color=self.colors['accent']
        )
        self.scroll_frame.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=2, pady=2)
        
        # Configure scrollable frame grid
        for i in range(4):
            self.scroll_frame.columnconfigure(i, weight=1 if i != 1 else 3)
    
    def add_entry(self, timestamp: str, code: str, grade: str, passed: bool):
        """Add a new entry to the log."""
        # Create entry data
        entry = {
            'timestamp': timestamp,
            'code': code,
            'grade': grade,
            'passed': passed
        }
        
        # Add to list
        self.entries.append(entry)
        
        # Trim if exceeds max
        while len(self.entries) > self.max_entries:
            self.entries.pop(0)
        
        # Rebuild display
        self._rebuild_display()
        
        # Update count
        self.count_label.configure(text=f"{len(self.entries)} записей")
    
    def _rebuild_display(self):
        """Rebuild the log display."""
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Add entries (newest first)
        for idx, entry in enumerate(reversed(self.entries[-50:])):  # Show last 50
            self._create_entry_row(entry, idx)
    
    def _create_entry_row(self, entry: dict, row_idx: int):
        """Create a single log entry row."""
        # Alternating background
        bg_color = self.colors['secondary_bg'] if row_idx % 2 == 0 else self.colors['panel_bg']
        
        # Timestamp
        time_label = ctk.CTkLabel(
            self.scroll_frame,
            text=entry['timestamp'],
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor='w'
        )
        time_label.grid(row=row_idx, column=0, sticky='ew', padx=5, pady=2)
        
        # Code
        code_text = entry['code']
        if len(code_text) > 30:
            code_text = code_text[:27] + "..."
        
        code_label = ctk.CTkLabel(
            self.scroll_frame,
            text=code_text,
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text'],
            anchor='w'
        )
        code_label.grid(row=row_idx, column=1, sticky='ew', padx=5, pady=2)
        
        # Grade
        grade_colors = {
            'A': self.colors['grade_a'],
            'B': self.colors['grade_b'],
            'C': self.colors['grade_c'],
            'D': self.colors['grade_d'],
            'F': self.colors['grade_f']
        }
        grade_color = grade_colors.get(entry['grade'], self.colors['text_secondary'])
        
        grade_label = ctk.CTkLabel(
            self.scroll_frame,
            text=entry['grade'],
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=grade_color,
            anchor='center'
        )
        grade_label.grid(row=row_idx, column=2, sticky='ew', padx=5, pady=2)
        
        # Status
        if entry['passed']:
            status_text = "✓ ПРОШЁЛ"
            status_color = self.colors['success']
        else:
            status_text = "✗ БРАК"
            status_color = self.colors['error']
        
        status_label = ctk.CTkLabel(
            self.scroll_frame,
            text=status_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_color,
            anchor='center'
        )
        status_label.grid(row=row_idx, column=3, sticky='ew', padx=5, pady=2)
    
    def clear(self):
        """Clear all log entries."""
        self.entries.clear()
        self._rebuild_display()
        self.count_label.configure(text="0 записей")
    
    def get_entries(self) -> List[dict]:
        """Get all log entries."""
        return self.entries.copy()
    
    def get_failed_entries(self) -> List[dict]:
        """Get only failed entries."""
        return [e for e in self.entries if not e['passed']]
    
    def export_to_csv(self, filepath: str) -> bool:
        """Export log to CSV file."""
        try:
            import csv
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if self.entries:
                    fieldnames = ['timestamp', 'code', 'grade', 'passed']
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                    writer.writeheader()
                    
                    for entry in self.entries:
                        row = entry.copy()
                        row['passed'] = 'ПРОШЁЛ' if entry['passed'] else 'БРАК'
                        writer.writerow(row)
            
            logger.info(f"Exported {len(self.entries)} entries to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False