"""
Base Tool Class

Abstract base class for all canvas tools. Provides common interface and behavior
that all tools should implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Optional


class ToolResult:
    """Action returned by a tool after handling a click."""
    NONE = "none"            # Do nothing (e.g., pan tool)
    ADD_POINT = "add_point"  # Add point, keep collecting
    COMPLETE = "complete"    # Add point AND complete the measurement


class BaseTool(ABC):
    """Abstract base class for all canvas tools"""
    
    def __init__(self, canvas, tool_name: str):
        self.canvas = canvas
        self.tool_name = tool_name
        self.cursor = "crosshair"
        self.color = "blue"
    
    @abstractmethod
    def handle_click(self, image_x: float, image_y: float, point_count: int) -> str:
        """Handle a click at image coordinates.
        
        Args:
            image_x, image_y: Click position in image coordinates.
            point_count: Number of points already collected (before this click).
            
        Returns:
            ToolResult constant (NONE, ADD_POINT, or COMPLETE).
        """
        pass
    
    @abstractmethod
    def get_points_needed(self) -> int:
        """Minimum number of points this tool needs to complete."""
        pass
    
    def get_cursor(self) -> str:
        return self.cursor
    
    def get_color(self) -> str:
        return self.color
    
    def activate(self):
        """Called when tool becomes active. Cursor change only — cleanup handled by ToolHandler."""
        self.canvas.config(cursor=self.get_cursor())
    
    def deactivate(self):
        """Called when tool becomes inactive."""
        pass