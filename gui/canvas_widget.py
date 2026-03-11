"""
Image Canvas Widget

Custom tkinter Canvas for image display and measurement interactions
"""

import tkinter as tk
from tkinter import Canvas
from typing import Optional, List, Tuple
from PIL import ImageTk, Image, ImageDraw, ImageFont
import math

from models.image_data import ImageData
from core.image_manager import ImageManager
from core.measurement_engine import MeasurementEngine
from models.measurement_data import MeasurementBase

# Phase 3: Import new architecture components
from gui.canvas.coordinate_manager import CoordinateManager
from gui.canvas.event_manager import EventManager
from gui.canvas.tool_handler import ToolHandler
from gui.canvas.overlay_manager import OverlayManager
from gui.canvas.calibration_handler import CalibrationHandler

class ImageCanvas(Canvas):
    """Custom canvas for interactive image display and measurements"""
    
    def __init__(self, parent, image_manager: ImageManager, measurement_engine: MeasurementEngine, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.image_manager = image_manager
        self.measurement_engine = measurement_engine
        
        # Reference to main application window for dialog callbacks
        self.main_app = None  # Will be set by main window
        
        # Phase 3: Initialize all managers
        self.coordinate_manager = CoordinateManager(self)
        self.event_manager = EventManager(self)
        self.tool_handler = ToolHandler(self)
        self.overlay_manager = OverlayManager(self)
        self.calibration_handler = CalibrationHandler(self)
        
        # Canvas state
        self.current_image: Optional[ImageData] = None
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.image_id: Optional[int] = None
        
        # Interaction state
        self.current_tool: str = "pan"
        self.temp_points: List[Tuple[float, float]] = []
        self.is_calibrating: bool = False
        
        # Display state
        self.zoom_level: float = 1.0  # Requested zoom level
        self.actual_zoom_level: float = 1.0  # Actual zoom level (after MAX_DISPLAY_SIZE limiting)
        self.last_mouse_pos: Tuple[int, int] = (0, 0)  # Track mouse position for zoom-to-cursor
        
        # Overlays - now managed by OverlayManager
        self.temp_overlays = []  # temporary drawing items
        
        # Bind events using event manager
        self.event_manager.bind_all_events()
    
    def bind_events(self):
        """Bind mouse and keyboard events"""
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<B1-Motion>", self.on_left_drag)
        self.bind("<ButtonRelease-1>", self.on_left_release)
        
        # ? NEW: Right mouse button for panning
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<B3-Motion>", self.on_right_drag)
        self.bind("<ButtonRelease-3>", self.on_right_release)
        
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<MouseWheel>", self.on_mousewheel)
        
        # Make canvas focusable for key events
        self.focus_set()
        self.bind("<Key>", self.on_key_press)
    
    def set_image(self, image_data: ImageData):
        """Set image to display"""
        self.current_image = image_data
        self.zoom_level = 1.0
        self.actual_zoom_level = 1.0  # Initialize actual zoom level
        self.update_image_display()
        self.center_image()
    
    def clear_image(self):
        """Clear current image"""
        self.current_image = None
        self.photo_image = None
        if self.image_id:
            self.delete(self.image_id)
            self.image_id = None
        self.clear_all_overlays()
        self.delete("all")
    
    def update_image_display(self):
        """Update image display at current zoom level"""
        if not self.current_image:
            return
        
        # Get image at current zoom level
        self.photo_image = self.image_manager.get_tk_image(self.zoom_level)
        
        if self.photo_image:
            # ? FIX: Calculate actual zoom factor after MAX_DISPLAY_SIZE limiting
            self.actual_zoom_level = self.image_manager.get_actual_zoom_factor(self.zoom_level)
            # Remove old image
            if self.image_id:
                self.delete(self.image_id)
            
            # Add new image
            self.image_id = self.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
            # ? FIX: Only update overlays when zoom changes, not on every display update
            self.redraw_all_overlays()
            # ? FIX: Redraw calibration overlays after zoom
            if self.is_calibrating:
                self.redraw_calibration_overlays()
            
            # Update scroll region
            self.configure(scrollregion=self.bbox("all"))
    
    def redraw_all_overlays(self):
        """Redraw all measurement overlays - delegates to OverlayManager"""
        self.overlay_manager.redraw_all_overlays()
    
    def center_image(self):
        """Center image in canvas"""
        if not self.photo_image:
            return
        
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet properly sized, schedule for later
            self.after(100, self.center_image)
            return
        
        image_width = self.photo_image.width()
        image_height = self.photo_image.height()
        
        # Calculate center position
        center_x = max(0, (canvas_width - image_width) // 2)
        center_y = max(0, (canvas_height - image_height) // 2)
        
        # Apply Microsoft Paint style smart boundaries to centering
        bounded_x, bounded_y = self._apply_smart_pan_boundaries(center_x, center_y)
        
        # Move image to bounded center position
        if self.image_id:
            self.coords(self.image_id, bounded_x, bounded_y)
        
        # Update scroll region
        self.configure(scrollregion=self.bbox("all"))
    
    def zoom_in(self):
        """Zoom in at last mouse position or canvas center"""
        # ? IMPROVED: Use mouse-centered zoom if available, otherwise use canvas center
        if hasattr(self, 'last_mouse_pos') and self.last_mouse_pos != (0, 0):
            self.zoom_at_cursor(self.last_mouse_pos[0], self.last_mouse_pos[1], zoom_in=True)
        else:
            # Fallback: zoom at canvas center
            canvas_center_x = self.winfo_width() // 2
            canvas_center_y = self.winfo_height() // 2
            self.zoom_at_cursor(canvas_center_x, canvas_center_y, zoom_in=True)
    
    def zoom_out(self):
        """Zoom out at last mouse position or canvas center"""
        # ? IMPROVED: Use mouse-centered zoom if available, otherwise use canvas center
        if hasattr(self, 'last_mouse_pos') and self.last_mouse_pos != (0, 0):
            self.zoom_at_cursor(self.last_mouse_pos[0], self.last_mouse_pos[1], zoom_in=False)
        else:
            # Fallback: zoom at canvas center
            canvas_center_x = self.winfo_width() // 2
            canvas_center_y = self.winfo_height() // 2
            self.zoom_at_cursor(canvas_center_x, canvas_center_y, zoom_in=False)
    
    def zoom_at_cursor(self, cursor_x: int, cursor_y: int, zoom_in: bool):
        """Zoom in or out while keeping the point under the cursor stationary"""
        if not self.current_image or not self.image_id:
            return
        
        # Calculate new zoom level
        max_zoom = self.image_manager.get_max_zoom() if hasattr(self.image_manager, 'get_max_zoom') else 10.0
        
        if zoom_in:
            new_zoom = min(max_zoom, self.zoom_level * 1.2)
        else:
            new_zoom = max(0.1, self.zoom_level / 1.2)
        
        # Don't zoom if we're already at the limit
        if abs(new_zoom - self.zoom_level) < 0.01:
            return
        
        # Get current image position and mouse position
        old_image_x, old_image_y = self.coords(self.image_id)
        
        # Convert cursor position to image coordinates (at current zoom)
        image_point = self.screen_to_image_coords(cursor_x, cursor_y)
        
        # Calculate where this image point will be at the new zoom level
        zoom_factor = new_zoom / self.zoom_level
        
        # The key insight: we want the image point under the cursor to stay under the cursor
        # So we calculate how much the image needs to move to keep that point stationary
        
        # Calculate the offset from image origin to cursor (in current display pixels)
        cursor_offset_x = cursor_x - old_image_x
        cursor_offset_y = cursor_y - old_image_y
        
        # After zoom, this offset will change by the zoom factor
        new_cursor_offset_x = cursor_offset_x * zoom_factor
        new_cursor_offset_y = cursor_offset_y * zoom_factor
        
        # Calculate where the image origin needs to be to keep cursor point stationary
        new_image_x = cursor_x - new_cursor_offset_x
        new_image_y = cursor_y - new_cursor_offset_y
        
        # Set new zoom level (this will update the image display)
        old_zoom = self.zoom_level
        self.set_zoom(new_zoom)
        
        # Only adjust position if zoom actually changed
        if self.zoom_level != old_zoom:
            # Apply Microsoft Paint style smart boundaries to zoom positioning
            bounded_x, bounded_y = self._apply_smart_pan_boundaries(new_image_x, new_image_y)
            
            # Move image to bounded position
            self.coords(self.image_id, bounded_x, bounded_y)
            
            # Stabilize coordinate system after zoom operation
            self._stabilize_coordinate_system()
            
            # Redraw overlays at new position
            self.redraw_all_overlays()
            # Redraw calibration overlays after zoom
            if self.is_calibrating:
                self.redraw_calibration_overlays()
    
    def zoom_fit(self):
        """Zoom to fit image in canvas"""
        if not self.current_image:
            return
        
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Calculate zoom to fit
        zoom_w = (canvas_width - 40) / self.current_image.width
        zoom_h = (canvas_height - 40) / self.current_image.height
        fit_zoom = min(zoom_w, zoom_h)
        
        self.set_zoom(fit_zoom)
    
    def set_zoom(self, zoom_level: float):
        """Set specific zoom level"""
        # ? IMPROVED: Use dynamic max zoom based on image size
        max_zoom = self.image_manager.get_max_zoom() if hasattr(self.image_manager, 'get_max_zoom') else 10.0
        self.zoom_level = max(0.1, min(max_zoom, zoom_level))
        self.update_image_display()
        
        # ? DEBUG: Add zoom debugging information
        if hasattr(self, 'image_manager') and self.image_manager.is_image_loaded:
            debug_info = self.image_manager.get_zoom_debug_info(self.zoom_level)
            if debug_info.get("is_limited", False):
                print(f"?? ZOOM DEBUG: Requested {debug_info['zoom_percentage']}, "
                      f"Actual {debug_info['actual_percentage']}, "
                      f"Limited by {debug_info['max_display_size']}")
        
        # Notify observers
        from core.app_state import app_state
        app_state.set_zoom_level(self.zoom_level)
    
    def screen_to_image_coords(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to image coordinates - delegates to CoordinateManager"""
        return self.coordinate_manager.screen_to_image(screen_x, screen_y)
    
    def image_to_screen_coords(self, image_x: float, image_y: float) -> Tuple[int, int]:
        """Convert image coordinates to screen coordinates - delegates to CoordinateManager"""
        return self.coordinate_manager.image_to_screen(image_x, image_y)
    
    def _update_actual_zoom_level(self):
        """Ensure actual_zoom_level is synchronized with current zoom state"""
        if self.current_image and self.image_manager:
            self.actual_zoom_level = self.image_manager.get_actual_zoom_factor(self.zoom_level)
    
    def _force_coordinate_system_refresh(self):
        print(f"  Coordinate system refreshed")
    
    def _apply_smart_pan_boundaries(self, intended_x: float, intended_y: float) -> Tuple[float, float]:
        """Apply unified pan boundaries for both image and canvas coordinate systems"""
        if not self.photo_image:
            return (intended_x, intended_y)
        
        # Get canvas and image dimensions
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        image_width = self.photo_image.width()
        image_height = self.photo_image.height()
        
        # ?? SOLUTION: Create unified panning limits
        # Instead of allowing image to go mostly off-screen, constrain both systems together
        
        # Calculate bounds that keep image and canvas coordinates synchronized
        if image_width <= canvas_width:
            # If image is smaller than canvas, center it and limit movement
            min_x = (canvas_width - image_width) // 2
            max_x = min_x
        else:
            # If image is larger than canvas, allow panning but keep edges visible
            margin = min(50, image_width // 10)  # 10% margin or 50px, whichever is smaller
            min_x = canvas_width - image_width - margin  # Left boundary
            max_x = margin  # Right boundary
        
        if image_height <= canvas_height:
            # If image is smaller than canvas, center it and limit movement
            min_y = (canvas_height - image_height) // 2
            max_y = min_y
        else:
            # If image is larger than canvas, allow panning but keep edges visible
            margin = min(50, image_height // 10)  # 10% margin or 50px, whichever is smaller
            min_y = canvas_height - image_height - margin  # Top boundary
            max_y = margin  # Bottom boundary
        
        # Apply unified boundaries
        bounded_x = max(min_x, min(max_x, intended_x))
        bounded_y = max(min_y, min(max_y, intended_y))
        
        # ?? CRITICAL: Update canvas scrollregion to match image boundaries
        # This ensures canvas and image coordinate systems stay synchronized
        image_left = bounded_x
        image_right = bounded_x + image_width
        image_top = bounded_y
        image_bottom = bounded_y + image_height
        
        # Set scrollregion to encompass the bounded image area
        # Add small padding to prevent edge issues
        padding = 10
        scroll_left = min(0, image_left - padding)
        scroll_top = min(0, image_top - padding)
        scroll_right = max(canvas_width, image_right + padding)
        scroll_bottom = max(canvas_height, image_bottom + padding)
        
        # Update scrollregion to match the actual bounded area
        self.configure(scrollregion=(scroll_left, scroll_top, scroll_right, scroll_bottom))
        
        return (bounded_x, bounded_y)
    
    def _stabilize_coordinate_system(self):
        """Stabilize the canvas coordinate system to prevent drift issues"""
        # Force tkinter to process all pending operations
        self.update_idletasks()
        
        # Refresh zoom level synchronization
        self._update_actual_zoom_level()
        
        # Update scroll region based on actual canvas content
        self.configure(scrollregion=self.bbox("all"))
        
        # Force another update to ensure stability
        self.update_idletasks()
    
    def _create_fixed_calibration_text(self, text: str):
        """Create calibration instruction text that stays fixed regardless of canvas state"""
        canvas_width = self.winfo_width()
        
        # Create text at a fixed position relative to canvas widget, not canvas content
        self.create_text(
            canvas_width // 2, 30,  # Fixed position
            text=text,
            fill="red", font=("Arial", 12, "bold"),
            tags="calibration_instruction"
        )
    
    def set_tool(self, tool_name: str):
        """Set current measurement tool - delegates to ToolHandler"""
        self.tool_handler.set_tool(tool_name)
    
    def start_calibration(self):
        """Start calibration mode - delegates to CalibrationHandler"""
        self.calibration_handler.start_calibration()
    
    def get_calibration_points(self) -> List[Tuple[float, float]]:
        """Get calibration points - delegates to CalibrationHandler"""
        return self.calibration_handler.get_calibration_points()
    
    def clear_calibration(self):
        """Clear calibration overlays - delegates to CalibrationHandler"""
        self.calibration_handler.clear_calibration()
    
    def redraw_calibration_overlays(self):
        """Redraw calibration overlays - delegates to CalibrationHandler"""
        self.calibration_handler.redraw_calibration_overlays()
    
    def simple_calibration_click(self, event):
        """Unified calibration click handler - delegates to CalibrationHandler"""
        self.calibration_handler.handle_click(event)
    
    def on_key_press(self, event):
        """Handle key press events"""
        if event.keysym == "Escape":
            self.temp_points.clear()
            self.clear_temp_overlays()
            if self.is_calibrating:
                self.calibration_handler.handle_escape()
                
                # Update status in main window
                if self.main_app and hasattr(self.main_app, 'status_label'):
                    self.main_app.status_label.config(text="Calibration cancelled")
    
    def handle_measurement_click(self, event):
        """Handle measurement tool click - delegates to ToolHandler"""
        self.tool_handler.handle_measurement_click(event)
    
    def handle_polygon_click(self, event):
        """Handle polygon area tool click - delegates to ToolHandler"""
        self.tool_handler.handle_polygon_click(event)
    
    def complete_measurement(self):
        """Complete current measurement"""
        try:
            measurement = None
            
            if self.current_tool == "distance" and len(self.temp_points) >= 2:
                measurement = self.measurement_engine.calculate_distance_measurement(
                    self.temp_points[0], self.temp_points[1]
                )
            elif self.current_tool == "radius" and len(self.temp_points) >= 3:
                measurement = self.measurement_engine.calculate_radius_measurement(
                    self.temp_points[0], self.temp_points[1], self.temp_points[2]
                )
            elif self.current_tool == "angle" and len(self.temp_points) >= 3:
                measurement = self.measurement_engine.calculate_angle_measurement(
                    self.temp_points[0], self.temp_points[1], self.temp_points[2]
                )
            elif self.current_tool == "two_line_angle" and len(self.temp_points) >= 4:
                measurement = self.measurement_engine.calculate_two_line_angle_measurement(
                    self.temp_points[0], self.temp_points[1], self.temp_points[2], self.temp_points[3]
                )
            # ? PHASE 3: Advanced measurement calculations
            elif self.current_tool == "polygon_area" and len(self.temp_points) >= 3:
                measurement = self.measurement_engine.calculate_polygon_area_measurement(
                    self.temp_points.copy()
                )
            elif self.current_tool == "coordinate" and len(self.temp_points) >= 1:
                coord_type = "single" if len(self.temp_points) == 1 else "difference"
                measurement = self.measurement_engine.calculate_coordinate_measurement(
                    self.temp_points.copy(), coord_type
                )
            elif self.current_tool == "point_to_line" and len(self.temp_points) >= 3:
                measurement = self.measurement_engine.calculate_point_to_line_measurement(
                    self.temp_points[0], self.temp_points[1], self.temp_points[2]
                )
            elif self.current_tool == "arc_length" and len(self.temp_points) >= 3:
                measurement = self.measurement_engine.calculate_arc_length_measurement(
                    self.temp_points[0], self.temp_points[1], self.temp_points[2]
                )
            else:
                return
            
            if measurement:
                # Add to application state
                from core.app_state import app_state
                app_state.add_measurement(measurement)
                
                # Draw measurement overlay
                self.draw_measurement_overlay(measurement)
                
                # Clear temporary elements
                self.temp_points.clear()
                self.clear_temp_overlays()
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Measurement Error", str(e))
            self.temp_points.clear()
            self.clear_temp_overlays()
    
    def draw_measurement_overlay(self, measurement: MeasurementBase):
        """Draw measurement overlay - delegates to OverlayManager"""
        self.overlay_manager.draw_measurement_overlay(measurement)
    
    def remove_measurement_overlay(self, measurement_id: str):
        """Remove measurement overlay - delegates to OverlayManager"""
        self.overlay_manager.remove_measurement_overlay(measurement_id)
    
    def clear_all_overlays(self):
        """Clear all measurement overlays - delegates to OverlayManager"""
        self.overlay_manager.clear_all_overlays()
        self.clear_temp_overlays()
    
    def clear_temp_overlays(self):
        """Clear temporary overlays"""
        self.delete("temp")
        self.temp_overlays.clear()
    
    def toggle_overlays_visibility(self):
        """Toggle visibility of all measurement overlays - delegates to OverlayManager"""
        return self.overlay_manager.toggle_visibility()
    
    def set_overlays_visibility(self, visible: bool):
        """Set overlay visibility state - delegates to OverlayManager"""
        self.overlay_manager.set_visibility(visible)
    
    def get_overlays_visibility(self) -> bool:
        """Get current overlay visibility state - delegates to OverlayManager"""
        return self.overlay_manager.get_visibility()
    
    def export_image(self, filename: str):
        """Export image with overlays rendered directly onto the image"""
        if not self.current_image or not self.current_image.original_image:
            raise ValueError("No image to export")
        
        from core.app_state import app_state
        
        # Create a copy of the original image to draw on
        export_image = self.current_image.original_image.copy()
        draw = ImageDraw.Draw(export_image)
        
        # Try to load a font for text rendering
        try:
            # Try to use a system font (adjust path as needed)
            font_size = max(12, min(24, int(export_image.width / 80)))  # Scale font with image size
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Fallback to default font
                font = ImageFont.load_default()
            except:
                font = None
        
        # Draw each measurement overlay on the original image
        for measurement in app_state.measurements:
            if not self.overlay_manager.get_visibility():  # Respect overlay visibility setting
                continue
                
            self._draw_measurement_on_image(draw, measurement, export_image.size, font)
        
        # Save the annotated image
        format_ext = filename.lower().split('.')[-1]
        if format_ext == 'jpg':
            format_ext = 'jpeg'
        
        # Save with high quality
        if format_ext.upper() == 'JPEG':
            export_image.save(filename, format='JPEG', quality=95, optimize=True)
        else:
            export_image.save(filename, format=format_ext.upper())
    
    def _draw_measurement_on_image(self, draw: ImageDraw.ImageDraw, measurement, image_size: tuple, font):
        """Draw a single measurement overlay on the PIL image"""
        # Scale line width based on image size
        line_width = max(2, int(min(image_size) / 500))
        
        if measurement.measurement_type == "distance":
            # Draw distance line
            x1, y1 = measurement.points[0]
            x2, y2 = measurement.points[1]
            
            draw.line([(x1, y1), (x2, y2)], fill="green", width=line_width)
            
            # Draw result text
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 - 15  # Offset text above line
            result_text = self.measurement_engine.format_measurement_result(measurement)
            
            if font:
                # Get text size for better positioning
                bbox = draw.textbbox((0, 0), result_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Draw text background for better visibility
                draw.rectangle([
                    mid_x - text_width//2 - 2, mid_y - text_height//2 - 2,
                    mid_x + text_width//2 + 2, mid_y + text_height//2 + 2
                ], fill="white", outline="green")
                
                draw.text((mid_x - text_width//2, mid_y - text_height//2), result_text, 
                         fill="green", font=font)
            else:
                draw.text((mid_x, mid_y), result_text, fill="green")
        
        elif measurement.measurement_type == "radius":
            # Draw radius circle
            if hasattr(measurement, 'center_point') and measurement.center_point:
                center_x, center_y = measurement.center_point
                
                # Calculate radius in pixels
                if self.measurement_engine.calibration:
                    radius_pixels = measurement.result / self.measurement_engine.calibration.scale_factor
                else:
                    radius_pixels = measurement.result
                
                # Draw circle
                draw.ellipse([
                    center_x - radius_pixels, center_y - radius_pixels,
                    center_x + radius_pixels, center_y + radius_pixels
                ], outline="blue", width=line_width)
                
                # Draw center point
                point_size = line_width * 2
                draw.ellipse([
                    center_x - point_size, center_y - point_size,
                    center_x + point_size, center_y + point_size
                ], fill="blue")
                
                # Draw result text
                result_text = self.measurement_engine.format_measurement_result(measurement)
                text_y = center_y - radius_pixels - 20
                
                if font:
                    bbox = draw.textbbox((0, 0), result_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        center_x - text_width//2 - 2, text_y - text_height//2 - 2,
                        center_x + text_width//2 + 2, text_y + text_height//2 + 2
                    ], fill="white", outline="blue")
                    
                    draw.text((center_x - text_width//2, text_y - text_height//2), result_text, 
                             fill="blue", font=font)
                else:
                    draw.text((center_x, text_y), result_text, fill="blue")
        
        elif measurement.measurement_type == "angle":
            # Draw angle lines
            if len(measurement.points) >= 3:
                vertex_x, vertex_y = measurement.points[1]  # Vertex is middle point
                p1_x, p1_y = measurement.points[0]
                p3_x, p3_y = measurement.points[2]
                
                # Draw lines from vertex
                draw.line([(vertex_x, vertex_y), (p1_x, p1_y)], fill="orange", width=line_width)
                draw.line([(vertex_x, vertex_y), (p3_x, p3_y)], fill="orange", width=line_width)
                
                # Draw result text near vertex
                result_text = self.measurement_engine.format_measurement_result(measurement)
                text_x = vertex_x + 20
                text_y = vertex_y - 20
                
                if font:
                    bbox = draw.textbbox((0, 0), result_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        text_x - 2, text_y - 2,
                        text_x + text_width + 2, text_y + text_height + 2
                    ], fill="white", outline="orange")
                    
                    draw.text((text_x, text_y), result_text, fill="orange", font=font)
                else:
                    draw.text((text_x, text_y), result_text, fill="orange")
        
        elif measurement.measurement_type == "two_line_angle":
            # Draw two lines
            if len(measurement.points) >= 4:
                # First line
                line1_p1 = measurement.points[0]
                line1_p2 = measurement.points[1]
                
                # Second line
                line2_p1 = measurement.points[2]
                line2_p2 = measurement.points[3]
                
                # Draw both lines
                draw.line([line1_p1, line1_p2], fill="purple", width=line_width)
                draw.line([line2_p1, line2_p2], fill="purple", width=line_width)
                
                # Draw result text in center
                center_x = (line1_p1[0] + line1_p2[0] + line2_p1[0] + line2_p2[0]) / 4
                center_y = (line1_p1[1] + line1_p2[1] + line2_p1[1] + line2_p2[1]) / 4 - 15
                
                result_text = self.measurement_engine.format_measurement_result(measurement)
                
                if font:
                    bbox = draw.textbbox((0, 0), result_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        center_x - text_width//2 - 2, center_y - text_height//2 - 2,
                        center_x + text_width//2 + 2, center_y + text_height//2 + 2
                    ], fill="white", outline="purple")
                    
                    draw.text((center_x - text_width//2, center_y - text_height//2), result_text, 
                             fill="purple", font=font)
                else:
                    draw.text((center_x, center_y), result_text, fill="purple")
        
        # ? PHASE 3: Advanced measurement export rendering
        elif measurement.measurement_type == "polygon_area":
            # Draw polygon area
            if len(measurement.points) >= 3:
                # Draw polygon outline
                polygon_coords = [(p[0], p[1]) for p in measurement.points]
                
                # Draw polygon lines
                for i in range(len(polygon_coords)):
                    next_i = (i + 1) % len(polygon_coords)
                    draw.line([polygon_coords[i], polygon_coords[next_i]], 
                             fill="cyan", width=line_width)
                
                # Draw result text at centroid
                center_x = sum(p[0] for p in polygon_coords) / len(polygon_coords)
                center_y = sum(p[1] for p in polygon_coords) / len(polygon_coords)
                
                result_text = self.measurement_engine.format_measurement_result(measurement)
                
                if font:
                    bbox = draw.textbbox((0, 0), result_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        center_x - text_width//2 - 2, center_y - text_height//2 - 2,
                        center_x + text_width//2 + 2, center_y + text_height//2 + 2
                    ], fill="white", outline="cyan")
                    
                    draw.text((center_x - text_width//2, center_y - text_height//2), result_text, 
                             fill="cyan", font=font)
                else:
                    draw.text((center_x, center_y), result_text, fill="cyan")
        
        elif measurement.measurement_type == "coordinate":
            # Draw coordinate points
            for i, point in enumerate(measurement.points):
                x, y = point
                point_size = line_width * 3
                
                # Draw point marker
                draw.ellipse([x - point_size, y - point_size, x + point_size, y + point_size], 
                           fill="yellow", outline="black", width=1)
                
                # Draw coordinate text
                if measurement.coordinate_type == "single":
                    coord_text = f"({x:.1f}, {y:.1f})"
                elif measurement.coordinate_type == "difference" and i == 1:
                    dx = measurement.points[1][0] - measurement.points[0][0]
                    dy = measurement.points[1][1] - measurement.points[0][1]
                    coord_text = f"?X: {dx:.1f}, ?Y: {dy:.1f}"
                else:
                    coord_text = f"P{i+1}"
                
                text_x = x + 15
                text_y = y - 15
                
                if font:
                    bbox = draw.textbbox((0, 0), coord_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        text_x - 2, text_y - 2,
                        text_x + text_width + 2, text_y + text_height + 2
                    ], fill="white", outline="yellow")
                    
                    draw.text((text_x, text_y), coord_text, fill="black", font=font)
                else:
                    draw.text((text_x, text_y), coord_text, fill="black")
        
        elif measurement.measurement_type == "point_to_line":
            # Draw point-to-line distance
            if len(measurement.points) >= 3:
                point = measurement.points[0]
                line_start = measurement.points[1]
                line_end = measurement.points[2]
                
                # ? FIXED: Calculate the actual closest point on the line
                from utils.math_utils import find_closest_point_on_line
                closest_point = find_closest_point_on_line(point, line_start, line_end)
                
                # Draw the line
                draw.line([line_start, line_end], fill="red", width=line_width)
                
                # Draw the point
                point_size = line_width * 2
                draw.ellipse([
                    point[0] - point_size, point[1] - point_size,
                    point[0] + point_size, point[1] + point_size
                ], fill="red", outline="white", width=1)
                
                # ? FIXED: Draw the actual perpendicular line to the closest point
                draw.line([point, closest_point], fill="red", width=line_width)
                
                # Draw a small marker at the closest point on the line
                marker_size = line_width
                draw.ellipse([
                    closest_point[0] - marker_size, closest_point[1] - marker_size,
                    closest_point[0] + marker_size, closest_point[1] + marker_size
                ], fill="yellow", outline="red", width=1)
                
                # Draw result text
                result_text = self.measurement_engine.format_measurement_result(measurement)
                text_x = point[0] + 20
                text_y = point[1] - 20
                
                if font:
                    bbox = draw.textbbox((0, 0), result_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        text_x - 2, text_y - 2,
                        text_x + text_width + 2, text_y + text_height + 2
                    ], fill="white", outline="red")
                    
                    draw.text((text_x, text_y), result_text, fill="red", font=font)
                else:
                    draw.text((text_x, text_y), result_text, fill="red")
        
        elif measurement.measurement_type == "arc_length":
            # Draw arc length measurement
            if len(measurement.points) >= 3:
                # Draw points along the arc
                for point in measurement.points:
                    point_size = line_width * 2
                    draw.ellipse([
                        point[0] - point_size, point[1] - point_size,
                        point[0] + point_size, point[1] + point_size
                    ], fill="magenta", outline="white", width=1)
                
                # Draw arc approximation (connecting lines)
                for i in range(len(measurement.points) - 1):
                    draw.line([measurement.points[i], measurement.points[i + 1]], 
                             fill="magenta", width=line_width)
                
                # Draw result text
                result_text = self.measurement_engine.format_measurement_result(measurement)
                center_x = sum(p[0] for p in measurement.points) / len(measurement.points)
                center_y = sum(p[1] for p in measurement.points) / len(measurement.points) - 20
                
                if font:
                    bbox = draw.textbbox((0, 0), result_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.rectangle([
                        center_x - text_width//2 - 2, center_y - text_height//2 - 2,
                        center_x + text_width//2 + 2, center_y + text_height//2 + 2
                    ], fill="white", outline="magenta")
                    
                    draw.text((center_x - text_width//2, center_y - text_height//2), result_text, 
                             fill="magenta", font=font)
                else:
                    draw.text((center_x, center_y), result_text, fill="magenta")

    def _try_show_calibration_dialog(self, pixel_distance: float):
        """Fallback method to show calibration dialog"""
        try:
            # Try to find the main window through widget hierarchy
            widget = self.master
            while widget and not hasattr(widget, 'show_calibration_dialog'):
                widget = widget.master
            
            if widget and hasattr(widget, 'show_calibration_dialog'):
                widget.show_calibration_dialog(pixel_distance)
            else:
                from tkinter import messagebox
                messagebox.showerror("Error", "Could not open calibration dialog")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Calibration dialog error: {e}")
    
    def set_main_app_reference(self, main_app):
        """Set reference to main application for callbacks"""
        self.main_app = main_app

    def __del__(self):
        """Cleanup when canvas is destroyed"""
        if self.photo_image:
            del self.photo_image
