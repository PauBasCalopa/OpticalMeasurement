"""
Measurement Data Models

Base classes and specific measurement types
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime
import uuid

@dataclass
class MeasurementBase:
    """Base class for all measurements"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    points: List[Tuple[float, float]] = field(default_factory=list)
    result: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    measurement_type: str = "base"
    
    def __post_init__(self):
        """Post-initialization setup"""
        if not self.label:
            # Create more descriptive default labels
            type_names = {
                "distance": "Distance",
                "radius": "Radius", 
                "angle": "Angle",
                "two_line_angle": "Line Angle",
                "polygon_area": "Area",
                "coordinate": "Coordinate",
                "point_to_line": "P-to-Line",
                "arc_length": "Arc Length"
            }
            type_name = type_names.get(self.measurement_type, self.measurement_type.title())
            self.label = f"{type_name} {self.id[:8]}"

@dataclass
class DistanceMeasurement(MeasurementBase):
    """Two-point distance measurement"""
    
    def __post_init__(self):
        self.measurement_type = "distance"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        return len(self.points) == 2

@dataclass
class RadiusMeasurement(MeasurementBase):
    """Three-point circle radius measurement"""
    
    center_point: Optional[Tuple[float, float]] = None
    
    def __post_init__(self):
        self.measurement_type = "radius"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        return len(self.points) == 3

@dataclass
class AngleMeasurement(MeasurementBase):
    """Three-point angle measurement"""
    
    vertex_index: int = 1  # Index of vertex point (usually middle point)
    
    def __post_init__(self):
        self.measurement_type = "angle"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        return len(self.points) == 3

@dataclass
class TwoLineAngleMeasurement(MeasurementBase):
    """Four-point angle between two lines measurement"""
    
    def __post_init__(self):
        self.measurement_type = "two_line_angle"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        return len(self.points) == 4
    
    @property
    def line1_points(self) -> List[Tuple[float, float]]:
        """Get first line points"""
        return self.points[:2] if len(self.points) >= 2 else []
    
    @property
    def line2_points(self) -> List[Tuple[float, float]]:
        """Get second line points"""
        return self.points[2:4] if len(self.points) >= 4 else []

@dataclass
class PolygonAreaMeasurement(MeasurementBase):
    """Multi-point polygon area measurement"""
    
    is_closed: bool = False
    
    def __post_init__(self):
        self.measurement_type = "polygon_area"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has minimum required points"""
        return len(self.points) >= 3

@dataclass
class CoordinateMeasurement(MeasurementBase):
    """Point coordinate measurement"""
    
    coordinate_type: str = "single"  # "single" or "difference"
    
    def __post_init__(self):
        self.measurement_type = "coordinate"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        if self.coordinate_type == "single":
            return len(self.points) == 1
        elif self.coordinate_type == "difference":
            return len(self.points) == 2
        return False

@dataclass
class PointToLineMeasurement(MeasurementBase):
    """Point-to-line distance measurement"""
    
    def __post_init__(self):
        self.measurement_type = "point_to_line"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        return len(self.points) == 3  # point + line (2 points)
    
    @property
    def point(self) -> Optional[Tuple[float, float]]:
        """Get the point"""
        return self.points[0] if len(self.points) >= 1 else None
    
    @property
    def line_points(self) -> List[Tuple[float, float]]:
        """Get line points"""
        return self.points[1:3] if len(self.points) >= 3 else []

@dataclass
class ArcLengthMeasurement(MeasurementBase):
    """Three-point arc length measurement"""
    
    center_point: Optional[Tuple[float, float]] = None
    radius: Optional[float] = None
    
    def __post_init__(self):
        self.measurement_type = "arc_length"
        super().__post_init__()
    
    @property
    def is_complete(self) -> bool:
        """Check if measurement has required points"""
        return len(self.points) == 3