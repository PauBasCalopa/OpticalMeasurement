"""
View State

Immutable representation of the current viewport state.
Pan and zoom are pure data — no canvas manipulation.
"""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ViewState:
    """Represents the current view configuration over the image.
    
    All coordinates and offsets are in IMAGE pixel space.
    The viewport defines what portion of the image is visible on screen.
    """
    # Zoom factor (1.0 = 100%, 2.0 = 200%)
    zoom: float = 1.0
    
    # Pan offset: position of image origin in screen coordinates.
    # (0,0) means image top-left is at canvas top-left.
    # Positive values shift the image right/down.
    pan_x: float = 0.0
    pan_y: float = 0.0
    
    # Canvas (screen) dimensions in pixels
    canvas_width: int = 0
    canvas_height: int = 0
    
    # Original image dimensions in pixels
    image_width: int = 0
    image_height: int = 0
    
    def with_zoom(self, zoom: float) -> 'ViewState':
        """Return new ViewState with updated zoom"""
        return replace(self, zoom=zoom)
    
    def with_pan(self, pan_x: float, pan_y: float) -> 'ViewState':
        """Return new ViewState with updated pan"""
        return replace(self, pan_x=pan_x, pan_y=pan_y)
    
    def with_canvas_size(self, width: int, height: int) -> 'ViewState':
        """Return new ViewState with updated canvas dimensions"""
        return replace(self, canvas_width=width, canvas_height=height)
    
    def with_image_size(self, width: int, height: int) -> 'ViewState':
        """Return new ViewState with updated image dimensions"""
        return replace(self, image_width=width, image_height=height)
    
    @property
    def display_image_width(self) -> float:
        """Width of the image as displayed on screen"""
        return self.image_width * self.zoom
    
    @property
    def display_image_height(self) -> float:
        """Height of the image as displayed on screen"""
        return self.image_height * self.zoom
    
    @property
    def has_image(self) -> bool:
        """Check if image dimensions are set"""
        return self.image_width > 0 and self.image_height > 0
    
    @property
    def has_canvas(self) -> bool:
        """Check if canvas dimensions are set"""
        return self.canvas_width > 0 and self.canvas_height > 0
