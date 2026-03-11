#!/usr/bin/env python3
"""
Optical Measurement Tool - Main Entry Point

A desktop application for precise measurements on digital images using
a pixel-to-real-world calibration system.
"""

import sys
import tkinter as tk
from tkinter import messagebox
import traceback

def main():
    """Main entry point for the application"""
    try:
        # Import here to catch import errors gracefully
        from gui.main_window import OpticalMeasurementApp
        
        # Create root window
        root = tk.Tk()
        
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