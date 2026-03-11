"""
Base Tool Class

Abstract base class for all canvas tools. Provides common interface and behavior
that all tools should implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Optional

class BaseTool(ABC):
    """Abstract base class for all canvas tools"""
    
    def __init__(self, canvas, tool_name: str):
        """Initialize base tool with canvas reference and name"""
        self.canvas = canvas
        self.tool_name = tool_name
        self.points_needed = 1  # Default, override in subclasses
        self.cursor = "crosshair"  # Default cursor
        self.color = "blue"  # Default drawing color
    
    @abstractmethod
    def handle_click(self, event) -> bool:
        """Handle mouse click for this tool
        
        Args:
            event: Mouse event from tkinter
            
        Returns:
            bool: True if click was handled, False otherwise
        """
        pass
    
    @abstractmethod
    def get_points_needed(self) -> int:
        """Get number of points this tool needs to complete a measurement
        
        Returns:
            int: Number of points needed
        """
        pass
    
    def get_cursor(self) -> str:
        """Get cursor type for this tool"""
        return self.cursor
    
    def get_color(self) -> str:
        """Get drawing color for this tool"""
        return self.color
    
    def activate(self):
        """Called when tool becomes active"""
        self.canvas.config(cursor=self.get_cursor())
        self.canvas.temp_points.clear()
        self.canvas.clear_temp_overlays()
    
    def deactivate(self):
        """Called when tool becomes inactive"""
        self.canvas.temp_points.clear()
        self.canvas.clear_temp_overlays()
    
    def draw_temp_point(self, event, color: Optional[str] = None):
        """Draw temporary point at click location"""
        draw_color = color or self.get_color()
        point_id = self.canvas.create_oval(
            event.x - 2, event.y - 2,
            event.x + 2, event.y + 2,
            fill=draw_color, outline=draw_color, tags="temp"
        )
        self.canvas.temp_overlays.append(point_id)
        return point_id
    
    def add_image_point(self, event) -> Tuple[float, float]:
        """Convert screen coordinates and add to temp_points"""
        image_coords = self.canvas.coordinate_manager.screen_to_image(event.x, event.y)
        self.canvas.temp_points.append(image_coords)
        return image_coords
    
    def is_measurement_complete(self) -> bool:
        """Check if enough points have been collected"""
        return len(self.canvas.temp_points) >= self.get_points_needed()
    
    def complete_measurement(self):
        """Complete the measurement using canvas's complete_measurement method"""
        self.canvas.complete_measurement()