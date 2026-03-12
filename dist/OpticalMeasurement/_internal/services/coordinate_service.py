"""
Coordinate Service

Pure functions for coordinate conversions between screen and image space.
All operations take a ViewState and return results — no internal state, no side effects.
"""

from typing import Tuple
from models.view_state import ViewState


class CoordinateService:
    """Stateless coordinate conversion service.
    
    The coordinate model:
    - Image space: pixel coordinates on the original image (0,0) to (width, height)
    - Screen space: pixel coordinates on the canvas widget
    - ViewState.pan_x/pan_y: position of image origin (0,0) in screen coordinates
    - ViewState.zoom: scale factor (image pixels * zoom = screen pixels)
    """
    
    @staticmethod
    def screen_to_image(screen_x: float, screen_y: float, vs: ViewState) -> Tuple[float, float]:
        """Convert screen coordinates to image coordinates.
        
        Formula: image = (screen - pan) / zoom
        """
        if vs.zoom <= 0:
            return (screen_x, screen_y)
        image_x = (screen_x - vs.pan_x) / vs.zoom
        image_y = (screen_y - vs.pan_y) / vs.zoom
        return (image_x, image_y)
    
    @staticmethod
    def image_to_screen(image_x: float, image_y: float, vs: ViewState) -> Tuple[float, float]:
        """Convert image coordinates to screen coordinates.
        
        Formula: screen = image * zoom + pan
        """
        screen_x = image_x * vs.zoom + vs.pan_x
        screen_y = image_y * vs.zoom + vs.pan_y
        return (screen_x, screen_y)
    
    @staticmethod
    def zoom_at_point(vs: ViewState, screen_x: float, screen_y: float, 
                      new_zoom: float, min_zoom: float = 0.1, max_zoom: float = 20.0) -> ViewState:
        """Calculate new ViewState after zooming, keeping the point under the cursor fixed.
        
        The point at (screen_x, screen_y) should map to the same image coordinate
        before and after the zoom.
        """
        new_zoom = max(min_zoom, min(max_zoom, new_zoom))
        if new_zoom == vs.zoom:
            return vs
        
        # Image coordinate under cursor (stays fixed)
        image_x = (screen_x - vs.pan_x) / vs.zoom
        image_y = (screen_y - vs.pan_y) / vs.zoom
        
        # New pan so that image_x,image_y maps back to screen_x,screen_y at new zoom
        new_pan_x = screen_x - image_x * new_zoom
        new_pan_y = screen_y - image_y * new_zoom
        
        new_vs = vs.with_zoom(new_zoom).with_pan(new_pan_x, new_pan_y)
        return CoordinateService.clamp_pan(new_vs)
    
    @staticmethod
    def fit_to_window(vs: ViewState, margin: int = 20) -> ViewState:
        """Calculate ViewState that fits the image centered in the canvas."""
        if not vs.has_image or not vs.has_canvas:
            return vs
        
        available_w = vs.canvas_width - 2 * margin
        available_h = vs.canvas_height - 2 * margin
        
        if available_w <= 0 or available_h <= 0:
            return vs
        
        zoom_w = available_w / vs.image_width
        zoom_h = available_h / vs.image_height
        zoom = min(zoom_w, zoom_h)
        zoom = max(0.1, zoom)
        
        # Center the image
        display_w = vs.image_width * zoom
        display_h = vs.image_height * zoom
        pan_x = (vs.canvas_width - display_w) / 2
        pan_y = (vs.canvas_height - display_h) / 2
        
        return vs.with_zoom(zoom).with_pan(pan_x, pan_y)
    
    @staticmethod
    def center_image(vs: ViewState) -> ViewState:
        """Center image in the canvas at current zoom."""
        if not vs.has_image or not vs.has_canvas:
            return vs
        
        display_w = vs.image_width * vs.zoom
        display_h = vs.image_height * vs.zoom
        pan_x = (vs.canvas_width - display_w) / 2
        pan_y = (vs.canvas_height - display_h) / 2
        
        new_vs = vs.with_pan(pan_x, pan_y)
        return CoordinateService.clamp_pan(new_vs)
    
    @staticmethod
    def pan_by_screen_delta(vs: ViewState, dx: float, dy: float) -> ViewState:
        """Apply a pan delta in screen pixels."""
        new_vs = vs.with_pan(vs.pan_x + dx, vs.pan_y + dy)
        return CoordinateService.clamp_pan(new_vs)
    
    @staticmethod
    def clamp_pan(vs: ViewState) -> ViewState:
        """Clamp pan so the image can't be dragged completely off screen.
        
        Policy: at least some portion of the image is always visible.
        - If image fits in canvas: center it (lock pan)
        - If image is larger: allow panning but keep edges from going too far
        """
        if not vs.has_image or not vs.has_canvas:
            return vs
        
        display_w = vs.image_width * vs.zoom
        display_h = vs.image_height * vs.zoom
        
        pan_x = vs.pan_x
        pan_y = vs.pan_y
        
        if display_w <= vs.canvas_width:
            # Image smaller than canvas: center horizontally
            pan_x = (vs.canvas_width - display_w) / 2
        else:
            # Image larger: keep some margin visible
            margin = min(50, display_w * 0.1)
            min_x = vs.canvas_width - display_w - margin
            max_x = margin
            pan_x = max(min_x, min(max_x, pan_x))
        
        if display_h <= vs.canvas_height:
            # Image smaller than canvas: center vertically
            pan_y = (vs.canvas_height - display_h) / 2
        else:
            # Image larger: keep some margin visible
            margin = min(50, display_h * 0.1)
            min_y = vs.canvas_height - display_h - margin
            max_y = margin
            pan_y = max(min_y, min(max_y, pan_y))
        
        if pan_x == vs.pan_x and pan_y == vs.pan_y:
            return vs
        return vs.with_pan(pan_x, pan_y)
    
    @staticmethod
    def get_visible_image_rect(vs: ViewState) -> Tuple[float, float, float, float]:
        """Get the visible portion of the image in image coordinates.
        
        Returns (x, y, width, height) in image space.
        """
        if vs.zoom <= 0:
            return (0, 0, vs.image_width, vs.image_height)
        
        # Top-left of canvas in image coords
        x, y = CoordinateService.screen_to_image(0, 0, vs)
        # Bottom-right of canvas in image coords 
        x2, y2 = CoordinateService.screen_to_image(vs.canvas_width, vs.canvas_height, vs)
        
        # Clamp to image bounds
        x = max(0, min(x, vs.image_width))
        y = max(0, min(y, vs.image_height))
        x2 = max(0, min(x2, vs.image_width))
        y2 = max(0, min(y2, vs.image_height))
        
        return (x, y, x2 - x, y2 - y)
    
    @staticmethod
    def get_image_bounds_on_screen(vs: ViewState) -> Tuple[float, float, float, float]:
        """Get the screen rectangle occupied by the image.
        
        Returns (left, top, right, bottom) in screen coordinates.
        """
        left, top = CoordinateService.image_to_screen(0, 0, vs)
        right, bottom = CoordinateService.image_to_screen(vs.image_width, vs.image_height, vs)
        return (left, top, right, bottom)
