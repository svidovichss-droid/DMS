"""Logging utilities for DataMatrix Scanner."""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "datamatrix_scanner", 
                log_file: str = "logs/scanner.log",
                level: int = logging.INFO) -> logging.Logger:
    """
    Setup application logger.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if needed
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger


class ScanLogger:
    """Logger for scan events with structured output."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.scan_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.start_time = datetime.now()
    
    def log_scan(self, code: str, grade: str, score: float, passed: bool, 
                scan_time_ms: float = 0):
        """Log a scan event."""
        self.scan_count += 1
        if passed:
            self.pass_count += 1
        else:
            self.fail_count += 1
        
        status = "PASS" if passed else "FAIL"
        self.logger.info(
            f"SCAN | Code: {code[:30]:<30} | Grade: {grade} | "
            f"Score: {score:.1f} | Status: {status} | Time: {scan_time_ms:.0f}ms"
        )
    
    def log_error(self, message: str, exception: Exception = None):
        """Log an error event."""
        if exception:
            self.logger.error(f"ERROR | {message} | Exception: {exception}")
        else:
            self.logger.error(f"ERROR | {message}")
    
    def log_warning(self, message: str):
        """Log a warning event."""
        self.logger.warning(f"WARNING | {message}")
    
    def log_camera_event(self, event: str, camera_id: int = 0):
        """Log camera-related event."""
        self.logger.info(f"CAMERA [{camera_id}] | {event}")
    
    def get_statistics(self) -> dict:
        """Get scan statistics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        rate = self.scan_count / uptime if uptime > 0 else 0
        
        return {
            'total_scans': self.scan_count,
            'passed': self.pass_count,
            'failed': self.fail_count,
            'pass_rate': self.pass_count / self.scan_count if self.scan_count > 0 else 0,
            'uptime_seconds': uptime,
            'scan_rate_per_minute': rate * 60
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.scan_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.start_time = datetime.now()


def get_logger(name: str = "datamatrix_scanner") -> logging.Logger:
    """Get or create logger instance."""
    return logging.getLogger(name)