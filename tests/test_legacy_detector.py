"""
Legacy Code Detector

Comprehensive tool to scan the codebase for legacy patterns and suggest refactoring opportunities.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import argparse

@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""
    file_path: str
    line_number: int
    issue_type: str
    message: str
    suggestion: str
    severity: str  # 'critical', 'major', 'minor'

class LegacyCodeDetector:
    """Detects legacy code patterns and suggests improvements"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[CodeIssue] = []
        self.stats = defaultdict(int)
        
        # Define patterns to detect
        self.legacy_patterns = {
            'dead_methods': [
                r'def handle_calibration_click\(',
                r'def _manual_screen_to_image_coords\(',
                r'def _manual_image_to_screen_coords\(',
                r'def _force_coordinate_system_refresh\(',
            ],
            'old_attributes': [
                r'self\.calibration_points\s*=',
                r'self\.calibration_screen_points\s*=',
                r'self\.measurement_overlays\s*=',
                r'self\.overlays_visible\s*=',
                r'self\.pan_start\s*=',
                r'self\.right_pan_start\s*=',
            ],
            'debug_code': [
                r'print\(f["\']??',
                r'print\(f["\']?',
                r'print\(f["\']??',
                r'print\(.*DEBUG',
                r'# ? DEBUG:',
                r'# ? FIX:',
                r'# ? NEW:',
            ],
            'deprecated_imports': [
                r'from gui\.coordinate_manager import',
                r'from gui\.event_manager import',
                r'from gui\.tool_handler import',
            ],
            'complex_methods': [
                r'def \w+\([^)]*\):[^}]{500,}',  # Methods over 500 chars
            ],
            'duplicate_logic': [
                r'if.*image_id:.*image_pos = self\.coords.*image_x =.*image_y =',
            ]
        }
        
        self.architectural_violations = {
            'canvas_responsibilities': [
                r'def draw_measurement_overlay.*:.*create_oval',  # Should delegate to OverlayManager
                r'def handle_.*_click.*:.*image_coords =',  # Should delegate to tools
                r'def start_calibration.*:.*config\(cursor',  # Should delegate to CalibrationHandler
            ],
            'manager_violations': [
                r'class.*Manager.*:.*def.*click',  # Managers shouldn't handle clicks directly
            ]
        }
    
    def scan_codebase(self) -> List[CodeIssue]:
        """Scan entire codebase for legacy patterns"""
        self.issues = []
        
        for py_file in self.project_root.glob('**/*.py'):
            if self._should_skip_file(py_file):
                continue
            
            self._scan_file(py_file)
        
        return self.issues
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['__pycache__', '.git', 'test_architecture_validation.py', 'test_legacy_detector.py']
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _scan_file(self, file_path: Path):
        """Scan individual file for issues"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Scan for legacy patterns
            self._scan_legacy_patterns(file_path, content, lines)
            
            # Scan for architectural violations
            self._scan_architectural_violations(file_path, content, lines)
            
            # Scan for code quality issues
            self._scan_code_quality(file_path, content, lines)
            
        except Exception as e:
            self.issues.append(CodeIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=0,
                issue_type='scan_error',
                message=f'Error scanning file: {e}',
                suggestion='Check file encoding and permissions',
                severity='minor'
            ))
    
    def _scan_legacy_patterns(self, file_path: Path, content: str, lines: List[str]):
        """Scan for legacy code patterns"""
        rel_path = str(file_path.relative_to(self.project_root))
        
        for pattern_type, patterns in self.legacy_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        severity = 'critical' if pattern_type in ['dead_methods', 'deprecated_imports'] else 'major'
                        
                        self.issues.append(CodeIssue(
                            file_path=rel_path,
                            line_number=line_num,
                            issue_type=f'legacy_{pattern_type}',
                            message=f'Legacy {pattern_type} found: {line.strip()}',
                            suggestion=self._get_suggestion(pattern_type, line.strip()),
                            severity=severity
                        ))
                        self.stats[f'legacy_{pattern_type}'] += 1
    
    def _scan_architectural_violations(self, file_path: Path, content: str, lines: List[str]):
        """Scan for architectural violations"""
        rel_path = str(file_path.relative_to(self.project_root))
        
        for violation_type, patterns in self.architectural_violations.items():
            for pattern in patterns:
                if re.search(pattern, content, re.DOTALL):
                    self.issues.append(CodeIssue(
                        file_path=rel_path,
                        line_number=0,
                        issue_type=f'architecture_{violation_type}',
                        message=f'Architectural violation: {violation_type}',
                        suggestion=self._get_architecture_suggestion(violation_type),
                        severity='major'
                    ))
                    self.stats[f'architecture_{violation_type}'] += 1
    
    def _scan_code_quality(self, file_path: Path, content: str, lines: List[str]):
        """Scan for code quality issues"""
        rel_path = str(file_path.relative_to(self.project_root))
        
        # Check file length
        if len(lines) > 800:
            self.issues.append(CodeIssue(
                file_path=rel_path,
                line_number=0,
                issue_type='code_quality_length',
                message=f'File too long: {len(lines)} lines',
                suggestion='Consider splitting into smaller modules',
                severity='minor'
            ))
        
        # Check for long methods
        current_method = None
        method_start = 0
        indent_level = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('def '):
                if current_method and (line_num - method_start) > 50:
                    self.issues.append(CodeIssue(
                        file_path=rel_path,
                        line_number=method_start,
                        issue_type='code_quality_method_length',
                        message=f'Method too long: {current_method} ({line_num - method_start} lines)',
                        suggestion='Consider breaking into smaller methods',
                        severity='minor'
                    ))
                
                current_method = stripped.split('(')[0].replace('def ', '')
                method_start = line_num
                indent_level = len(line) - len(line.lstrip())
            
            elif line.strip() and current_method:
                # Check if we've left the method
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and stripped.startswith(('def ', 'class ', 'if __name__')):
                    current_method = None
    
    def _get_suggestion(self, pattern_type: str, line: str) -> str:
        """Get suggestion for fixing legacy pattern"""
        suggestions = {
            'dead_methods': 'Remove this unused method completely',
            'old_attributes': 'This attribute should be moved to appropriate manager class',
            'debug_code': 'Remove debug print statements from production code',
            'deprecated_imports': 'Update import to use new manager location in gui.canvas',
            'complex_methods': 'Break this method into smaller, focused methods',
            'duplicate_logic': 'Extract common logic into a shared method'
        }
        return suggestions.get(pattern_type, 'Consider refactoring this code')
    
    def _get_architecture_suggestion(self, violation_type: str) -> str:
        """Get suggestion for fixing architectural violation"""
        suggestions = {
            'canvas_responsibilities': 'Canvas should delegate to appropriate manager class',
            'manager_violations': 'Managers should focus on their specific responsibility'
        }
        return suggestions.get(violation_type, 'Follow single responsibility principle')
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        report = []
        report.append("?? LEGACY CODE DETECTION REPORT")
        report.append("=" * 50)
        
        # Summary
        report.append(f"\n?? SUMMARY:")
        report.append(f"Total Issues Found: {len(self.issues)}")
        
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        major_issues = [i for i in self.issues if i.severity == 'major']
        minor_issues = [i for i in self.issues if i.severity == 'minor']
        
        report.append(f"Critical Issues: {len(critical_issues)}")
        report.append(f"Major Issues: {len(major_issues)}")
        report.append(f"Minor Issues: {len(minor_issues)}")
        
        # Issues by category
        report.append(f"\n?? ISSUES BY CATEGORY:")
        for issue_type, count in sorted(self.stats.items()):
            report.append(f"{issue_type}: {count}")
        
        # Critical issues detail
        if critical_issues:
            report.append(f"\n?? CRITICAL ISSUES (MUST FIX):")
            for issue in critical_issues:
                report.append(f"  ?? {issue.file_path}:{issue.line_number}")
                report.append(f"     Type: {issue.issue_type}")
                report.append(f"     Issue: {issue.message}")
                report.append(f"     Fix: {issue.suggestion}")
                report.append("")
        
        # Major issues detail
        if major_issues:
            report.append(f"\n?? MAJOR ISSUES (SHOULD FIX):")
            for issue in major_issues[:10]:  # Show first 10
                report.append(f"  ?? {issue.file_path}:{issue.line_number}")
                report.append(f"     Type: {issue.issue_type}")
                report.append(f"     Issue: {issue.message}")
                report.append(f"     Fix: {issue.suggestion}")
                report.append("")
            
            if len(major_issues) > 10:
                report.append(f"   ... and {len(major_issues) - 10} more major issues")
        
        # Recommendations
        report.append(f"\n?? RECOMMENDATIONS:")
        
        if critical_issues:
            report.append("1. ?? Address all critical issues immediately")
            report.append("   - Remove dead methods and attributes")
            report.append("   - Fix deprecated imports")
        
        if any(i.issue_type.startswith('architecture_') for i in self.issues):
            report.append("2. ??? Improve architecture separation")
            report.append("   - Canvas should only delegate to managers")
            report.append("   - Managers should have single responsibilities")
        
        if any(i.issue_type.startswith('code_quality_') for i in self.issues):
            report.append("3. ?? Improve code quality")
            report.append("   - Break down long methods and files")
            report.append("   - Extract common logic")
        
        # Overall assessment
        report.append(f"\n?? OVERALL ASSESSMENT:")
        if len(critical_issues) == 0 and len(major_issues) < 5:
            report.append("? Codebase is in good shape!")
            report.append("   - No critical legacy code issues")
            report.append("   - Architecture is well-structured")
        elif len(critical_issues) == 0:
            report.append("?? Codebase is decent but needs improvement")
            report.append("   - No critical issues, but several major ones")
            report.append("   - Focus on architectural improvements")
        else:
            report.append("?? Codebase needs immediate attention")
            report.append("   - Critical legacy code issues found")
            report.append("   - Address critical issues before proceeding")
        
        return "\n".join(report)

def main():
    """Main function to run legacy code detection"""
    parser = argparse.ArgumentParser(description='Detect legacy code patterns')
    parser.add_argument('--project-root', type=str, default='.',
                        help='Project root directory')
    parser.add_argument('--output', type=str, help='Output report file')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root).resolve()
    detector = LegacyCodeDetector(project_root)
    
    print("?? Scanning codebase for legacy patterns...")
    issues = detector.scan_codebase()
    
    report = detector.generate_report()
    print(report)
    
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"\n?? Report saved to: {args.output}")

if __name__ == "__main__":
    main()