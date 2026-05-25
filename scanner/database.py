"""Database module for scan history and statistics."""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScanRecord:
    """Record of a single scan operation."""
    id: Optional[int]
    timestamp: str
    code_data: str
    grade: str
    score: float
    sc: float
    ed: float
    an: float
    gn: float
    uect: float
    fpd: float
    decode_success: bool
    passed: bool
    camera_id: str
    image_path: Optional[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class DatabaseManager:
    """Manages SQLite database for scan history."""
    
    def __init__(self, db_path: str = "datamatrix_scanner.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    code_data TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    score REAL NOT NULL,
                    sc REAL NOT NULL,
                    ed REAL NOT NULL,
                    an REAL NOT NULL,
                    gn REAL NOT NULL,
                    uect REAL NOT NULL,
                    fpd REAL NOT NULL,
                    decode_success INTEGER NOT NULL,
                    passed INTEGER NOT NULL,
                    camera_id TEXT NOT NULL,
                    image_path TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON scans(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_grade ON scans(grade)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_code ON scans(code_data)
            ''')
            
            self.connection.commit()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def insert_scan(self, record: ScanRecord) -> int:
        """Insert a new scan record."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO scans (
                    timestamp, code_data, grade, score, sc, ed, an, gn, uect, fpd,
                    decode_success, passed, camera_id, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.timestamp,
                record.code_data,
                record.grade,
                record.score,
                record.sc,
                record.ed,
                record.an,
                record.gn,
                record.uect,
                record.fpd,
                int(record.decode_success),
                int(record.passed),
                record.camera_id,
                record.image_path
            ))
            
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Insert error: {e}")
            self.connection.rollback()
            return -1
    
    def get_recent_scans(self, limit: int = 100) -> List[ScanRecord]:
        """Get recent scan records."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM scans 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_scans_by_date_range(self, start: datetime, end: datetime) -> List[ScanRecord]:
        """Get scans within date range."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM scans 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start.isoformat(), end.isoformat()))
            
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """Get statistics for the specified time period."""
        try:
            since = datetime.now() - timedelta(hours=hours)
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_scans,
                    SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                    SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) as failed,
                    AVG(score) as avg_score
                FROM scans
                WHERE timestamp >= ?
            ''', (since.isoformat(),))
            
            row = cursor.fetchone()
            
            # Get grade distribution
            cursor.execute('''
                SELECT grade, COUNT(*) as count
                FROM scans
                WHERE timestamp >= ?
                GROUP BY grade
            ''', (since.isoformat(),))
            
            grade_dist = {row['grade']: row['count'] for row in cursor.fetchall()}
            
            # Get unique codes count
            cursor.execute('''
                SELECT COUNT(DISTINCT code_data) as unique_codes
                FROM scans
                WHERE timestamp >= ?
            ''', (since.isoformat(),))
            
            unique_row = cursor.fetchone()
            
            return {
                'total_scans': row['total_scans'] or 0,
                'passed': row['passed'] or 0,
                'failed': row['failed'] or 0,
                'avg_score': round(row['avg_score'] or 0, 2),
                'grade_distribution': grade_dist,
                'unique_codes': unique_row['unique_codes'] or 0
            }
            
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {
                'total_scans': 0,
                'passed': 0,
                'failed': 0,
                'avg_score': 0.0,
                'grade_distribution': {},
                'unique_codes': 0
            }
    
    def cleanup_old_records(self, days: int = 30):
        """Delete records older than specified days."""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            cursor = self.connection.cursor()
            cursor.execute('''
                DELETE FROM scans WHERE timestamp < ?
            ''', (cutoff.isoformat(),))
            
            deleted = cursor.rowcount
            self.connection.commit()
            logger.info(f"Deleted {deleted} old records")
            return deleted
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            self.connection.rollback()
            return 0
    
    def export_to_csv(self, filepath: str, start: Optional[datetime] = None,
                     end: Optional[datetime] = None) -> bool:
        """Export scans to CSV file."""
        try:
            import csv
            
            if start is None:
                start = datetime.now() - timedelta(days=30)
            if end is None:
                end = datetime.now()
            
            scans = self.get_scans_by_date_range(start, end)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if scans:
                    fieldnames = list(scans[0].to_dict().keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                    writer.writeheader()
                    
                    for scan in scans:
                        writer.writerow(scan.to_dict())
            
            logger.info(f"Exported {len(scans)} records to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    def _row_to_record(self, row: sqlite3.Row) -> ScanRecord:
        """Convert database row to ScanRecord."""
        return ScanRecord(
            id=row['id'],
            timestamp=row['timestamp'],
            code_data=row['code_data'],
            grade=row['grade'],
            score=row['score'],
            sc=row['sc'],
            ed=row['ed'],
            an=row['an'],
            gn=row['gn'],
            uect=row['uect'],
            fpd=row['fpd'],
            decode_success=bool(row['decode_success']),
            passed=bool(row['passed']),
            camera_id=row['camera_id'],
            image_path=row['image_path']
        )
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
