"""
Calibration Data Model

Contains scale factor and calibration information
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

@dataclass
class CalibrationData:
    """Scale factor and calibration information"""
    
    # Calibration points (in image coordinates)
    point1: Optional[Tuple[float, float]] = None
    point2: Optional[Tuple[float, float]] = None
    
    # Real world distance between points
    real_distance: Optional[float] = None
    
    # Calculated scale factor (units per pixel)
    scale_factor: Optional[float] = None
    
    # Pixel distance between calibration points
    pixel_distance: Optional[float] = None
    
    def calibrate(self, point1: Tuple[float, float], point2: Tuple[float, float], real_distance: float):
        """Establish calibration from two points and real distance"""
        if real_distance <= 0:
            raise ValueError("Real distance must be positive")
        
        self.point1 = point1
        self.point2 = point2
        self.real_distance = real_distance
        
        # Calculate pixel distance
        self.pixel_distance = np.sqrt((point2[0] - point1[0])**2 + 
                                    (point2[1] - point1[1])**2)
        
        if self.pixel_distance == 0:
            raise ValueError("Calibration points cannot be the same")
        
        # Calculate scale factor (units per pixel)
        self.scale_factor = real_distance / self.pixel_distance
    
    def pixels_to_units(self, pixel_value: float) -> float:
        """Convert pixels to real-world units"""
        if self.scale_factor is None:
            raise ValueError("Calibration not set")
        return pixel_value * self.scale_factor
    
    def units_to_pixels(self, unit_value: float) -> float:
        """Convert real-world units to pixels"""
        if self.scale_factor is None:
            raise ValueError("Calibration not set")
        return unit_value / self.scale_factor
    
    @property
    def is_calibrated(self) -> bool:
        """Check if calibration is valid"""
        return (self.scale_factor is not None and 
                self.scale_factor > 0 and
                self.point1 is not None and
                self.point2 is not None)
    
    @property
    def precision(self) -> float:
        """Get measurement precision (plus/minus units)"""
        if not self.is_calibrated:
            return 0.0
        # Half-pixel precision
        return self.scale_factor * 0.5
    
    def __str__(self) -> str:
        """String representation"""
        if self.is_calibrated:
            return f"Scale: 1 pixel = {self.scale_factor:.4f} units (+/-{self.precision:.4f})"
        return "Not calibrated"