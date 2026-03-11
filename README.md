# Optical Measurement Tool

A professional desktop application for precise measurements on digital images using a pixel-to-real-world calibration system.

## ?? Features

- **?? Image Support**: Load common image formats (JPEG, PNG, BMP, TIFF, GIF)
- **?? Calibration System**: Two-point calibration with any units
- **?? Measurements**: 
  - **Distance** (two points)
  - **Radius** (three points on circle)
  - **Angle** (three points)
- **??? Professional Interface**: 
  - Right-click pan + mouse wheel zoom
  - Keyboard shortcuts for all tools
  - Clean, toolbar-free design
- **?? Export**: Save annotated images with measurements

## ?? Requirements

- **Python 3.8+**
- **Required packages** (auto-install via requirements.txt):
  ```bash
  pip install -r requirements.txt
  ```

## ??? Installation

1. **Clone or download** this repository
2. **Navigate** to the project directory
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```

## ?? Usage

### **?? Quick Start Workflow**

1. **?? Open Image**: `Ctrl+O` or File ? Open Image
2. **?? Calibrate**: `F4` or Tools ? Calibration ? Click two points on known distance
3. **?? Measure**: `F5` Distance | `F6` Radius | `F7` Angle
4. **?? Export**: `Ctrl+E` or File ? Export Image

### **??? Professional Mouse Controls**

- **??? Left Click**: Use selected tool (calibration, measurements)
- **??? Right Click + Drag**: Pan image (always available)
- **??? Mouse Wheel**: Zoom in/out
- **??? Double-Click**: Delete measurement from list

### **?? Keyboard Shortcuts**

#### **?? File Operations**
- `Ctrl+O` - Open Image
- `Ctrl+W` - Close Image  
- `Ctrl+E` - Export Image

#### **??? View Controls**
- `Ctrl++` - Zoom In
- `Ctrl+-` - Zoom Out
- `Ctrl+0` - Zoom to Fit
- `Ctrl+1` - Actual Size
- `Ctrl+R` - Reset View
- `Space` - Pan Tool

#### **?? Measurement Tools**
- `F4` - Calibration
- `F5` - Distance Measurement
- `F6` - Radius Measurement
- `F7` - Angle Measurement
- `Esc` - Reset Tools

#### **?? Measurement Management**
- `Delete` - Delete Selected
- `Ctrl+Shift+C` - Clear All

### **?? Calibration System**

The "**bananas for scale**" philosophy - use any reference object:

1. **Find a known distance** in your image
2. **Click Calibrate** (`F4`) 
3. **Click two points** on that known distance
4. **Enter the real distance** (in any units you prefer)
5. **All measurements** will now be in those same units

#### **?? Examples:**
- Bolt diameter = 10mm ? All measurements in **mm**
- Ruler marking = 2 inches ? All measurements in **inches**  
- Coin diameter = 24.3mm ? All measurements in **mm**

## ??? Technical Details

### **?? Architecture**
- **Built with**: Python, tkinter, Pillow, numpy
- **Cross-platform**: Windows, macOS, Linux
- **No internet required**: Fully offline operation
- **High-res support**: Handles large images efficiently

### **?? Current Status** ?
This is the **Phase 1 MVP** with full functionality:
- ? Image loading and display
- ? Professional zoom and pan controls
- ? Two-point calibration system
- ? Distance measurement (two points)
- ? Radius measurement (three-point method)
- ? Angle measurement (three points)
- ? Measurement management (delete, clear)
- ? Image export with measurements
- ? Professional user interface

### **?? Future Enhancements**
- Area measurements (polygon tool)
- Point coordinates and coordinate differences
- Point-to-line distance measurements
- Arc length measurements
- Undo/redo system
- Enhanced export options (CSV data, PDF reports)
- Overlay visibility controls

## ?? Project Structure

```
OpticalMeasurement/
??? main.py                 # Application entry point
??? requirements.txt        # Python dependencies
??? README.md              # This file
??? core/                  # Core functionality
?   ??? app_state.py       # Application state management
?   ??? image_manager.py   # Image loading and processing
?   ??? measurement_engine.py # Measurement calculations
??? gui/                   # User interface
?   ??? main_window.py     # Main application window
?   ??? canvas_widget.py   # Image canvas and interactions  
?   ??? menus.py          # Menu system
?   ??? dialogs.py        # Dialog windows
??? models/               # Data models
?   ??? image_data.py     # Image metadata
?   ??? calibration_data.py # Calibration information
?   ??? measurement_data.py # Measurement results
??? utils/                # Utilities
?   ??? math_utils.py     # Mathematical calculations
??? tests/               # Test suite
    ??? test_core_components.py
    ??? test_integration.py
    ??? test_manual.py
    ??? test_math_utils.py
```

## ?? Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_core_components.py
pytest tests/test_math_utils.py
```

## ?? Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality  
4. **Ensure** all tests pass
5. **Submit** a pull request

## ?? License

This project is open source. See LICENSE file for details.

## ?? Support

For issues, questions, or feature requests:
- **Create an issue** in the project repository
- **Check existing issues** for similar problems
- **Provide details** about your system and steps to reproduce

---

## ?? Professional Measurement Tool

**Industry-standard mouse controls** • **Clean interface** • **Accurate measurements** • **Cross-platform**