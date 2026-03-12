"""
Application State Management

Centralized state management for the Optical Measurement Tool.
Includes undo/redo support via a command stack.
"""

from typing import Optional, List
from models.image_data import ImageData
from models.calibration_data import CalibrationData
from models.measurement_data import MeasurementBase
from models.view_state import ViewState


class _UndoEntry:
    """Represents a reversible action on the measurement list."""
    __slots__ = ("kind", "measurement", "snapshot")

    def __init__(self, kind: str, measurement: Optional[MeasurementBase] = None,
                 snapshot: Optional[List[MeasurementBase]] = None):
        self.kind = kind              # "add" | "remove" | "clear"
        self.measurement = measurement  # for add / remove
        self.snapshot = snapshot        # for clear (full list before clearing)


class ApplicationState:
    """Centralized application state management"""
    
    def __init__(self):
        # Core state
        self.current_image: Optional[ImageData] = None
        self.calibration: Optional[CalibrationData] = None
        self.measurements: List[MeasurementBase] = []
        
        # UI state
        self.active_tool: Optional[str] = None
        self.view_state: ViewState = ViewState()
        
        # Grid state
        self.grid_visible: bool = False
        self.grid_spacing: int = 50
        self.grid_color: str = "#cccccc"
        self.grid_opacity: float = 0.5
        
        # Image adjustment state
        self.brightness: float = 1.0
        self.contrast: float = 1.0
        
        # Legacy accessors (kept for compatibility during migration)
        self.zoom_level: float = 1.0
        self.pan_offset: tuple = (0, 0)
        
        # Undo / Redo stacks
        self._undo_stack: List[_UndoEntry] = []
        self._redo_stack: List[_UndoEntry] = []
        
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
    
    def update_view_state(self, view_state: ViewState):
        """Update the view state (zoom, pan, canvas size)"""
        self.view_state = view_state
        self.zoom_level = view_state.zoom  # Keep legacy field in sync
        self.pan_offset = (view_state.pan_x, view_state.pan_y)
        self.notify_observers("view_changed", view_state)
    
    def load_image(self, image_data: ImageData):
        """Load new image and reset state"""
        self.current_image = image_data
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.clear_measurements()
        self.clear_calibration()
        self.view_state = ViewState(
            image_width=image_data.width,
            image_height=image_data.height
        )
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.notify_observers("image_loaded", image_data)
    
    def close_image(self):
        """Close current image and reset state"""
        self.current_image = None
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.clear_measurements()
        self.clear_calibration()
        self.view_state = ViewState()
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
        """Add new measurement (undoable)"""
        self._undo_stack.append(_UndoEntry("add", measurement=measurement))
        self._redo_stack.clear()
        self.measurements.append(measurement)
        self.notify_observers("measurement_added", measurement)
    
    def remove_measurement(self, measurement_id: str):
        """Remove measurement by ID (undoable)"""
        removed = [m for m in self.measurements if m.id == measurement_id]
        self.measurements = [m for m in self.measurements if m.id != measurement_id]
        if removed:
            self._undo_stack.append(_UndoEntry("remove", measurement=removed[0]))
            self._redo_stack.clear()
        self.notify_observers("measurement_removed", measurement_id)
    
    def clear_measurements(self):
        """Clear all measurements (undoable)"""
        if self.measurements:
            self._undo_stack.append(_UndoEntry("clear", snapshot=list(self.measurements)))
            self._redo_stack.clear()
        self.measurements.clear()
        self.notify_observers("measurements_cleared", None)
    
    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self):
        """Undo the last measurement action."""
        if not self._undo_stack:
            return
        entry = self._undo_stack.pop()
        self._redo_stack.append(entry)
        if entry.kind == "add":
            # Reverse of add → remove
            self.measurements = [m for m in self.measurements if m.id != entry.measurement.id]
            self.notify_observers("measurement_removed", entry.measurement.id)
        elif entry.kind == "remove":
            # Reverse of remove → re-add
            self.measurements.append(entry.measurement)
            self.notify_observers("measurement_added", entry.measurement)
        elif entry.kind == "clear":
            # Reverse of clear → restore snapshot
            self.measurements = list(entry.snapshot)
            self.notify_observers("measurements_cleared", None)
            for m in self.measurements:
                self.notify_observers("measurement_added", m)
        self.notify_observers("undo_redo_changed", None)

    def redo(self):
        """Redo the last undone action."""
        if not self._redo_stack:
            return
        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        if entry.kind == "add":
            # Re-do add
            self.measurements.append(entry.measurement)
            self.notify_observers("measurement_added", entry.measurement)
        elif entry.kind == "remove":
            # Re-do remove
            self.measurements = [m for m in self.measurements if m.id != entry.measurement.id]
            self.notify_observers("measurement_removed", entry.measurement.id)
        elif entry.kind == "clear":
            # Re-do clear
            self.measurements.clear()
            self.notify_observers("measurements_cleared", None)
        self.notify_observers("undo_redo_changed", None)
    
    def set_active_tool(self, tool_name: str):
        """Set active measurement tool"""
        self.active_tool = tool_name
        self.notify_observers("tool_changed", tool_name)
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.grid_visible = not self.grid_visible
        self.notify_observers("grid_changed", self.grid_visible)
    
    def set_grid_settings(self, spacing: int, color: str):
        """Update grid settings"""
        self.grid_spacing = spacing
        self.grid_color = color
        self.notify_observers("grid_changed", self.grid_visible)
    
    def set_brightness(self, value: float):
        """Set brightness adjustment (1.0 = original)"""
        self.brightness = value
        self.notify_observers("image_adjustment_changed", {"brightness": value, "contrast": self.contrast})
    
    def set_contrast(self, value: float):
        """Set contrast adjustment (1.0 = original)"""
        self.contrast = value
        self.notify_observers("image_adjustment_changed", {"brightness": self.brightness, "contrast": value})
    
    def reset_adjustments(self):
        """Reset brightness and contrast to defaults"""
        self.brightness = 1.0
        self.contrast = 1.0
        self.notify_observers("image_adjustment_changed", {"brightness": 1.0, "contrast": 1.0})
    
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