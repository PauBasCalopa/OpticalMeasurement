"""
Polygon Tool

Handles polygon area measurements. This tool allows multiple points and is completed
by right-clicking rather than reaching a specific point count.
"""

from gui.canvas.tools.base_tool import BaseTool

class PolygonTool(BaseTool):
    """Tool for polygon area measurements"""
    
    def __init__(self, canvas):
        super().__init__(canvas, "polygon_area")
        self.points_needed = 3  # Minimum for a polygon
        self.color = "cyan"
    
    def get_points_needed(self) -> int:
        """Get minimum number of points needed for a polygon"""
        return self.points_needed
    
    def handle_click(self, event) -> bool:
        """Handle polygon tool click - add point to polygon"""
        # Add point to polygon
        image_coords = self.add_image_point(event)
        
        # Draw temporary point in cyan
        self.draw_temp_point(event, self.color)
        
        # Polygon doesn't auto-complete - user right-clicks to finish
        # But we can provide visual feedback about minimum points
        if len(self.canvas.temp_points) >= self.points_needed:
            # Could add visual indicator that polygon can now be completed
            pass
        
        return True
    
    def can_complete(self) -> bool:
        """Check if polygon has enough points to be completed"""
        return len(self.canvas.temp_points) >= self.points_needed
    
    def handle_right_click(self, event) -> bool:
        """Handle right-click to complete polygon (if enough points)"""
        if self.can_complete():
            self.complete_measurement()
            return True
        return False
    
    def get_tool_info(self):
        """Get information about this tool"""
        return {
            "type": "polygon",
            "measurement_type": "polygon_area",
            "min_points": self.points_needed,
            "color": self.color,
            "completion_method": "right_click"
        }