"""
Architecture Validation Tests

Tests to verify the refactored architecture is clean and detect any legacy code patterns.
"""

import pytest
import ast
import inspect
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

class ArchitectureValidator:
    """Validates the refactored architecture and detects legacy patterns"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.legacy_patterns = self._define_legacy_patterns()
        self.architecture_rules = self._define_architecture_rules()
    
    def _define_legacy_patterns(self) -> Dict[str, List[str]]:
        """Define patterns that indicate legacy code"""
        return {
            'dead_methods': [
                'handle_calibration_click',
                '_manual_screen_to_image_coords', 
                '_manual_image_to_screen_coords',
                '_force_coordinate_system_refresh'
            ],
            'old_attributes': [
                'calibration_points',
                'calibration_screen_points',
                'measurement_overlays',
                'overlays_visible',
                'pan_start',
                'right_pan_start'
            ],
            'debug_prints': [
                'print(f"??',
                'print(f"?',
                'print(f"??',
                'CALIBRATION CLICK DEBUG',
                'ZOOM DEBUG'
            ],
            'deprecated_imports': [
                'from gui.coordinate_manager',
                'from gui.event_manager', 
                'from gui.tool_handler'
            ]
        }
    
    def _define_architecture_rules(self) -> Dict[str, any]:
        """Define rules for the new architecture"""
        return {
            'required_managers': [
                'coordinate_manager',
                'event_manager', 
                'tool_handler',
                'overlay_manager',
                'calibration_handler'
            ],
            'canvas_max_lines': 600,  # Main canvas should be simplified
            'single_responsibility': {
                'CoordinateManager': ['screen_to_image', 'image_to_screen'],
                'EventManager': ['handle_left_click', 'handle_right_click'],
                'ToolHandler': ['set_tool', 'handle_measurement_click'],
                'OverlayManager': ['draw_measurement_overlay', 'remove_measurement_overlay'],
                'CalibrationHandler': ['start_calibration', 'handle_click']
            }
        }

class TestArchitectureValidation:
    """Test suite to validate architecture and detect legacy code"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.validator = ArchitectureValidator()
    
    def test_no_legacy_methods_exist(self):
        """Test that no legacy methods exist in any files"""
        legacy_methods_found = []
        
        for py_file in self.validator.project_root.glob('**/*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            for method_name in self.validator.legacy_patterns['dead_methods']:
                if f'def {method_name}(' in content:
                    legacy_methods_found.append(f"{py_file.relative_to(self.validator.project_root)}: {method_name}")
        
        assert not legacy_methods_found, f"Legacy methods found: {legacy_methods_found}"
    
    def test_no_legacy_attributes_in_canvas(self):
        """Test that canvas widget doesn't have old attributes"""
        canvas_file = self.validator.project_root / 'gui' / 'canvas_widget.py'
        content = canvas_file.read_text(encoding='utf-8', errors='ignore')
        
        legacy_attributes_found = []
        for attr in self.validator.legacy_patterns['old_attributes']:
            # Check for self.attribute assignments
            if f'self.{attr}' in content and f'self.{attr} =' in content:
                legacy_attributes_found.append(attr)
        
        assert not legacy_attributes_found, f"Legacy attributes in canvas: {legacy_attributes_found}"
    
    def test_no_debug_prints_in_production_code(self):
        """Test that no debug print statements exist"""
        debug_prints_found = []
        
        for py_file in self.validator.project_root.glob('**/*.py'):
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
                
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            for debug_pattern in self.validator.legacy_patterns['debug_prints']:
                if debug_pattern in content:
                    debug_prints_found.append(f"{py_file.relative_to(self.validator.project_root)}: {debug_pattern}")
        
        # Allow some debug prints but flag excessive ones
        if len(debug_prints_found) > 5:
            pytest.fail(f"Too many debug prints found: {debug_prints_found}")
    
    def test_no_deprecated_imports(self):
        """Test that no deprecated import paths exist"""
        deprecated_imports_found = []
        
        for py_file in self.validator.project_root.glob('**/*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            for deprecated_import in self.validator.legacy_patterns['deprecated_imports']:
                if deprecated_import in content:
                    deprecated_imports_found.append(f"{py_file.relative_to(self.validator.project_root)}: {deprecated_import}")
        
        assert not deprecated_imports_found, f"Deprecated imports found: {deprecated_imports_found}"
    
    def test_canvas_widget_is_simplified(self):
        """Test that main canvas widget is properly simplified"""
        canvas_file = self.validator.project_root / 'gui' / 'canvas_widget.py'
        content = canvas_file.read_text(encoding='utf-8', errors='ignore')
        
        line_count = len(content.splitlines())
        max_lines = self.validator.architecture_rules['canvas_max_lines']
        
        assert line_count <= max_lines, f"Canvas widget has {line_count} lines, should be <= {max_lines}"
    
    def test_managers_exist_and_initialized(self):
        """Test that all required managers exist and are properly initialized"""
        canvas_file = self.validator.project_root / 'gui' / 'canvas_widget.py'
        content = canvas_file.read_text(encoding='utf-8', errors='ignore')
        
        missing_managers = []
        for manager in self.validator.architecture_rules['required_managers']:
            if f'self.{manager} =' not in content:
                missing_managers.append(manager)
        
        assert not missing_managers, f"Missing managers in canvas: {missing_managers}"
    
    def test_manager_files_exist(self):
        """Test that all manager files exist in correct locations"""
        expected_files = [
            'gui/canvas/coordinate_manager.py',
            'gui/canvas/event_manager.py',
            'gui/canvas/tool_handler.py', 
            'gui/canvas/overlay_manager.py',
            'gui/canvas/calibration_handler.py'
        ]
        
        missing_files = []
        for file_path in expected_files:
            if not (self.validator.project_root / file_path).exists():
                missing_files.append(file_path)
        
        assert not missing_files, f"Missing manager files: {missing_files}"
    
    def test_tool_hierarchy_exists(self):
        """Test that tool class hierarchy is properly implemented"""
        tool_files = [
            'gui/canvas/tools/base_tool.py',
            'gui/canvas/tools/pan_tool.py',
            'gui/canvas/tools/measurement_tool.py',
            'gui/canvas/tools/polygon_tool.py'
        ]
        
        missing_tool_files = []
        for file_path in tool_files:
            if not (self.validator.project_root / file_path).exists():
                missing_tool_files.append(file_path)
        
        assert not missing_tool_files, f"Missing tool files: {missing_tool_files}"
    
    def test_single_responsibility_principle(self):
        """Test that managers follow single responsibility principle"""
        violations = []
        
        for manager_name, expected_methods in self.validator.architecture_rules['single_responsibility'].items():
            # This is a simplified check - in a real implementation you'd parse the AST
            # For now, just verify the key methods exist
            
            # Find the manager file
            manager_file = None
            for py_file in self.validator.project_root.glob('**/*.py'):
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if f'class {manager_name}' in content:
                    manager_file = py_file
                    break
            
            if manager_file:
                content = manager_file.read_text(encoding='utf-8', errors='ignore')
                for method in expected_methods:
                    if f'def {method}(' not in content:
                        violations.append(f"{manager_name} missing {method}")
        
        assert not violations, f"Single responsibility violations: {violations}"

class TestFunctionalIntegration:
    """Test that the refactored architecture works correctly"""
    
    def test_imports_work_correctly(self):
        """Test that all imports work without circular dependencies"""
        try:
            # Test core imports
            import core.app_state
            import core.image_manager
            import core.measurement_engine
            
            # Test GUI imports
            import gui.canvas_widget
            import gui.main_window
            
            # Test manager imports
            from gui.canvas.coordinate_manager import CoordinateManager
            from gui.canvas.event_manager import EventManager
            from gui.canvas.tool_handler import ToolHandler
            from gui.canvas.overlay_manager import OverlayManager
            from gui.canvas.calibration_handler import CalibrationHandler
            
            # Test tool imports
            from gui.canvas.tools import BaseTool, PanTool, MeasurementTool, PolygonTool
            
        except ImportError as e:
            pytest.fail(f"Import error: {e}")
    
    def test_manager_initialization(self):
        """Test that managers can be initialized without errors"""
        try:
            # Mock canvas object for testing
            class MockCanvas:
                def __init__(self):
                    self.current_image = None
                    self.image_id = None
                    self.actual_zoom_level = 1.0
                    self.is_calibrating = False
                    self.current_tool = "pan"
                    self.temp_points = []
                
                def coords(self, item_id):
                    return (0, 0)
                
                def _update_actual_zoom_level(self):
                    pass
                
                def config(self, **kwargs):
                    pass
                
                def create_oval(self, *args, **kwargs):
                    return 1
                
                def create_text(self, *args, **kwargs):
                    return 2
                    
                def winfo_width(self):
                    return 800
                    
                def bind(self, *args, **kwargs):
                    pass
                    
                def focus_set(self):
                    pass
            
            mock_canvas = MockCanvas()
            
            # Test manager initialization
            from gui.canvas.coordinate_manager import CoordinateManager
            from gui.canvas.event_manager import EventManager
            from gui.canvas.tool_handler import ToolHandler
            from gui.canvas.overlay_manager import OverlayManager
            from gui.canvas.calibration_handler import CalibrationHandler
            
            coord_mgr = CoordinateManager(mock_canvas)
            event_mgr = EventManager(mock_canvas)
            tool_handler = ToolHandler(mock_canvas)
            overlay_mgr = OverlayManager(mock_canvas)
            calib_handler = CalibrationHandler(mock_canvas)
            
            # Basic functionality test
            assert coord_mgr.screen_to_image(100, 200) == (100.0, 200.0)  # No image case
            assert tool_handler.get_points_needed("distance") == 2
            
        except Exception as e:
            pytest.fail(f"Manager initialization failed: {e}")

class TestCodeQualityMetrics:
    """Test code quality metrics of the refactored codebase"""
    
    def test_no_duplicate_code_blocks(self):
        """Test for duplicate code blocks that should be refactored"""
        # This is a simplified version - in practice you'd use more sophisticated tools
        code_blocks = {}
        duplicates_found = []
        
        for py_file in Path(__file__).parent.parent.glob('**/*.py'):
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
                
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Look for method definitions as potential duplicates
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and len(lines) > i + 5:
                    # Get a small block to check for similarity
                    block = '\n'.join(lines[i:i+5])
                    block_hash = hash(block.replace(' ', '').replace('\t', ''))
                    
                    if block_hash in code_blocks:
                        duplicates_found.append(f"Potential duplicate: {py_file.name} and {code_blocks[block_hash]}")
                    else:
                        code_blocks[block_hash] = py_file.name
        
        # Allow a few false positives, but flag excessive duplication
        if len(duplicates_found) > 10:
            pytest.fail(f"Too much duplicate code found: {duplicates_found[:5]}...")
    
    def test_proper_separation_of_concerns(self):
        """Test that code is properly separated by concerns"""
        # Check that canvas widget delegates properly
        canvas_file = Path(__file__).parent.parent / 'gui' / 'canvas_widget.py'
        content = canvas_file.read_text(encoding='utf-8', errors='ignore')
        
        # Canvas should delegate to managers, not implement complex logic
        delegation_patterns = [
            'self.coordinate_manager.',
            'self.event_manager.',
            'self.tool_handler.',
            'self.overlay_manager.',
            'self.calibration_handler.'
        ]
        
        delegation_count = sum(content.count(pattern) for pattern in delegation_patterns)
        
        # Should have many delegations if properly refactored
        assert delegation_count > 10, f"Canvas should delegate more to managers, found {delegation_count} delegations"

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])