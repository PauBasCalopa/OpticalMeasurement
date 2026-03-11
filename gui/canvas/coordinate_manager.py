"""
Coordinate Manager

Handles all coordinate conversions between screen and image space for the canvas widget.
Provides a centralized, consistent approach to coordinate transformations.
"""

from typing import Tuple, Optional
from tkinter import Canvas

class CoordinateManager:
    """Handles all coordinate conversions between screen and image space"""
    
    def __init__(self, canvas):
        """Initialize coordinate manager with canvas reference"""
        self.canvas = canvas
    
    def screen_to_image(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to image coordinates
        
        Args:
            screen_x: Screen X coordinate (pixel position on canvas)
            screen_y: Screen Y coordinate (pixel position on canvas)
            
        Returns:
            Tuple of (image_x, image_y) in original image coordinate space
        """
        if not self.canvas.current_image or not self.canvas.image_id:
            return (float(screen_x), float(screen_y))
        
        # Get current image position on canvas
        image_x, image_y = self.canvas.coords(self.canvas.image_id)
        
        # Ensure zoom level is up-to-date
        self.canvas._update_actual_zoom_level()
        
        # Convert screen click to original image coordinates
        rel_x = (screen_x - image_x) / self.canvas.actual_zoom_level
        rel_y = (screen_y - image_y) / self.canvas.actual_zoom_level
        
        return (rel_x, rel_y)
    
    def image_to_screen(self, image_x: float, image_y: float) -> Tuple[int, int]:
        """Convert image coordinates to screen coordinates
        
        Args:
            image_x: X coordinate in original image space
            image_y: Y coordinate in original image space
            
        Returns:
            Tuple of (screen_x, screen_y) pixel positions on canvas
        """
        if not self.canvas.current_image or not self.canvas.image_id:
            return (int(image_x), int(image_y))
        
        # Get current image position on canvas
        canvas_image_x, canvas_image_y = self.canvas.coords(self.canvas.image_id)
        
        # Ensure zoom level is up-to-date
        self.canvas._update_actual_zoom_level()
        
        # Convert stored image coordinates to current screen position
        screen_x = int(canvas_image_x + image_x * self.canvas.actual_zoom_level)
        screen_y = int(canvas_image_y + image_y * self.canvas.actual_zoom_level)
        
        return (screen_x, screen_y)
    
    def get_zoom_factor(self) -> float:
        """Get current zoom factor"""
        return self.canvas.actual_zoom_level
    
    def is_valid_coordinate_system(self) -> bool:
        """Check if coordinate system is in a valid state for conversions"""
        return (self.canvas.current_image is not None and 
                self.canvas.image_id is not None and
                self.canvas.actual_zoom_level > 0)
    
    def validate_coordinates_after_pan(self) -> bool:
        """Validate that coordinate system is consistent after pan operations
        
        This helps detect when image and canvas coordinate systems become desynchronized.
        """
        if not self.is_valid_coordinate_system():
            return False
        
        try:
            # Test coordinate conversion round-trip
            # Pick a point in the middle of the canvas
            canvas_center_x = self.canvas.winfo_width() // 2
            canvas_center_y = self.canvas.winfo_height() // 2
            
            # Convert to image coordinates and back
            image_coords = self.screen_to_image(canvas_center_x, canvas_center_y)
            screen_coords = self.image_to_screen(image_coords[0], image_coords[1])
            
            # Check if round-trip conversion is reasonably accurate
            error_x = abs(screen_coords[0] - canvas_center_x)
            error_y = abs(screen_coords[1] - canvas_center_y)
            
            # Allow for small rounding errors
            max_error = 2.0
            return error_x <= max_error and error_y <= max_error
            
        except Exception:
            return False
    
    def get_image_boundaries_in_screen_coords(self) -> Tuple[int, int, int, int]:
        """Get the screen coordinates of image boundaries
        
        Returns:
            Tuple of (left, top, right, bottom) in screen coordinates
        """
        if not self.is_valid_coordinate_system():
            return (0, 0, 0, 0)
        
        # Get image dimensions
        image_width = self.canvas.current_image.width
        image_height = self.canvas.current_image.height
        
        # Convert image corners to screen coordinates
        top_left = self.image_to_screen(0, 0)
        bottom_right = self.image_to_screen(image_width, image_height)
        
        return (top_left[0], top_left[1], bottom_right[0], bottom_right[1])