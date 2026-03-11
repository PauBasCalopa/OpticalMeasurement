# Optical Measurement Tool - Software Development Plan

## 1. Project Overview

### 1.1 Project Description
The Optical Measurement Tool is a desktop application that enables users to perform precise measurements on digital images by establishing a pixel-to-real-world calibration and then measuring distances, radii, and angles directly on the image.

### 1.2 Project Goals
- Provide accurate measurement capabilities for images
- Establish calibration system for pixel-to-unit conversion
- Support multiple measurement types (distance, radius, angle)
- Deliver intuitive user interface for technical and non-technical users
- Export measurement results for further analysis

### 1.3 Target Audience
- Engineers and technicians
- Quality control professionals
- Researchers and scientists
- Educational institutions
- Manufacturing and inspection personnel

## 2. Functional Requirements

### 2.1 Image Management

#### 2.1.1 Image Loading
- **REQ-IMG-001**: Support common image formats (JPEG, PNG, BMP, TIFF, GIF)
- **REQ-IMG-002**: Handle high-resolution images up to 50MP
- **REQ-IMG-003**: Display image with initial fit-to-window scaling
- **REQ-IMG-004**: Maintain original image aspect ratio
- **REQ-IMG-005**: Support drag-and-drop image loading
- **REQ-IMG-006**: Enable closing current image and opening new image
- **REQ-IMG-007**: Clear all measurements and calibration when new image is loaded

#### 2.1.2 Image Display
- **REQ-IMG-008**: Implement smooth zoom functionality (25% to 1000%)
- **REQ-IMG-009**: Enable pan functionality with mouse drag
- **REQ-IMG-010**: Show zoom level indicator
- **REQ-IMG-011**: Implement zoom-to-fit and actual size buttons
- **REQ-IMG-012**: Display image metadata (dimensions, format, file size)

### 2.2 Calibration System

#### 2.2.1 Two-Point Calibration
- **REQ-CAL-001**: Enable user to select two points on the image
- **REQ-CAL-002**: Accept real-world distance input via dialog (numeric value only, no unit specification)
- **REQ-CAL-003**: Calculate and store pixels-per-unit ratio
- **REQ-CAL-004**: Use generic "units" allowing user to define their own scale (no predefined unit systems)
- **REQ-CAL-005**: Display calibration line with measurement overlay
- **REQ-CAL-006**: Allow recalibration at any time

#### 2.2.2 Calibration Management
- **REQ-CAL-008**: Display current calibration status and scale
- **REQ-CAL-009**: Allow calibration reset
- **REQ-CAL-010**: Show measurement precision based on pixel resolution (±X units)

### 2.3 Measurement Tools

#### 2.3.1 Distance Measurement
- **REQ-MEAS-001**: Enable two-point distance measurement
- **REQ-MEAS-002**: Display real-time measurement during point selection
- **REQ-MEAS-003**: Show measurement line overlay on image
- **REQ-MEAS-004**: Display measurement result with appropriate precision
- **REQ-MEAS-005**: Support multiple simultaneous distance measurements

#### 2.3.2 Radius Measurement (3-Point Method)
- **REQ-MEAS-006**: Enable three-point circle radius measurement
- **REQ-MEAS-007**: Calculate circle center and radius from three points
- **REQ-MEAS-008**: Display circle overlay with center point
- **REQ-MEAS-009**: Show radius measurement result
- **REQ-MEAS-010**: Handle collinear point detection and error messaging

#### 2.3.3 Angle Measurement
- **REQ-MEAS-011**: Enable three-point angle measurement
- **REQ-MEAS-012**: Display angle arc overlay
- **REQ-MEAS-013**: Support both degrees and radians
- **REQ-MEAS-014**: Show angle measurement with vertex indication
- **REQ-MEAS-015**: Calculate both acute and obtuse angles as appropriate
- **REQ-MEAS-016**: Enable angle measurement between two lines (four-point method)
- **REQ-MEAS-017**: Display line segments and angle indication for two-line angle measurement

#### 2.3.4 Area Measurement
- **REQ-MEAS-018**: Enable polygon area measurement (multi-point method)
- **REQ-MEAS-019**: Display polygon outline overlay
- **REQ-MEAS-020**: Calculate area using shoelace formula
- **REQ-MEAS-021**: Support closing polygon automatically or manually

#### 2.3.5 Coordinate Measurement
- **REQ-MEAS-022**: Enable point coordinate display
- **REQ-MEAS-023**: Show X,Y coordinates for selected points
- **REQ-MEAS-024**: Display coordinate differences (ΔX, ΔY) between two points

#### 2.3.6 Advanced Geometric Measurement
- **REQ-MEAS-025**: Enable point-to-line distance measurement
- **REQ-MEAS-026**: Enable arc length measurement (three-point method)
- **REQ-MEAS-027**: Display arc overlay with length indication

#### 2.3.7 Measurement Management
- **REQ-MEAS-028**: Assign unique labels to measurements
- **REQ-MEAS-029**: Enable measurement deletion and editing
- **REQ-MEAS-030**: Show/hide measurement overlays
- **REQ-MEAS-031**: Display measurement list with results
- **REQ-MEAS-032**: Support undo/redo operations

### 2.4 User Interface

#### 2.4.1 Main Interface
- **REQ-UI-001**: Provide main canvas for image display and interaction
- **REQ-UI-002**: Include toolbar with measurement tools
- **REQ-UI-003**: Display measurement results panel
- **REQ-UI-004**: Show calibration status bar
- **REQ-UI-005**: Implement standard menu structure:
- **File**: Open Image, Close Image, Export Image, Exit
- **Edit**: Undo, Redo, Clear All Measurements
- **View**: Zoom In/Out/Fit, Show/Hide Overlays
- **Tools**: Calibration, Measurement Tools
- **Help**: About, User Guide

#### 2.4.2 Interactive Elements
- **REQ-UI-006**: Provide visual feedback for point selection (crosshair cursor)
- **REQ-UI-007**: Highlight selectable points and measurements
- **REQ-UI-008**: Show measurement previews during tool use
- **REQ-UI-009**: Display tooltips and contextual help
- **REQ-UI-010**: Implement keyboard shortcuts for common operations

#### 2.4.3 Dialogs and Forms
- **REQ-UI-011**: Calibration input dialog for numeric value (no unit selection)
- **REQ-UI-012**: Measurement properties dialog
- **REQ-UI-013**: Export options dialog
- **REQ-UI-014**: About and help dialogs
- **REQ-UI-015**: Error and confirmation dialogs

### 2.5 Data Management

#### 2.5.1 Data Export
- **REQ-DATA-001**: Export annotated image with measurements (PNG/JPG format)

## 3. Non-Functional Requirements

### 3.1 Performance
- **REQ-PERF-001**: Application startup time < 3 seconds
- **REQ-PERF-002**: Image loading time < 2 seconds for files up to 20MB
- **REQ-PERF-003**: Zoom/pan operations should be smooth (>30 FPS)
- **REQ-PERF-004**: Measurement calculations should be instantaneous (<100ms)
- **REQ-PERF-005**: Memory usage should not exceed 2GB for typical operations

### 3.2 Accuracy and Precision
- **REQ-ACC-001**: Measurement accuracy limited by image resolution and calibration quality
- **REQ-ACC-002**: Support sub-pixel accuracy for measurements
- **REQ-ACC-003**: Display measurements with appropriate significant figures
- **REQ-ACC-004**: Maintain precision through zoom operations
- **REQ-ACC-005**: Implement error propagation calculations

### 3.3 Usability
- **REQ-USE-001**: Interface should be intuitive for users with minimal training
- **REQ-USE-002**: Provide comprehensive help documentation
- **REQ-USE-003**: Support standard Windows keyboard shortcuts
- **REQ-USE-004**: Implement consistent visual design following Windows guidelines
- **REQ-USE-005**: Provide clear error messages and recovery suggestions

### 3.4 Compatibility
- **REQ-COMP-001**: Support Windows 10, Windows 11, macOS, and Linux
- **REQ-COMP-002**: Compatible with standard display resolutions (1920x1080 to 4K)
- **REQ-COMP-003**: Support high-DPI displays
- **REQ-COMP-004**: Minimum system requirements: 4GB RAM, 1GB free disk space
- **REQ-COMP-005**: Python 3.8+ runtime dependency

### 3.5 Reliability
- **REQ-REL-001**: Application should handle unexpected shutdowns gracefully
- **REQ-REL-002**: Implement comprehensive error handling
- **REQ-REL-003**: Provide data recovery mechanisms
- **REQ-REL-004**: Log errors for debugging purposes
- **REQ-REL-005**: Handle corrupt or unsupported image files gracefully

## 4. Technical Architecture

### 4.1 Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: tkinter (built-in, cross-platform)
- **Image Processing**: Pillow (PIL) for image loading and manipulation
- **Mathematical Operations**: numpy for fast calculations
- **Graphics/Overlays**: tkinter Canvas for interactive measurement overlays
- **Data Handling**: Built-in json module for simple data operations
- **Testing**: pytest for unit testing

### 4.2 Application Architecture

#### 4.2.1 Core Components
- **ImageManager**: Image loading, processing, and display using Pillow
- **CalibrationManager**: Pixel-to-unit conversion calculations using numpy
- **MeasurementEngine**: Distance, radius, and angle calculations using numpy
- **CanvasController**: tkinter Canvas management for overlays and interactions
- **ExportManager**: Annotated image export using Pillow

#### 4.2.2 Data Models (Python Classes)
- **ImageData**: Image metadata and display properties
- **CalibrationData**: Scale factor and unit information  
- **MeasurementBase**: Base class for all measurements
- **DistanceMeasurement**: Two-point distance data
- **RadiusMeasurement**: Three-point radius data
- **AngleMeasurement**: Three-point angle data
- **TwoLineAngleMeasurement**: Four-point angle between two lines data
- **PolygonAreaMeasurement**: Multi-point polygon area data
- **CoordinateMeasurement**: Single or dual-point coordinate data
- **PointToLineMeasurement**: Point-to-line distance data
- **ArcLengthMeasurement**: Three-point arc length data

#### 4.2.3 User Interface Structure (tkinter)
```
MainWindow (tk.Tk)
├── MenuBar (tk.Menu)
├── ToolFrame (tk.Frame)
│   └── ToolButtons (tk.Button)
├── MainFrame (tk.Frame)
│   ├── ImageCanvas (tk.Canvas) - Interactive image display and overlays
│   └── ScrollBars (tk.Scrollbar)
├── SidePanel (tk.Frame)
│   ├── CalibrationFrame (tk.LabelFrame)
│   ├── MeasurementsFrame (tk.LabelFrame)
│   └── MeasurementsList (tk.Listbox)
└── StatusBar (tk.Frame)
    └── StatusLabels (tk.Label)
```

### 4.3 Mathematical Algorithms

#### 4.3.1 Distance Calculation
```
distance = ?[(x?-x?)² + (y?-y?)²] × scale_factor
```

#### 4.3.2 Radius Calculation (3-Point Method)
```
Given points A(x?,y?), B(x?,y?), C(x?,y?):
1. Calculate circumcenter using perpendicular bisectors
2. Calculate radius as distance from circumcenter to any point
3. Apply scale factor
```

#### 4.3.3 Angle Calculation
```
Given points A, B(vertex), C:
Vector BA = (x?-x?, y?-y?)
Vector BC = (x?-x?, y?-y?)
angle = arccos[(BA·BC)/(|BA||BC|)]
```

#### 4.3.4 Two-Line Angle Calculation
```
Given two lines:
Line 1: points A(x₁,y₁), B(x₂,y₂)
Line 2: points C(x₃,y₃), D(x₄,y₄)
Vector 1 = (x₂-x₁, y₂-y₁)
Vector 2 = (x₄-x₃, y₄-y₃)
angle = arccos[(Vector1·Vector2)/(|Vector1||Vector2|)]
```

#### 4.3.5 Polygon Area Calculation (Shoelace Formula)
```
Given n points (x₁,y₁), (x₂,y₂), ..., (xₙ,yₙ):
area = 0.5 × |∑(xᵢ × y(ᵢ+1) - x(ᵢ+1) × yᵢ)| × scale_factor²
where i goes from 1 to n, and (n+1) wraps to 1
```

#### 4.3.6 Point-to-Line Distance
```
Given point P(x₀,y₀) and line through A(x₁,y₁), B(x₂,y₂):
distance = |((y₂-y₁)×x₀ - (x₂-x₁)×y₀ + x₂×y₁ - y₂×x₁)| / 
           √((y₂-y₁)² + (x₂-x₁)²) × scale_factor
```

#### 4.3.7 Arc Length Calculation
```
Given three points A, B, C on an arc:
1. Calculate radius using circumcenter method (same as radius calculation)
2. Calculate central angle θ between vectors from center to A and C
3. arc_length = radius × θ × scale_factor
```

## 5. User Interface Specifications

### 5.1 Main Window Layout
- **Title Bar**: Application name and current file
- **Menu Bar**: File, Edit, View, Tools, Help
- **Tool Bar**: Quick access to measurement tools and common functions
- **Main Canvas**: Scrollable, zoomable image display area
- **Properties Panel**: Current tool settings and measurement properties
- **Results Panel**: List of measurements with values
- **Status Bar**: Zoom level, calibration status, cursor coordinates

### 5.2 Tool Icons and Cursors
- **Calibration Tool**: Ruler icon, crosshair cursor
- **Distance Tool**: Line icon, precision cursor
- **Radius Tool**: Circle icon, crosshair cursor
- **Angle Tool**: Angle icon, precision cursor
- **Two-Line Angle Tool**: Double-line angle icon, precision cursor
- **Area Tool**: Polygon icon, crosshair cursor
- **Coordinate Tool**: Crosshair icon, precision cursor
- **Point-to-Line Tool**: Point-line icon, precision cursor
- **Arc Length Tool**: Arc icon, crosshair cursor
- **Pan Tool**: Hand icon, grab cursor
- **Zoom Tool**: Magnifying glass icon

### 5.3 Color Scheme and Visual Design
- **Background**: Light gray (#F5F5F5)
- **Primary UI**: Windows system colors
- **Measurement Overlays**: Bright colors (red, blue, green) for visibility
- **Selection Highlights**: Blue (#0078D4)
- **Error States**: Red (#D13438)
- **Success States**: Green (#107C10)

## 6. File Formats and Data Structure

### 6.2 Export Formats

#### 6.2.1 Annotated Image Export
- Export current image with all measurement overlays visible
- Support PNG format (lossless, good for technical drawings)
- Support JPG format (smaller file size for sharing)
- Include measurement labels, values, and visual indicators
- Maintain original image quality while adding measurement annotations

## 7. Testing Requirements

### 7.1 Unit Testing
- **Mathematical calculations accuracy**
- **Coordinate transformations**
- **Data model validation**
- **File I/O operations**
- **Calibration calculations**

### 7.2 Integration Testing
- **UI interaction workflows**
- **Image loading and display**
- **Measurement tool operations**
- **Export functionality**

### 7.3 User Acceptance Testing
- **Complete measurement workflows**
- **Accuracy validation with known measurements**
- **Usability testing with target users**
- **Performance testing with various image sizes**
- **Error handling scenarios**

## 8. Implementation Phases

### 8.1 Phase 1: Core Foundation (MVP)
- Basic tkinter application structure
- Image loading and display using Pillow
- Zoom and pan functionality on Canvas
- Two-point calibration with numpy calculations
- Distance measurement tool
- Basic image export (PNG/JPG) using Pillow

### 8.2 Phase 2: Extended Measurements
- Radius measurement (3-point method)
- Angle measurement (3-point method)
- Two-line angle measurement (4-point method)
- Measurement management (labels, deletion)
- Enhanced UI polish

### 8.3 Phase 3: Advanced Measurements
- Polygon area measurement
- Point coordinate display and coordinate differences
- Point-to-line distance measurement
- Arc length measurement

### 8.4 Phase 4: Advanced Features
- Undo/redo system

### 8.5 Phase 5: Polish and Optimization
- Performance optimization
- UI/UX improvements
- Comprehensive testing
- Documentation completion
- Installer creation

## 9. Risk Assessment

### 9.1 Technical Risks
- **High-resolution image performance**: Mitigation through efficient rendering
- **Measurement accuracy**: Extensive testing with calibrated references
- **UI responsiveness**: Asynchronous operations and progress indicators
- **Memory management**: Proper image disposal and caching strategies

### 9.2 User Experience Risks
- **Learning curve**: Comprehensive tutorials and contextual help
- **Workflow complexity**: Intuitive tool design and clear visual feedback
- **Error recovery**: Robust error handling and data recovery features

## 10. Success Criteria

### 10.1 Functional Success
- All measurement types work accurately within image resolution limits
- Calibration system provides reliable pixel-to-unit conversion
- Export functionality generates usable data formats
- Application handles common image formats reliably

### 10.2 Performance Success
- Smooth operation with images up to 50MP
- Response time under 100ms for measurements
- Startup time under 3 seconds
- Memory usage remains reasonable during extended use

### 10.3 User Success
- Users can complete measurement workflows without training
- Measurement results match manual/physical measurements within tolerance
- Export formats integrate well with analysis tools
- Application provides clear feedback for all user actions

---

**Document Version**: 1.0  
**Last Updated**: [Current Date]  
**Author**: Development Team  
**Review Status**: Draft