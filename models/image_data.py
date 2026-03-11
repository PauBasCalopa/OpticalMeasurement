"""
Image Data Model

Contains image metadata and display properties
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import Image
import os

@dataclass
class ImageData:
    """Image metadata and display properties"""
    
    # File information
    file_path: str
    file_name: str
    file_size: int  # in bytes
    
    # Image properties
    width: int
    height: int
    format: str
    mode: str  # RGB, RGBA, etc.
    
    # PIL Image objects
    original_image: Optional[Image.Image] = None
    display_image: Optional[Image.Image] = None
    
    def __post_init__(self):
        """Initialize computed properties"""
        if self.file_path and os.path.exists(self.file_path):
            self.file_name = os.path.basename(self.file_path)
            self.file_size = os.path.getsize(self.file_path)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'ImageData':
        """Create ImageData from file path"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        # Load image to get properties
        with Image.open(file_path) as img:
            width, height = img.size
            format_name = img.format or "Unknown"
            mode = img.mode
        
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        return cls(
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            width=width,
            height=height,
            format=format_name,
            mode=mode
        )
    
    @property
    def size(self) -> Tuple[int, int]:
        """Get image size as tuple"""
        return (self.width, self.height)
    
    @property
    def aspect_ratio(self) -> float:
        """Get image aspect ratio"""
        return self.width / self.height if self.height > 0 else 1.0
    
    @property
    def megapixels(self) -> float:
        """Get image size in megapixels"""
        return (self.width * self.height) / 1_000_000
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.file_name} ({self.width}x{self.height}, {self.format})"