"""
Pan Tool

Handles panning (dragging) the image around the canvas. This tool is always available
through right-click, but can also be selected as the primary tool.
"""

from gui.canvas.tools.base_tool import BaseTool

class PanTool(BaseTool):
    """Tool for panning the image around the canvas"""
    
    def __init__(self, canvas):
        super().__init__(canvas, "pan")
        self.cursor = "hand2"
        self.pan_start = None
    
    def get_points_needed(self) -> int:
        """Pan tool doesn't need points for measurements"""
        return 0
    
    def handle_click(self, event) -> bool:
        """Handle pan tool click - start panning"""
        self.pan_start = (event.x, event.y)
        return True
    
    def handle_drag(self, event) -> bool:
        """Handle pan drag movement"""
        if not self.pan_start:
            return False
        
        # Calculate intended movement
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]
        
        if self.canvas.image_id:
            # Get current position and calculate intended new position
            current_pos = self.canvas.coords(self.canvas.image_id)
            intended_x = current_pos[0] + dx
            intended_y = current_pos[1] + dy
            
            # Apply smart boundaries
            bounded_x, bounded_y = self.canvas._apply_smart_pan_boundaries(intended_x, intended_y)
            
            # Move to bounded position
            self.canvas.coords(self.canvas.image_id, bounded_x, bounded_y)
        
        self.pan_start = (event.x, event.y)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        return True
    
    def handle_release(self, event) -> bool:
        """Handle pan release - complete panning"""
        if self.pan_start:
            self.pan_start = None
            self.canvas._stabilize_coordinate_system()
            self.canvas.redraw_all_overlays()
            if self.canvas.is_calibrating:
                self.canvas.redraw_calibration_overlays()
            return True
        return False