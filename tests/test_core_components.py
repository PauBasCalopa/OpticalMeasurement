"""
Unit Tests for Core Components

Tests for ImageManager, CalibrationManager, and MeasurementEngine
"""

import pytest
import tempfile
import os
from PIL import Image
import numpy as np

from core.image_manager import ImageManager
from core.measurement_engine import MeasurementEngine
from models.calibration_data import CalibrationData
from models.measurement_data import DistanceMeasurement, RadiusMeasurement, AngleMeasurement

class TestCalibrationData:
    """Test CalibrationData class"""
    
    def test_basic_calibration(self):
        """Test basic calibration setup"""
        calibration = CalibrationData()
        
        # Test before calibration
        assert not calibration.is_calibrated
        assert calibration.scale_factor is None
        
        # Perform calibration
        calibration.calibrate((0, 0), (10, 0), 5.0)  # 10 pixels = 5 units
        
        # Test after calibration
        assert calibration.is_calibrated
        assert abs(calibration.scale_factor - 0.5) < 0.0001  # 5/10 = 0.5 units per pixel
        assert abs(calibration.pixel_distance - 10.0) < 0.0001
        assert calibration.real_distance == 5.0
    
    def test_calibration_validation(self):
        """Test calibration input validation"""
        calibration = CalibrationData()
        
        # Test negative distance
        with pytest.raises(ValueError, match="positive"):
            calibration.calibrate((0, 0), (10, 0), -1.0)
        
        # Test zero distance
        with pytest.raises(ValueError, match="positive"):
            calibration.calibrate((0, 0), (10, 0), 0.0)
        
        # Test same points
        with pytest.raises(ValueError, match="same"):
            calibration.calibrate((5, 5), (5, 5), 10.0)
    
    def test_unit_conversions(self):
        """Test pixel-to-unit and unit-to-pixel conversions"""
        calibration = CalibrationData()
        calibration.calibrate((0, 0), (20, 0), 10.0)  # 20 pixels = 10 units, so 0.5 units/pixel
        
        # Test pixel to units
        assert abs(calibration.pixels_to_units(20.0) - 10.0) < 0.0001
        assert abs(calibration.pixels_to_units(10.0) - 5.0) < 0.0001
        
        # Test units to pixels
        assert abs(calibration.units_to_pixels(10.0) - 20.0) < 0.0001
        assert abs(calibration.units_to_pixels(5.0) - 10.0) < 0.0001
    
    def test_precision_calculation(self):
        """Test measurement precision calculation"""
        calibration = CalibrationData()
        calibration.calibrate((0, 0), (100, 0), 50.0)  # Scale factor = 0.5
        
        expected_precision = 0.5 * 0.5  # scale_factor * 0.5
        assert abs(calibration.precision - expected_precision) < 0.0001

class TestImageManager:
    """Test ImageManager class"""
    
    def setUp(self):
        """Set up test image files"""
        # Create a temporary test image
        self.test_image = Image.new('RGB', (100, 80), color='red')
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.test_image.save(self.temp_file.name)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test files"""
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_image_loading(self):
        """Test image loading functionality"""
        self.setUp()
        
        try:
            manager = ImageManager()
            
            # Test loading valid image
            image_data = manager.load_image(self.temp_file.name)
            
            assert image_data is not None
            assert image_data.width == 100
            assert image_data.height == 80
            assert image_data.format == 'PNG'
            assert manager.is_image_loaded
            
            # Test image size property
            assert manager.image_size == (100, 80)
            
        finally:
            self.tearDown()
    
    def test_invalid_file_handling(self):
        """Test handling of invalid files"""
        manager = ImageManager()
        
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            manager.load_image("nonexistent_file.png")
        
        # Test unsupported format - create a temporary text file
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b"This is not an image")
        temp_file.close()  # Close the file before trying to use it
        
        try:
            with pytest.raises(ValueError, match="Unsupported"):
                manager.load_image(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_zoom_calculations(self):
        """Test zoom-related calculations"""
        self.setUp()
        
        try:
            manager = ImageManager()
            image_data = manager.load_image(self.temp_file.name)
            
            # Test fit-to-window zoom calculation
            zoom = manager.get_fit_to_window_zoom(200, 160, 20)  # Window size with margin
            # Available space: 160x120, image: 100x80
            # Scale factors: 160/100=1.6, 120/80=1.5, so min=1.5
            expected_zoom = min(160/100, 120/80)
            assert abs(zoom - expected_zoom) < 0.01
            
        finally:
            self.tearDown()

class TestMeasurementEngine:
    """Test MeasurementEngine class"""
    
    def setUp(self):
        """Set up measurement engine with calibration"""
        self.engine = MeasurementEngine()
        self.calibration = CalibrationData()
        self.calibration.calibrate((0, 0), (100, 0), 50.0)  # 100 pixels = 50 units
        self.engine.set_calibration(self.calibration)
    
    def test_distance_measurement(self):
        """Test distance measurement calculation"""
        self.setUp()
        
        # Test calibrated measurement
        measurement = self.engine.calculate_distance_measurement((0, 0), (60, 80))
        
        # Expected: sqrt(60^2 + 80^2) = 100 pixels = 50 units
        expected_pixels = 100.0
        expected_units = 50.0
        
        assert abs(measurement.result - expected_units) < 0.1
        assert len(measurement.points) == 2
        assert measurement.measurement_type == "distance"
    
    def test_distance_measurement_uncalibrated(self):
        """Test distance measurement without calibration"""
        engine = MeasurementEngine()  # No calibration
        
        measurement = engine.calculate_distance_measurement((0, 0), (3, 4))
        
        # Should return pixel distance
        assert abs(measurement.result - 5.0) < 0.0001
    
    def test_radius_measurement(self):
        """Test radius measurement calculation"""
        self.setUp()
        
        # Circle with radius 50 pixels (25 units when calibrated)
        p1 = (50, 0)
        p2 = (0, 50)
        p3 = (-50, 0)
        
        measurement = self.engine.calculate_radius_measurement(p1, p2, p3)
        
        # Expected radius: 50 pixels = 25 units
        expected_units = 25.0
        assert abs(measurement.result - expected_units) < 0.1
        assert measurement.measurement_type == "radius"
        assert measurement.center_point is not None
    
    def test_radius_measurement_collinear(self):
        """Test radius measurement with collinear points"""
        self.setUp()
        
        # Collinear points should raise ValueError
        with pytest.raises(ValueError, match="collinear"):
            self.engine.calculate_radius_measurement((0, 0), (1, 1), (2, 2))
    
    def test_angle_measurement(self):
        """Test angle measurement calculation"""
        self.setUp()
        
        # 90-degree angle
        p1 = (1, 0)
        vertex = (0, 0)
        p3 = (0, 1)
        
        measurement = self.engine.calculate_angle_measurement(p1, vertex, p3)
        
        assert abs(measurement.result - 90.0) < 0.1
        assert measurement.measurement_type == "angle"
        assert measurement.vertex_index == 1
    
    def test_measurement_formatting(self):
        """Test measurement result formatting"""
        self.setUp()
        
        # Test distance formatting
        distance_measurement = DistanceMeasurement()
        distance_measurement.result = 12.345
        distance_measurement.measurement_type = "distance"
        
        formatted = self.engine.format_measurement_result(distance_measurement)
        assert "12.35 units" in formatted
        
        # Test angle formatting
        angle_measurement = AngleMeasurement()
        angle_measurement.result = 45.678
        angle_measurement.measurement_type = "angle"
        
        formatted = self.engine.format_measurement_result(angle_measurement)
        assert "45.68 degrees" in formatted
    
    def test_measurement_formatting_uncalibrated(self):
        """Test measurement formatting without calibration"""
        engine = MeasurementEngine()  # No calibration
        
        distance_measurement = DistanceMeasurement()
        distance_measurement.result = 12.345
        distance_measurement.measurement_type = "distance"
        
        formatted = engine.format_measurement_result(distance_measurement)
        assert "12.35 px" in formatted

if __name__ == "__main__":
    pytest.main([__file__])