"""
Mathematical Utilities

Core mathematical functions for measurements using numpy
"""

import numpy as np
from typing import Tuple, List
import math

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def calculate_angle_3_points(p1: Tuple[float, float], vertex: Tuple[float, float], 
                           p3: Tuple[float, float]) -> float:
    """Calculate angle at vertex from three points (in degrees)"""
    # Create vectors from vertex to other points
    v1 = np.array([p1[0] - vertex[0], p1[1] - vertex[1]])
    v2 = np.array([p3[0] - vertex[0], p3[1] - vertex[1]])
    
    # Calculate dot product and magnitudes
    dot_product = np.dot(v1, v2)
    magnitude1 = np.linalg.norm(v1)
    magnitude2 = np.linalg.norm(v2)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # Calculate angle using dot product formula
    cos_angle = dot_product / (magnitude1 * magnitude2)
    
    # Clamp to valid range for arccos
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    # Convert to degrees
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

def calculate_two_line_angle(line1_p1: Tuple[float, float], line1_p2: Tuple[float, float],
                           line2_p1: Tuple[float, float], line2_p2: Tuple[float, float]) -> float:
    """Calculate angle between two lines (in degrees)"""
    # Create direction vectors for each line
    v1 = np.array([line1_p2[0] - line1_p1[0], line1_p2[1] - line1_p1[1]])
    v2 = np.array([line2_p2[0] - line2_p1[0], line2_p2[1] - line2_p1[1]])
    
    # Normalize vectors
    v1_norm = v1 / np.linalg.norm(v1) if np.linalg.norm(v1) > 0 else v1
    v2_norm = v2 / np.linalg.norm(v2) if np.linalg.norm(v2) > 0 else v2
    
    # Calculate dot product
    dot_product = np.dot(v1_norm, v2_norm)
    
    # Clamp to valid range for arccos
    dot_product = np.clip(dot_product, -1.0, 1.0)
    
    # Calculate angle
    angle_rad = np.arccos(abs(dot_product))  # Use abs to get acute angle
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

def calculate_circle_center_radius(p1: Tuple[float, float], p2: Tuple[float, float], 
                                 p3: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
    """Calculate circle center and radius from three points"""
    # Convert to numpy arrays
    A = np.array(p1)
    B = np.array(p2)
    C = np.array(p3)
    
    # Check if points are collinear
    if are_points_collinear(p1, p2, p3):
        raise ValueError("Points are collinear - cannot form a circle")
    
    # Calculate perpendicular bisectors
    # Midpoints of AB and BC
    mid_AB = (A + B) / 2
    mid_BC = (B + C) / 2
    
    # Direction vectors of AB and BC
    dir_AB = B - A
    dir_BC = C - B
    
    # Perpendicular vectors (rotate 90 degrees)
    perp_AB = np.array([-dir_AB[1], dir_AB[0]])
    perp_BC = np.array([-dir_BC[1], dir_BC[0]])
    
    # Find intersection of perpendicular bisectors
    # mid_AB + t * perp_AB = mid_BC + s * perp_BC
    # Solve for t
    denominator = perp_AB[0] * perp_BC[1] - perp_AB[1] * perp_BC[0]
    
    if abs(denominator) < 1e-10:
        raise ValueError("Cannot calculate circle center - perpendicular bisectors are parallel")
    
    diff = mid_BC - mid_AB
    t = (diff[0] * perp_BC[1] - diff[1] * perp_BC[0]) / denominator
    
    # Calculate center
    center = mid_AB + t * perp_AB
    
    # Calculate radius as distance from center to any point
    radius = calculate_distance(tuple(center), p1)
    
    return (tuple(center), radius)

def calculate_polygon_area(points: List[Tuple[float, float]]) -> float:
    """Calculate polygon area using the shoelace formula"""
    if len(points) < 3:
        return 0.0
    
    # Convert to numpy array for easier calculation
    points_array = np.array(points)
    x = points_array[:, 0]
    y = points_array[:, 1]
    
    # Shoelace formula
    area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    
    return area

def calculate_point_to_line_distance(point: Tuple[float, float], 
                                   line_start: Tuple[float, float], 
                                   line_end: Tuple[float, float]) -> float:
    """Calculate perpendicular distance from point to line"""
    # Point coordinates
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Calculate distance using the formula:
    # |((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)| / sqrt((y2-y1)^2 + (x2-x1)^2)
    
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    if denominator == 0:
        # Line start and end are the same point - return distance to that point
        return calculate_distance(point, line_start)
    
    return numerator / denominator

def find_closest_point_on_line(point: Tuple[float, float], 
                              line_start: Tuple[float, float], 
                              line_end: Tuple[float, float]) -> Tuple[float, float]:
    """Find the closest point on a line segment to a given point"""
    # Point coordinates
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Vector from line_start to line_end
    dx = x2 - x1
    dy = y2 - y1
    
    # If line_start and line_end are the same point
    if dx == 0 and dy == 0:
        return line_start
    
    # Calculate parameter t for the closest point
    # Closest point = line_start + t * (line_end - line_start)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    
    # Clamp t to [0, 1] to stay within the line segment
    t = max(0, min(1, t))
    
    # Calculate the closest point
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    return (closest_x, closest_y)

def get_perpendicular_point_on_line(point: Tuple[float, float], 
                                   line_start: Tuple[float, float], 
                                   line_end: Tuple[float, float]) -> Tuple[float, float]:
    """Find the perpendicular point on an infinite line from a given point
    
    This is similar to find_closest_point_on_line but doesn't clamp to the line segment.
    """
    # Point coordinates
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Vector from line_start to line_end
    dx = x2 - x1
    dy = y2 - y1
    
    # If line_start and line_end are the same point
    if dx == 0 and dy == 0:
        return line_start
    
    # Calculate parameter t for the perpendicular point
    # Perpendicular point = line_start + t * (line_end - line_start)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    
    # Don't clamp t - allow point to be outside the line segment
    perp_x = x1 + t * dx
    perp_y = y1 + t * dy
    
    return (perp_x, perp_y)

def calculate_arc_length(p1: Tuple[float, float], p2: Tuple[float, float], 
                        p3: Tuple[float, float]) -> float:
    """Calculate arc length through three points"""
    try:
        # Get circle center and radius
        (center_x, center_y), radius = calculate_circle_center_radius(p1, p2, p3)
        
        # Calculate angles from center to each point
        angle1 = math.atan2(p1[1] - center_y, p1[0] - center_x)
        angle3 = math.atan2(p3[1] - center_y, p3[0] - center_x)
        
        # Calculate the central angle (always take the smaller arc)
        central_angle = abs(angle3 - angle1)
        if central_angle > math.pi:
            central_angle = 2 * math.pi - central_angle
        
        # Arc length = radius * central_angle
        arc_length = radius * central_angle
        
        return arc_length
        
    except ValueError:
        # If points are collinear, return sum of distances
        dist1 = calculate_distance(p1, p2)
        dist2 = calculate_distance(p2, p3)
        return dist1 + dist2

def are_points_collinear(p1: Tuple[float, float], p2: Tuple[float, float], 
                        p3: Tuple[float, float], tolerance: float = 1e-10) -> bool:
    """Check if three points are collinear"""
    # Calculate cross product of vectors (p2-p1) and (p3-p1)
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p3[0] - p1[0], p3[1] - p1[1])
    
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]
    
    return abs(cross_product) < tolerance

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """Check if point is inside polygon using ray casting algorithm"""
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        
        p1x, p1y = p2x, p2y
    
    return inside

def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians"""
    return math.radians(degrees)

def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees"""
    return math.degrees(radians)