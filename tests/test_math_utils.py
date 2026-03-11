"""
Unit Tests for Mathematical Utilities

Tests for core mathematical functions used in measurements
"""

import pytest
import math
from utils.math_utils import (
    calculate_distance,
    calculate_angle_3_points,
    calculate_two_line_angle,
    calculate_circle_center_radius,
    calculate_polygon_area,
    calculate_point_to_line_distance,
    calculate_arc_length,
    are_points_collinear,
    degrees_to_radians,
    radians_to_degrees
)

class TestDistanceCalculation:
    """Test distance calculation functions"""
    
    def test_basic_distance(self):
        """Test basic distance calculation"""
        # 3-4-5 triangle
        distance = calculate_distance((0, 0), (3, 4))
        assert abs(distance - 5.0) < 0.0001
    
    def test_zero_distance(self):
        """Test distance between same points"""
        distance = calculate_distance((5, 5), (5, 5))
        assert abs(distance - 0.0) < 0.0001
    
    def test_negative_coordinates(self):
        """Test distance with negative coordinates"""
        distance = calculate_distance((-3, -4), (0, 0))
        assert abs(distance - 5.0) < 0.0001
    
    def test_float_coordinates(self):
        """Test distance with floating point coordinates"""
        distance = calculate_distance((1.5, 2.5), (4.5, 6.5))
        expected = math.sqrt((4.5-1.5)**2 + (6.5-2.5)**2)
        assert abs(distance - expected) < 0.0001

class TestAngleCalculation:
    """Test angle calculation functions"""
    
    def test_right_angle(self):
        """Test 90-degree angle"""
        angle = calculate_angle_3_points((0, 0), (0, 0), (1, 0))
        # This should be 0 because points are at origin
        
        # Better test: right angle
        angle = calculate_angle_3_points((1, 0), (0, 0), (0, 1))
        assert abs(angle - 90.0) < 0.1
    
    def test_straight_angle(self):
        """Test 180-degree angle (straight line)"""
        angle = calculate_angle_3_points((1, 0), (0, 0), (-1, 0))
        assert abs(angle - 180.0) < 0.1
    
    def test_45_degree_angle(self):
        """Test 45-degree angle"""
        angle = calculate_angle_3_points((1, 0), (0, 0), (1, 1))
        assert abs(angle - 45.0) < 0.1
    
    def test_acute_angle(self):
        """Test acute angle"""
        angle = calculate_angle_3_points((2, 0), (0, 0), (1, 1))
        assert 0 < angle < 90

class TestCircleCalculation:
    """Test circle center and radius calculation"""
    
    def test_simple_circle(self):
        """Test circle with known center and radius"""
        # Circle centered at origin with radius 1
        p1 = (1, 0)
        p2 = (0, 1)
        p3 = (-1, 0)
        
        center, radius = calculate_circle_center_radius(p1, p2, p3)
        
        assert abs(center[0] - 0.0) < 0.1
        assert abs(center[1] - 0.0) < 0.1
        assert abs(radius - 1.0) < 0.1
    
    def test_collinear_points(self):
        """Test that collinear points raise ValueError"""
        with pytest.raises(ValueError, match="collinear"):
            calculate_circle_center_radius((0, 0), (1, 1), (2, 2))
    
    def test_larger_circle(self):
        """Test circle with larger radius"""
        # Circle centered at (0, 0) with radius 5
        p1 = (5, 0)
        p2 = (0, 5)
        p3 = (-5, 0)
        
        center, radius = calculate_circle_center_radius(p1, p2, p3)
        
        assert abs(center[0] - 0.0) < 0.1
        assert abs(center[1] - 0.0) < 0.1
        assert abs(radius - 5.0) < 0.1

class TestPolygonArea:
    """Test polygon area calculation"""
    
    def test_triangle_area(self):
        """Test area of a triangle"""
        # Right triangle with legs 3 and 4
        points = [(0, 0), (3, 0), (0, 4)]
        area = calculate_polygon_area(points)
        expected = 0.5 * 3 * 4  # 6
        assert abs(area - expected) < 0.0001
    
    def test_square_area(self):
        """Test area of a square"""
        points = [(0, 0), (2, 0), (2, 2), (0, 2)]
        area = calculate_polygon_area(points)
        expected = 4.0
        assert abs(area - expected) < 0.0001
    
    def test_rectangle_area(self):
        """Test area of a rectangle"""
        points = [(0, 0), (5, 0), (5, 3), (0, 3)]
        area = calculate_polygon_area(points)
        expected = 15.0
        assert abs(area - expected) < 0.0001
    
    def test_insufficient_points(self):
        """Test area with insufficient points"""
        points = [(0, 0), (1, 1)]
        area = calculate_polygon_area(points)
        assert area == 0.0

class TestPointToLineDistance:
    """Test point-to-line distance calculation"""
    
    def test_perpendicular_distance(self):
        """Test perpendicular distance to horizontal line"""
        point = (0, 3)
        line_start = (-5, 0)
        line_end = (5, 0)
        
        distance = calculate_point_to_line_distance(point, line_start, line_end)
        assert abs(distance - 3.0) < 0.0001
    
    def test_point_on_line(self):
        """Test distance when point is on the line"""
        point = (2, 0)
        line_start = (0, 0)
        line_end = (5, 0)
        
        distance = calculate_point_to_line_distance(point, line_start, line_end)
        assert abs(distance - 0.0) < 0.0001
    
    def test_diagonal_line(self):
        """Test distance to diagonal line"""
        point = (0, 2)
        line_start = (0, 0)
        line_end = (2, 2)
        
        distance = calculate_point_to_line_distance(point, line_start, line_end)
        # Distance from (0,2) to line y=x should be sqrt(2)
        expected = math.sqrt(2)
        assert abs(distance - expected) < 0.1

class TestCollinearityCheck:
    """Test collinearity checking"""
    
    def test_collinear_points(self):
        """Test that collinear points are detected"""
        assert are_points_collinear((0, 0), (1, 1), (2, 2))
        assert are_points_collinear((0, 0), (5, 0), (10, 0))
    
    def test_non_collinear_points(self):
        """Test that non-collinear points are not detected as collinear"""
        assert not are_points_collinear((0, 0), (1, 0), (0, 1))
        assert not are_points_collinear((0, 0), (1, 1), (1, 0))

class TestAngleConversion:
    """Test angle conversion functions"""
    
    def test_degrees_to_radians(self):
        """Test degree to radian conversion"""
        assert abs(degrees_to_radians(90) - math.pi/2) < 0.0001
        assert abs(degrees_to_radians(180) - math.pi) < 0.0001
        assert abs(degrees_to_radians(360) - 2*math.pi) < 0.0001
    
    def test_radians_to_degrees(self):
        """Test radian to degree conversion"""
        assert abs(radians_to_degrees(math.pi/2) - 90) < 0.0001
        assert abs(radians_to_degrees(math.pi) - 180) < 0.0001
        assert abs(radians_to_degrees(2*math.pi) - 360) < 0.0001

class TestArcLength:
    """Test arc length calculation"""
    
    def test_quarter_circle_arc(self):
        """Test arc length for quarter circle"""
        # Quarter circle with radius 2
        p1 = (2, 0)
        p2 = (math.sqrt(2), math.sqrt(2))
        p3 = (0, 2)
        
        arc_length = calculate_arc_length(p1, p2, p3)
        expected = math.pi  # Quarter of circumference 2?*2
        assert abs(arc_length - expected) < 0.1
    
    def test_semicircle_arc(self):
        """Test arc length for semicircle"""
        # Semicircle with radius 1
        p1 = (1, 0)
        p2 = (0, 1)
        p3 = (-1, 0)
        
        arc_length = calculate_arc_length(p1, p2, p3)
        expected = math.pi  # Half of circumference 2?*1
        assert abs(arc_length - expected) < 0.1

if __name__ == "__main__":
    pytest.main([__file__])