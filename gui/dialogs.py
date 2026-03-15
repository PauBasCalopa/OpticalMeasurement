"""
Dialog Windows

Various dialog windows for user input and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

APP_NAME = "Optical Measurement Tool"
APP_VERSION = "2.5"
APP_AUTHOR = "Pau Bas Calopa"
APP_YEAR = "2026"
APP_LICENSE = "MIT License"

class CalibrationDialog:
    """Dialog for calibration distance input"""
    
    def __init__(self, parent, pixel_distance: float):
        self.parent = parent
        self.pixel_distance = pixel_distance
        self.result: Optional[float] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Calibration")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        self.create_widgets()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Set Calibration Distance",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Info
        info_text = f"You selected two points {self.pixel_distance:.1f} pixels apart.\n"
        info_text += "Enter the real-world distance between these points:"
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 15))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(input_frame, text="Distance:").pack(side=tk.LEFT)
        
        self.distance_var = tk.StringVar()
        self.distance_entry = ttk.Entry(
            input_frame, 
            textvariable=self.distance_var,
            width=15
        )
        self.distance_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Label(input_frame, text="units").pack(side=tk.LEFT)
        
        # Focus on entry
        self.distance_entry.focus()
        
        # Note
        note_label = ttk.Label(
            main_frame,
            text="Note: Use any unit you prefer (mm, inches, etc.)\nAll measurements will be in the same units.",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        note_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="OK", 
            command=self.ok
        ).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
    
    def ok(self):
        """Handle OK button"""
        try:
            value = float(self.distance_var.get().strip())
            if value <= 0:
                messagebox.showerror("Invalid Input", "Distance must be positive")
                return
            
            self.result = value
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
    
    def cancel(self):
        """Handle Cancel button"""
        self.result = None
        self.dialog.destroy()

class AboutDialog:
    """About dialog"""
    
    def __init__(self, parent):
        self.parent = parent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Optical Measurement Tool")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        self.create_widgets()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=APP_NAME,
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(main_frame, text=f"Version {APP_VERSION}")
        version_label.pack(pady=(0, 15))
        
        # Description
        description = (f"A desktop application for precise measurements on digital images.\n\n"
                       f"By: {APP_AUTHOR} (C) {APP_YEAR}.\n"
                       f"Licensed under the {APP_LICENSE}.")
        
        description_label = ttk.Label(
            main_frame, 
            text=description,
            justify=tk.LEFT
        )
        description_label.pack(pady=(0, 20))
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack()
        
        # Bind Escape key
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())

class MeasurementPropertiesDialog:
    """Dialog for editing measurement properties"""
    
    def __init__(self, parent, measurement):
        self.parent = parent
        self.measurement = measurement
        self.result: Optional[dict] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Measurement Properties")
        self.dialog.geometry("420x420")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        self.create_widgets()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"Edit {self.measurement.measurement_type.title()} Properties",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Label input
        label_frame = ttk.LabelFrame(main_frame, text="Label", padding="10")
        label_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.label_var = tk.StringVar(value=self.measurement.label)
        label_entry = ttk.Entry(label_frame, textvariable=self.label_var, width=30)
        label_entry.pack(fill=tk.X)
        label_entry.focus()
        
        # Measurement info
        info_frame = ttk.LabelFrame(main_frame, text="Measurement Info", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Type
        type_label = ttk.Label(info_frame, text=f"Type: {self.measurement.measurement_type.replace('_', ' ').title()}")
        type_label.pack(anchor=tk.W)
        
        # Type-specific details
        self._add_measurement_details(info_frame)
        
        # Points count
        points_count = len(self.measurement.points)
        points_label = ttk.Label(info_frame, text=f"Points: {points_count}")
        points_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Point coordinates
        for i, (px, py) in enumerate(self.measurement.points):
            pt_label = ttk.Label(info_frame, text=f"  P{i+1}: ({px:.1f}, {py:.1f}) px",
                                font=("TkDefaultFont", 8), foreground="#555")
            pt_label.pack(anchor=tk.W)
        
        # Timestamp
        timestamp_str = self.measurement.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        timestamp_label = ttk.Label(info_frame, text=f"Created: {timestamp_str}")
        timestamp_label.pack(anchor=tk.W, pady=(5, 0))
        
        # ID (for technical users)
        id_label = ttk.Label(info_frame, text=f"ID: {self.measurement.id[:8]}...", 
                            font=("TkDefaultFont", 8), foreground="gray")
        id_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="OK", 
            command=self.ok
        ).pack(side=tk.RIGHT)
        
        # Bind keys
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
    
    def _add_measurement_details(self, parent_frame):
        """Add type-specific measurement details to the info frame."""
        m = self.measurement
        mt = m.measurement_type
        
        if mt == "distance":
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Distance: {m.result:.3f}").pack(anchor=tk.W, pady=(5, 0))
        
        elif mt == "radius":
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Radius: {m.result:.3f}").pack(anchor=tk.W, pady=(5, 0))
            if hasattr(m, 'center_point') and m.center_point:
                cx, cy = m.center_point
                ttk.Label(parent_frame, text=f"Center: ({cx:.1f}, {cy:.1f}) px").pack(anchor=tk.W, pady=(2, 0))
        
        elif mt in ("angle", "two_line_angle"):
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Angle: {m.result:.3f}\u00b0").pack(anchor=tk.W, pady=(5, 0))
        
        elif mt == "polygon_area":
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Area: {m.result:.3f}").pack(anchor=tk.W, pady=(5, 0))
            if hasattr(m, 'perimeter') and m.perimeter is not None:
                ttk.Label(parent_frame, text=f"Perimeter: {m.perimeter:.3f}").pack(anchor=tk.W, pady=(2, 0))
        
        elif mt == "coordinate":
            coord_type = getattr(m, 'coordinate_type', 'single')
            ttk.Label(parent_frame, text=f"Mode: {coord_type}").pack(anchor=tk.W, pady=(5, 0))
            if coord_type == "single" and len(m.points) >= 1:
                x, y = m.points[0]
                ttk.Label(parent_frame, text=f"Coordinates: ({x:.2f}, {y:.2f}) px").pack(anchor=tk.W, pady=(2, 0))
            elif coord_type == "difference" and len(m.points) >= 2:
                dx = getattr(m, 'dx', None)
                dy = getattr(m, 'dy', None)
                if dx is not None and dy is not None:
                    ttk.Label(parent_frame, text=f"\u0394x: {dx:.3f}").pack(anchor=tk.W, pady=(2, 0))
                    ttk.Label(parent_frame, text=f"\u0394y: {dy:.3f}").pack(anchor=tk.W, pady=(2, 0))
                if m.result is not None:
                    ttk.Label(parent_frame, text=f"Distance: {m.result:.3f}").pack(anchor=tk.W, pady=(2, 0))
        
        elif mt == "point_to_line":
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Distance: {m.result:.3f}").pack(anchor=tk.W, pady=(5, 0))
        
        elif mt == "arc_length":
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Arc Length: {m.result:.3f}").pack(anchor=tk.W, pady=(5, 0))
            if hasattr(m, 'radius') and m.radius is not None:
                ttk.Label(parent_frame, text=f"Radius: {m.radius:.3f}").pack(anchor=tk.W, pady=(2, 0))
            if hasattr(m, 'central_angle') and m.central_angle is not None:
                ttk.Label(parent_frame, text=f"Central Angle: {m.central_angle:.2f}\u00b0").pack(anchor=tk.W, pady=(2, 0))
            if hasattr(m, 'center_point') and m.center_point:
                cx, cy = m.center_point
                ttk.Label(parent_frame, text=f"Center: ({cx:.1f}, {cy:.1f}) px").pack(anchor=tk.W, pady=(2, 0))
        
        else:
            if m.result is not None:
                ttk.Label(parent_frame, text=f"Value: {m.result:.3f}").pack(anchor=tk.W, pady=(5, 0))
    
    def ok(self):
        """Handle OK button"""
        label = self.label_var.get().strip()
        if not label:
            messagebox.showerror("Invalid Input", "Label cannot be empty")
            return
        
        self.result = {"label": label}
        self.dialog.destroy()
    
    def cancel(self):
        """Handle Cancel button"""
        self.result = None
        self.dialog.destroy()


class GridSettingsDialog:
    """Dialog for grid overlay settings"""
    
    def __init__(self, parent, current_spacing: int = 50, current_color: str = "#cccccc"):
        self.parent = parent
        self.result: Optional[dict] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Grid Settings")
        self.dialog.geometry("300x180")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Grid Settings", font=("TkDefaultFont", 12, "bold")).pack(pady=(0, 10))
        
        # Spacing
        spacing_frame = ttk.Frame(main_frame)
        spacing_frame.pack(fill=tk.X, pady=3)
        ttk.Label(spacing_frame, text="Spacing (px):").pack(side=tk.LEFT)
        self.spacing_var = tk.IntVar(value=current_spacing)
        ttk.Spinbox(spacing_frame, from_=10, to=500, textvariable=self.spacing_var, width=8).pack(side=tk.RIGHT)
        
        # Color
        color_frame = ttk.Frame(main_frame)
        color_frame.pack(fill=tk.X, pady=3)
        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value=current_color)
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_var, width=10,
                                   values=["#cccccc", "#999999", "#666666", "#ff0000", "#00ff00", "#0000ff"])
        color_combo.pack(side=tk.RIGHT)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="OK", command=self._ok).pack(side=tk.RIGHT)
        
        self.dialog.bind("<Return>", lambda e: self._ok())
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())
    
    def _ok(self):
        spacing = self.spacing_var.get()
        if spacing < 10:
            spacing = 10
        self.result = {"spacing": spacing, "color": self.color_var.get()}
        self.dialog.destroy()