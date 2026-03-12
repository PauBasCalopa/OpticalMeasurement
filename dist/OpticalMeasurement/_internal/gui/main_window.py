"""
Main Application Window

The main tkinter window that contains all UI components
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from core.app_state import app_state
from core.image_manager import ImageManager
from core.measurement_engine import MeasurementEngine
from models.calibration_data import CalibrationData
from gui.canvas_widget import ImageCanvas
from gui.dialogs import CalibrationDialog, MeasurementPropertiesDialog
from gui.menus import MenuManager
from services.export_service import ExportService

class OpticalMeasurementApp:
    """Main application window and controller"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Initialize core components
        self.image_manager = ImageManager()
        self.measurement_engine = MeasurementEngine()
        self.export_service = ExportService(self.measurement_engine)
        
        # Set up window
        self.setup_window()
        
        # Create UI components
        self.create_widgets()
        
        # Set up observers
        self.setup_observers()
        
        # Initialize menu manager
        self.menu_manager = MenuManager(self.root, self)
        
        # Update UI state
        self.update_ui_state()
    
    def setup_window(self):
        """Configure main window properties"""
        self.root.title("Optical Measurement Tool")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid weights (adjusted for no toolbar)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)  # Main content now at row 0
    
    def create_widgets(self):
        """Create and layout all widgets"""
        # Create main frames (removed toolbar)
        self.create_main_content()
        self.create_sidebar()
        self.create_statusbar()
    
    
    def create_main_content(self):
        """Create main content area with image canvas"""
        # Main frame for canvas and scrollbars (adjusted grid position)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create image canvas
        self.canvas = ImageCanvas(
            self.main_frame, 
            self.image_manager,
            self.measurement_engine,
            width=800, 
            height=600,
            bg="white"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Set reference to main app for dialog callbacks
        self.canvas.set_main_app_reference(self)
        
        # Scrollbars
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
    
    def create_sidebar(self):
        """Create sidebar with calibration info and measurements list"""
        self.sidebar_frame = ttk.Frame(self.root, width=250)
        self.sidebar_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)  # Adjusted row
        self.sidebar_frame.grid_propagate(False)
        
        # Calibration frame
        self.calibration_frame = ttk.LabelFrame(self.sidebar_frame, text="Calibration")
        self.calibration_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.calibration_status_label = ttk.Label(
            self.calibration_frame, 
            text="Not calibrated",
            foreground="red"
        )
        self.calibration_status_label.pack(pady=5)
        
        self.calibration_info_label = ttk.Label(
            self.calibration_frame, 
            text="",
            font=("TkDefaultFont", 8)
        )
        self.calibration_info_label.pack(pady=2)
        
        # Calibration button (single button, no reset needed)
        ttk.Button(
            self.calibration_frame, 
            text="Calibrate", 
            command=self.start_calibration
        ).pack(pady=5)
        
        # Measurements frame
        self.measurements_frame = ttk.LabelFrame(self.sidebar_frame, text="Measurements")
        self.measurements_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Measurements listbox with scrollbar
        listbox_frame = ttk.Frame(self.measurements_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.measurements_listbox = tk.Listbox(listbox_frame)
        self.measurements_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add double-click to edit properties functionality
        self.measurements_listbox.bind("<Double-Button-1>", lambda e: self.edit_selected_measurement())
        
        # Selection → highlight overlay on canvas
        self.measurements_listbox.bind("<<ListboxSelect>>", self._on_measurement_selected)
        
        # Add right-click context menu
        self.measurements_listbox.bind("<Button-3>", self.show_measurement_context_menu)
        
        measurements_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        measurements_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.measurements_listbox.config(yscrollcommand=measurements_scrollbar.set)
        measurements_scrollbar.config(command=self.measurements_listbox.yview)
        
        # Measurement buttons
        meas_buttons_frame = ttk.Frame(self.measurements_frame)
        meas_buttons_frame.pack(fill=tk.X, pady=5)
        
        self.properties_measurement_btn = ttk.Button(
            meas_buttons_frame, 
            text="Properties", 
            command=self.edit_selected_measurement
        )
        self.properties_measurement_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_measurement_btn = ttk.Button(
            meas_buttons_frame, 
            text="Delete", 
            command=self.delete_selected_measurement
        )
        self.delete_measurement_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_measurements_btn = ttk.Button(
            meas_buttons_frame, 
            text="Clear All", 
            command=self.clear_all_measurements
        )
        self.clear_measurements_btn.pack(side=tk.LEFT, padx=2)
    
    def create_statusbar(self):
        """Create status bar"""
        self.statusbar_frame = ttk.Frame(self.root)
        self.statusbar_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)  # Adjusted row
        
        # Status labels
        self.status_label = ttk.Label(self.statusbar_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Separator(self.statusbar_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        self.coords_label = ttk.Label(self.statusbar_frame, text="")
        self.coords_label.pack(side=tk.RIGHT, padx=10)
        
        self.zoom_label = ttk.Label(self.statusbar_frame, text="Zoom: 100%")
        self.zoom_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_observers(self):
        """Set up observers for application state changes"""
        app_state.add_observer(self.on_state_change)
    
    def on_state_change(self, change_type: str, data=None):
        """Handle application state changes"""
        if change_type == "image_loaded":
            self.update_ui_state()
        elif change_type == "image_closed":
            self.update_ui_state()
        elif change_type == "calibration_changed":
            self.update_calibration_display()
            self.measurement_engine.set_calibration(data)
            self.update_ui_state()  # Update UI state when calibration changes
        elif change_type == "calibration_cleared":
            self.update_calibration_display()
            self.measurement_engine.set_calibration(None)
            self.update_ui_state()  # Update UI state when calibration cleared
        elif change_type in ["measurement_added", "measurement_removed", "measurements_cleared"]:
            self.update_measurements_list()
            self.canvas.redraw_all_overlays()
            self.update_ui_state()
        elif change_type == "undo_redo_changed":
            self.update_ui_state()
        elif change_type in ["zoom_changed", "view_changed"]:
            zoom = data.zoom if hasattr(data, 'zoom') else data
            max_zoom = self.canvas.image_manager.get_max_zoom() if (hasattr(self.canvas, 'image_manager') and 
                                                                   hasattr(self.canvas.image_manager, 'get_max_zoom')) else 10.0
            self.zoom_label.config(text=f"Zoom: {zoom*100:.0f}% (max: {max_zoom*100:.0f}%)")
    
    def update_ui_state(self):
        """Update UI state based on current application state"""
        image_loaded = app_state.is_image_loaded
        is_calibrated = app_state.is_calibrated
        has_measurements = app_state.has_measurements
        
        # Update measurement buttons based on whether measurements exist
        self.properties_measurement_btn.config(state=tk.NORMAL if has_measurements else tk.DISABLED)
        self.delete_measurement_btn.config(state=tk.NORMAL if has_measurements else tk.DISABLED)
        self.clear_measurements_btn.config(state=tk.NORMAL if has_measurements else tk.DISABLED)
        
        # Update calibration display
        self.update_calibration_display()
        
        # Update measurements list
        self.update_measurements_list()
        
        # Update menu states
        self.menu_manager.update_menu_states()
    
    def update_calibration_display(self):
        """Update calibration status display"""
        if app_state.is_calibrated:
            self.calibration_status_label.config(text="Calibrated", foreground="green")
            calibration = app_state.calibration
            info_text = f"Scale: 1 px = {calibration.scale_factor:.4f} units\n"
            info_text += f"Precision: +/-{calibration.precision:.4f} units"
            self.calibration_info_label.config(text=info_text)
        else:
            self.calibration_status_label.config(text="Not calibrated", foreground="red")
            self.calibration_info_label.config(text="")
    
    def update_measurements_list(self):
        """Update measurements listbox"""
        self.measurements_listbox.delete(0, tk.END)
        
        for measurement in app_state.measurements:
            result_text = self.measurement_engine.format_measurement_result(measurement)
            display_text = f"{measurement.label}: {result_text}"
            self.measurements_listbox.insert(tk.END, display_text)
    
    def _on_measurement_selected(self, event):
        """Highlight the selected measurement's overlay on the canvas."""
        selection = self.measurements_listbox.curselection()
        if not selection:
            self.canvas.overlay_renderer.clear_highlight()
            return
        index = selection[0]
        if 0 <= index < len(app_state.measurements):
            m = app_state.measurements[index]
            self.canvas.overlay_renderer.highlight_measurement(m.id)
        else:
            self.canvas.overlay_renderer.clear_highlight()
    
    # Menu command methods
    def open_image(self):
        """Open image file dialog"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.gif"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Image",
            filetypes=file_types
        )
        
        if filename:
            try:
                image_data = self.image_manager.load_image(filename)
                app_state.load_image(image_data)
                self.canvas.set_image(image_data)
                self.status_label.config(text=f"Loaded: {image_data.file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def close_image(self):
        """Close current image"""
        if app_state.is_image_loaded:
            self.image_manager.close_image()
            app_state.close_image()
            self.canvas.clear_image()
            self.status_label.config(text="Ready")
    
    def export_image(self):
        """Export annotated image"""
        if not app_state.is_image_loaded:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        if not app_state.has_measurements:
            messagebox.showwarning("Warning", "No measurements to export")
            return
        
        file_types = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Export Annotated Image",
            filetypes=file_types,
            defaultextension=".png"
        )
        
        if filename:
            try:
                self.export_service.export(
                    self.canvas.current_image.original_image,
                    app_state.measurements,
                    filename,
                    overlays_visible=self.canvas.get_overlays_visibility()
                )
                self.status_label.config(text=f"Exported: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Image exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export image: {str(e)}")
    
    def start_calibration(self):
        """Start calibration process"""
        if not app_state.is_image_loaded:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        self.canvas.start_calibration()
        self.status_label.config(text="Calibration: Click two points on the image...")
    
    def reset_calibration(self):
        """Reset calibration"""
        app_state.clear_calibration()
        self.canvas.clear_calibration()
        self.status_label.config(text="Calibration reset")
    
    def select_tool(self, tool_name: str):
        """Select measurement tool"""
        # ? PHASE 3: Check calibration requirements for new tools
        if tool_name in ["distance", "radius", "polygon_area", "point_to_line", "arc_length"] and not app_state.is_calibrated:
            messagebox.showwarning("Warning", "Please calibrate the image first")
            return
        
        if tool_name in ["angle", "two_line_angle", "coordinate"] and not app_state.is_image_loaded:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        app_state.set_active_tool(tool_name)
        self.canvas.set_tool(tool_name)
        
        # ? PHASE 3: Enhanced status messages for all tools
        tool_messages = {
            "pan": "Pan mode - Right-click and drag to pan anytime",
            "distance": "Distance mode - Click two points to measure distance",
            "radius": "Radius mode - Click three points on circle edge",
            "angle": "Angle mode - Click three points (vertex in middle)",
            "two_line_angle": "Two-Line Angle mode - Click four points (two per line)",
            "polygon_area": "Polygon Area mode - Click points to define polygon (right-click to finish)",
            "coordinate": "Coordinate mode - Click point(s) to show coordinates or differences",
            "point_to_line": "Point-to-Line mode - Click point, then two points to define line",
            "arc_length": "Arc Length mode - Click three points along the arc"
        }
        
        message = tool_messages.get(tool_name, f"Tool: {tool_name.title()}")
        self.status_label.config(text=message)
    
    def delete_selected_measurement(self):
        """Delete selected measurement"""
        selection = self.measurements_listbox.curselection()
        if not selection:
            messagebox.showinfo("Selection Required", "Please select a measurement to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Deletion", "Delete the selected measurement?")
        if not result:
            return
        
        index = selection[0]
        if 0 <= index < len(app_state.measurements):
            measurement = app_state.measurements[index]
            # Remove from canvas first
            self.canvas.remove_measurement_overlay(measurement.id)
            # Remove from app state  
            app_state.remove_measurement(measurement.id)
            self.status_label.config(text="Measurement deleted")
        else:
            messagebox.showerror("Error", "Invalid selection index")
    
    def clear_all_measurements(self):
        """Clear all measurements"""
        if not app_state.has_measurements:
            messagebox.showinfo("No Measurements", "There are no measurements to clear")
            return
            
        result = messagebox.askyesno("Confirm Clear All", 
                                   f"Delete all {len(app_state.measurements)} measurements?")
        if result:
            # Clear from canvas first
            self.canvas.clear_all_overlays()
            # Clear from app state
            app_state.clear_measurements()
            self.status_label.config(text="All measurements cleared")
    
    def undo(self):
        """Undo last measurement action."""
        if app_state.can_undo:
            app_state.undo()
            self.status_label.config(text="Undo")

    def redo(self):
        """Redo last undone action."""
        if app_state.can_redo:
            app_state.redo()
            self.status_label.config(text="Redo")
    
    def edit_selected_measurement(self):
        """Edit selected measurement properties"""
        selection = self.measurements_listbox.curselection()
        if not selection:
            messagebox.showinfo("Selection Required", "Please select a measurement to edit")
            return
        
        index = selection[0]
        if 0 <= index < len(app_state.measurements):
            measurement = app_state.measurements[index]
            
            try:
                dialog = MeasurementPropertiesDialog(self.root, measurement)
                self.root.wait_window(dialog.dialog)
                
                if dialog.result:
                    # Update measurement properties
                    old_label = measurement.label
                    measurement.label = dialog.result["label"]
                    
                    # Update the display
                    self.update_measurements_list()
                    self.status_label.config(text=f"Updated measurement: {measurement.label}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to edit measurement: {e}")
        else:
            messagebox.showerror("Error", "Invalid selection index")
    
    def show_measurement_context_menu(self, event):
        """Show context menu for measurements list"""
        # Select the item under cursor
        index = self.measurements_listbox.nearest(event.y)
        if 0 <= index < self.measurements_listbox.size():
            self.measurements_listbox.selection_clear(0, tk.END)
            self.measurements_listbox.selection_set(index)
            self.measurements_listbox.activate(index)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Properties", command=self.edit_selected_measurement)
            context_menu.add_separator()
            context_menu.add_command(label="Delete", command=self.delete_selected_measurement)
            
            # Show menu at cursor position
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def show_calibration_dialog(self, pixel_distance: float):
        """Show calibration input dialog"""
        try:
            dialog = CalibrationDialog(self.root, pixel_distance)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                real_distance = dialog.result
                calibration = CalibrationData()
                try:
                    # Get calibration points from canvas
                    points = self.canvas.get_calibration_points()
                    
                    if len(points) == 2:
                        calibration.calibrate(points[0], points[1], real_distance)
                        app_state.set_calibration(calibration)
                        
                        # ? CLEAN UP: Remove calibration graphics after successful calibration
                        self.canvas.clear_calibration()
                        
                        self.status_label.config(text="Calibration complete - Ready to measure!")
                    else:
                        messagebox.showerror("Error", f"Expected 2 calibration points, got {len(points)}")
                        
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
            else:
                # Clear calibration points since user cancelled
                self.canvas.clear_calibration()
                self.status_label.config(text="Calibration cancelled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show calibration dialog: {e}")
    
    def update_cursor_position(self, x: int, y: int):
        """Update cursor position display"""
        if app_state.is_image_loaded:
            # Convert screen coordinates to image coordinates if needed
            self.coords_label.config(text=f"Position: ({x}, {y})")
        else:
            self.coords_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = OpticalMeasurementApp(root)
    root.mainloop()