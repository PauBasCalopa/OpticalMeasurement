"""
Measurement Tool

Handles standard measurement tools like distance, radius, angle, etc.
Each measurement type is configured with specific behavior.
"""

from gui.canvas.tools.base_tool import BaseTool, ToolResult
from typing import Dict, Any

class MeasurementTool(BaseTool):
    """Tool for standard measurements (distance, radius, angle, etc.)"""
    
    TOOL_CONFIG = {
        "distance": {"points": 2, "color": "blue"},
        "radius": {"points": 3, "color": "blue"},
        "angle": {"points": 3, "color": "blue"},
        "two_line_angle": {"points": 4, "color": "blue"},
        "coordinate": {"points": 1, "max_points": 2, "color": "blue"},
        "point_to_line": {"points": 3, "color": "blue"},
        "arc_length": {"points": 3, "color": "blue"},
    }
    
    def __init__(self, canvas, measurement_type: str):
        super().__init__(canvas, measurement_type)
        config = self.TOOL_CONFIG.get(measurement_type, {"points": 2, "color": "blue"})
        self.measurement_type = measurement_type
        self.points_needed = config["points"]
        self.max_points = config.get("max_points", self.points_needed)
        self.color = config["color"]
    
    def get_points_needed(self) -> int:
        return self.points_needed
    
    def handle_click(self, image_x: float, image_y: float, point_count: int) -> str:
        """Return ADD_POINT or COMPLETE based on collected point count."""
        new_count = point_count + 1
        if self.measurement_type == "coordinate":
            if new_count >= self.max_points:
                return ToolResult.COMPLETE
        elif new_count >= self.points_needed:
            return ToolResult.COMPLETE
        return ToolResult.ADD_POINT
    
    def get_tool_info(self) -> Dict[str, Any]:
        return {
            "type": "measurement",
            "measurement_type": self.measurement_type,
            "points_needed": self.points_needed,
            "max_points": self.max_points,
            "color": self.color
        }