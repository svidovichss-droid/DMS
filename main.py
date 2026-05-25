#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataMatrix Quality Scanner - Main Entry Point
ISO 15415 DataMatrix code quality verification system
"""

import sys
import os
import logging
from pathlib import Path

# Add the application directory to the path for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys.executable
    base_path = Path(sys.executable).parent
else:
    # Running in a normal Python environment
    application_path = __file__
    base_path = Path(__file__).parent.parent

# Setup logging
log_dir = base_path / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scanner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    logger.info("Starting DataMatrix Quality Scanner")
    
    try:
        import customtkinter as ctk
        from utils.config import ConfigManager
        from scanner.database import DatabaseManager
        from ui.main_window import MainWindow
        
        # Initialize configuration
        config_path = base_path / 'config.json'
        config_example = base_path / 'config.json.example'
        
        if not config_path.exists() and config_example.exists():
            logger.info("Creating config.json from example")
            import shutil
            shutil.copy(config_example, config_path)
        
        config_manager = ConfigManager(str(config_path))
        config = config_manager.get_config()
        
        # Initialize database
        db_path = base_path / 'scans.db'
        db_manager = DatabaseManager(str(db_path))
        
        # Create and run application
        app = MainWindow(config)
        
        def on_scan_action(action: str):
            """Handle scan start/stop actions."""
            if action == 'start':
                logger.info("Scanning started")
            elif action == 'stop':
                logger.info("Scanning stopped")
        
        app.on_scan_callback = on_scan_action
        app.mainloop()
        
        # Cleanup
        db_manager.close()
        logger.info("Application closed")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Error: {e}")
        input("Press Enter to exit...")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
