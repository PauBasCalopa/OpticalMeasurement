"""
Manual Test Script for Phase 1 MVP

Interactive tests to verify GUI functionality and user workflows
"""

import tkinter as tk
from tkinter import messagebox
import tempfile
import os
from PIL import Image
import sys
import traceback

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import OpticalMeasurementApp
from core.app_state import app_state

def create_test_images():
    """Create test images for manual testing"""
    test_images = []
    
    # Test Image 1: Simple geometric shapes
    img1 = Image.new('RGB', (400, 300), color='white')
    # You could add drawing code here with PIL ImageDraw
    temp1 = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img1.save(temp1.name)
    test_images.append(temp1.name)
    
    # Test Image 2: Different size
    img2 = Image.new('RGB', (800, 600), color='lightblue')
    temp2 = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img2.save(temp2.name)
    test_images.append(temp2.name)
    
    return test_images

def run_automated_gui_tests():
    """Run automated GUI tests that don't require user interaction"""
    print("Running Automated GUI Tests...")
    print("=" * 40)
    
    test_results = []
    
    try:
        # Test 1: Application startup
        print("Test 1: Application Startup")
        root = tk.Tk()
        app = OpticalMeasurementApp(root)
        
        # Verify initial state
        assert not app_state.is_image_loaded, "Image should not be loaded initially"
        assert not app_state.is_calibrated, "Should not be calibrated initially"
        assert not app_state.has_measurements, "Should have no measurements initially"
        
        print("? Application starts correctly")
        test_results.append(("Application Startup", True, None))
        
        # Test 2: State management
        print("\nTest 2: State Management")
        
        # Create test image
        test_images = create_test_images()
        try:
            # Load image through image manager
            image_data = app.image_manager.load_image(test_images[0])
            app_state.load_image(image_data)
            app.canvas.set_image(image_data)
            
            assert app_state.is_image_loaded, "Image should be loaded"
            assert app_state.current_image is not None, "Current image should be set"
            
            print("? Image loading works")
            test_results.append(("Image Loading", True, None))
            
            # Test calibration
            from models.calibration_data import CalibrationData
            calibration = CalibrationData()
            calibration.calibrate((0, 0), (100, 0), 50.0)
            app_state.set_calibration(calibration)
            
            assert app_state.is_calibrated, "Should be calibrated"
            assert abs(app_state.calibration.scale_factor - 0.5) < 0.001, "Scale factor should be 0.5"
            
            print("? Calibration works")
            test_results.append(("Calibration", True, None))
            
            # Test measurements
            measurement = app.measurement_engine.calculate_distance_measurement((0, 0), (60, 80))
            app_state.add_measurement(measurement)
            
            assert app_state.has_measurements, "Should have measurements"
            assert len(app_state.measurements) == 1, "Should have 1 measurement"
            assert abs(measurement.result - 25.0) < 0.1, "Distance should be ~25 units"
            
            print("? Measurements work")
            test_results.append(("Measurements", True, None))
            
        finally:
            # Cleanup test images
            for img_path in test_images:
                try:
                    os.unlink(img_path)
                except OSError:
                    pass
        
        # Test 3: UI state updates
        print("\nTest 3: UI State Updates")
        
        # Test that UI elements are properly enabled/disabled
        assert app.calibration_btn['state'] == 'normal', "Calibration button should be enabled with image"
        assert app.distance_btn['state'] == 'normal', "Distance button should be enabled when calibrated"
        assert app.radius_btn['state'] == 'normal', "Radius button should be enabled when calibrated"
        
        print("? UI state management works")
        test_results.append(("UI State Management", True, None))
        
        root.destroy()
        
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(f"? Test failed: {error_msg}")
        test_results.append(("Automated Tests", False, error_msg))
    
    # Print summary
    print("\n" + "=" * 40)
    print("Automated Test Results:")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, success, error in test_results:
        if success:
            print(f"? {test_name}")
            passed += 1
        else:
            print(f"? {test_name}: {error}")
            failed += 1
    
    print(f"\nPassed: {passed}, Failed: {failed}")
    
    return len(test_results) > 0 and failed == 0

def run_manual_test_instructions():
    """Provide instructions for manual testing"""
    print("\n" + "=" * 50)
    print("MANUAL TESTING INSTRUCTIONS")
    print("=" * 50)
    
    print("""
Phase 1 MVP Manual Test Checklist:

1. APPLICATION STARTUP:
   ? Run: python main.py
   ? Application window opens without errors
   ? Window title shows "Optical Measurement Tool"
   ? Toolbar, sidebar, and status bar are visible
   ? All buttons are properly labeled

2. IMAGE LOADING:
   ? File ? Open Image works
   ? Drag and drop an image file works
   ? Image displays properly in canvas
   ? Zoom controls work (mouse wheel, Ctrl++, Ctrl+-)
   ? Pan works (drag with mouse)
   ? Status bar shows image loaded message

3. CALIBRATION WORKFLOW:
   ? Click "Calibrate" button
   ? Status shows "Click two points..."
   ? Click two points on image
   ? Red calibration line appears
   ? Calibration dialog opens
   ? Enter a distance value and click OK
   ? Calibration status changes to "Calibrated" (green)
   ? Scale factor is displayed

4. DISTANCE MEASUREMENT:
   ? Click "Distance" button (only works after calibration)
   ? Click two points on image
   ? Green measurement line appears
   ? Result shows in measurements list
   ? Result is in correct units

5. RADIUS MEASUREMENT:
   ? Click "Radius" button
   ? Click three points on a circle edge
   ? Blue circle overlay appears with center point
   ? Result shows in measurements list
   ? Handles collinear points with error message

6. ANGLE MEASUREMENT:
   ? Click "Angle" button
   ? Click three points (vertex in middle)
   ? Orange angle lines appear
   ? Result shows in degrees
   ? Works without calibration

7. MEASUREMENT MANAGEMENT:
   ? Multiple measurements can be made
   ? Measurements appear in list with labels
   ? "Delete" button removes selected measurement
   ? "Clear All" removes all measurements
   ? Visual overlays are removed with measurements

8. EXPORT FUNCTIONALITY:
   ? File ? Export Image works
   ? Saves PNG or JPG file
   ? Exported image contains measurement overlays
   ? Shows success message

9. KEYBOARD SHORTCUTS:
   ? Ctrl+O opens image
   ? Ctrl+E exports image
   ? F4 starts calibration
   ? F5, F6, F7 select tools
   ? Space selects pan tool
   ? Escape resets tools

10. ERROR HANDLING:
    ? Invalid image files show error message
    ? Calibration with invalid input shows error
    ? Measurement tools disabled without proper setup
    ? Collinear points in radius measurement handled
    ? Application doesn't crash on errors

11. UI RESPONSIVENESS:
    ? Large images load quickly (< 2 seconds)
    ? Zoom/pan operations are smooth
    ? Measurement calculations are instantaneous
    ? No UI freezing during operations

12. MENU SYSTEM:
    ? All menu items work correctly
    ? Menu items are enabled/disabled appropriately
    ? Keyboard shortcuts match menu accelerators
    ? About dialog displays correctly

TESTING TIPS:
- Test with various image sizes (small, large, high-resolution)
- Test with different image formats (JPG, PNG, BMP)
- Try edge cases (very small distances, large angles)
- Test error scenarios (invalid files, bad input)
- Verify measurements with known values

If any test fails, note the specific steps and error messages.
""")

def run_performance_check():
    """Check basic performance requirements"""
    print("\n" + "=" * 50)
    print("PERFORMANCE VERIFICATION")
    print("=" * 50)
    
    import time
    from core.measurement_engine import MeasurementEngine
    from models.calibration_data import CalibrationData
    
    try:
        # Test measurement calculation speed
        print("Testing measurement calculation performance...")
        
        engine = MeasurementEngine()
        calibration = CalibrationData()
        calibration.calibrate((0, 0), (1000, 0), 500.0)
        engine.set_calibration(calibration)
        
        # Time 100 distance measurements
        start_time = time.time()
        for i in range(100):
            measurement = engine.calculate_distance_measurement((i, i), (i+300, i+400))
        end_time = time.time()
        
        measurement_time = (end_time - start_time) * 1000  # Convert to milliseconds
        avg_time = measurement_time / 100
        
        print(f"100 measurements took {measurement_time:.2f}ms")
        print(f"Average per measurement: {avg_time:.2f}ms")
        
        # Check requirement: measurements should be < 100ms
        if avg_time < 100:
            print("? Meets performance requirement (<100ms per measurement)")
        else:
            print("? Does not meet performance requirement")
        
        return avg_time < 100
        
    except Exception as e:
        print(f"? Performance test failed: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("PHASE 1 MVP TESTING SUITE")
    print("=" * 50)
    
    # Run automated tests
    automated_passed = run_automated_gui_tests()
    
    # Run performance check
    performance_passed = run_performance_check()
    
    # Show manual test instructions
    run_manual_test_instructions()
    
    # Final summary
    print("\n" + "=" * 50)
    print("TESTING SUMMARY")
    print("=" * 50)
    
    print(f"Automated Tests: {'? PASSED' if automated_passed else '? FAILED'}")
    print(f"Performance Check: {'? PASSED' if performance_passed else '? FAILED'}")
    print("Manual Tests: See checklist above")
    
    if automated_passed and performance_passed:
        print("\n?? Phase 1 MVP appears to be working correctly!")
        print("Complete the manual testing checklist to verify full functionality.")
    else:
        print("\n??  Some automated tests failed. Check the output above for details.")
    
    print("\nTo run the application manually: python main.py")

if __name__ == "__main__":
    main()