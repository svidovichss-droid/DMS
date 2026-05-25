"""ISO 15415 quality analysis for Data Matrix codes."""

import cv2
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """ISO 15415 quality metrics for Data Matrix."""
    symbol_contrast: float = 0.0
    edge_determinacy: float = 0.0
    axial_non_uniformity: float = 0.0
    grid_non_uniformity: float = 0.0
    unused_error_correction: float = 0.0
    fixed_pattern_damage: float = 0.0
    decode_success: bool = False
    overall_grade: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'symbol_contrast': self.symbol_contrast,
            'edge_determinacy': self.edge_determinacy,
            'axial_non_uniformity': self.axial_non_uniformity,
            'grid_non_uniformity': self.grid_non_uniformity,
            'unused_error_correction': self.unused_error_correction,
            'fixed_pattern_damage': self.fixed_pattern_damage,
            'decode_success': self.decode_success,
            'overall_grade': self.overall_grade
        }


class QualityAnalyzer:
    """Analyzes Data Matrix quality according to ISO 15415."""
    
    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {
            'symbol_contrast_min': 0.80,
            'edge_determinacy_min': 0.50,
            'axial_uniformity_max': 0.08,
            'grid_uniformity_max': 0.08,
            'unused_error_correction_min': 0.50,
            'fixed_pattern_damage_min': 0.60
        }
        
    def analyze(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                decoded_data: str) -> QualityMetrics:
        """
        Analyze Data Matrix quality.
        
        Args:
            frame: Original BGR image
            bbox: Bounding box (x, y, w, h)
            decoded_data: Decoded string from Data Matrix
            
        Returns:
            QualityMetrics object with all quality parameters
        """
        x, y, w, h = bbox
        
        # Add margin for analysis
        margin = max(w, h) // 4
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(frame.shape[1], x + w + margin)
        y2 = min(frame.shape[0], y + h + margin)
        
        # Extract region
        region = frame[y1:y2, x1:x2]
        
        # Convert to grayscale
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        
        metrics = QualityMetrics()
        metrics.decode_success = len(decoded_data) > 0
        
        if not metrics.decode_success:
            metrics.overall_grade = 0.0
            return metrics
        
        # Calculate all metrics
        metrics.symbol_contrast = self._calculate_symbol_contrast(gray)
        metrics.edge_determinacy = self._calculate_edge_determinacy(gray)
        metrics.axial_non_uniformity = self._calculate_axial_uniformity(gray)
        metrics.grid_non_uniformity = self._calculate_grid_uniformity(gray)
        metrics.unused_error_correction = self._estimate_uect(region)
        metrics.fixed_pattern_damage = self._calculate_fixed_pattern_damage(gray, w, h)
        
        # Calculate overall grade
        metrics.overall_grade = self._calculate_overall_grade(metrics)
        
        return metrics
    
    def _calculate_symbol_contrast(self, gray: np.ndarray) -> float:
        """
        Calculate Symbol Contrast (SC).
        SC = (Rmax - Rmin) / (Rmax + Rmin)
        Minimum: 0.80 for Grade A
        """
        min_val = np.min(gray)
        max_val = np.max(gray)
        
        if max_val + min_val == 0:
            return 0.0
            
        sc = (max_val - min_val) / (max_val + min_val)
        return min(1.0, sc)
    
    def _calculate_edge_determinacy(self, gray: np.ndarray) -> float:
        """
        Calculate Module Edge Determinacy (ED).
        Measures the edge sharpness of modules.
        Minimum: 0.50 for Grade A
        """
        # Calculate gradients
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Calculate edge determinacy as ratio of strong edges
        threshold = np.mean(gradient_magnitude) * 0.5
        strong_edges = gradient_magnitude > threshold
        
        ed = np.sum(strong_edges) / gradient_magnitude.size
        return min(1.0, ed * 2)  # Scale to 0-1
    
    def _calculate_axial_uniformity(self, gray: np.ndarray) -> float:
        """
        Calculate Axial Non-Uniformity (AN).
        Measures variation in horizontal vs vertical module sizes.
        Maximum: 0.08 for Grade A
        """
        # Project intensity onto X and Y axes
        proj_x = np.sum(gray, axis=0) / gray.shape[0]
        proj_y = np.sum(gray, axis=1) / gray.shape[1]
        
        # Find peaks (module boundaries)
        peaks_x = self._find_peaks(proj_x)
        peaks_y = self._find_peaks(proj_y)
        
        if len(peaks_x) < 2 or len(peaks_y) < 2:
            return 0.0
            
        # Calculate module sizes
        sizes_x = np.diff(peaks_x)
        sizes_y = np.diff(peaks_y)
        
        # Calculate non-uniformity
        mean_x = np.mean(sizes_x) if len(sizes_x) > 0 else 1
        mean_y = np.mean(sizes_y) if len(sizes_y) > 0 else 1
        
        if mean_x + mean_y == 0:
            return 0.0
            
        an = abs(mean_x - mean_y) / (mean_x + mean_y)
        return min(1.0, an)
    
    def _calculate_grid_uniformity(self, gray: np.ndarray) -> float:
        """
        Calculate Grid Non-Uniformity (GN).
        Measures distortion in the grid pattern.
        Maximum: 0.08 for Grade A
        """
        # Find grid intersection points
        corners = self._find_grid_corners(gray)
        
        if len(corners) < 4:
            return 0.5  # Return middle value if grid not detected
            
        # Calculate grid spacing
        distances = []
        for i in range(len(corners)):
            for j in range(i + 1, len(corners)):
                dist = np.sqrt((corners[i][0] - corners[j][0])**2 + 
                              (corners[i][1] - corners[j][1])**2)
                distances.append(dist)
        
        if len(distances) < 2:
            return 0.0
            
        std_dev = np.std(distances)
        mean_dist = np.mean(distances)
        
        if mean_dist == 0:
            return 0.0
            
        gn = std_dev / mean_dist
        return min(1.0, gn)
    
    def _estimate_uect(self, region: np.ndarray) -> float:
        """
        Estimate Unused Error Correction (UEC).
        For Data Matrix, this is related to the contrast in finder patterns.
        Minimum: 0.50 for Grade A
        """
        # Estimate based on overall image quality
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
            
        # Calculate local contrast variance
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        variance = np.var(blur)
        
        # Normalize to 0-1 range
        uect = min(1.0, variance / 1000)
        return uect
    
    def _calculate_fixed_pattern_damage(self, gray: np.ndarray, 
                                       width: int, height: int) -> float:
        """
        Calculate Fixed Pattern Damage (FPD).
        Measures damage to finder patterns and timing patterns.
        Minimum: 0.60 for Grade A
        """
        # Look for the L-shaped finder pattern (common in Data Matrix)
        edges = cv2.Canny(gray, 50, 150)
        
        # Count edge pixels in the border region
        border_size = max(3, min(width, height) // 8)
        top_border = edges[:border_size, :]
        left_border = edges[:, :border_size]
        
        border_pixels = np.sum(top_border > 0) + np.sum(left_border > 0)
        total_border = top_border.size + left_border.size
        
        if total_border == 0:
            return 0.5
            
        # Calculate damage ratio
        damage_ratio = border_pixels / total_border
        
        # More edges in border means better pattern detection
        fpd = min(1.0, damage_ratio)
        return fpd
    
    def _find_peaks(self, signal: np.ndarray) -> np.ndarray:
        """Find peaks in a 1D signal."""
        if len(signal) < 3:
            return np.array([])
            
        # Simple peak detection
        threshold = np.mean(signal)
        peaks = []
        
        for i in range(1, len(signal) - 1):
            if signal[i] > threshold:
                if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                    peaks.append(i)
        
        return np.array(peaks)
    
    def _find_grid_corners(self, gray: np.ndarray) -> list:
        """Find potential grid corner points."""
        # Use corner detection
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=20, qualityLevel=0.01, 
                                          minDistance=10)
        
        if corners is None:
            return []
            
        return [(int(c[0][0]), int(c[0][1])) for c in corners]
    
    def _calculate_overall_grade(self, metrics: QualityMetrics) -> float:
        """
        Calculate overall quality grade (0-5 scale).
        Weighted average of all metrics.
        """
        # ISO 15415 weighted grading
        # Decode is critical - if fails, grade is 0
        if not metrics.decode_success:
            return 0.0
        
        # Calculate grade based on thresholds
        sc_grade = 5.0 if metrics.symbol_contrast >= self.thresholds['symbol_contrast_min'] else \
                   4.0 if metrics.symbol_contrast >= 0.65 else \
                   3.0 if metrics.symbol_contrast >= 0.50 else \
                   2.0 if metrics.symbol_contrast >= 0.35 else 0.0
                   
        ed_grade = 5.0 if metrics.edge_determinacy >= self.thresholds['edge_determinacy_min'] else \
                   4.0 if metrics.edge_determinacy >= 0.40 else \
                   3.0 if metrics.edge_determinacy >= 0.30 else \
                   2.0 if metrics.edge_determinacy >= 0.20 else 0.0
                   
        an_grade = 5.0 if metrics.axial_non_uniformity <= self.thresholds['axial_uniformity_max'] else \
                   4.0 if metrics.axial_non_uniformity <= 0.12 else \
                   3.0 if metrics.axial_non_uniformity <= 0.15 else \
                   2.0 if metrics.axial_non_uniformity <= 0.20 else 0.0
                   
        gn_grade = 5.0 if metrics.grid_non_uniformity <= self.thresholds['grid_uniformity_max'] else \
                   4.0 if metrics.grid_non_uniformity <= 0.12 else \
                   3.0 if metrics.grid_non_uniformity <= 0.15 else \
                   2.0 if metrics.grid_non_uniformity <= 0.20 else 0.0
                   
        uect_grade = 5.0 if metrics.unused_error_correction >= self.thresholds['unused_error_correction_min'] else \
                     4.0 if metrics.unused_error_correction >= 0.40 else \
                     3.0 if metrics.unused_error_correction >= 0.30 else \
                     2.0 if metrics.unused_error_correction >= 0.20 else 0.0
                     
        fpd_grade = 5.0 if metrics.fixed_pattern_damage >= self.thresholds['fixed_pattern_damage_min'] else \
                    4.0 if metrics.fixed_pattern_damage >= 0.50 else \
                    3.0 if metrics.fixed_pattern_damage >= 0.40 else \
                    2.0 if metrics.fixed_pattern_damage >= 0.30 else 0.0
        
        # Weighted average (ISO 15415 style)
        # SC and DEC are most important
        overall = (sc_grade * 0.25 + 
                  ed_grade * 0.15 + 
                  an_grade * 0.15 + 
                  gn_grade * 0.15 + 
                  uect_grade * 0.15 + 
                  fpd_grade * 0.15)
        
        return round(overall, 1)
    
    def get_grade_letter(self, score: float) -> str:
        """Convert numeric grade to letter grade."""
        if score >= 3.5:
            return 'A'
        elif score >= 2.5:
            return 'B'
        elif score >= 1.5:
            return 'C'
        elif score >= 0.5:
            return 'D'
        else:
            return 'F'
    
    def is_pass(self, metrics: QualityMetrics, 
               min_grade: float = 2.0) -> bool:
        """Check if quality passes minimum requirements."""
        return metrics.overall_grade >= min_grade and metrics.decode_success
