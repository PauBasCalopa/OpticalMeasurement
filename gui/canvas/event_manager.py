"""
Event Manager

Centralizes all mouse and keyboard event handling for the canvas widget.
Provides clean separation between event binding and event handling logic.
"""

import tkinter as tk
from typing import Optional

class EventManager:
    """Centralizes all mouse and keyboard event handling"""
    
    def __init__(self, canvas):
        """Initialize event manager with canvas reference"""
        self.canvas = canvas
        self.pan_start: Optional[tuple] = None
        self.right_pan_start: Optional[tuple] = None
        
    def bind_all_events(self):
        """Bind all mouse and keyboard events to their handlers"""
        # Mouse events
        self.canvas.bind("<Button-1>", self.handle_left_click)
        self.canvas.bind("<B1-Motion>", self.handle_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_left_release)
        
        self.canvas.bind("<Button-3>", self.handle_right_click)
        self.canvas.bind("<B3-Motion>", self.handle_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.handle_right_release)
        
        self.canvas.bind("<Motion>", self.handle_mouse_move)
        self.canvas.bind("<MouseWheel>", self.handle_mousewheel)
        
        # Keyboard events
        self.canvas.focus_set()  # Make canvas focusable
        self.canvas.bind("<Key>", self.handle_key_press)
    
    def handle_left_click(self, event):
        """Central left click dispatcher"""
        if self.canvas.is_calibrating:
            self.canvas.simple_calibration_click(event)
        elif self.canvas.current_tool == "pan":
            self.pan_start = (event.x, event.y)
        elif self.canvas.current_tool == "polygon_area":
            self.canvas.handle_polygon_click(event)
        elif self.canvas.current_tool in ["distance", "radius", "angle", "two_line_angle", "coordinate", "point_to_line", "arc_length"]:
            self.canvas.handle_measurement_click(event)
    
    def handle_left_drag(self, event):
        """Handle left mouse button drag with unified coordinate validation"""
        if self.canvas.current_tool == "pan" and self.pan_start:
            # Calculate intended movement
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            
            if self.canvas.image_id:
                # Get current position and calculate intended new position
                current_pos = self.canvas.coords(self.canvas.image_id)
                intended_x = current_pos[0] + dx
                intended_y = current_pos[1] + dy
                
                # Apply unified smart boundaries (this also updates scrollregion)
                bounded_x, bounded_y = self.canvas._apply_smart_pan_boundaries(intended_x, intended_y)
                
                # Move to bounded position
                self.canvas.coords(self.canvas.image_id, bounded_x, bounded_y)
                
                # ?? CRITICAL: Validate coordinate system consistency
                if not self.canvas.coordinate_manager.validate_coordinates_after_pan():
                    # If coordinate system becomes inconsistent, stabilize it
                    self.canvas._stabilize_coordinate_system()
            
            self.pan_start = (event.x, event.y)
    
    def handle_left_release(self, event):
        """Handle left mouse button release"""
        if self.canvas.current_tool == "pan" and self.pan_start:
            self.pan_start = None
            self.canvas._stabilize_coordinate_system()
            self.canvas.redraw_all_overlays()
            if self.canvas.is_calibrating:
                self.canvas.redraw_calibration_overlays()
    
    def handle_right_click(self, event):
        """Central right click dispatcher"""
        # Special handling for polygon area tool
        if self.canvas.current_tool == "polygon_area" and len(self.canvas.temp_points) >= 3:
            self.canvas.complete_measurement()
            return
        
        # Default behavior: pan mode
        self.right_pan_start = (event.x, event.y)
        self.canvas.config(cursor="fleur")  # Four-direction arrow cursor
    
    def handle_right_drag(self, event):
        """Handle right mouse button drag (pan) with unified coordinate validation"""
        if self.right_pan_start:
            # Calculate intended movement
            dx = event.x - self.right_pan_start[0]
            dy = event.y - self.right_pan_start[1]
            
            if self.canvas.image_id:
                # Get current position and calculate intended new position
                current_pos = self.canvas.coords(self.canvas.image_id)
                intended_x = current_pos[0] + dx
                intended_y = current_pos[1] + dy
                
                # Apply unified smart boundaries (this also updates scrollregion)
                bounded_x, bounded_y = self.canvas._apply_smart_pan_boundaries(intended_x, intended_y)
                
                # Move to bounded position
                self.canvas.coords(self.canvas.image_id, bounded_x, bounded_y)
                
                # ?? CRITICAL: Validate coordinate system consistency
                if not self.canvas.coordinate_manager.validate_coordinates_after_pan():
                    # If coordinate system becomes inconsistent, stabilize it
                    self.canvas._stabilize_coordinate_system()
            
            self.right_pan_start = (event.x, event.y)
    
    def handle_right_release(self, event):
        """Handle right mouse button release"""
        if self.right_pan_start:
            self.right_pan_start = None
            # Restore cursor to tool-appropriate cursor
            self.canvas.set_tool(self.canvas.current_tool)
            # Stabilize coordinate system after pan
            self.canvas._stabilize_coordinate_system()
            # Update overlays after pan is complete
            self.canvas.redraw_all_overlays()
            if self.canvas.is_calibrating:
                self.canvas.redraw_calibration_overlays()
    
    def handle_mouse_move(self, event):
        """Handle mouse movement"""
        # Track mouse position for zoom-to-cursor functionality
        self.canvas.last_mouse_pos = (event.x, event.y)
        
        # Update cursor position in main window
        image_coords = self.canvas.coordinate_manager.screen_to_image(event.x, event.y)
        if hasattr(self.canvas.master.master, 'update_cursor_position'):
            self.canvas.master.master.update_cursor_position(int(image_coords[0]), int(image_coords[1]))
    
    def handle_mousewheel(self, event):
        """Handle mouse wheel zoom - zoom toward cursor position"""
        self.canvas.zoom_at_cursor(event.x, event.y, event.delta > 0)
    
    def handle_key_press(self, event):
        """Handle key press events"""
        if event.keysym == "Escape":
            self.canvas.temp_points.clear()
            self.canvas.clear_temp_overlays()
            if self.canvas.is_calibrating:
                self.canvas.is_calibrating = False
                self.canvas.calibration_points.clear()
                self.canvas.delete("calibration")
                self.canvas.delete("calibration_instruction")
                self.canvas.config(cursor="")
                
                # Update status in main window
                if self.canvas.main_app and hasattr(self.canvas.main_app, 'status_label'):
                    self.canvas.main_app.status_label.config(text="Calibration cancelled")