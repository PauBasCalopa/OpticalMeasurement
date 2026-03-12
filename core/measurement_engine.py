"""
Measurement Engine

Handles all measurement calculations and management
"""

from typing import Tuple, List, Optional
from models.measurement_data import *
from models.calibration_data import CalibrationData
from utils.math_utils import *

class MeasurementEngine:
    """Handles measurement calculations and management"""
    
    def __init__(self):
        self.calibration: Optional[CalibrationData] = None
    
    def set_calibration(self, calibration: CalibrationData):
        """Set calibration data"""
        self.calibration = calibration
    
    def calculate_distance_measurement(self, point1: Tuple[float, float], 
                                     point2: Tuple[float, float]) -> DistanceMeasurement:
        """Calculate distance measurement between two points"""
        measurement = DistanceMeasurement()
        measurement.points = [point1, point2]
        
        # Calculate pixel distance
        pixel_distance = calculate_distance(point1, point2)
        
        # Convert to real-world units if calibrated
        if self.calibration and self.calibration.is_calibrated:
            measurement.result = self.calibration.pixels_to_units(pixel_distance)
        else:
            measurement.result = pixel_distance
        
        return measurement
    
    def calculate_radius_measurement(self, p1: Tuple[float, float], 
                                   p2: Tuple[float, float], 
                                   p3: Tuple[float, float]) -> RadiusMeasurement:
        """Calculate radius measurement from three points"""
        measurement = RadiusMeasurement()
        measurement.points = [p1, p2, p3]
        
        try:
            # Calculate circle center and radius
            center, pixel_radius = calculate_circle_center_radius(p1, p2, p3)
            measurement.center_point = center
            
            # Convert to real-world units if calibrated
            if self.calibration and self.calibration.is_calibrated:
                measurement.result = self.calibration.pixels_to_units(pixel_radius)
            else:
                measurement.result = pixel_radius
                
        except ValueError as e:
            # Handle collinear points
            measurement.result = None
            raise ValueError(str(e))
        
        return measurement
    
    def calculate_angle_measurement(self, p1: Tuple[float, float], 
                                  vertex: Tuple[float, float], 
                                  p3: Tuple[float, float]) -> AngleMeasurement:
        """Calculate angle measurement from three points"""
        measurement = AngleMeasurement()
        measurement.points = [p1, vertex, p3]
        measurement.vertex_index = 1
        
        # Calculate angle in degrees
        angle = calculate_angle_3_points(p1, vertex, p3)
        measurement.result = angle
        
        return measurement
    
    def calculate_two_line_angle_measurement(self, line1_p1: Tuple[float, float], 
                                           line1_p2: Tuple[float, float],
                                           line2_p1: Tuple[float, float], 
                                           line2_p2: Tuple[float, float]) -> TwoLineAngleMeasurement:
        """Calculate angle between two lines"""
        measurement = TwoLineAngleMeasurement()
        measurement.points = [line1_p1, line1_p2, line2_p1, line2_p2]
        
        # Calculate angle between lines
        angle = calculate_two_line_angle(line1_p1, line1_p2, line2_p1, line2_p2)
        measurement.result = angle
        
        return measurement
    
    def calculate_polygon_area_measurement(self, points: List[Tuple[float, float]]) -> PolygonAreaMeasurement:
        """Calculate polygon area measurement"""
        measurement = PolygonAreaMeasurement()
        measurement.points = points.copy()
        measurement.is_closed = True
        
        # Calculate pixel area
        pixel_area = calculate_polygon_area(points)
        
        # Convert to real-world units if calibrated
        if self.calibration and self.calibration.is_calibrated:
            # Area scales with square of the scale factor
            scale_factor_squared = self.calibration.scale_factor ** 2
            measurement.result = pixel_area * scale_factor_squared
        else:
            measurement.result = pixel_area
        
        return measurement
    
    def calculate_coordinate_measurement(self, points: List[Tuple[float, float]], 
                                       coord_type: str = "single") -> CoordinateMeasurement:
        """Calculate coordinate measurement"""
        measurement = CoordinateMeasurement()
        measurement.points = points.copy()
        measurement.coordinate_type = coord_type
        
        if coord_type == "single" and len(points) >= 1:
            # Single point coordinates
            x, y = points[0]
            
            # Convert to real-world units if calibrated
            if self.calibration and self.calibration.is_calibrated:
                # For coordinates, we might want to keep them as pixels
                # or define a coordinate system origin
                measurement.result = None  # Coordinates don't have a single result value
            else:
                measurement.result = None
                
        elif coord_type == "difference" and len(points) >= 2:
            # Coordinate differences
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]
            
            # Convert to real-world units if calibrated
            if self.calibration and self.calibration.is_calibrated:
                dx_units = self.calibration.pixels_to_units(abs(dx))
                dy_units = self.calibration.pixels_to_units(abs(dy))
                # Store the distance as the result
                measurement.result = calculate_distance((0, 0), (dx_units, dy_units))
            else:
                measurement.result = calculate_distance((0, 0), (dx, dy))
        
        return measurement
    
    def calculate_point_to_line_measurement(self, point: Tuple[float, float],
                                          line_start: Tuple[float, float], 
                                          line_end: Tuple[float, float]) -> PointToLineMeasurement:
        """Calculate point-to-line distance measurement"""
        measurement = PointToLineMeasurement()
        measurement.points = [point, line_start, line_end]
        
        # Calculate pixel distance
        pixel_distance = calculate_point_to_line_distance(point, line_start, line_end)
        
        # Convert to real-world units if calibrated
        if self.calibration and self.calibration.is_calibrated:
            measurement.result = self.calibration.pixels_to_units(pixel_distance)
        else:
            measurement.result = pixel_distance
        
        return measurement
    
    def calculate_arc_length_measurement(self, p1: Tuple[float, float], 
                                       p2: Tuple[float, float], 
                                       p3: Tuple[float, float]) -> ArcLengthMeasurement:
        """Calculate arc length measurement"""
        measurement = ArcLengthMeasurement()
        measurement.points = [p1, p2, p3]
        
        try:
            # Calculate arc length in pixels
            pixel_arc_length = calculate_arc_length(p1, p2, p3)
            
            # Also calculate center and radius for display
            center, radius = calculate_circle_center_radius(p1, p2, p3)
            measurement.center_point = center
            
            if self.calibration and self.calibration.is_calibrated:
                measurement.radius = self.calibration.pixels_to_units(radius)
            else:
                measurement.radius = radius
            
            # Convert arc length to real-world units if calibrated
            if self.calibration and self.calibration.is_calibrated:
                measurement.result = self.calibration.pixels_to_units(pixel_arc_length)
            else:
                measurement.result = pixel_arc_length
                
        except ValueError as e:
            # Handle collinear points - fallback to line segments
            dist1 = calculate_distance(p1, p2)
            dist2 = calculate_distance(p2, p3)
            pixel_length = dist1 + dist2
            
            if self.calibration and self.calibration.is_calibrated:
                measurement.result = self.calibration.pixels_to_units(pixel_length)
            else:
                measurement.result = pixel_length
        
        return measurement
    
    def format_measurement_result(self, measurement: MeasurementBase, 
                                decimal_places: int = 2) -> str:
        """Format measurement result for display"""
        if measurement.result is None:
            return "N/A"
        
        # Format based on measurement type
        if measurement.measurement_type in ["distance", "radius", "point_to_line", "arc_length"]:
            if self.calibration and self.calibration.is_calibrated:
                return f"{measurement.result:.{decimal_places}f} units"
            else:
                return f"{measurement.result:.{decimal_places}f} px"
                
        elif measurement.measurement_type == "polygon_area":
            if self.calibration and self.calibration.is_calibrated:
                return f"{measurement.result:.{decimal_places}f} units^2"
            else:
                return f"{measurement.result:.{decimal_places}f} px^2"
                
        elif measurement.measurement_type in ["angle", "two_line_angle"]:
            return f"{measurement.result:.{decimal_places}f} degrees"
            
        elif measurement.measurement_type == "coordinate":
            if measurement.coordinate_type == "single" and len(measurement.points) > 0:
                x, y = measurement.points[0]
                if self.calibration and self.calibration.is_calibrated:
                    x_units = self.calibration.pixels_to_units(x)
                    y_units = self.calibration.pixels_to_units(y)
                    return f"({x_units:.{decimal_places}f}, {y_units:.{decimal_places}f}) units"
                else:
                    return f"({x:.{decimal_places}f}, {y:.{decimal_places}f}) px"
            elif measurement.coordinate_type == "difference":
                return f"{measurement.result:.{decimal_places}f} {'units' if self.calibration and self.calibration.is_calibrated else 'px'}"
        
        return str(measurement.result)
    
    def complete(self, tool_type: str, points: List[Tuple[float, float]]) -> Optional[MeasurementBase]:
        """Unified measurement completion — dispatches to the appropriate calculator.
        
        Returns the completed measurement, or None if insufficient points.
        Raises ValueError on calculation errors (e.g. collinear points for radius).
        """
        if tool_type == "distance" and len(points) >= 2:
            return self.calculate_distance_measurement(points[0], points[1])
        elif tool_type == "radius" and len(points) >= 3:
            return self.calculate_radius_measurement(points[0], points[1], points[2])
        elif tool_type == "angle" and len(points) >= 3:
            return self.calculate_angle_measurement(points[0], points[1], points[2])
        elif tool_type == "two_line_angle" and len(points) >= 4:
            return self.calculate_two_line_angle_measurement(
                points[0], points[1], points[2], points[3])
        elif tool_type == "polygon_area" and len(points) >= 3:
            return self.calculate_polygon_area_measurement(list(points))
        elif tool_type == "coordinate" and len(points) >= 1:
            coord_type = "single" if len(points) == 1 else "difference"
            return self.calculate_coordinate_measurement(list(points), coord_type)
        elif tool_type == "point_to_line" and len(points) >= 3:
            return self.calculate_point_to_line_measurement(points[0], points[1], points[2])
        elif tool_type == "arc_length" and len(points) >= 3:
            return self.calculate_arc_length_measurement(points[0], points[1], points[2])
        return None