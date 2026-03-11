"""
Code Simplification Analyzer

Analyzes the codebase for refactoring opportunities and suggests simplifications.
"""

import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

@dataclass
class SimplificationOpportunity:
    """Represents an opportunity for code simplification"""
    file_path: str
    line_number: int
    opportunity_type: str
    current_code: str
    suggested_code: str
    benefit: str
    complexity_reduction: int  # 1-5 scale

class CodeSimplificationAnalyzer:
    """Analyzes code for simplification opportunities"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.opportunities: List[SimplificationOpportunity] = []
        self.metrics = defaultdict(int)
    
    def analyze_codebase(self) -> List[SimplificationOpportunity]:
        """Analyze entire codebase for simplification opportunities"""
        self.opportunities = []
        
        for py_file in self.project_root.glob('**/*.py'):
            if self._should_skip_file(py_file):
                continue
            
            self._analyze_file(py_file)
        
        return self.opportunities
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['__pycache__', '.git', 'test_']
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path):
        """Analyze individual file for simplification opportunities"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree, lines)
            except SyntaxError:
                pass  # Skip files with syntax errors
            
            # Text-based analysis
            self._analyze_text_patterns(file_path, content, lines)
            
        except Exception as e:
            pass  # Skip problematic files
    
    def _analyze_ast(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """Analyze AST for structural simplification opportunities"""
        rel_path = str(file_path.relative_to(self.project_root))
        
        class SimplificationVisitor(ast.NodeVisitor):
            def __init__(self, analyzer, rel_path, lines):
                self.analyzer = analyzer
                self.rel_path = rel_path
                self.lines = lines
            
            def visit_FunctionDef(self, node):
                # Check for overly complex methods
                if len(node.body) > 20:
                    self.analyzer._add_opportunity(
                        file_path=self.rel_path,
                        line_number=node.lineno,
                        opportunity_type='method_too_complex',
                        current_code=f'def {node.name}(...): # {len(node.body)} statements',
                        suggested_code='Break into smaller, focused methods',
                        benefit='Improved readability and maintainability',
                        complexity_reduction=3
                    )
                
                # Check for too many parameters
                if len(node.args.args) > 5:
                    self.analyzer._add_opportunity(
                        file_path=self.rel_path,
                        line_number=node.lineno,
                        opportunity_type='too_many_parameters',
                        current_code=f'def {node.name}({len(node.args.args)} parameters)',
                        suggested_code='Use parameter object or configuration class',
                        benefit='Easier to understand and maintain',
                        complexity_reduction=2
                    )
                
                self.generic_visit(node)
            
            def visit_If(self, node):
                # Check for deeply nested conditionals
                depth = self._get_nesting_depth(node)
                if depth > 3:
                    self.analyzer._add_opportunity(
                        file_path=self.rel_path,
                        line_number=node.lineno,
                        opportunity_type='deep_nesting',
                        current_code=f'if statement with {depth} levels of nesting',
                        suggested_code='Use early returns or extract methods',
                        benefit='Reduced cognitive complexity',
                        complexity_reduction=2
                    )
                
                self.generic_visit(node)
            
            def _get_nesting_depth(self, node, depth=0):
                """Calculate nesting depth of conditionals"""
                max_depth = depth
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                        if child != node:  # Don't count the current node
                            child_depth = self._get_nesting_depth(child, depth + 1)
                            max_depth = max(max_depth, child_depth)
                return max_depth
        
        visitor = SimplificationVisitor(self, rel_path, lines)
        visitor.visit(tree)
    
    def _analyze_text_patterns(self, file_path: Path, content: str, lines: List[str]):
        """Analyze text patterns for simplification opportunities"""
        rel_path = str(file_path.relative_to(self.project_root))
        
        # Check for duplicate code blocks
        self._find_duplicate_blocks(rel_path, lines)
        
        # Check for long parameter lists
        self._find_long_parameter_lists(rel_path, lines)
        
        # Check for complex conditionals
        self._find_complex_conditionals(rel_path, lines)
        
        # Check for magic numbers
        self._find_magic_numbers(rel_path, lines)
        
        # Check for string concatenation patterns
        self._find_string_concatenation_issues(rel_path, lines)
    
    def _find_duplicate_blocks(self, rel_path: str, lines: List[str]):
        """Find potential duplicate code blocks"""
        # Simple heuristic: look for similar method bodies
        method_bodies = []
        current_method = None
        method_start = 0
        
        for line_num, line in enumerate(lines):
            if line.strip().startswith('def '):
                if current_method:
                    method_bodies.append((current_method, method_start, line_num - 1))
                current_method = line.strip()
                method_start = line_num
        
        # Check for similar method patterns
        for i, (method1, start1, end1) in enumerate(method_bodies):
            for method2, start2, end2 in method_bodies[i+1:]:
                if self._are_methods_similar(lines[start1:end1], lines[start2:end2]):
                    self._add_opportunity(
                        file_path=rel_path,
                        line_number=start1 + 1,
                        opportunity_type='duplicate_logic',
                        current_code=f'Similar logic in {method1} and {method2}',
                        suggested_code='Extract common logic into shared method',
                        benefit='DRY principle, easier maintenance',
                        complexity_reduction=3
                    )
    
    def _are_methods_similar(self, method1_lines: List[str], method2_lines: List[str]) -> bool:
        """Check if two methods have similar structure"""
        # Simple similarity check based on line count and keywords
        if abs(len(method1_lines) - len(method2_lines)) > 3:
            return False
        
        # Check for common patterns
        method1_text = ' '.join(method1_lines).lower()
        method2_text = ' '.join(method2_lines).lower()
        
        common_patterns = ['if ', 'for ', 'return ', 'self.']
        similarity_score = 0
        
        for pattern in common_patterns:
            if pattern in method1_text and pattern in method2_text:
                similarity_score += 1
        
        return similarity_score >= 3 and len(method1_lines) > 5
    
    def _find_long_parameter_lists(self, rel_path: str, lines: List[str]):
        """Find methods with too many parameters"""
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('def ') and '(' in line and ')' in line:
                # Count parameters (simple heuristic)
                param_part = line[line.find('('):line.find(')')+1]
                param_count = param_part.count(',') + 1 if param_part.count(',') > 0 else (1 if 'self' in param_part else 0)
                
                if param_count > 5:
                    self._add_opportunity(
                        file_path=rel_path,
                        line_number=line_num,
                        opportunity_type='too_many_parameters',
                        current_code=line.strip()[:80] + '...' if len(line.strip()) > 80 else line.strip(),
                        suggested_code='Use parameter object or kwargs',
                        benefit='Easier to understand and extend',
                        complexity_reduction=2
                    )
    
    def _find_complex_conditionals(self, rel_path: str, lines: List[str]):
        """Find overly complex conditional statements"""
        for line_num, line in enumerate(lines, 1):
            if 'if ' in line and ('and' in line or 'or' in line):
                # Count logical operators
                logical_ops = line.count(' and ') + line.count(' or ')
                if logical_ops > 2:
                    self._add_opportunity(
                        file_path=rel_path,
                        line_number=line_num,
                        opportunity_type='complex_conditional',
                        current_code=line.strip()[:80] + '...' if len(line.strip()) > 80 else line.strip(),
                        suggested_code='Extract to boolean methods or variables',
                        benefit='Improved readability and testability',
                        complexity_reduction=2
                    )
    
    def _find_magic_numbers(self, rel_path: str, lines: List[str]):
        """Find magic numbers that should be constants"""
        magic_number_pattern = re.compile(r'\b\d{2,}\b')  # Numbers with 2+ digits
        common_numbers = {'100', '200', '300', '400', '500', '800', '1000'}  # Common UI numbers
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip().startswith('#'):  # Skip comments
                for match in magic_number_pattern.finditer(line):
                    number = match.group()
                    if number in common_numbers and 'create_' not in line and 'width' not in line and 'height' not in line:
                        self._add_opportunity(
                            file_path=rel_path,
                            line_number=line_num,
                            opportunity_type='magic_number',
                            current_code=f'Magic number: {number}',
                            suggested_code=f'Use named constant: MAX_WIDTH = {number}',
                            benefit='Self-documenting code',
                            complexity_reduction=1
                        )
    
    def _find_string_concatenation_issues(self, rel_path: str, lines: List[str]):
        """Find inefficient string concatenation patterns"""
        for line_num, line in enumerate(lines, 1):
            # Look for multiple string concatenations
            if line.count(' + ') > 2 and ('"' in line or "'" in line):
                self._add_opportunity(
                    file_path=rel_path,
                    line_number=line_num,
                    opportunity_type='string_concatenation',
                    current_code=line.strip()[:80] + '...' if len(line.strip()) > 80 else line.strip(),
                    suggested_code='Use f-strings or .join() for better performance',
                    benefit='Better performance and readability',
                    complexity_reduction=1
                )
    
    def _add_opportunity(self, file_path: str, line_number: int, opportunity_type: str,
                        current_code: str, suggested_code: str, benefit: str, complexity_reduction: int):
        """Add a simplification opportunity"""
        self.opportunities.append(SimplificationOpportunity(
            file_path=file_path,
            line_number=line_number,
            opportunity_type=opportunity_type,
            current_code=current_code,
            suggested_code=suggested_code,
            benefit=benefit,
            complexity_reduction=complexity_reduction
        ))
        self.metrics[opportunity_type] += 1
    
    def generate_simplification_report(self) -> str:
        """Generate comprehensive simplification report"""
        report = []
        report.append("?? CODE SIMPLIFICATION OPPORTUNITIES")
        report.append("=" * 50)
        
        # Summary
        total_opportunities = len(self.opportunities)
        total_complexity_reduction = sum(op.complexity_reduction for op in self.opportunities)
        
        report.append(f"\n?? SUMMARY:")
        report.append(f"Total Simplification Opportunities: {total_opportunities}")
        report.append(f"Potential Complexity Reduction: {total_complexity_reduction} points")
        
        if total_opportunities == 0:
            report.append("\n?? Excellent! No major simplification opportunities found.")
            report.append("Your code appears to be well-structured and clean.")
            return "\n".join(report)
        
        # High-impact opportunities
        high_impact = [op for op in self.opportunities if op.complexity_reduction >= 3]
        medium_impact = [op for op in self.opportunities if op.complexity_reduction == 2]
        low_impact = [op for op in self.opportunities if op.complexity_reduction == 1]
        
        report.append(f"High Impact Opportunities: {len(high_impact)}")
        report.append(f"Medium Impact Opportunities: {len(medium_impact)}")
        report.append(f"Low Impact Opportunities: {len(low_impact)}")
        
        # Opportunities by category
        report.append(f"\n?? OPPORTUNITIES BY TYPE:")
        for opp_type, count in sorted(self.metrics.items()):
            report.append(f"{opp_type}: {count}")
        
        # High impact opportunities detail
        if high_impact:
            report.append(f"\n?? HIGH IMPACT OPPORTUNITIES (Priority 1):")
            for op in high_impact[:10]:  # Show first 10
                report.append(f"  ?? {op.file_path}:{op.line_number}")
                report.append(f"     Type: {op.opportunity_type}")
                report.append(f"     Current: {op.current_code}")
                report.append(f"     Suggested: {op.suggested_code}")
                report.append(f"     Benefit: {op.benefit}")
                report.append(f"     Complexity Reduction: {op.complexity_reduction}")
                report.append("")
        
        # Medium impact opportunities
        if medium_impact:
            report.append(f"\n? MEDIUM IMPACT OPPORTUNITIES (Priority 2):")
            for op in medium_impact[:8]:  # Show first 8
                report.append(f"  ?? {op.file_path}:{op.line_number}")
                report.append(f"     Type: {op.opportunity_type}")
                report.append(f"     Suggested: {op.suggested_code}")
                report.append(f"     Benefit: {op.benefit}")
                report.append("")
        
        # Recommendations
        report.append(f"\n?? REFACTORING RECOMMENDATIONS:")
        
        if high_impact:
            report.append("1. ?? Focus on high-impact opportunities first")
            report.append("   - Break down complex methods")
            report.append("   - Extract duplicate logic")
            report.append("   - Simplify parameter lists")
        
        if any(op.opportunity_type == 'duplicate_logic' for op in self.opportunities):
            report.append("2. ?? Eliminate code duplication")
            report.append("   - Extract common patterns into shared methods")
            report.append("   - Create utility functions for repeated logic")
        
        if any(op.opportunity_type in ['magic_number', 'string_concatenation'] for op in self.opportunities):
            report.append("3. ?? Clean up code quality issues")
            report.append("   - Replace magic numbers with named constants")
            report.append("   - Use modern string formatting")
        
        # Estimated benefits
        report.append(f"\n?? ESTIMATED BENEFITS:")
        report.append(f"- Reduced code complexity by {total_complexity_reduction} points")
        report.append(f"- Improved maintainability and readability")
        report.append(f"- Easier testing and debugging")
        
        if total_complexity_reduction > 20:
            report.append(f"- Significant improvement in code quality expected")
        elif total_complexity_reduction > 10:
            report.append(f"- Moderate improvement in code quality expected")
        else:
            report.append(f"- Minor improvements, code is already quite good")
        
        return "\n".join(report)

def main():
    """Main function to run simplification analysis"""
    project_root = Path('.').resolve()
    analyzer = CodeSimplificationAnalyzer(project_root)
    
    print("?? Analyzing codebase for simplification opportunities...")
    opportunities = analyzer.analyze_codebase()
    
    report = analyzer.generate_simplification_report()
    print(report)
    
    # Save report
    report_file = project_root / 'docs' / 'simplification_report.md'
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding='utf-8')
    print(f"\n?? Report saved to: {report_file}")

if __name__ == "__main__":
    main()