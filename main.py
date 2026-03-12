#!/usr/bin/env python3
"""
Optical Measurement Tool - Main Entry Point

A desktop application for precise measurements on digital images using
a pixel-to-real-world calibration system.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback


def _resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def main():
    """Main entry point for the application"""
    try:
        # Import here to catch import errors gracefully
        from gui.main_window import OpticalMeasurementApp
        
        # Create root window
        root = tk.Tk()
        
        # Set window icon
        icon_path = _resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        
        # Create application
        app = OpticalMeasurementApp(root)
        
        # Start main loop
        root.mainloop()
        
    except ImportError as e:
        messagebox.showerror("Import Error", 
                           f"Failed to import required modules: {e}")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("Startup Error", 
                           f"Failed to start application: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()