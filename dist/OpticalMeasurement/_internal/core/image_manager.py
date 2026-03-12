"""
Image Manager

Handles image loading, processing, and display optimization using Pillow
"""

import os
from typing import Optional, Tuple
from PIL import Image, ImageTk
import tkinter as tk

from models.image_data import ImageData

class ImageManager:
    """Manages image loading, processing, and display optimization"""
    
    # Supported image formats
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'
    }
    
    # Maximum display size for performance (width, height)
    # ? INCREASED: Allow higher zoom levels for detailed inspection
    MAX_DISPLAY_SIZE = (8192, 8192)  # Increased from 2048 to support high zoom
    
    def __init__(self):
        self.current_image_data: Optional[ImageData] = None
        self._display_cache = {}  # Cache for display images at different zoom levels
        self.max_zoom_level = 10.0  # ? NEW: Dynamic max zoom based on image size
    
    def load_image(self, file_path: str) -> ImageData:
        """Load image from file path with error handling"""
        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {ext}")
        
        try:
            # Create image data object
            image_data = ImageData.from_file(file_path)
            
            # Load the original image
            image_data.original_image = Image.open(file_path)
            
            # Create initial display image
            image_data.display_image = self._create_display_image(
                image_data.original_image, 1.0
            )
            
            # Store current image data
            self.current_image_data = image_data
            
            # ? NEW: Calculate dynamic max zoom based on image size
            self._calculate_max_zoom()
            
            # Clear display cache
            self._display_cache.clear()
            
            return image_data
            
        except Exception as e:
            raise IOError(f"Failed to load image: {str(e)}")
    
    def close_image(self):
        """Close current image and free memory"""
        if self.current_image_data:
            # Close PIL images
            if self.current_image_data.original_image:
                self.current_image_data.original_image.close()
            if self.current_image_data.display_image:
                self.current_image_data.display_image.close()
            
            # Clear references
            self.current_image_data = None
            
            # Clear cache
            self._display_cache.clear()
    
    def get_display_image(self, zoom_level: float = 1.0) -> Optional[Image.Image]:
        """Get display-optimized image at specified zoom level"""
        if not self.current_image_data or not self.current_image_data.original_image:
            return None
        
        # Check cache first
        cache_key = f"{zoom_level:.2f}"
        if cache_key in self._display_cache:
            return self._display_cache[cache_key]
        
        # Create new display image
        display_image = self._create_display_image(
            self.current_image_data.original_image, zoom_level
        )
        
        # Cache it (limit cache size)
        if len(self._display_cache) < 10:  # Limit cache size
            self._display_cache[cache_key] = display_image
        
        return display_image
    
    def get_tk_image(self, zoom_level: float = 1.0) -> Optional[ImageTk.PhotoImage]:
        """Get tkinter-compatible PhotoImage at specified zoom level"""
        display_image = self.get_display_image(zoom_level)
        if display_image is None:
            return None
        
        try:
            return ImageTk.PhotoImage(display_image)
        except Exception as e:
            # Error creating PhotoImage, return None
            return None
    
    def _calculate_max_zoom(self):
        """Calculate maximum safe zoom level based on image dimensions"""
        if not self.current_image_data:
            self.max_zoom_level = 10.0
            return
        
        width, height = self.current_image_data.original_image.size
        
        # Calculate max zoom that keeps image under reasonable pixel limits
        # Allow higher zoom for smaller images, lower zoom for larger images
        max_width_zoom = self.MAX_DISPLAY_SIZE[0] / width
        max_height_zoom = self.MAX_DISPLAY_SIZE[1] / height
        calculated_max = min(max_width_zoom, max_height_zoom)
        
        # Ensure we can zoom to at least 2x, but no more than 20x
        self.max_zoom_level = max(2.0, min(20.0, calculated_max))
        
    
    def get_max_zoom(self) -> float:
        """Get maximum zoom level for current image"""
        return self.max_zoom_level
    
    def _create_display_image(self, original_image: Image.Image, zoom_level: float) -> Image.Image:
        """Create optimized display image"""
        # Calculate target size
        original_width, original_height = original_image.size
        target_width = int(original_width * zoom_level)
        target_height = int(original_height * zoom_level)
        
        # ? IMPROVED: Better high-zoom handling with performance considerations
        max_pixels = self.MAX_DISPLAY_SIZE[0] * self.MAX_DISPLAY_SIZE[1]
        target_pixels = target_width * target_height
        
        # Only limit if the total pixel count exceeds reasonable limits
        if target_pixels > max_pixels:
            # Calculate scale factor to fit within pixel budget
            scale = (max_pixels / target_pixels) ** 0.5
            target_width = int(target_width * scale)
            target_height = int(target_height * scale)
        
        # Additional safety check for extreme dimensions
        if target_width > self.MAX_DISPLAY_SIZE[0]:
            scale = self.MAX_DISPLAY_SIZE[0] / target_width
            target_width = int(target_width * scale)
            target_height = int(target_height * scale)
            
        if target_height > self.MAX_DISPLAY_SIZE[1]:
            scale = self.MAX_DISPLAY_SIZE[1] / target_height
            target_width = int(target_width * scale)
            target_height = int(target_height * scale)
        
        # Resize image with appropriate resampling
        if zoom_level < 1.0:
            # Use LANCZOS for downscaling (better quality)
            resample = Image.Resampling.LANCZOS
        else:
            # Use NEAREST for upscaling (faster, preserves pixel boundaries for measurements)
            resample = Image.Resampling.NEAREST
        
        try:
            resized_image = original_image.resize(
                (target_width, target_height), 
                resample=resample
            )
            return resized_image
        except Exception as e:
            # Error resizing image, use fallback
            # Fallback: return copy of original
            return original_image.copy()
    
    def get_actual_zoom_factor(self, requested_zoom: float) -> float:
        """Get the actual zoom factor after MAX_DISPLAY_SIZE limiting
        
        This is crucial for coordinate calculations - the displayed image might
        be smaller than the requested zoom due to MAX_DISPLAY_SIZE limits.
        """
        if not self.current_image_data:
            return requested_zoom
        
        # Get the actual display image at this zoom level
        display_image = self.get_display_image(requested_zoom)
        if display_image is None:
            return requested_zoom
        
        # Calculate actual zoom from actual image dimensions
        actual_width, actual_height = display_image.size
        actual_zoom_w = actual_width / self.current_image_data.width
        actual_zoom_h = actual_height / self.current_image_data.height
        
        # Return the average (should be the same for both dimensions)
        return (actual_zoom_w + actual_zoom_h) / 2
    
    def get_fit_to_window_zoom(self, window_width: int, window_height: int, 
                              margin: int = 20) -> float:
        """Calculate zoom level to fit image in window"""
        if not self.current_image_data:
            return 1.0
        
        # Account for margins
        available_width = window_width - 2 * margin
        available_height = window_height - 2 * margin
        
        # Calculate scale factors
        scale_w = available_width / self.current_image_data.width
        scale_h = available_height / self.current_image_data.height
        
        # Use the smaller scale factor to fit entirely
        fit_zoom = min(scale_w, scale_h)
        
        # Ensure minimum zoom level
        return max(0.1, fit_zoom)
    
    @property
    def is_image_loaded(self) -> bool:
        """Check if image is currently loaded"""
        return (self.current_image_data is not None and 
                self.current_image_data.original_image is not None)
    
    @property
    def image_size(self) -> Tuple[int, int]:
        """Get current image size"""
        if self.current_image_data:
            return (self.current_image_data.width, self.current_image_data.height)
        return (0, 0)
    
    def get_zoom_debug_info(self, zoom_level: float) -> dict:
        """Get detailed zoom information for debugging"""
        if not self.current_image_data:
            return {"error": "No image loaded"}
        
        original_width, original_height = self.current_image_data.original_image.size
        target_width = int(original_width * zoom_level)
        target_height = int(original_height * zoom_level)
        
        # Get actual display image
        display_image = self.get_display_image(zoom_level)
        actual_width, actual_height = display_image.size if display_image else (0, 0)
        
        actual_zoom = self.get_actual_zoom_factor(zoom_level)
        
        return {
            "requested_zoom": zoom_level,
            "actual_zoom": actual_zoom,
            "original_size": (original_width, original_height),
            "target_size": (target_width, target_height),
            "actual_size": (actual_width, actual_height),
            "max_display_size": self.MAX_DISPLAY_SIZE,
            "is_limited": actual_zoom < zoom_level * 0.99,  # Allow 1% tolerance
            "zoom_percentage": f"{zoom_level * 100:.1f}%",
            "actual_percentage": f"{actual_zoom * 100:.1f}%"
        }
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_image()
