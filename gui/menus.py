"""
Menu Manager

Handles creation and management of the application menu bar
"""

import tkinter as tk
from tkinter import messagebox
from gui.dialogs import AboutDialog

class MenuManager:
    """Manages the application menu bar"""
    
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app  # Reference to main app
        
        self.create_menus()
        self.bind_shortcuts()
    
    def create_menus(self):
        """Create menu bar and all menus"""
        # Create menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Create menus
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_help_menu()
    
    def create_file_menu(self):
        """Create File menu"""
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        
        self.file_menu.add_command(
            label="Open Image...",
            command=self.app.open_image,
            accelerator="Ctrl+O"
        )
        
        self.file_menu.add_command(
            label="Close Image",
            command=self.app.close_image,
            accelerator="Ctrl+W"
        )
        
        self.file_menu.add_separator()
        
        self.file_menu.add_command(
            label="Export Image...",
            command=self.app.export_image,
            accelerator="Ctrl+E"
        )
        
        self.file_menu.add_separator()
        
        self.file_menu.add_command(
            label="Exit",
            command=self.root.quit,
            accelerator="Alt+F4"
        )
    
    def create_edit_menu(self):
        """Create Edit menu"""
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        
        # TODO: Implement undo/redo
        self.edit_menu.add_command(
            label="Undo",
            command=self.not_implemented,
            accelerator="Ctrl+Z",
            state=tk.DISABLED
        )
        
        self.edit_menu.add_command(
            label="Redo",
            command=self.not_implemented,
            accelerator="Ctrl+Y",
            state=tk.DISABLED
        )
        
        self.edit_menu.add_separator()
        
        self.edit_menu.add_command(
            label="Clear All Measurements",
            command=self.app.clear_all_measurements,
            accelerator="Ctrl+Shift+C"
        )
        
        self.edit_menu.add_command(
            label="Delete Selected",
            command=self.app.delete_selected_measurement,
            accelerator="Delete"
        )
    
    def create_view_menu(self):
        """Create View menu"""
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        
        self.view_menu.add_command(
            label="Zoom In",
            command=self.app.canvas.zoom_in,
            accelerator="Ctrl++"
        )
        
        self.view_menu.add_command(
            label="Zoom Out",
            command=self.app.canvas.zoom_out,
            accelerator="Ctrl+-"
        )
        
        self.view_menu.add_command(
            label="Zoom to Fit",
            command=self.app.canvas.zoom_fit,
            accelerator="Ctrl+0"
        )
        
        self.view_menu.add_command(
            label="Actual Size",
            command=lambda: self.app.canvas.set_zoom(1.0),
            accelerator="Ctrl+1"
        )
        
        self.view_menu.add_separator()
        
        # ? MOVED: Pan to View menu (more logical location)
        self.view_menu.add_command(
            label="Pan",
            command=lambda: self.app.select_tool("pan"),
            accelerator="Space / Right Click"
        )
        
        self.view_menu.add_separator()
        
        # TODO: Implement show/hide overlays
        self.view_menu.add_command(
            label="Show/Hide Overlays",
            command=self.not_implemented,
            accelerator="F2",
            state=tk.DISABLED
        )
        
        self.view_menu.add_separator()
        
        self.view_menu.add_command(
            label="Reset View",
            command=self.reset_view,
            accelerator="Ctrl+R"
        )
    
    def create_tools_menu(self):
        """Create Tools menu"""
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=self.tools_menu)
        
        self.tools_menu.add_command(
            label="Calibration",
            command=self.app.start_calibration,
            accelerator="F4"
        )
        
        self.tools_menu.add_separator()
        
        self.tools_menu.add_command(
            label="Distance Measurement",
            command=lambda: self.app.select_tool("distance"),
            accelerator="F5"
        )
        
        self.tools_menu.add_command(
            label="Radius Measurement",
            command=lambda: self.app.select_tool("radius"),
            accelerator="F6"
        )
        
        self.tools_menu.add_command(
            label="Angle Measurement",
            command=lambda: self.app.select_tool("angle"),
            accelerator="F7"
        )
        
        # TODO: Add more measurement tools
        
        self.tools_menu.add_separator()
        
        self.tools_menu.add_command(
            label="Reset All Tools",
            command=self.reset_tools,
            accelerator="Esc"
        )
    
    def create_help_menu(self):
        """Create Help menu"""
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        
        self.help_menu.add_command(
            label="Keyboard Shortcuts",
            command=self.show_shortcuts,
            accelerator="F1"
        )
        
        self.help_menu.add_separator()
        
        self.help_menu.add_command(
            label="About",
            command=self.show_about
        )
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # File menu shortcuts
        self.root.bind('<Control-o>', lambda e: self.app.open_image())
        self.root.bind('<Control-w>', lambda e: self.app.close_image())
        self.root.bind('<Control-e>', lambda e: self.app.export_image())
        
        # Edit menu shortcuts
        self.root.bind('<Control-Shift-C>', lambda e: self.app.clear_all_measurements())
        self.root.bind('<Delete>', lambda e: self.app.delete_selected_measurement())
        
        # View menu shortcuts
        self.root.bind('<Control-plus>', lambda e: self.app.canvas.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.app.canvas.zoom_in())  # For US keyboards
        self.root.bind('<Control-minus>', lambda e: self.app.canvas.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.app.canvas.zoom_fit())
        self.root.bind('<Control-1>', lambda e: self.app.canvas.set_zoom(1.0))
        self.root.bind('<Control-r>', lambda e: self.reset_view())
        self.root.bind('<space>', lambda e: self.app.select_tool("pan"))  # Keep space for pan
        
        # Tools menu shortcuts
        self.root.bind('<F4>', lambda e: self.app.start_calibration())
        self.root.bind('<F5>', lambda e: self.app.select_tool("distance"))
        self.root.bind('<F6>', lambda e: self.app.select_tool("radius"))
        self.root.bind('<F7>', lambda e: self.app.select_tool("angle"))
        self.root.bind('<Escape>', lambda e: self.reset_tools())
        
        # Help shortcuts
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
    
    def reset_view(self):
        """Reset view to fit image"""
        self.app.canvas.zoom_fit()
        self.app.canvas.center_image()
    
    def reset_tools(self):
        """Reset to pan tool"""
        self.app.select_tool("pan")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
  Ctrl+O    Open Image
  Ctrl+W    Close Image
  Ctrl+E    Export Image

View:
  Ctrl++    Zoom In
  Ctrl+-    Zoom Out
  Ctrl+0    Zoom to Fit
  Ctrl+1    Actual Size
  Ctrl+R    Reset View
  Space     Pan
  Right Click    Pan (hold and drag)

Tools:
  F4        Calibration
  F5        Distance Measurement
  F6        Radius Measurement
  F7        Angle Measurement
  Esc       Reset Tools

Measurements:
  Delete              Delete Selected
  Ctrl+Shift+C       Clear All
  
General:
  F1        Show Shortcuts
  Alt+F4    Exit"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog"""
        AboutDialog(self.root)
    
    def not_implemented(self):
        """Placeholder for not implemented features"""
        messagebox.showinfo("Not Implemented", "This feature is not yet implemented.")
    
    def update_menu_states(self):
        """Update menu item states based on application state"""
        from core.app_state import app_state
        
        image_loaded = app_state.is_image_loaded
        is_calibrated = app_state.is_calibrated
        has_measurements = app_state.has_measurements
        
        # Update File menu
        self.file_menu.entryconfig("Close Image", state=tk.NORMAL if image_loaded else tk.DISABLED)
        self.file_menu.entryconfig("Export Image...", state=tk.NORMAL if (image_loaded and has_measurements) else tk.DISABLED)
        
        # Update Edit menu
        self.edit_menu.entryconfig("Clear All Measurements", state=tk.NORMAL if has_measurements else tk.DISABLED)
        self.edit_menu.entryconfig("Delete Selected", state=tk.NORMAL if has_measurements else tk.DISABLED)
        
        # Update View menu  
        self.view_menu.entryconfig("Pan", state=tk.NORMAL if image_loaded else tk.DISABLED)
        
        # Update Tools menu
        self.tools_menu.entryconfig("Calibration", state=tk.NORMAL if image_loaded else tk.DISABLED)
        self.tools_menu.entryconfig("Distance Measurement", state=tk.NORMAL if is_calibrated else tk.DISABLED)
        self.tools_menu.entryconfig("Radius Measurement", state=tk.NORMAL if is_calibrated else tk.DISABLED)
        self.tools_menu.entryconfig("Angle Measurement", state=tk.NORMAL if image_loaded else tk.DISABLED)