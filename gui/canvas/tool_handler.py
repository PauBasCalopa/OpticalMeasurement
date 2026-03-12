"""
Tool Handler

Manages tool selection, temporary points, and the measurement completion flow.
This is the single owner of temp_points and temporary canvas overlays.
"""

from typing import Dict, Any, List, Tuple
from gui.canvas.tools import PanTool, MeasurementTool, PolygonTool, ToolResult
from services.coordinate_service import CoordinateService

class ToolHandler:
    """Manages tool selection and processes ToolResult actions."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        
        # Tool instances
        self.tools = {
            "pan": PanTool(canvas),
            "distance": MeasurementTool(canvas, "distance"),
            "radius": MeasurementTool(canvas, "radius"),
            "angle": MeasurementTool(canvas, "angle"),
            "two_line_angle": MeasurementTool(canvas, "two_line_angle"),
            "coordinate": MeasurementTool(canvas, "coordinate"),
            "point_to_line": MeasurementTool(canvas, "point_to_line"),
            "arc_length": MeasurementTool(canvas, "arc_length"),
            "polygon_area": PolygonTool(canvas),
        }
        
        self.current_tool = None
        
        # ToolHandler owns temporary measurement state
        self.temp_points: List[Tuple[float, float]] = []
    
    # ------------------------------------------------------------------
    # Tool selection
    # ------------------------------------------------------------------
    
    def set_tool(self, tool_name: str):
        """Switch to a new tool, clearing any in-progress measurement."""
        if self.current_tool:
            self.current_tool.deactivate()
        
        self.cancel()  # clear temp state from previous tool
        
        self.canvas.current_tool = tool_name
        tool = self.tools.get(tool_name)
        if tool:
            self.current_tool = tool
            tool.activate()
        else:
            self.current_tool = None
    
    # ------------------------------------------------------------------
    # Event entry points (called by EventManager)
    # ------------------------------------------------------------------
    
    def handle_click(self, event):
        """Handle a left-click for the active tool."""
        tool = self.current_tool
        if not tool:
            return
        
        # Pan tool: start dragging (screen coords, no image point)
        if self.canvas.current_tool == "pan":
            tool.start_pan(event.x, event.y)
            return
        
        # Measurement / polygon tools: convert to image coords, ask tool
        ix, iy = self.canvas.screen_to_image_coords(event.x, event.y)
        result = tool.handle_click(ix, iy, len(self.temp_points))
        self._process_result(result, ix, iy, event.x, event.y)
    
    def handle_drag(self, event):
        """Handle left-button drag (pan tool only)."""
        if self.canvas.current_tool == "pan" and self.current_tool:
            self.current_tool.handle_drag(event.x, event.y)
    
    def handle_release(self, event):
        """Handle left-button release (pan tool only)."""
        if self.canvas.current_tool == "pan" and self.current_tool:
            self.current_tool.handle_release()
    
    def handle_right_click(self, event) -> bool:
        """Handle right-click. Returns True if consumed (e.g., polygon completion)."""
        if self.canvas.current_tool == "polygon_area":
            tool = self.tools.get("polygon_area")
            if tool:
                result = tool.handle_right_click(len(self.temp_points))
                if result == ToolResult.COMPLETE:
                    self._complete_measurement()
                    return True
        return False
    
    def cancel(self):
        """Cancel in-progress measurement: clear temp points and overlays."""
        self.temp_points.clear()
        self.canvas.delete("temp")
        self.canvas.delete("preview")
    
    def handle_motion(self, screen_x: int, screen_y: int):
        """Draw a live preview line from the last placed point to the cursor."""
        self.canvas.delete("preview")
        if not self.temp_points or self.canvas.current_tool == "pan":
            return
        last_img = self.temp_points[-1]
        sx, sy = self.canvas.image_to_screen_coords(*last_img)
        color = self.current_tool.get_color() if self.current_tool else "blue"
        self.canvas.create_line(
            sx, sy, screen_x, screen_y,
            fill=color, width=1, dash=(4, 4), tags="preview"
        )
    
    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    
    def _process_result(self, result: str, ix: float, iy: float,
                        screen_x: int, screen_y: int):
        """Process a ToolResult returned by a tool."""
        if result == ToolResult.ADD_POINT:
            self.temp_points.append((ix, iy))
            self._draw_temp_point(screen_x, screen_y)
        elif result == ToolResult.COMPLETE:
            self.temp_points.append((ix, iy))
            self._draw_temp_point(screen_x, screen_y)
            self._complete_measurement()
    
    def _draw_temp_point(self, sx: int, sy: int):
        """Draw a small temporary point marker at screen coordinates."""
        color = self.current_tool.get_color() if self.current_tool else "blue"
        self.canvas.create_oval(
            sx - 2, sy - 2, sx + 2, sy + 2,
            fill=color, outline=color, tags="temp"
        )
    
    def _complete_measurement(self):
        """Complete the current measurement and store it."""
        try:
            measurement = self.canvas.measurement_engine.complete(
                self.canvas.current_tool, self.temp_points
            )
            if measurement:
                from core.app_state import app_state
                app_state.add_measurement(measurement)
                self.canvas.overlay_renderer.draw_measurement_overlay(measurement)
                self.cancel()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Measurement Error", str(e))
            self.cancel()
    
    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    
    def get_current_tool(self):
        return self.current_tool
    
    def get_points_needed(self, tool_name: str) -> int:
        tool = self.tools.get(tool_name)
        return tool.get_points_needed() if tool else 2