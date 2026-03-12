"""
Event Manager

Centralizes mouse and keyboard event binding for the canvas widget.
Delegates tool-specific logic to ToolHandler; handles right-click pan directly.
"""

import tkinter as tk
from typing import Optional
from services.coordinate_service import CoordinateService

class EventManager:
    """Binds canvas events and dispatches them."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        # Right-click pan is always available, independent of the active tool
        self.right_pan_start: Optional[tuple] = None
        
    def bind_all_events(self):
        """Bind all mouse and keyboard events."""
        self.canvas.bind("<Button-1>", self.handle_left_click)
        self.canvas.bind("<B1-Motion>", self.handle_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_left_release)
        
        self.canvas.bind("<Button-3>", self.handle_right_click)
        self.canvas.bind("<B3-Motion>", self.handle_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.handle_right_release)
        
        self.canvas.bind("<Motion>", self.handle_mouse_move)
        self.canvas.bind("<MouseWheel>", self.handle_mousewheel)
        
        self.canvas.focus_set()
        self.canvas.bind("<Key>", self.handle_key_press)
    
    # ------------------------------------------------------------------
    # Left button — delegates to calibration or ToolHandler
    # ------------------------------------------------------------------
    
    def handle_left_click(self, event):
        if self.canvas.is_calibrating:
            self.canvas.calibration_handler.handle_click(event)
        else:
            # In pan mode, check if user clicked on an overlay first
            if self.canvas.current_tool == "pan":
                mid = self.canvas.overlay_renderer.find_measurement_at(event.x, event.y)
                if mid:
                    self._select_measurement_in_sidebar(mid)
                    return
            self.canvas.tool_handler.handle_click(event)
    
    def handle_left_drag(self, event):
        if not self.canvas.is_calibrating:
            self.canvas.tool_handler.handle_drag(event)
    
    def handle_left_release(self, event):
        if not self.canvas.is_calibrating:
            self.canvas.tool_handler.handle_release(event)
    
    # ------------------------------------------------------------------
    # Right button — polygon completion or always-available pan
    # ------------------------------------------------------------------
    
    def handle_right_click(self, event):
        # Let ToolHandler try first (e.g., polygon completion)
        if self.canvas.tool_handler.handle_right_click(event):
            return
        # Otherwise start right-pan
        self.right_pan_start = (event.x, event.y)
        self.canvas.config(cursor="fleur")
    
    def handle_right_drag(self, event):
        if self.right_pan_start:
            dx = event.x - self.right_pan_start[0]
            dy = event.y - self.right_pan_start[1]
            self._do_pan(dx, dy)
            self.right_pan_start = (event.x, event.y)
    
    def handle_right_release(self, event):
        if self.right_pan_start:
            self.right_pan_start = None
            self.canvas.set_tool(self.canvas.current_tool)  # restore cursor
            self.canvas._refresh_display()
    
    # ------------------------------------------------------------------
    # Other events
    # ------------------------------------------------------------------
    
    def handle_mouse_move(self, event):
        self.canvas.last_mouse_pos = (event.x, event.y)
        image_coords = self.canvas.screen_to_image_coords(event.x, event.y)
        if hasattr(self.canvas.master.master, 'update_cursor_position'):
            self.canvas.master.master.update_cursor_position(
                int(image_coords[0]), int(image_coords[1]))
        # Live preview line while placing measurement points
        self.canvas.tool_handler.handle_motion(event.x, event.y)
    
    def handle_mousewheel(self, event):
        self.canvas.zoom_at_cursor(event.x, event.y, event.delta > 0)
    
    def handle_key_press(self, event):
        if event.keysym == "Escape":
            self.canvas.tool_handler.cancel()
            if self.canvas.is_calibrating:
                self.canvas.calibration_handler.handle_escape()
    
    # ------------------------------------------------------------------
    # Sidebar selection helper
    # ------------------------------------------------------------------
    
    def _select_measurement_in_sidebar(self, measurement_id: str):
        """Select the measurement in the main window's sidebar listbox."""
        from core.app_state import app_state
        main_app = self.canvas.main_app
        if not main_app:
            return
        for i, m in enumerate(app_state.measurements):
            if m.id == measurement_id:
                lb = main_app.measurements_listbox
                lb.selection_clear(0, "end")
                lb.selection_set(i)
                lb.see(i)
                lb.event_generate("<<ListboxSelect>>")
                return
    
    # ------------------------------------------------------------------
    # Pan helper (shared by right-drag)
    # ------------------------------------------------------------------
    
    def _do_pan(self, dx: float, dy: float):
        """Apply a screen-space pan delta via CoordinateService."""
        vs = self.canvas._ensure_canvas_size_in_vs(self.canvas.view_state)
        vs = CoordinateService.pan_by_screen_delta(vs, dx, dy)
        self.canvas._update_view_state(vs)
        if self.canvas.image_id:
            self.canvas.coords(self.canvas.image_id, int(vs.pan_x), int(vs.pan_y))