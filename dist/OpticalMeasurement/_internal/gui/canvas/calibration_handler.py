"""
Calibration Handler

Handles all calibration-related functionality for the canvas widget.
Provides specialized logic for calibration mode and calibration overlays.
"""

from typing import List, Tuple

class CalibrationHandler:
    """Handles calibration mode and calibration overlays"""
    
    def __init__(self, canvas):
        """Initialize calibration handler with canvas reference"""
        self.canvas = canvas
        self.calibration_points = []  # Image coordinates
        self.calibration_screen_points = []  # Screen coordinates for drawing
    
    def start_calibration(self):
        """Start calibration mode"""
        self.canvas.is_calibrating = True
        self.calibration_points.clear()
        self.calibration_screen_points.clear()
        self.canvas.tool_handler.cancel()
        
        # Clear any existing calibration overlays
        self.canvas.delete("calibration")
        self.canvas.delete("calibration_instruction")
        
        # Set crosshair cursor
        self.canvas.config(cursor="crosshair")
        
        # Create instruction text
        self._create_instruction_text("CALIBRATION MODE: Click two points")
    
    def handle_click(self, event):
        """Handle calibration click with improved overlay positioning"""
        image_coords = self.canvas.screen_to_image_coords(event.x, event.y)
        self.calibration_points.append(image_coords)
        
        # Store the actual click location for consistent overlay drawing
        # But use image coordinate system for calculations
        self.calibration_screen_points.append((event.x, event.y))
        
        # Draw point at exact screen click location
        point_id = self.canvas.create_oval(
            event.x - 5, event.y - 5,
            event.x + 5, event.y + 5,
            fill="red", outline="white", width=2, tags="calibration"
        )
        
        # Update UI based on progress
        if len(self.calibration_points) == 1:
            self.canvas.delete("calibration_instruction")
            self._create_instruction_text("CALIBRATION: Click second point")
        elif len(self.calibration_points) == 2:
            self._complete_calibration()
    
    def _complete_calibration(self):
        """Complete the calibration process with proper coordinate handling"""
        self.canvas.delete("calibration_instruction")
        
        # Use image coordinates converted to current screen position for line drawing
        # This ensures the line stays properly positioned even after pan/zoom operations
        screen_pt1 = self.canvas.image_to_screen_coords(*self.calibration_points[0])
        screen_pt2 = self.canvas.image_to_screen_coords(*self.calibration_points[1])
        
        line_id = self.canvas.create_line(
            screen_pt1[0], screen_pt1[1],
            screen_pt2[0], screen_pt2[1],
            fill="red", width=3, tags="calibration"
        )
        
        # Calculate pixel distance using image coordinates (not screen coordinates)
        from utils.math_utils import calculate_distance
        pixel_distance = calculate_distance(self.calibration_points[0], self.calibration_points[1])
        
        # Exit calibration mode
        self.canvas.is_calibrating = False
        self.canvas.config(cursor="")
        
        # Show calibration dialog
        self._show_calibration_dialog(pixel_distance)
    
    def _create_instruction_text(self, text: str):
        """Create calibration instruction text positioned relative to image boundaries"""
        if not self.canvas.current_image or not self.canvas.image_id:
            # Fallback to canvas center if no image
            canvas_width = self.canvas.winfo_width()
            text_x = canvas_width // 2
            text_y = 30
        else:
            # Position text relative to actual image boundaries
            from services.coordinate_service import CoordinateService
            left, top, right, bottom = CoordinateService.get_image_bounds_on_screen(self.canvas.view_state)
            image_left, image_top, image_right, image_bottom = int(left), int(top), int(right), int(bottom)
            
            # Center text horizontally within the image bounds
            text_x = (image_left + image_right) // 2
            
            # Position text above the image, or inside if image is at top edge
            if image_top > 40:
                text_y = image_top - 20  # Above image
            else:
                text_y = image_top + 30  # Inside image, near top
        
        self.canvas.create_text(
            text_x, text_y,
            text=text,
            fill="red", font=("Arial", 12, "bold"),
            tags="calibration_instruction"
        )
    
    def _show_calibration_dialog(self, pixel_distance: float):
        """Show calibration dialog"""
        if self.canvas.main_app and hasattr(self.canvas.main_app, 'show_calibration_dialog'):
            self.canvas.main_app.show_calibration_dialog(pixel_distance)
        else:
            self._try_show_calibration_dialog(pixel_distance)
    
    def _try_show_calibration_dialog(self, pixel_distance: float):
        """Fallback method to show calibration dialog"""
        try:
            # Try to find the main window through widget hierarchy
            widget = self.canvas.master
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
    
    def clear_calibration(self):
        """Clear calibration overlays and exit calibration mode"""
        self.canvas.delete("calibration")
        self.canvas.delete("calibration_instruction")
        self.calibration_points.clear()
        self.calibration_screen_points.clear()
        self.canvas.is_calibrating = False
        self.canvas.config(cursor="")
    
    def redraw_calibration_overlays(self):
        """Redraw calibration overlays at current zoom/pan position"""
        if not self.canvas.is_calibrating:
            return
        
        # Clear existing calibration overlays
        self.canvas.delete("calibration")
        self.canvas.delete("calibration_instruction")
        
        # Redraw calibration points
        for i, point in enumerate(self.calibration_points):
            screen_coords = self.canvas.image_to_screen_coords(*point)
            
            self.canvas.create_oval(
                screen_coords[0] - 5, screen_coords[1] - 5,
                screen_coords[0] + 5, screen_coords[1] + 5,
                fill="red", outline="white", width=2, tags="calibration"
            )
        
        # Update instruction text based on current state
        if len(self.calibration_points) == 0:
            self._create_instruction_text("CALIBRATION MODE: Click two points")
        elif len(self.calibration_points) == 1:
            self._create_instruction_text("CALIBRATION: Click second point")
        elif len(self.calibration_points) == 2:
            # Draw calibration line between points
            screen1 = self.canvas.image_to_screen_coords(*self.calibration_points[0])
            screen2 = self.canvas.image_to_screen_coords(*self.calibration_points[1])
            
            self.canvas.create_line(
                screen1[0], screen1[1], screen2[0], screen2[1],
                fill="red", width=3, tags="calibration"
            )
    
    def get_calibration_points(self) -> List[Tuple[float, float]]:
        """Get calibration points in image coordinates"""
        return self.calibration_points.copy()
    
    def handle_escape(self):
        """Handle escape key during calibration"""
        self.clear_calibration()
        
        # Update status in main window
        if self.canvas.main_app and hasattr(self.canvas.main_app, 'status_label'):
            self.canvas.main_app.status_label.config(text="Calibration cancelled")