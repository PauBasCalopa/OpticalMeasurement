"""
Overlay Manager

Handles all measurement overlay drawing and management for the canvas widget.
Provides centralized control over measurement visualization.
"""

from typing import Dict, List, Any
from models.measurement_data import MeasurementBase

class OverlayManager:
    """Manages measurement overlays and their visibility"""
    
    def __init__(self, canvas):
        """Initialize overlay manager with canvas reference"""
        self.canvas = canvas
        self.measurement_overlays = {}  # measurement_id -> canvas_items
        self.overlays_visible = True
    
    def draw_measurement_overlay(self, measurement: MeasurementBase):
        """Draw measurement overlay on canvas"""
        if not self.overlays_visible:
            return
            
        # Route to appropriate drawing method based on measurement type
        draw_method = getattr(self, f'_draw_{measurement.measurement_type}_overlay', None)
        if draw_method:
            overlay_items = draw_method(measurement)
            self.measurement_overlays[measurement.id] = overlay_items
        else:
            print(f"Warning: No overlay drawing method for {measurement.measurement_type}")
    
    def _draw_distance_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw distance measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 2:
            # Draw line between points
            screen1 = self.canvas.coordinate_manager.image_to_screen(*measurement.points[0])
            screen2 = self.canvas.coordinate_manager.image_to_screen(*measurement.points[1])
            
            line_id = self.canvas.create_line(
                screen1[0], screen1[1], screen2[0], screen2[1],
                fill="green", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line_id)
            
            # Draw result text
            mid_x = (screen1[0] + screen2[0]) / 2
            mid_y = (screen1[1] + screen2[1]) / 2
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            
            text_id = self.canvas.create_text(
                mid_x, mid_y - 10, text=result_text,
                fill="green", font=("Arial", 8), tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def _draw_radius_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw radius measurement overlay"""
        overlay_items = []
        
        if hasattr(measurement, 'center_point') and measurement.center_point:
            center_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.center_point)
            
            # Calculate radius in screen pixels
            if self.canvas.measurement_engine.calibration:
                radius_pixels = measurement.result / self.canvas.measurement_engine.calibration.scale_factor
            else:
                radius_pixels = measurement.result
            
            radius_screen = radius_pixels * self.canvas.actual_zoom_level
            
            # Draw circle
            circle_id = self.canvas.create_oval(
                center_screen[0] - radius_screen, center_screen[1] - radius_screen,
                center_screen[0] + radius_screen, center_screen[1] + radius_screen,
                outline="blue", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(circle_id)
            
            # Draw center point
            center_id = self.canvas.create_oval(
                center_screen[0] - 2, center_screen[1] - 2,
                center_screen[0] + 2, center_screen[1] + 2,
                fill="blue", outline="blue", tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(center_id)
            
            # Draw result text
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                center_screen[0], center_screen[1] - radius_screen - 15,
                text=result_text, fill="blue", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def _draw_angle_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw angle measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 3:
            vertex_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[1])
            p1_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[0])
            p3_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[2])
            
            # Draw lines from vertex
            line1_id = self.canvas.create_line(
                vertex_screen[0], vertex_screen[1], p1_screen[0], p1_screen[1],
                fill="orange", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line1_id)
            
            line2_id = self.canvas.create_line(
                vertex_screen[0], vertex_screen[1], p3_screen[0], p3_screen[1],
                fill="orange", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line2_id)
            
            # Draw result text near vertex
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                vertex_screen[0] + 20, vertex_screen[1] - 20,
                text=result_text, fill="orange", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def _draw_polygon_area_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw polygon area measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 3:
            screen_points = [self.canvas.coordinate_manager.image_to_screen(*point) for point in measurement.points]
            
            # Draw polygon lines
            for i in range(len(screen_points)):
                next_i = (i + 1) % len(screen_points)  # Wrap to first point for closing
                line_id = self.canvas.create_line(
                    screen_points[i][0], screen_points[i][1],
                    screen_points[next_i][0], screen_points[next_i][1],
                    fill="cyan", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(line_id)
            
            # Draw center text
            center_x = sum(p[0] for p in screen_points) / len(screen_points)
            center_y = sum(p[1] for p in screen_points) / len(screen_points)
            
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                center_x, center_y,
                text=result_text, fill="cyan", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def _draw_two_line_angle_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw two-line angle measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 4:
            # Get line points
            line1_p1_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[0])
            line1_p2_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[1])
            line2_p1_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[2])
            line2_p2_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[3])
            
            # Draw first line
            line1_id = self.canvas.create_line(
                line1_p1_screen[0], line1_p1_screen[1],
                line1_p2_screen[0], line1_p2_screen[1],
                fill="purple", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line1_id)
            
            # Draw second line
            line2_id = self.canvas.create_line(
                line2_p1_screen[0], line2_p1_screen[1],
                line2_p2_screen[0], line2_p2_screen[1],
                fill="purple", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line2_id)
            
            # Find intersection or midpoint for text placement
            mid_x = (line1_p1_screen[0] + line1_p2_screen[0] + line2_p1_screen[0] + line2_p2_screen[0]) / 4
            mid_y = (line1_p1_screen[1] + line1_p2_screen[1] + line2_p1_screen[1] + line2_p2_screen[1]) / 4
            
            # Draw result text
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                mid_x, mid_y - 15,
                text=result_text, fill="purple", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def _draw_coordinate_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw coordinate measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 1:
            # Draw point marker
            point_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[0])
            
            # Draw crosshair for point
            cross_size = 5
            # Horizontal line
            h_line_id = self.canvas.create_line(
                point_screen[0] - cross_size, point_screen[1],
                point_screen[0] + cross_size, point_screen[1],
                fill="red", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(h_line_id)
            
            # Vertical line
            v_line_id = self.canvas.create_line(
                point_screen[0], point_screen[1] - cross_size,
                point_screen[0], point_screen[1] + cross_size,
                fill="red", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(v_line_id)
            
            # Draw coordinate text
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                point_screen[0] + 15, point_screen[1] - 15,
                text=result_text, fill="red", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
            
            # If difference measurement, draw second point and line
            if hasattr(measurement, 'coordinate_type') and measurement.coordinate_type == "difference" and len(measurement.points) >= 2:
                point2_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[1])
                
                # Draw second crosshair
                h_line2_id = self.canvas.create_line(
                    point2_screen[0] - cross_size, point2_screen[1],
                    point2_screen[0] + cross_size, point2_screen[1],
                    fill="red", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(h_line2_id)
                
                v_line2_id = self.canvas.create_line(
                    point2_screen[0], point2_screen[1] - cross_size,
                    point2_screen[0], point2_screen[1] + cross_size,
                    fill="red", width=2, tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(v_line2_id)
                
                # Draw line between points
                line_id = self.canvas.create_line(
                    point_screen[0], point_screen[1],
                    point2_screen[0], point2_screen[1],
                    fill="red", width=1, dash=(5, 5), tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(line_id)
        
        return overlay_items
    
    def _draw_point_to_line_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw point-to-line distance measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 3:
            # Get screen coordinates
            point_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[0])
            line_start_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[1])
            line_end_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[2])
            
            # Draw the line
            line_id = self.canvas.create_line(
                line_start_screen[0], line_start_screen[1],
                line_end_screen[0], line_end_screen[1],
                fill="brown", width=2, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line_id)
            
            # Draw the point
            point_id = self.canvas.create_oval(
                point_screen[0] - 3, point_screen[1] - 3,
                point_screen[0] + 3, point_screen[1] + 3,
                fill="brown", outline="white", width=1,
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(point_id)
            
            # Calculate perpendicular point on line for visualization
            try:
                # Simple perpendicular calculation
                # This is a simplified version - in production you'd use the math_utils function
                mid_line_x = (line_start_screen[0] + line_end_screen[0]) / 2
                mid_line_y = (line_start_screen[1] + line_end_screen[1]) / 2
                
                # Draw perpendicular line (simplified - just to the line midpoint)
                perp_line_id = self.canvas.create_line(
                    point_screen[0], point_screen[1],
                    mid_line_x, mid_line_y,
                    fill="brown", width=1, dash=(3, 3),
                    tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(perp_line_id)
                
                # Text placement
                text_x = (point_screen[0] + mid_line_x) / 2
                text_y = (point_screen[1] + mid_line_y) / 2
                
            except:
                # Fallback: place text near the point
                text_x = point_screen[0] + 15
                text_y = point_screen[1] - 15
            
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                text_x, text_y,
                text=result_text, fill="brown", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def _draw_arc_length_overlay(self, measurement: MeasurementBase) -> List[int]:
        """Draw arc length measurement overlay"""
        overlay_items = []
        
        if len(measurement.points) >= 3:
            # Get screen coordinates
            p1_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[0])
            p2_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[1])
            p3_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.points[2])
            
            # Draw arc as connected line segments (simplified)
            line1_id = self.canvas.create_line(
                p1_screen[0], p1_screen[1], p2_screen[0], p2_screen[1],
                fill="magenta", width=3, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line1_id)
            
            line2_id = self.canvas.create_line(
                p2_screen[0], p2_screen[1], p3_screen[0], p3_screen[1],
                fill="magenta", width=3, tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(line2_id)
            
            # Draw points on arc
            for point_screen in [p1_screen, p2_screen, p3_screen]:
                point_id = self.canvas.create_oval(
                    point_screen[0] - 2, point_screen[1] - 2,
                    point_screen[0] + 2, point_screen[1] + 2,
                    fill="magenta", outline="magenta",
                    tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(point_id)
            
            # Draw center point if available
            if hasattr(measurement, 'center_point') and measurement.center_point:
                center_screen = self.canvas.coordinate_manager.image_to_screen(*measurement.center_point)
                center_id = self.canvas.create_oval(
                    center_screen[0] - 2, center_screen[1] - 2,
                    center_screen[0] + 2, center_screen[1] + 2,
                    fill="magenta", outline="white", width=1,
                    tags=f"measurement_{measurement.id}"
                )
                overlay_items.append(center_id)
            
            # Draw result text near the arc
            text_x = (p1_screen[0] + p2_screen[0] + p3_screen[0]) / 3
            text_y = (p1_screen[1] + p2_screen[1] + p3_screen[1]) / 3
            
            result_text = self.canvas.measurement_engine.format_measurement_result(measurement)
            text_id = self.canvas.create_text(
                text_x, text_y - 20,
                text=result_text, fill="magenta", font=("Arial", 8),
                tags=f"measurement_{measurement.id}"
            )
            overlay_items.append(text_id)
        
        return overlay_items
    
    def remove_measurement_overlay(self, measurement_id: str):
        """Remove measurement overlay"""
        if measurement_id in self.measurement_overlays:
            for item_id in self.measurement_overlays[measurement_id]:
                self.canvas.delete(item_id)
            del self.measurement_overlays[measurement_id]
    
    def clear_all_overlays(self):
        """Clear all measurement overlays"""
        for measurement_id in list(self.measurement_overlays.keys()):
            self.remove_measurement_overlay(measurement_id)
    
    def redraw_all_overlays(self):
        """Redraw all measurement overlays at current zoom/pan position"""
        if not self.overlays_visible:
            return
            
        from core.app_state import app_state
        
        # Clear all existing overlays
        self.clear_all_overlays()
        
        # Redraw each measurement
        for measurement in app_state.measurements:
            self.draw_measurement_overlay(measurement)
    
    def toggle_visibility(self) -> bool:
        """Toggle visibility of all measurement overlays"""
        self.overlays_visible = not self.overlays_visible
        
        if self.overlays_visible:
            self.redraw_all_overlays()
        else:
            # Hide all overlays
            for measurement_id in self.measurement_overlays:
                for item_id in self.measurement_overlays[measurement_id]:
                    try:
                        self.canvas.itemconfig(item_id, state="hidden")
                    except:
                        pass  # Item might have been deleted
        
        return self.overlays_visible
    
    def set_visibility(self, visible: bool):
        """Set overlay visibility state"""
        if self.overlays_visible != visible:
            self.toggle_visibility()
    
    def get_visibility(self) -> bool:
        """Get current overlay visibility state"""
        return self.overlays_visible