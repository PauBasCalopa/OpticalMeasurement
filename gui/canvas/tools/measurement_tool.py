"""
Measurement Tool

Handles standard measurement tools like distance, radius, angle, etc.
Each measurement type is configured with specific behavior.
"""

from gui.canvas.tools.base_tool import BaseTool
from typing import Dict, Any

class MeasurementTool(BaseTool):
    """Tool for standard measurements (distance, radius, angle, etc.)"""
    
    # Configuration for different measurement types
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
        
        # Get configuration for this measurement type
        config = self.TOOL_CONFIG.get(measurement_type, {"points": 2, "color": "blue"})
        
        self.measurement_type = measurement_type
        self.points_needed = config["points"]
        self.max_points = config.get("max_points", self.points_needed)
        self.color = config["color"]
    
    def get_points_needed(self) -> int:
        """Get number of points needed for this measurement"""
        return self.points_needed
    
    def handle_click(self, event) -> bool:
        """Handle measurement tool click"""
        # Add point to measurement
        image_coords = self.add_image_point(event)
        
        # Draw temporary point
        self.draw_temp_point(event, self.color)
        
        # Check if measurement should be completed
        if self._should_complete_measurement():
            self.complete_measurement()
        
        return True
    
    def _should_complete_measurement(self) -> bool:
        """Check if measurement should be completed based on points collected"""
        point_count = len(self.canvas.temp_points)
        
        # Special handling for coordinate tool (can work with 1 or 2 points)
        if self.measurement_type == "coordinate":
            return point_count >= self.max_points
        
        # Standard tools complete when they have enough points
        return point_count >= self.points_needed
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about this tool"""
        return {
            "type": "measurement",
            "measurement_type": self.measurement_type,
            "points_needed": self.points_needed,
            "max_points": self.max_points,
            "color": self.color
        }