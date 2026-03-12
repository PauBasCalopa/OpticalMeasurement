"""
Image Canvas Widget

Custom tkinter Canvas for image display and measurement interactions
"""

import tkinter as tk
from tkinter import Canvas
from typing import Optional, List, Tuple
from PIL import ImageTk

from models.image_data import ImageData
from models.view_state import ViewState
from core.image_manager import ImageManager
from core.measurement_engine import MeasurementEngine
from models.measurement_data import MeasurementBase
from services.coordinate_service import CoordinateService

# Canvas sub-components
from gui.canvas.event_manager import EventManager
from gui.canvas.tool_handler import ToolHandler
from gui.canvas.overlay_renderer import OverlayRenderer
from gui.canvas.calibration_handler import CalibrationHandler

class ImageCanvas(Canvas):
    """Custom canvas for interactive image display and measurements"""
    
    def __init__(self, parent, image_manager: ImageManager, measurement_engine: MeasurementEngine, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.image_manager = image_manager
        self.measurement_engine = measurement_engine
        
        # Reference to main application window for dialog callbacks
        self.main_app = None  # Will be set by main window
        
        # View state — single source of truth for zoom/pan
        self._view_state = ViewState()
        
        # Sub-components
        self.event_manager = EventManager(self)
        self.tool_handler = ToolHandler(self)
        self.overlay_renderer = OverlayRenderer(self)
        self.calibration_handler = CalibrationHandler(self)
        
        # Canvas state
        self.current_image: Optional[ImageData] = None
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.image_id: Optional[int] = None
        
        # Interaction state
        self.current_tool: str = "pan"
        self.is_calibrating: bool = False
        
        # Legacy fields kept for backward compat during migration
        self.zoom_level: float = 1.0
        self.actual_zoom_level: float = 1.0
        self.last_mouse_pos: Tuple[int, int] = (0, 0)
        
        # Bind events using event manager
        self.event_manager.bind_all_events()
    
    @property
    def view_state(self) -> ViewState:
        """Current ViewState — single source of truth for coordinate conversions."""
        return self._view_state
    
    def _update_view_state(self, vs: ViewState):
        """Update internal view state and sync legacy fields."""
        self._view_state = vs
        self.zoom_level = vs.zoom
        self.actual_zoom_level = vs.zoom
        # Sync to app_state
        from core.app_state import app_state
        app_state.update_view_state(vs)
    
    def _current_canvas_size(self) -> Tuple[int, int]:
        """Get current canvas widget dimensions."""
        return (self.winfo_width(), self.winfo_height())
    
    def _ensure_canvas_size_in_vs(self, vs: ViewState) -> ViewState:
        """Ensure ViewState has current canvas dimensions."""
        cw, ch = self._current_canvas_size()
        if cw > 1 and ch > 1 and (vs.canvas_width != cw or vs.canvas_height != ch):
            return vs.with_canvas_size(cw, ch)
        return vs
    
    def set_image(self, image_data: ImageData):
        """Set image to display"""
        self.current_image = image_data
        cw, ch = self._current_canvas_size()
        vs = ViewState(
            zoom=1.0, pan_x=0, pan_y=0,
            canvas_width=max(1, cw), canvas_height=max(1, ch),
            image_width=image_data.width, image_height=image_data.height
        )
        self._view_state = vs  # Set directly before display (app_state notified via center_image)
        self.zoom_level = 1.0
        self.actual_zoom_level = 1.0
        self._refresh_display()
        self.center_image()
    
    def clear_image(self):
        """Clear current image"""
        self.current_image = None
        self.photo_image = None
        if self.image_id:
            self.delete(self.image_id)
            self.image_id = None
        self.clear_all_overlays()
        self.delete("all")
        self._update_view_state(ViewState())
    
    def _refresh_display(self):
        """Refresh the canvas display based on current ViewState.
        
        This is the ONLY method that positions the image on the canvas.
        Position is always derived from ViewState.pan_x/pan_y.
        """
        if not self.current_image:
            return
        
        vs = self._view_state
        
        # Get display image at current zoom level
        self.photo_image = self.image_manager.get_tk_image(vs.zoom)
        if not self.photo_image:
            return
        
        # Remove old image
        if self.image_id:
            self.delete(self.image_id)
        
        # Place image at position derived from ViewState
        self.image_id = self.create_image(
            int(vs.pan_x), int(vs.pan_y), anchor=tk.NW, image=self.photo_image
        )
        
        # Redraw all overlays at current positions
        self.overlay_renderer.redraw_all_overlays()
        if self.is_calibrating:
            self.calibration_handler.redraw_calibration_overlays()
        
        # Grid overlay
        from core.app_state import app_state
        if app_state.grid_visible:
            self.overlay_renderer.render_grid(vs, app_state.grid_spacing, app_state.grid_color)
        else:
            self.overlay_renderer.clear_grid()
        
        # Update scroll region
        iw = self.photo_image.width()
        ih = self.photo_image.height()
        padding = 10
        cw, ch = self._current_canvas_size()
        sr_left = min(0, int(vs.pan_x) - padding)
        sr_top = min(0, int(vs.pan_y) - padding)
        sr_right = max(cw, int(vs.pan_x) + iw + padding)
        sr_bottom = max(ch, int(vs.pan_y) + ih + padding)
        self.configure(scrollregion=(sr_left, sr_top, sr_right, sr_bottom))
    
    def redraw_all_overlays(self):
        """Redraw all measurement overlays - delegates to OverlayManager"""
        self.overlay_renderer.redraw_all_overlays()
    
    def center_image(self):
        """Center image in canvas"""
        if not self.current_image:
            return
        
        cw, ch = self._current_canvas_size()
        if cw <= 1 or ch <= 1:
            self.after(100, self.center_image)
            return
        
        vs = self._ensure_canvas_size_in_vs(self._view_state)
        vs = CoordinateService.center_image(vs)
        self._update_view_state(vs)
        self._refresh_display()
    
    def zoom_in(self):
        """Zoom in at last mouse position or canvas center"""
        sx, sy = self.last_mouse_pos if self.last_mouse_pos != (0, 0) else (
            self.winfo_width() // 2, self.winfo_height() // 2)
        self.zoom_at_cursor(sx, sy, zoom_in=True)
    
    def zoom_out(self):
        """Zoom out at last mouse position or canvas center"""
        sx, sy = self.last_mouse_pos if self.last_mouse_pos != (0, 0) else (
            self.winfo_width() // 2, self.winfo_height() // 2)
        self.zoom_at_cursor(sx, sy, zoom_in=False)
    
    def zoom_at_cursor(self, cursor_x: int, cursor_y: int, zoom_in: bool):
        """Zoom in or out while keeping the point under the cursor stationary"""
        if not self.current_image:
            return
        
        max_zoom = self.image_manager.get_max_zoom() if hasattr(self.image_manager, 'get_max_zoom') else 10.0
        vs = self._ensure_canvas_size_in_vs(self._view_state)
        
        new_zoom = vs.zoom * 1.2 if zoom_in else vs.zoom / 1.2
        new_zoom = max(0.1, min(max_zoom, new_zoom))
        
        if abs(new_zoom - vs.zoom) < 0.01:
            return
        
        vs = CoordinateService.zoom_at_point(vs, cursor_x, cursor_y, new_zoom, 
                                              min_zoom=0.1, max_zoom=max_zoom)
        self._update_view_state(vs)
        self._refresh_display()
    
    def zoom_fit(self):
        """Zoom to fit image in canvas"""
        if not self.current_image:
            return
        
        cw, ch = self._current_canvas_size()
        if cw <= 1 or ch <= 1:
            return
        
        vs = self._ensure_canvas_size_in_vs(self._view_state)
        vs = CoordinateService.fit_to_window(vs)
        self._update_view_state(vs)
        self._refresh_display()
    
    def set_zoom(self, zoom_level: float):
        """Set specific zoom level (centers image)"""
        if not self.current_image:
            return
        max_zoom = self.image_manager.get_max_zoom() if hasattr(self.image_manager, 'get_max_zoom') else 10.0
        zoom_level = max(0.1, min(max_zoom, zoom_level))
        
        vs = self._ensure_canvas_size_in_vs(self._view_state).with_zoom(zoom_level)
        vs = CoordinateService.center_image(vs)
        self._update_view_state(vs)
        self._refresh_display()
    
    def screen_to_image_coords(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to image coordinates"""
        return CoordinateService.screen_to_image(screen_x, screen_y, self._view_state)
    
    def image_to_screen_coords(self, image_x: float, image_y: float) -> Tuple[int, int]:
        """Convert image coordinates to screen coordinates"""
        sx, sy = CoordinateService.image_to_screen(image_x, image_y, self._view_state)
        return (int(sx), int(sy))
    
    def _create_fixed_calibration_text(self, text: str):
        """Create calibration instruction text that stays fixed regardless of canvas state"""
        canvas_width = self.winfo_width()
        
        # Create text at a fixed position relative to canvas widget, not canvas content
        self.create_text(
            canvas_width // 2, 30,  # Fixed position
            text=text,
            fill="red", font=("Arial", 12, "bold"),
            tags="calibration_instruction"
        )
    
    def set_tool(self, tool_name: str):
        """Set current measurement tool - delegates to ToolHandler"""
        self.tool_handler.set_tool(tool_name)
    
    def start_calibration(self):
        """Start calibration mode - delegates to CalibrationHandler"""
        self.calibration_handler.start_calibration()
    
    def get_calibration_points(self) -> List[Tuple[float, float]]:
        """Get calibration points - delegates to CalibrationHandler"""
        return self.calibration_handler.get_calibration_points()
    
    def clear_calibration(self):
        """Clear calibration overlays - delegates to CalibrationHandler"""
        self.calibration_handler.clear_calibration()
    
    def redraw_calibration_overlays(self):
        """Redraw calibration overlays - delegates to CalibrationHandler"""
        self.calibration_handler.redraw_calibration_overlays()
    
    def draw_measurement_overlay(self, measurement: MeasurementBase):
        """Draw measurement overlay - delegates to OverlayManager"""
        self.overlay_renderer.draw_measurement_overlay(measurement)
    
    def remove_measurement_overlay(self, measurement_id: str):
        """Remove measurement overlay - delegates to OverlayManager"""
        self.overlay_renderer.remove_measurement_overlay(measurement_id)
    
    def clear_all_overlays(self):
        """Clear all measurement overlays and temp markers."""
        self.overlay_renderer.clear_all_overlays()
        self.tool_handler.cancel()
    
    def clear_temp_overlays(self):
        """Clear temporary overlays (tag-based)."""
        self.delete("temp")
    
    def toggle_overlays_visibility(self):
        """Toggle visibility of all measurement overlays - delegates to OverlayManager"""
        return self.overlay_renderer.toggle_visibility()
    
    def set_overlays_visibility(self, visible: bool):
        """Set overlay visibility state - delegates to OverlayManager"""
        self.overlay_renderer.set_visibility(visible)
    
    def get_overlays_visibility(self) -> bool:
        """Get current overlay visibility state - delegates to OverlayManager"""
        return self.overlay_renderer.get_visibility()
    
    def set_main_app_reference(self, main_app):
        """Set reference to main application for callbacks"""
        self.main_app = main_app

    def __del__(self):
        """Cleanup when canvas is destroyed"""
        if self.photo_image:
            del self.photo_image
