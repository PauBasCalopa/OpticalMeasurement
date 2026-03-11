"""
Image Canvas Widget

Custom tkinter Canvas for image display and measurement interactions
"""

import tkinter as tk
from tkinter import Canvas
from typing import Optional, List, Tuple
from PIL import ImageTk
import math

from models.image_data import ImageData
from core.image_manager import ImageManager
from core.measurement_engine import MeasurementEngine
from models.measurement_data import MeasurementBase

class ImageCanvas(Canvas):
    """Custom canvas for interactive image display and measurements"""
    
    def __init__(self, parent, image_manager: ImageManager, measurement_engine: MeasurementEngine, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.image_manager = image_manager
        self.measurement_engine = measurement_engine
        
        # Reference to main application window for dialog callbacks
        self.main_app = None  # Will be set by main window
        
        # Canvas state
        self.current_image: Optional[ImageData] = None
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.image_id: Optional[int] = None
        
        # Interaction state
        self.current_tool: str = "pan"
        self.temp_points: List[Tuple[float, float]] = []
        self.calibration_points: List[Tuple[float, float]] = []
        self.is_calibrating: bool = False
        
        # Display state
        self.zoom_level: float = 1.0  # Requested zoom level
        self.actual_zoom_level: float = 1.0  # Actual zoom level (after MAX_DISPLAY_SIZE limiting)
        self.pan_start: Optional[Tuple[int, int]] = None
        self.right_pan_start: Optional[Tuple[int, int]] = None  # ? NEW: Right-click pan state
        
        # Overlays
        self.measurement_overlays = {}  # measurement_id -> canvas_items
        self.temp_overlays = []  # temporary drawing items
        self.overlays_visible = True  # ? NEW: Track overlay visibility state
        
        # Bind events
        self.bind_events()
    
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
            
            # Update scroll region
            self.configure(scrollregion=self.bbox("all"))
    
    def redraw_all_overlays(self):
        """Redraw all measurement overlays at current zoom/pan position"""
        # Only redraw if overlays should be visible
        if not self.overlays_visible:
            return
            
        # Simple approach: just redraw all overlays using stored image coordinates
        from core.app_state import app_state
        
        # Clear all existing overlays
        for measurement_id in list(self.measurement_overlays.keys()):
            self.remove_measurement_overlay(measurement_id)
        
        # Redraw each measurement
        for measurement in app_state.measurements:
            self.draw_measurement_overlay(measurement)
    
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
        
        # Move image to center
        if self.image_id:
            self.coords(self.image_id, center_x, center_y)
        
        # ? FIX: Don't update overlays here - they should track automatically
        
        # Update scroll region
        self.configure(scrollregion=self.bbox("all"))
    
    def zoom_in(self):
        """Zoom in"""
        new_zoom = min(10.0, self.zoom_level * 1.2)
        self.set_zoom(new_zoom)
    
    def zoom_out(self):
        """Zoom out"""
        new_zoom = max(0.1, self.zoom_level / 1.2)
        self.set_zoom(new_zoom)
    
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
        self.zoom_level = max(0.1, min(10.0, zoom_level))
        self.update_image_display()
        
        # Notify observers
        from core.app_state import app_state
        app_state.set_zoom_level(self.zoom_level)
    
    def screen_to_image_coords(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to image coordinates"""
        if not self.current_image or not self.image_id:
            return (screen_x, screen_y)
        
        # Get current image position on canvas
        image_x, image_y = self.coords(self.image_id)
        
        # ? SIMPLE FIX: Basic coordinate conversion
        # Convert screen click to original image coordinates
        rel_x = (screen_x - image_x) / self.actual_zoom_level
        rel_y = (screen_y - image_y) / self.actual_zoom_level
        
        return (rel_x, rel_y)
    
    def image_to_screen_coords(self, image_x: float, image_y: float) -> Tuple[int, int]:
        """Convert image coordinates to screen coordinates"""
        if not self.current_image or not self.image_id:
            return (int(image_x), int(image_y))
        
        # Get current image position on canvas
        canvas_image_x, canvas_image_y = self.coords(self.image_id)
        
        # ? SIMPLE FIX: Basic coordinate conversion
        # Convert stored image coordinates to current screen position
        screen_x = int(canvas_image_x + image_x * self.actual_zoom_level)
        screen_y = int(canvas_image_y + image_y * self.actual_zoom_level)
        
        return (screen_x, screen_y)
    
    def set_tool(self, tool_name: str):
        """Set current measurement tool"""
        self.current_tool = tool_name
        self.temp_points.clear()
        self.clear_temp_overlays()
        
        # Update cursor
        if tool_name == "pan":
            self.config(cursor="hand2")
        else:
            self.config(cursor="crosshair")
    
    def start_calibration(self):
        """Start calibration mode"""
        self.is_calibrating = True
        self.calibration_points.clear()
        self.temp_points.clear()
        self.clear_temp_overlays()
        
        # Clear any existing calibration overlays
        self.delete("calibration")
        
        # Set crosshair cursor
        self.config(cursor="crosshair")
        
        # Add visual indication that we're in calibration mode
        # Draw instruction text on canvas
        self.create_text(
            self.winfo_width() // 2, 30,
            text="CALIBRATION MODE: Click two points",
            fill="red", font=("Arial", 12, "bold"),
            tags="calibration_instruction"
        )
    
    def get_calibration_points(self) -> List[Tuple[float, float]]:
        """Get calibration points"""
        return self.calibration_points.copy()
    
    def clear_calibration(self):
        """Clear calibration overlays"""
        self.delete("calibration")
        self.delete("calibration_instruction")
        self.calibration_points.clear()
        self.is_calibrating = False
        self.config(cursor="")  # Reset cursor
    
    def on_left_click(self, event):
        """Handle left mouse button click (tools and measurements)"""
        if self.is_calibrating:
            self.handle_calibration_click(event)
        elif self.current_tool == "pan":
            # Left-click pan (traditional behavior, still available when pan tool is active)
            self.pan_start = (event.x, event.y)
        elif self.current_tool in ["distance", "radius", "angle", "two_line_angle"]:
            self.handle_measurement_click(event)
    
    def on_left_drag(self, event):
        """Handle left mouse button drag"""
        if self.current_tool == "pan" and self.pan_start:
            # Traditional pan with left button (when pan tool is active)
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            
            if self.image_id:
                self.move(self.image_id, dx, dy)
            
            self.pan_start = (event.x, event.y)
            self.configure(scrollregion=self.bbox("all"))
    
    def on_left_release(self, event):
        """Handle left mouse button release"""
        if self.current_tool == "pan" and self.pan_start:
            self.pan_start = None
            self.redraw_all_overlays()
    
    def on_right_click(self, event):
        """Handle right mouse button click (always pan, regardless of tool)"""
        self.right_pan_start = (event.x, event.y)
        # ? NEW: Change cursor to indicate panning mode
        self.config(cursor="fleur")  # Four-direction arrow cursor
    
    def on_right_drag(self, event):
        """Handle right mouse button drag (pan)"""
        if self.right_pan_start:
            dx = event.x - self.right_pan_start[0]
            dy = event.y - self.right_pan_start[1]
            
            if self.image_id:
                self.move(self.image_id, dx, dy)
            
            self.right_pan_start = (event.x, event.y)
            self.configure(scrollregion=self.bbox("all"))
    
    def on_right_release(self, event):
        """Handle right mouse button release"""
        if self.right_pan_start:
            self.right_pan_start = None
            # ? NEW: Restore cursor to tool-appropriate cursor
            self.set_tool(self.current_tool)  # This will set the proper cursor
            # Update overlays after pan is complete
            self.redraw_all_overlays()
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        # Update cursor position in main window
        image_coords = self.screen_to_image_coords(event.x, event.y)
        if hasattr(self.master.master, 'update_cursor_position'):
            self.master.master.update_cursor_position(int(image_coords[0]), int(image_coords[1]))
    
    def on_mousewheel(self, event):
        """Handle mouse wheel zoom"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_key_press(self, event):
        """Handle key press events"""
        if event.keysym == "Escape":
            self.temp_points.clear()
            self.clear_temp_overlays()
            if self.is_calibrating:
                self.is_calibrating = False
                self.calibration_points.clear()
                self.delete("calibration")
                self.delete("calibration_instruction")
                self.config(cursor="")
                
                # Update status in main window
                if self.main_app and hasattr(self.main_app, 'status_label'):
                    self.main_app.status_label.config(text="Calibration cancelled")
    
    def handle_calibration_click(self, event):
        """Handle calibration click"""
        # Convert to image coordinates
        image_coords = self.screen_to_image_coords(event.x, event.y)
        self.calibration_points.append(image_coords)
        
        # Draw calibration point
        screen_coords = self.image_to_screen_coords(*image_coords)
        point_id = self.create_oval(
            screen_coords[0] - 5, screen_coords[1] - 5,
            screen_coords[0] + 5, screen_coords[1] + 5,
            fill="red", outline="white", width=2, tags="calibration"
        )
        
        # Update instruction text
        if len(self.calibration_points) == 1:
            self.delete("calibration_instruction")
            self.create_text(
                self.winfo_width() // 2, 30,
                text="CALIBRATION: Click second point",
                fill="red", font=("Arial", 12, "bold"),
                tags="calibration_instruction"
            )
        
        if len(self.calibration_points) == 2:
            # Remove instruction text
            self.delete("calibration_instruction")
            
            # Draw calibration line
            screen1 = self.image_to_screen_coords(*self.calibration_points[0])
            screen2 = self.image_to_screen_coords(*self.calibration_points[1])
            
            line_id = self.create_line(
                screen1[0], screen1[1], screen2[0], screen2[1],
                fill="red", width=3, tags="calibration"
            )
            
            # Calculate pixel distance and show dialog
            from utils.math_utils import calculate_distance
            pixel_distance = calculate_distance(self.calibration_points[0], self.calibration_points[1])
            
            self.is_calibrating = False
            self.config(cursor="")  # Reset cursor
            
            # Trigger calibration dialog
            if self.main_app and hasattr(self.main_app, 'show_calibration_dialog'):
                self.main_app.show_calibration_dialog(pixel_distance)
            else:
                # Fallback - try to find main window
                self._try_show_calibration_dialog(pixel_distance)
    
    def handle_measurement_click(self, event):
        """Handle measurement tool click"""
        # Convert to image coordinates
        image_coords = self.screen_to_image_coords(event.x, event.y)
        self.temp_points.append(image_coords)
        
        # Draw temporary point
        screen_coords = self.image_to_screen_coords(*image_coords)
        point_id = self.create_oval(
            screen_coords[0] - 2, screen_coords[1] - 2,
            screen_coords[0] + 2, screen_coords[1] + 2,
            fill="blue", outline="blue", tags="temp"
        )
        self.temp_overlays.append(point_id)
        
        # Check if measurement is complete
        points_needed = {
            "distance": 2,
            "radius": 3,
            "angle": 3,
            "two_line_angle": 4
        }
        
        if len(self.temp_points) >= points_needed.get(self.current_tool, 2):
            self.complete_measurement()
    
    def complete_measurement(self):
        """Complete current measurement"""
        try:
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
            else:
                return
            
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
        """Draw measurement overlay on canvas"""
        # Don't draw if overlays are hidden
        if not self.overlays_visible:
            return
            
        overlay_items = []
        
        if measurement.measurement_type == "distance":
            # Draw line between points
            screen1 = self.image_to_screen_coords(*measurement.points[0])
            screen2 = self.image_to_screen_coords(*measurement.points[1])
            
            line_id = self.create_line(
                screen1[0], screen1[1], screen2[0], screen2[1],
                fill="green", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line_id)
            
            # Draw result text
            mid_x = (screen1[0] + screen2[0]) / 2
            mid_y = (screen1[1] + screen2[1]) / 2
            result_text = self.measurement_engine.format_measurement_result(measurement)
            
            text_id = self.create_text(
                mid_x, mid_y - 10, text=result_text,
                fill="green", font=("Arial", 8), tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        elif measurement.measurement_type == "radius":
            # Draw circle
            if hasattr(measurement, 'center_point') and measurement.center_point:
                center_screen = self.image_to_screen_coords(*measurement.center_point)
                radius_pixels = measurement.result / self.measurement_engine.calibration.scale_factor if self.measurement_engine.calibration else measurement.result
                # ? FIX: Use actual zoom factor for circle scaling
                radius_screen = radius_pixels * self.actual_zoom_level
                
                circle_id = self.create_oval(
                    center_screen[0] - radius_screen, center_screen[1] - radius_screen,
                    center_screen[0] + radius_screen, center_screen[1] + radius_screen,
                    outline="blue", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(circle_id)
                
                # Draw center point
                center_id = self.create_oval(
                    center_screen[0] - 2, center_screen[1] - 2,
                    center_screen[0] + 2, center_screen[1] + 2,
                    fill="blue", outline="blue", tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(center_id)
                
                # Draw result text
                result_text = self.measurement_engine.format_measurement_result(measurement)
                text_id = self.create_text(
                    center_screen[0], center_screen[1] - radius_screen - 15,
                    text=result_text, fill="blue", font=("Arial", 8),
                    tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(text_id)
        
        elif measurement.measurement_type == "angle":
            # Draw angle arc between three points
            if len(measurement.points) >= 3:
                vertex_screen = self.image_to_screen_coords(*measurement.points[1])
                p1_screen = self.image_to_screen_coords(*measurement.points[0])
                p3_screen = self.image_to_screen_coords(*measurement.points[2])
                
                # Draw lines from vertex
                line1_id = self.create_line(
                    vertex_screen[0], vertex_screen[1], p1_screen[0], p1_screen[1],
                    fill="orange", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(line1_id)
                
                line2_id = self.create_line(
                    vertex_screen[0], vertex_screen[1], p3_screen[0], p3_screen[1],
                    fill="orange", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(line2_id)
                
                # Draw result text near vertex
                result_text = self.measurement_engine.format_measurement_result(measurement)
                text_id = self.create_text(
                    vertex_screen[0] + 20, vertex_screen[1] - 20,
                    text=result_text, fill="orange", font=("Arial", 8),
                    tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(text_id)
        
        elif measurement.measurement_type == "two_line_angle":
            # Draw two lines and angle between them
            if len(measurement.points) >= 4:
                # First line
                line1_p1_screen = self.image_to_screen_coords(*measurement.points[0])
                line1_p2_screen = self.image_to_screen_coords(*measurement.points[1])
                
                # Second line  
                line2_p1_screen = self.image_to_screen_coords(*measurement.points[2])
                line2_p2_screen = self.image_to_screen_coords(*measurement.points[3])
                
                # Draw first line
                line1_id = self.create_line(
                    line1_p1_screen[0], line1_p1_screen[1], line1_p2_screen[0], line1_p2_screen[1],
                    fill="purple", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(line1_id)
                
                # Draw second line
                line2_id = self.create_line(
                    line2_p1_screen[0], line2_p1_screen[1], line2_p2_screen[0], line2_p2_screen[1],
                    fill="purple", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(line2_id)
                
                # Draw result text in center of the two lines
                center_x = (line1_p1_screen[0] + line1_p2_screen[0] + line2_p1_screen[0] + line2_p2_screen[0]) / 4
                center_y = (line1_p1_screen[1] + line1_p2_screen[1] + line2_p1_screen[1] + line2_p2_screen[1]) / 4
                
                result_text = self.measurement_engine.format_measurement_result(measurement)
                text_id = self.create_text(
                    center_x, center_y - 15,
                    text=result_text, fill="purple", font=("Arial", 8),
                    tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(text_id)
        
        # Store overlay items
        self.measurement_overlays[measurement.id] = overlay_items
    
    def remove_measurement_overlay(self, measurement_id: str):
        """Remove measurement overlay"""
        if measurement_id in self.measurement_overlays:
            for item_id in self.measurement_overlays[measurement_id]:
                self.delete(item_id)
            del self.measurement_overlays[measurement_id]
    
    def clear_all_overlays(self):
        """Clear all measurement overlays"""
        for measurement_id in list(self.measurement_overlays.keys()):
            self.remove_measurement_overlay(measurement_id)
        self.clear_temp_overlays()
    
    def clear_temp_overlays(self):
        """Clear temporary overlays"""
        self.delete("temp")
        self.temp_overlays.clear()
    
    def toggle_overlays_visibility(self):
        """Toggle visibility of all measurement overlays"""
        self.overlays_visible = not self.overlays_visible
        
        if self.overlays_visible:
            # Show overlays - make all overlay items visible again
            for measurement_id in self.measurement_overlays:
                for item_id in self.measurement_overlays[measurement_id]:
                    try:
                        self.itemconfig(item_id, state="normal")
                    except:
                        pass  # Item might have been deleted
            # Also redraw to ensure everything is current
            self.redraw_all_overlays()
        else:
            # Hide overlays - hide all overlay items
            for measurement_id in self.measurement_overlays:
                for item_id in self.measurement_overlays[measurement_id]:
                    try:
                        self.itemconfig(item_id, state="hidden")
                    except:
                        pass  # Item might have been deleted
        
        return self.overlays_visible
    
    def set_overlays_visibility(self, visible: bool):
        """Set overlay visibility state"""
        if self.overlays_visible != visible:
            self.toggle_overlays_visibility()
    
    def get_overlays_visibility(self) -> bool:
        """Get current overlay visibility state"""
        return self.overlays_visible
        """Export image with overlays"""
        if not self.current_image or not self.current_image.original_image:
            raise ValueError("No image to export")
        
        # For now, just save the original image
        # TODO: Implement overlay rendering
        format_ext = filename.lower().split('.')[-1]
        if format_ext == 'jpg':
            format_ext = 'jpeg'
        
        self.current_image.original_image.save(filename, format=format_ext.upper())

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