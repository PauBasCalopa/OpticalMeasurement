"""
Integration Tests for Phase 1 MVP

Tests complete workflows and integration between components
"""

import pytest
import tempfile
import os
from PIL import Image
import tkinter as tk

from core.app_state import app_state, ApplicationState
from core.image_manager import ImageManager
from core.measurement_engine import MeasurementEngine
from models.calibration_data import CalibrationData
from models.image_data import ImageData

class TestApplicationState:
    """Test application state management"""
    
    def setUp(self):
        """Set up fresh application state"""
        self.app_state = ApplicationState()
        self.callbacks_received = []
        
        # Set up observer to track changes
        def test_observer(change_type, data):
            self.callbacks_received.append((change_type, data))
        
        self.app_state.add_observer(test_observer)
    
    def test_image_loading_workflow(self):
        """Test complete image loading workflow"""
        self.setUp()
        
        # Create test image
        test_image = Image.new('RGB', (200, 150), color='blue')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        test_image.save(temp_file.name)
        temp_file.close()
        
        try:
            # Create image data
            image_data = ImageData.from_file(temp_file.name)
            
            # Load image into state
            self.app_state.load_image(image_data)
            
            # Verify state
            assert self.app_state.is_image_loaded
            assert self.app_state.current_image == image_data
            assert not self.app_state.is_calibrated
            assert not self.app_state.has_measurements
            
            # Verify observer was called
            assert any(change[0] == "image_loaded" for change in self.callbacks_received)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_calibration_workflow(self):
        """Test complete calibration workflow"""
        self.setUp()
        
        # Create test image first
        test_image = Image.new('RGB', (100, 100), color='green')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        test_image.save(temp_file.name)
        temp_file.close()
        
        try:
            image_data = ImageData.from_file(temp_file.name)
            self.app_state.load_image(image_data)
            
            # Set up calibration
            calibration = CalibrationData()
            calibration.calibrate((10, 10), (90, 10), 40.0)  # 80 pixels = 40 units
            
            # Apply calibration
            self.app_state.set_calibration(calibration)
            
            # Verify state
            assert self.app_state.is_calibrated
            assert self.app_state.calibration == calibration
            
            # Verify observer was called
            assert any(change[0] == "calibration_changed" for change in self.callbacks_received)
            
            # Test clearing calibration
            self.app_state.clear_calibration()
            assert not self.app_state.is_calibrated
            assert any(change[0] == "calibration_cleared" for change in self.callbacks_received)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_measurement_workflow(self):
        """Test complete measurement workflow"""
        self.setUp()
        
        # Set up image and calibration
        test_image = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        test_image.save(temp_file.name)
        temp_file.close()
        
        try:
            image_data = ImageData.from_file(temp_file.name)
            self.app_state.load_image(image_data)
            
            calibration = CalibrationData()
            calibration.calibrate((0, 0), (50, 0), 25.0)
            self.app_state.set_calibration(calibration)
            
            # Create measurement engine and add measurements
            engine = MeasurementEngine()
            engine.set_calibration(calibration)
            
            # Add distance measurement
            distance_measurement = engine.calculate_distance_measurement((0, 0), (30, 40))
            self.app_state.add_measurement(distance_measurement)
            
            # Verify state
            assert self.app_state.has_measurements
            assert len(self.app_state.measurements) == 1
            
            # Verify observer was called
            assert any(change[0] == "measurement_added" for change in self.callbacks_received)
            
            # Test removing measurement
            measurement_id = distance_measurement.id
            self.app_state.remove_measurement(measurement_id)
            
            assert not self.app_state.has_measurements
            assert any(change[0] == "measurement_removed" for change in self.callbacks_received)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_complete_workflow(self):
        """Test complete measurement workflow from start to finish"""
        self.setUp()
        
        # 1. Load image
        test_image = Image.new('RGB', (200, 200), color='white')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        test_image.save(temp_file.name)
        temp_file.close()
        
        try:
            # Load image
            manager = ImageManager()
            image_data = manager.load_image(temp_file.name)
            self.app_state.load_image(image_data)
            
            # 2. Calibrate
            calibration = CalibrationData()
            calibration.calibrate((0, 0), (100, 0), 50.0)  # 100 pixels = 50 units
            self.app_state.set_calibration(calibration)
            
            # 3. Make measurements
            engine = MeasurementEngine()
            engine.set_calibration(calibration)
            
            # Distance measurement: 60-80-100 triangle
            distance_measurement = engine.calculate_distance_measurement((0, 0), (60, 80))
            self.app_state.add_measurement(distance_measurement)
            
            # Radius measurement: circle with radius 50 pixels (25 units)
            radius_measurement = engine.calculate_radius_measurement((50, 0), (0, 50), (-50, 0))
            self.app_state.add_measurement(radius_measurement)
            
            # Angle measurement: 90 degrees
            angle_measurement = engine.calculate_angle_measurement((1, 0), (0, 0), (0, 1))
            self.app_state.add_measurement(angle_measurement)
            
            # 4. Verify final state
            assert self.app_state.is_image_loaded
            assert self.app_state.is_calibrated
            assert self.app_state.has_measurements
            assert len(self.app_state.measurements) == 3
            
            # Verify measurement results
            assert abs(distance_measurement.result - 50.0) < 0.1  # 100 pixels = 50 units
            assert abs(radius_measurement.result - 25.0) < 0.1   # 50 pixels = 25 units  
            assert abs(angle_measurement.result - 90.0) < 0.1    # 90 degrees
            
            # 5. Test clearing everything
            self.app_state.close_image()
            
            assert not self.app_state.is_image_loaded
            assert not self.app_state.is_calibrated
            assert not self.app_state.has_measurements
            
        finally:
            os.unlink(temp_file.name)

class TestDataModelIntegration:
    """Test integration between data models"""
    
    def test_image_data_creation(self):
        """Test ImageData creation and properties"""
        # Create test image
        test_image = Image.new('RGB', (150, 100), color='yellow')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        test_image.save(temp_file.name)
        temp_file.close()
        
        try:
            # Test ImageData creation
            image_data = ImageData.from_file(temp_file.name)
            
            assert image_data.width == 150
            assert image_data.height == 100
            assert image_data.size == (150, 100)
            assert image_data.aspect_ratio == 1.5
            assert image_data.megapixels == 0.015
            assert image_data.file_size > 0
            
        finally:
            os.unlink(temp_file.name)
    
    def test_measurement_data_properties(self):
        """Test measurement data model properties"""
        from models.measurement_data import (
            DistanceMeasurement, RadiusMeasurement, AngleMeasurement,
            TwoLineAngleMeasurement, PolygonAreaMeasurement, CoordinateMeasurement
        )
        
        # Test distance measurement
        distance = DistanceMeasurement()
        distance.points = [(0, 0), (3, 4)]
        distance.result = 5.0
        
        assert distance.is_complete
        assert distance.measurement_type == "distance"
        assert len(distance.points) == 2
        
        # Test radius measurement
        radius = RadiusMeasurement()
        radius.points = [(1, 0), (0, 1), (-1, 0)]
        radius.center_point = (0, 0)
        radius.result = 1.0
        
        assert radius.is_complete
        assert radius.measurement_type == "radius"
        
        # Test angle measurement
        angle = AngleMeasurement()
        angle.points = [(1, 0), (0, 0), (0, 1)]
        angle.result = 90.0
        
        assert angle.is_complete
        assert angle.measurement_type == "angle"
        
        # Test incomplete measurements
        incomplete_distance = DistanceMeasurement()
        incomplete_distance.points = [(0, 0)]  # Only one point
        
        assert not incomplete_distance.is_complete

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_calibration_error_handling(self):
        """Test calibration error scenarios"""
        calibration = CalibrationData()
        
        # Test using calibration before setting it up
        with pytest.raises(ValueError, match="Calibration not set"):
            calibration.pixels_to_units(10.0)
        
        with pytest.raises(ValueError, match="Calibration not set"):
            calibration.units_to_pixels(5.0)
    
    def test_measurement_engine_error_handling(self):
        """Test measurement engine error scenarios"""
        engine = MeasurementEngine()
        
        # Test radius measurement with collinear points
        with pytest.raises(ValueError):
            engine.calculate_radius_measurement((0, 0), (1, 1), (2, 2))
    
    def test_image_manager_error_handling(self):
        """Test image manager error scenarios"""
        manager = ImageManager()
        
        # Test operations without loaded image
        assert not manager.is_image_loaded
        assert manager.image_size == (0, 0)
        
        # Test invalid file paths
        with pytest.raises(FileNotFoundError):
            manager.load_image("nonexistent.png")
        
        # Test unsupported format - create a temporary text file
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b"This is not an image")
        temp_file.close()
        
        try:
            with pytest.raises(ValueError, match="Unsupported"):
                manager.load_image(temp_file.name)
        finally:
            os.unlink(temp_file.name)

class TestPerformance:
    """Basic performance tests"""
    
    def test_measurement_calculation_performance(self):
        """Test that measurements are calculated quickly"""
        import time
        
        engine = MeasurementEngine()
        calibration = CalibrationData()
        calibration.calibrate((0, 0), (1000, 0), 500.0)
        engine.set_calibration(calibration)
        
        # Test distance measurement performance
        start_time = time.time()
        for _ in range(1000):
            measurement = engine.calculate_distance_measurement((0, 0), (300, 400))
        end_time = time.time()
        
        # Should complete 1000 measurements in well under 1 second
        assert (end_time - start_time) < 1.0
        
        # Verify result is correct
        assert abs(measurement.result - 250.0) < 0.1  # 500 pixels = 250 units

def run_all_tests():
    """Run all Phase 1 tests"""
    print("Running Phase 1 MVP Tests...")
    print("=" * 50)
    
    # Run pytest with verbose output
    test_files = [
        "tests/test_math_utils.py",
        "tests/test_core_components.py", 
        "tests/test_integration.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nRunning {test_file}...")
            pytest.main(["-v", test_file])
        else:
            print(f"Test file {test_file} not found")

if __name__ == "__main__":
    run_all_tests()