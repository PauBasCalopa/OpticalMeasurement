"""
Application State Management

Centralized state management for the Optical Measurement Tool
"""

from typing import Optional, List
from models.image_data import ImageData
from models.calibration_data import CalibrationData
from models.measurement_data import MeasurementBase

class ApplicationState:
    """Centralized application state management"""
    
    def __init__(self):
        # Core state
        self.current_image: Optional[ImageData] = None
        self.calibration: Optional[CalibrationData] = None
        self.measurements: List[MeasurementBase] = []
        
        # UI state
        self.active_tool: Optional[str] = None
        self.zoom_level: float = 1.0
        self.pan_offset: tuple = (0, 0)
        
        # Observers for state changes
        self._observers = []
    
    def add_observer(self, callback):
        """Add observer for state changes"""
        self._observers.append(callback)
    
    def remove_observer(self, callback):
        """Remove observer"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def notify_observers(self, change_type: str, data=None):
        """Notify all observers of state change"""
        for callback in self._observers:
            try:
                callback(change_type, data)
            except Exception as e:
                print(f"Error in observer callback: {e}")
    
    def load_image(self, image_data: ImageData):
        """Load new image and reset state"""
        self.current_image = image_data
        self.clear_measurements()
        self.clear_calibration()
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.notify_observers("image_loaded", image_data)
    
    def close_image(self):
        """Close current image and reset state"""
        self.current_image = None
        self.clear_measurements()
        self.clear_calibration()
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.active_tool = None
        self.notify_observers("image_closed", None)
    
    def set_calibration(self, calibration_data: CalibrationData):
        """Set calibration data"""
        self.calibration = calibration_data
        self.notify_observers("calibration_changed", calibration_data)
    
    def clear_calibration(self):
        """Clear calibration data"""
        self.calibration = None
        self.notify_observers("calibration_cleared", None)
    
    def add_measurement(self, measurement: MeasurementBase):
        """Add new measurement"""
        self.measurements.append(measurement)
        self.notify_observers("measurement_added", measurement)
    
    def remove_measurement(self, measurement_id: str):
        """Remove measurement by ID"""
        self.measurements = [m for m in self.measurements if m.id != measurement_id]
        self.notify_observers("measurement_removed", measurement_id)
    
    def clear_measurements(self):
        """Clear all measurements"""
        self.measurements.clear()
        self.notify_observers("measurements_cleared", None)
    
    def set_active_tool(self, tool_name: str):
        """Set active measurement tool"""
        self.active_tool = tool_name
        self.notify_observers("tool_changed", tool_name)
    
    def set_zoom_level(self, zoom: float):
        """Set zoom level"""
        self.zoom_level = max(0.25, min(10.0, zoom))
        self.notify_observers("zoom_changed", self.zoom_level)
    
    def set_pan_offset(self, offset: tuple):
        """Set pan offset"""
        self.pan_offset = offset
        self.notify_observers("pan_changed", offset)
    
    @property
    def is_image_loaded(self) -> bool:
        """Check if image is loaded"""
        return self.current_image is not None
    
    @property
    def is_calibrated(self) -> bool:
        """Check if calibration is set"""
        return self.calibration is not None and self.calibration.scale_factor is not None
    
    @property
    def has_measurements(self) -> bool:
        """Check if any measurements exist"""
        return len(self.measurements) > 0

# Global application state instance
app_state = ApplicationState()