"""
Polygon Tool

Handles polygon area measurements. This tool allows multiple points and is completed
by right-clicking rather than reaching a specific point count.
"""

from gui.canvas.tools.base_tool import BaseTool, ToolResult

class PolygonTool(BaseTool):
    """Tool for polygon area measurements"""
    
    def __init__(self, canvas):
        super().__init__(canvas, "polygon_area")
        self.color = "cyan"
    
    def get_points_needed(self) -> int:
        return 3  # Minimum for a polygon
    
    def handle_click(self, image_x: float, image_y: float, point_count: int) -> str:
        """Always add point — polygon completes on right-click."""
        return ToolResult.ADD_POINT
    
    def handle_right_click(self, point_count: int) -> str:
        """Complete polygon if enough points, otherwise do nothing."""
        if point_count >= 3:
            return ToolResult.COMPLETE
        return ToolResult.NONE
    
    def get_tool_info(self):
        return {
            "type": "polygon",
            "measurement_type": "polygon_area",
            "min_points": 3,
            "color": self.color,
            "completion_method": "right_click"
        }