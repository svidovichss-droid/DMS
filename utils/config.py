"""Configuration management module."""

import json
import os
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration."""
    
    DEFAULT_CONFIG = {
        "app_name": "DataMatrix Quality Scanner",
        "version": "1.0.0",
        "camera": {
            "preferred_camera": 0,
            "resolution_width": 1280,
            "resolution_height": 720,
            "fps": 30,
            "auto_exposure": True,
            "brightness": 50,
            "contrast": 50
        },
        "scanning": {
            "auto_start": True,
            "scan_delay_ms": 100,
            "duplicate_filter_seconds": 2.0,
            "min_scan_interval_ms": 500
        },
        "quality_thresholds": {
            "grade_a_min": 3.5,
            "grade_b_min": 2.5,
            "grade_c_min": 1.5,
            "grade_d_min": 0.5,
            "symbol_contrast_min": 0.80,
            "edge_determinacy_min": 0.50,
            "axial_uniformity_max": 0.08,
            "grid_uniformity_max": 0.08,
            "unused_error_correction_min": 0.50,
            "fixed_pattern_damage_min": 0.60
        },
        "alarms": {
            "enable_audio": True,
            "enable_visual": True,
            "fail_only": True,
            "audio_file": "resources/sounds/alarm.wav"
        },
        "database": {
            "retention_days": 30,
            "auto_cleanup": True
        },
        "ui": {
            "language": "ru",
            "theme": "dark",
            "log_auto_scroll": True,
            "max_log_entries": 1000
        },
        "export": {
            "default_path": "",
            "csv_delimiter": ";",
            "include_images": False
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: dict = self.DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._merge_config(self.config, loaded)
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self._save_config()
        else:
            self._save_config()
            logger.info("Created default configuration")
    
    def _merge_config(self, base: dict, update: dict):
        """Recursively merge update dict into base dict."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else '.', 
                       exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key path."""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value by dot-separated key path."""
        keys = key_path.split('.')
        target = self.config
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
        self._save_config()
    
    def get_section(self, section: str) -> dict:
        """Get entire configuration section."""
        return self.config.get(section, {})
    
    def update_section(self, section: str, values: dict):
        """Update configuration section."""
        if section in self.config:
            self.config[section].update(values)
        else:
            self.config[section] = values
        self._save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config()
        logger.info("Configuration reset to defaults")
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()