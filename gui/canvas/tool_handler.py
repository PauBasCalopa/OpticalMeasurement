"""
Tool Handler

Manages tool selection and tool-specific behaviors for the canvas widget.
Provides centralized tool management and consistent tool behavior.
"""

from typing import Dict, Any
from gui.canvas.tools import PanTool, MeasurementTool, PolygonTool

class ToolHandler:
    """Manages tool selection and tool-specific behaviors"""
    
    def __init__(self, canvas):
        """Initialize tool handler with canvas reference"""
        self.canvas = canvas
        
        # Initialize tool instances
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
        
        # Current active tool
        self.current_tool = None
    
    def set_tool(self, tool_name: str):
        """Set current measurement tool"""
        # Deactivate old tool
        if self.current_tool:
            self.current_tool.deactivate()
        
        # Set new tool
        self.canvas.current_tool = tool_name
        tool = self.tools.get(tool_name)
        
        if tool:
            self.current_tool = tool
            tool.activate()
        else:
            print(f"Warning: Unknown tool '{tool_name}'")
            self.current_tool = None
    
    def handle_measurement_click(self, event):
        """Handle measurement tool click with unified logic"""
        tool = self.tools.get(self.canvas.current_tool)
        if tool and tool != self.tools["pan"]:  # Don't use pan tool for measurements
            return tool.handle_click(event)
        
        # Fallback: use old logic for unknown tools
        image_coords = self.canvas.coordinate_manager.screen_to_image(event.x, event.y)
        self.canvas.temp_points.append(image_coords)
        
        point_id = self.canvas.create_oval(
            event.x - 2, event.y - 2,
            event.x + 2, event.y + 2,
            fill="blue", outline="blue", tags="temp"
        )
        self.canvas.temp_overlays.append(point_id)
        
        # Check completion using tool configuration
        self._check_measurement_completion()
        return True
    
    def handle_polygon_click(self, event):
        """Handle polygon area tool click"""
        tool = self.tools.get("polygon_area")
        if tool:
            return tool.handle_click(event)
        
        return False
    
    def handle_right_click(self, event):
        """Handle right-click for polygon completion"""
        if self.canvas.current_tool == "polygon_area":
            tool = self.tools.get("polygon_area")
            if tool and hasattr(tool, 'handle_right_click'):
                return tool.handle_right_click(event)
        
        return False
    
    def _check_measurement_completion(self):
        """Check if current measurement should be completed (fallback method)"""
        tool_config = {
            "distance": 2,
            "radius": 3,
            "angle": 3,
            "two_line_angle": 4,
            "coordinate": 2,  # Max points for coordinate
            "point_to_line": 3,
            "arc_length": 3,
        }
        
        points_needed = tool_config.get(self.canvas.current_tool, 2)
        
        if self.canvas.current_tool == "coordinate" and len(self.canvas.temp_points) >= 2:
            self.canvas.complete_measurement()
        elif len(self.canvas.temp_points) >= points_needed:
            self.canvas.complete_measurement()
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration information for a tool"""
        tool = self.tools.get(tool_name)
        if tool and hasattr(tool, 'get_tool_info'):
            return tool.get_tool_info()
        
        return {"type": "unknown", "tool_name": tool_name}
    
    def get_current_tool(self):
        """Get current active tool instance"""
        return self.current_tool
    
    def get_points_needed(self, tool_name: str) -> int:
        """Get number of points needed for a tool"""
        tool = self.tools.get(tool_name)
        if tool:
            return tool.get_points_needed()
        return 2  # Default