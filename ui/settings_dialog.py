"""Settings dialog for configuration."""

import customtkinter as ctk
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class SettingsDialog(ctk.CTkToplevel):
    """Settings configuration dialog."""
    
    def __init__(self, parent, config, on_save: Optional[Callable] = None):
        super().__init__(parent)
        
        self.config = config
        self.on_save = on_save
        
        self.title("Настройки")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog components."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Camera settings section
        camera_frame = self._create_section(main_frame, "Камера")
        
        self.camera_dropdown = ctk.CTkOptionMenu(
            camera_frame,
            values=["Camera 0", "Camera 1", "Camera 2"],
            width=200
        )
        self.camera_dropdown.pack(anchor='w', pady=5)
        
        resolution_frame = ctk.CTkFrame(camera_frame, fg_color="transparent")
        resolution_frame.pack(anchor='w', pady=5)
        
        ctk.CTkLabel(resolution_frame, text="Разрешение:").pack(side='left')
        
        self.width_entry = ctk.CTkEntry(resolution_frame, width=80)
        self.width_entry.insert(0, str(self.config.get('camera.resolution_width', 1280)))
        self.width_entry.pack(side='left', padx=5)
        
        ctk.CTkLabel(resolution_frame, text="×").pack(side='left')
        
        self.height_entry = ctk.CTkEntry(resolution_frame, width=80)
        self.height_entry.insert(0, str(self.config.get('camera.resolution_height', 720)))
        self.height_entry.pack(side='left', padx=5)
        
        # Quality thresholds section
        threshold_frame = self._create_section(main_frame, "Пороги качества")
        
        thresholds = [
            ('symbol_contrast_min', 'SC (Контраст)', 0.80),
            ('edge_determinacy_min', 'ED (Края)', 0.50),
            ('axial_uniformity_max', 'AN (Осевая)', 0.08),
            ('grid_uniformity_max', 'GN (Сеточная)', 0.08),
            ('unused_error_correction_min', 'UEC (Коррекция)', 0.50),
            ('fixed_pattern_damage_min', 'FPD (Шаблон)', 0.60),
        ]
        
        self.threshold_entries = {}
        
        for key, name, default in thresholds:
            row = ctk.CTkFrame(threshold_frame, fg_color="transparent")
            row.pack(fill='x', pady=2)
            
            ctk.CTkLabel(row, text=name, width=150, anchor='w').pack(side='left')
            
            entry = ctk.CTkEntry(row, width=80)
            entry.insert(0, str(self.config.get(f'quality_thresholds.{key}', default)))
            entry.pack(side='left')
            
            self.threshold_entries[key] = entry
        
        # Scanning settings section
        scan_frame = self._create_section(main_frame, "Сканирование")
        
        auto_start_var = ctk.BooleanVar(value=self.config.get('scanning.auto_start', True))
        self.auto_start_check = ctk.CTkCheckBox(
            scan_frame,
            text="Автозапуск сканирования",
            variable=auto_start_var
        )
        self.auto_start_check.pack(anchor='w', pady=5)
        
        delay_row = ctk.CTkFrame(scan_frame, fg_color="transparent")
        delay_row.pack(anchor='w', pady=5)
        
        ctk.CTkLabel(delay_row, text="Интервал (мс):").pack(side='left')
        
        self.delay_entry = ctk.CTkEntry(delay_row, width=80)
        self.delay_entry.insert(0, str(self.config.get('scanning.min_scan_interval_ms', 500)))
        self.delay_entry.pack(side='left', padx=5)
        
        dup_row = ctk.CTkFrame(scan_frame, fg_color="transparent")
        dup_row.pack(anchor='w', pady=5)
        
        ctk.CTkLabel(dup_row, text="Фильтр дубликатов (с):").pack(side='left')
        
        self.dup_entry = ctk.CTkEntry(dup_row, width=80)
        self.dup_entry.insert(0, str(self.config.get('scanning.duplicate_filter_seconds', 2.0)))
        self.dup_entry.pack(side='left', padx=5)
        
        # Alarm settings
        alarm_frame = self._create_section(main_frame, "Сигнализация")
        
        enable_audio_var = ctk.BooleanVar(value=self.config.get('alarms.enable_audio', True))
        ctk.CTkCheckBox(
            alarm_frame,
            text="Звуковой сигнал при браке",
            variable=enable_audio_var
        ).pack(anchor='w', pady=2)
        
        enable_visual_var = ctk.BooleanVar(value=self.config.get('alarms.enable_visual', True))
        ctk.CTkCheckBox(
            alarm_frame,
            text="Визуальный сигнал",
            variable=enable_visual_var
        ).pack(anchor='w', pady=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            width=100,
            command=self.destroy
        ).pack(side='right', padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            width=100,
            fg_color="#00ff88",
            command=self._on_save
        ).pack(side='right', padx=5)
    
    def _create_section(self, parent, title: str) -> ctk.CTkFrame:
        """Create a settings section frame."""
        frame = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=6)
        frame.pack(fill='x', pady=5)
        
        label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor='w'
        )
        label.pack(anchor='w', padx=10, pady=(10, 5))
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill='x', padx=10, pady=(0, 10))
        
        return content
    
    def _on_save(self):
        """Handle save button click."""
        # Update config
        try:
            # Camera settings
            self.config.set('camera.resolution_width', int(self.width_entry.get()))
            self.config.set('camera.resolution_height', int(self.height_entry.get()))
            
            # Quality thresholds
            for key, entry in self.threshold_entries.items():
                value = float(entry.get())
                self.config.set(f'quality_thresholds.{key}', value)
            
            # Scanning settings
            self.config.set('scanning.min_scan_interval_ms', int(self.delay_entry.get()))
            self.config.set('scanning.duplicate_filter_seconds', float(self.dup_entry.get()))
            self.config.set('scanning.auto_start', self.auto_start_check.get() == 1)
            
            logger.info("Settings saved")
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except ValueError as e:
            logger.error(f"Invalid setting value: {e}")