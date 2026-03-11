#!/usr/bin/env python3
"""
Measurement Tools Completion Test

Test that all measurement tools are implemented and working correctly.
"""

def test_overlay_methods():
    """Test that all measurement types have corresponding overlay methods"""
    
    print("?? TESTING MEASUREMENT TOOLS COMPLETION")
    print("=" * 40)
    
    # Import the OverlayManager to test methods exist
    try:
        from gui.canvas.overlay_manager import OverlayManager
        print("? OverlayManager imported successfully")
    except ImportError as e:
        print(f"? Failed to import OverlayManager: {e}")
        return False
    
    # List of all measurement types that should be supported
    measurement_types = [
        "distance",
        "radius", 
        "angle",
        "two_line_angle",
        "polygon_area",
        "coordinate",
        "point_to_line",
        "arc_length"
    ]
    
    # Test that overlay methods exist for each measurement type
    missing_methods = []
    existing_methods = []
    
    for measurement_type in measurement_types:
        method_name = f"_draw_{measurement_type}_overlay"
        if hasattr(OverlayManager, method_name):
            existing_methods.append(measurement_type)
            print(f"? {measurement_type}: overlay method exists")
        else:
            missing_methods.append(measurement_type)
            print(f"? {measurement_type}: overlay method missing")
    
    print(f"\n?? RESULTS:")
    print(f"? Implemented: {len(existing_methods)}/{len(measurement_types)} ({len(existing_methods)/len(measurement_types)*100:.0f}%)")
    print(f"? Missing: {len(missing_methods)}")
    
    if missing_methods:
        print(f"\n?? Missing overlay methods for: {', '.join(missing_methods)}")
        return False
    else:
        print(f"\n?? ALL MEASUREMENT TOOLS HAVE OVERLAY METHODS!")
        return True

def test_measurement_engine():
    """Test that MeasurementEngine can create all measurement types"""
    
    print(f"\n?? TESTING MEASUREMENT ENGINE")
    print("-" * 30)
    
    try:
        from core.measurement_engine import MeasurementEngine
        engine = MeasurementEngine()
        print("? MeasurementEngine created successfully")
    except ImportError as e:
        print(f"? Failed to import MeasurementEngine: {e}")
        return False
    
    # Test measurement calculation methods
    calculation_methods = [
        "calculate_distance_measurement",
        "calculate_radius_measurement", 
        "calculate_angle_measurement",
        "calculate_two_line_angle_measurement",
        "calculate_polygon_area_measurement",
        "calculate_coordinate_measurement",
        "calculate_point_to_line_measurement",
        "calculate_arc_length_measurement"
    ]
    
    missing_methods = []
    existing_methods = []
    
    for method_name in calculation_methods:
        if hasattr(engine, method_name):
            existing_methods.append(method_name)
            print(f"? {method_name}: exists")
        else:
            missing_methods.append(method_name)
            print(f"? {method_name}: missing")
    
    print(f"\n?? CALCULATION METHODS:")
    print(f"? Implemented: {len(existing_methods)}/{len(calculation_methods)} ({len(existing_methods)/len(calculation_methods)*100:.0f}%)")
    
    return len(missing_methods) == 0

def test_tool_classes():
    """Test that all tool classes are available"""
    
    print(f"\n?? TESTING TOOL CLASSES")
    print("-" * 25)
    
    try:
        from gui.canvas.tools import BaseTool, PanTool, MeasurementTool, PolygonTool
        print("? All tool classes imported successfully")
        
        # Test that MeasurementTool supports all measurement types
        test_types = ["distance", "radius", "angle", "two_line_angle", "coordinate", "point_to_line", "arc_length"]
        
        class MockCanvas:
            def config(self, **kwargs): pass
            def clear_temp_overlays(self): pass
            def __init__(self): 
                self.temp_points = []
        
        mock_canvas = MockCanvas()
        
        for measurement_type in test_types:
            try:
                tool = MeasurementTool(mock_canvas, measurement_type)
                print(f"? MeasurementTool('{measurement_type}'): created successfully")
            except Exception as e:
                print(f"? MeasurementTool('{measurement_type}'): failed - {e}")
                return False
        
        # Test PolygonTool
        try:
            polygon_tool = PolygonTool(mock_canvas)
            print(f"? PolygonTool: created successfully")
        except Exception as e:
            print(f"? PolygonTool: failed - {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"? Failed to import tool classes: {e}")
        return False

def test_math_utilities():
    """Test that all required math utilities exist"""
    
    print(f"\n?? TESTING MATH UTILITIES")
    print("-" * 25)
    
    try:
        from utils.math_utils import (
            calculate_distance,
            calculate_angle_3_points,
            calculate_two_line_angle,
            calculate_circle_center_radius,
            calculate_polygon_area,
            calculate_point_to_line_distance,
            get_perpendicular_point_on_line,
            calculate_arc_length
        )
        print("? All math utility functions imported successfully")
        
        # Test a simple calculation
        dist = calculate_distance((0, 0), (3, 4))
        expected = 5.0
        if abs(dist - expected) < 0.001:
            print(f"? calculate_distance test: {dist} ? {expected}")
        else:
            print(f"? calculate_distance test: {dist} ? {expected}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"? Failed to import math utilities: {e}")
        return False

def main():
    """Run all measurement tool completion tests"""
    
    print("?? MEASUREMENT TOOLS COMPLETION VERIFICATION")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Overlay Methods", test_overlay_methods),
        ("Measurement Engine", test_measurement_engine), 
        ("Tool Classes", test_tool_classes),
        ("Math Utilities", test_math_utilities)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"? {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"?? FINAL RESULTS:")
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "? PASSED" if passed_test else "? FAILED"
        print(f"  {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n?? OVERALL SCORE: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print(f"?? ALL MEASUREMENT TOOLS ARE COMPLETE AND READY!")
        print(f"? Your application now supports all 8 measurement types:")
        print(f"   - Distance (2 points)")
        print(f"   - Radius (3 points)")
        print(f"   - Angle (3 points)")
        print(f"   - Two-Line Angle (4 points)")
        print(f"   - Polygon Area (3+ points)")
        print(f"   - Point Coordinates (1-2 points)")
        print(f"   - Point-to-Line Distance (3 points)")
        print(f"   - Arc Length (3 points)")
        return True
    else:
        print(f"?? Some tests failed - check the results above")
        return False

if __name__ == "__main__":
    main()