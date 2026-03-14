# Optical Measurement Tool

A professional desktop application for precise measurements on digital images using a pixel-to-real-world calibration system.

![Version](https://img.shields.io/badge/version-2.5-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Features

### Measurement Tools (8 types)

| Tool | Shortcut | Description |
|------|----------|-------------|
| Distance | `F5` | Two-point linear distance |
| Radius | `F6` | Circle radius from 3 points on circumference |
| Angle | `F7` | Angle at vertex from 3 points |
| Two-Line Angle | `F8` | Angle between two lines (4 points) |
| Polygon Area | `F9` | Area + perimeter from 3+ points (right-click to close) |
| Coordinates | `F10` | Single point or difference between two points |
| Point-to-Line | `F11` | Perpendicular distance from point to line |
| Arc Length | `F12` | Arc length through 3 points |

### Interface

- **Toolbar** with icons for all tools and pan mode
- **Minimap** showing full image thumbnail with viewport indicator
- **Grid overlay** toggled with `G`
- **Brightness/Contrast** sliders in the sidebar
- **Measurement panel** with selection, properties, and highlighting
- **Overlay visibility** toggle with `F2`
- **Undo/Redo** support (`Ctrl+Z` / `Ctrl+Y`)

### Calibration System

Two-point calibration with any real-world unit:

1. Select Calibration tool (`F4`)
2. Click two points on a known distance
3. Enter the real distance and units
4. All measurements display in those units

### Image and Export

- **Formats**: JPEG, PNG, BMP, TIFF, GIF
- **Export** (`Ctrl+E`): Save annotated image with all measurement overlays rendered
- **Zoom**: Mouse wheel or `Ctrl++` / `Ctrl+-`, fit with `Ctrl+0`, actual size with `Ctrl+1`
- **Pan**: Right-click drag (always available) or `Space` for pan tool

## Download

**Standalone Windows executable** (no Python required):

Go to [Releases](../../releases) and download `OpticalMeasurement.exe`

## Installation (from source)

```bash
git clone https://github.com/PauBasCalopa/OpticalMeasurement.git
cd OpticalMeasurement
pip install -r requirements.txt
python main.py
```

### Build standalone .exe

```bash
build.bat
```

Generates `dist/OpticalMeasurement.exe` — a single-file standalone executable.

## Keyboard Shortcuts

### File

| Key | Action |
|-----|--------|
| `Ctrl+O` | Open Image |
| `Ctrl+W` | Close Image |
| `Ctrl+E` | Export Image |

### Edit

| Key | Action |
|-----|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Delete` | Delete Selected Measurement |
| `Ctrl+Shift+C` | Clear All Measurements |

### View

| Key | Action |
|-----|--------|
| `Ctrl++` | Zoom In |
| `Ctrl+-` | Zoom Out |
| `Ctrl+0` | Zoom to Fit |
| `Ctrl+1` | Actual Size |
| `Ctrl+R` | Reset View |
| `Space` | Pan Tool |
| `F2` | Toggle Overlays |
| `G` | Toggle Grid |

### Tools

| Key | Action |
|-----|--------|
| `F4` | Calibration |
| `F5` - `F12` | Measurement tools (see table above) |
| `Esc` | Cancel / Reset tool |
| `F1` | Show Keyboard Shortcuts |

## Project Structure

```
OpticalMeasurement/
├── main.py                    # Entry point
├── build.bat                  # Standalone .exe build script
├── requirements.txt           # Python dependencies
├── assets/                    # Application icon
├── core/
│   ├── app_state.py           # Centralized state + undo/redo
│   ├── image_manager.py       # Image loading, brightness/contrast
│   └── measurement_engine.py  # Measurement calculations
├── gui/
│   ├── main_window.py         # Main application window
│   ├── canvas_widget.py       # Image canvas display
│   ├── toolbar.py             # Tool buttons with icons
│   ├── minimap_widget.py      # Thumbnail viewport navigator
│   ├── menus.py               # Menu bar + shortcuts
│   ├── dialogs.py             # Dialog windows
│   └── canvas/
│       ├── event_manager.py   # Mouse/keyboard event handling
│       ├── overlay_renderer.py# Measurement overlay rendering
│       ├── tool_handler.py    # Tool activation/switching
│       ├── calibration_handler.py
│       └── tools/
│           ├── base_tool.py   # Abstract tool base
│           ├── measurement_tool.py
│           ├── polygon_tool.py
│           └── pan_tool.py
├── models/
│   ├── calibration_data.py    # Calibration scale factor
│   ├── image_data.py          # Image metadata
│   ├── measurement_data.py    # 8 measurement dataclasses
│   └── view_state.py          # Zoom, pan, canvas/image sizes
├── services/
│   ├── coordinate_service.py  # Image <-> screen coordinate conversions
│   └── export_service.py      # Image export with overlays
└── utils/
    └── math_utils.py          # Geometric calculations
```

## Technical Details

- **Built with**: Python, tkinter, Pillow, numpy
- **Architecture**: MVC-inspired with centralized state, stateless coordinate service, and modular canvas tools
- **No internet required**: Fully offline operation
- **High-res support**: Handles large images efficiently

## License

MIT License. See [LICENSE](LICENSE) for details.

---

By Pau Bas Calopa &copy; 2026
