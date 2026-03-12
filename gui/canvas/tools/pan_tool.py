"""
Pan Tool

Handles panning (dragging) the image around the canvas. This tool is always available
through right-click, but can also be selected as the primary tool.
"""

from gui.canvas.tools.base_tool import BaseTool, ToolResult
from services.coordinate_service import CoordinateService

class PanTool(BaseTool):
    """Tool for panning the image around the canvas"""
    
    def __init__(self, canvas):
        super().__init__(canvas, "pan")
        self.cursor = "hand2"
        self.pan_start = None
    
    def get_points_needed(self) -> int:
        return 0
    
    def handle_click(self, image_x: float, image_y: float, point_count: int) -> str:
        """Pan tool doesn't add measurement points."""
        return ToolResult.NONE
    
    def start_pan(self, screen_x: int, screen_y: int):
        """Begin a pan drag from screen coordinates."""
        self.pan_start = (screen_x, screen_y)
    
    def handle_drag(self, screen_x: int, screen_y: int) -> bool:
        """Handle pan drag movement. Returns True if handled."""
        if not self.pan_start:
            return False
        dx = screen_x - self.pan_start[0]
        dy = screen_y - self.pan_start[1]
        vs = self.canvas._ensure_canvas_size_in_vs(self.canvas.view_state)
        vs = CoordinateService.pan_by_screen_delta(vs, dx, dy)
        self.canvas._update_view_state(vs)
        if self.canvas.image_id:
            self.canvas.coords(self.canvas.image_id, int(vs.pan_x), int(vs.pan_y))
        self.pan_start = (screen_x, screen_y)
        return True
    
    def handle_release(self) -> bool:
        """Handle pan release — triggers full display refresh."""
        if self.pan_start:
            self.pan_start = None
            self.canvas._refresh_display()
            return True
        return False