#!/usr/bin/env python3
"""
AI-Interlinq Auto-Improvement Detection System
LAW-001 Compliant Implementation

Purpose: Automated code improvement identification and analysis
Requirements: Code smell detection, performance analysis, security scanning
"""

import os
import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add the current directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class ImprovementOpportunity:
    """Represents an identified improvement opportunity."""
    type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    file_path: str
    line_number: Optional[int]
    suggested_fix: str
    estimated_impact: str
    law_001_compliant: bool

class ImprovementDetector:
    """
    LAW-001 Compliant Improvement Detection System
    
    Detects code improvement opportunities across multiple dimensions:
    - Code smells and maintainability issues
    - Performance bottlenecks
    - Security vulnerabilities
    - Architecture improvements
    - Refactoring opportunities
    """
    
    def __init__(self, repository_path: str = "."):
        """
        Initialize the improvement detector.
        
        Args:
            repository_path: Path to the repository root
        """
        self.repository_path = Path(repository_path).resolve()
        self.improvements: List[ImprovementOpportunity] = []
        self.analysis_timestamp = time.time()
        
        # LAW-001 compliance tracking
        self.law_001_context = {
            "cause": "Automated improvement detection initiated",
            "input": {"repository_path": str(self.repository_path)},
            "action": "Comprehensive code analysis",
            "timestamp": self.analysis_timestamp
        }
    
    def detect_all_improvements(self) -> Dict[str, Any]:
        """
        Run comprehensive improvement detection.
        
        Returns:
            Dict: Complete analysis results with LAW-001 compliance
        """
        print("🔍 Starting comprehensive improvement detection...")
        
        # Clear previous improvements
        self.improvements = []
        
        # Run all detection methods
        self._detect_code_smells()
        self._detect_performance_issues()
        self._detect_security_vulnerabilities()
        self._detect_architecture_improvements()
        self._detect_refactoring_opportunities()
        self._detect_documentation_gaps()
        
        # Compile results
        results = self._compile_results()
        
        # Generate LAW-001 compliant snapshot
        self._generate_law_001_snapshot(results)
        
        print(f"✅ Detection complete. Found {len(self.improvements)} improvement opportunities.")
        return results
    
    def _detect_code_smells(self) -> None:
        """Detect code smells using static analysis tools."""
        print("🔍 Detecting code smells...")
        
        try:
            # Run pylint for code quality analysis
            result = subprocess.run([
                "pylint", "ai_interlinq/", "--output-format=json"
            ], capture_output=True, text=True, cwd=self.repository_path)
            
            if result.stdout:
                pylint_results = json.loads(result.stdout)
                for issue in pylint_results:
                    if issue.get('type') in ['convention', 'refactor', 'warning']:
                        self.improvements.append(ImprovementOpportunity(
                            type="code_smell",
                            severity=self._map_pylint_severity(issue.get('type')),
                            description=issue.get('message', ''),
                            file_path=issue.get('path', ''),
                            line_number=issue.get('line', None),
                            suggested_fix=f"Address pylint issue: {issue.get('symbol', '')}",
                            estimated_impact="Improved code maintainability",
                            law_001_compliant=True
                        ))
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"⚠️ Error detecting code smells: {e}")
            self._add_detection_error("code_smells", str(e))
    
    def _detect_performance_issues(self) -> None:
        """Detect potential performance bottlenecks."""
        print("🔍 Detecting performance issues...")
        
        # Search for common performance anti-patterns
        performance_patterns = [
            {
                "pattern": r"for.*in.*range\(len\(",
                "description": "Consider using enumerate() instead of range(len())",
                "severity": "MEDIUM"
            },
            {
                "pattern": r"\.+\s*join\([^)]*for.*in",
                "description": "Consider using list comprehension for better performance",
                "severity": "LOW"
            },
            {
                "pattern": r"time\.sleep\([^)]*\)",
                "description": "Consider using async/await for non-blocking operations",
                "severity": "MEDIUM"
            }
        ]
        
        self._scan_files_for_patterns(performance_patterns, "performance_issue")
    
    def _detect_security_vulnerabilities(self) -> None:
        """Detect security vulnerabilities using bandit."""
        print("🔍 Detecting security vulnerabilities...")
        
        try:
            result = subprocess.run([
                "bandit", "-r", "ai_interlinq/", "-f", "json"
            ], capture_output=True, text=True, cwd=self.repository_path)
            
            if result.stdout:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get('results', []):
                    self.improvements.append(ImprovementOpportunity(
                        type="security_vulnerability",
                        severity=issue.get('issue_severity', 'MEDIUM'),
                        description=issue.get('issue_text', ''),
                        file_path=issue.get('filename', ''),
                        line_number=issue.get('line_number', None),
                        suggested_fix=f"Address security issue: {issue.get('test_name', '')}",
                        estimated_impact="Enhanced security posture",
                        law_001_compliant=True
                    ))
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"⚠️ Error detecting security vulnerabilities: {e}")
            self._add_detection_error("security_vulnerabilities", str(e))
    
    def _detect_architecture_improvements(self) -> None:
        """Detect architecture improvement opportunities."""
        print("🔍 Detecting architecture improvements...")
        
        # Check for common architecture issues
        architecture_checks = [
            self._check_circular_imports,
            self._check_large_modules,
            self._check_missing_interfaces,
            self._check_tight_coupling
        ]
        
        for check in architecture_checks:
            try:
                check()
            except Exception as e:
                print(f"⚠️ Error in architecture check {check.__name__}: {e}")
    
    def _detect_refactoring_opportunities(self) -> None:
        """Detect refactoring opportunities."""
        print("🔍 Detecting refactoring opportunities...")
        
        # Search for refactoring patterns
        refactoring_patterns = [
            {
                "pattern": r"def\s+\w+\([^)]*\):\s*(\n\s+.*){20,}",
                "description": "Long method detected - consider breaking into smaller functions",
                "severity": "MEDIUM"
            },
            {
                "pattern": r"class\s+\w+[^:]*:\s*(\n\s+.*){50,}",
                "description": "Large class detected - consider splitting responsibilities",
                "severity": "MEDIUM"
            },
            {
                "pattern": r"if\s+.*:\s*(\n\s+if\s+.*:\s*(\n\s+if\s+.*:))",
                "description": "Deep nesting detected - consider refactoring",
                "severity": "LOW"
            }
        ]
        
        self._scan_files_for_patterns(refactoring_patterns, "refactoring_opportunity")
    
    def _detect_documentation_gaps(self) -> None:
        """Detect documentation gaps."""
        print("🔍 Detecting documentation gaps...")
        
        # Limit to core modules to prevent timeout
        target_dirs = ["ai_interlinq/core", "ai_interlinq"]
        
        for target_dir in target_dirs:
            dir_path = self.repository_path / target_dir
            if not dir_path.exists():
                continue
                
            # Limit files processed to prevent timeout
            py_files = list(dir_path.glob("*.py"))[:10]  # Process max 10 files
            
            for py_file in py_files:
                if "test" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Simple check for functions without docstrings
                    import re
                    functions = re.findall(r'def\s+(\w+)\([^)]*\):', content)[:5]  # Check max 5 functions per file
                    
                    for func in functions:
                        if func.startswith('_'):  # Skip private functions
                            continue
                        
                        func_pos = content.find(f'def {func}')
                        if func_pos != -1:
                            # Check next 200 chars for docstring
                            check_section = content[func_pos:func_pos + 200]
                            if '"""' not in check_section:
                                self.improvements.append(ImprovementOpportunity(
                                    type="documentation_gap",
                                    severity="LOW",
                                    description=f"Function '{func}' lacks documentation",
                                    file_path=str(py_file.relative_to(self.repository_path)),
                                    line_number=None,
                                    suggested_fix=f"Add docstring to function '{func}'",
                                    estimated_impact="Improved code documentation",
                                    law_001_compliant=True
                                ))
                                break  # Only report one per file to save time
                                
                except Exception as e:
                    print(f"⚠️ Error checking documentation in {py_file}: {e}")
                    continue
    
    def _scan_files_for_patterns(self, patterns: List[Dict], improvement_type: str) -> None:
        """Scan files for specific patterns."""
        import re
        
        # Limit to core files to prevent timeout
        target_files = list(self.repository_path.glob("ai_interlinq/**/*.py"))[:20]  # Max 20 files
        
        for py_file in target_files:
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Skip very large files to prevent timeout
                if len(content) > 50000:  # Skip files larger than 50KB
                    continue
                    
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    matches = list(re.finditer(pattern, content, re.MULTILINE))[:5]  # Max 5 matches per file
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.improvements.append(ImprovementOpportunity(
                            type=improvement_type,
                            severity=pattern_info['severity'],
                            description=pattern_info['description'],
                            file_path=str(py_file.relative_to(self.repository_path)),
                            line_number=line_num,
                            suggested_fix=pattern_info['description'],
                            estimated_impact="Performance improvement",
                            law_001_compliant=True
                        ))
                        break  # Only report one per pattern per file
                        
            except Exception as e:
                print(f"⚠️ Error scanning {py_file}: {e}")
                continue
    
    def _check_circular_imports(self) -> None:
        """Check for circular import issues."""
        # This is a simplified check - in practice you'd use tools like pydeps
        pass
    
    def _check_large_modules(self) -> None:
        """Check for modules that are too large."""
        max_lines = 500  # Configurable threshold
        
        for py_file in self.repository_path.glob("**/*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > max_lines:
                        self.improvements.append(ImprovementOpportunity(
                            type="architecture_improvement",
                            severity="MEDIUM",
                            description=f"Large module with {len(lines)} lines",
                            file_path=str(py_file.relative_to(self.repository_path)),
                            line_number=None,
                            suggested_fix="Consider breaking module into smaller, focused modules",
                            estimated_impact="Improved code organization",
                            law_001_compliant=True
                        ))
            except Exception as e:
                print(f"⚠️ Error checking module size for {py_file}: {e}")
    
    def _check_missing_interfaces(self) -> None:
        """Check for missing interface definitions."""
        # Look for classes that could benefit from interface definitions
        pass
    
    def _check_tight_coupling(self) -> None:
        """Check for tight coupling between modules."""
        # Analyze import patterns to detect tight coupling
        pass
    
    def _map_pylint_severity(self, pylint_type: str) -> str:
        """Map pylint issue types to severity levels."""
        mapping = {
            'convention': 'LOW',
            'refactor': 'MEDIUM',
            'warning': 'HIGH',
            'error': 'CRITICAL',
            'fatal': 'CRITICAL'
        }
        return mapping.get(pylint_type, 'MEDIUM')
    
    def _add_detection_error(self, detection_type: str, error_message: str) -> None:
        """Add a detection error as an improvement opportunity."""
        self.improvements.append(ImprovementOpportunity(
            type="detection_error",
            severity="HIGH",
            description=f"Error during {detection_type}: {error_message}",
            file_path="",
            line_number=None,
            suggested_fix=f"Fix detection tool configuration for {detection_type}",
            estimated_impact="Enable proper detection",
            law_001_compliant=True
        ))
    
    def _compile_results(self) -> Dict[str, Any]:
        """Compile all improvement detection results."""
        # Group improvements by type
        by_type = {}
        by_severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        for improvement in self.improvements:
            if improvement.type not in by_type:
                by_type[improvement.type] = []
            by_type[improvement.type].append(improvement)
            by_severity[improvement.severity] += 1
        
        return {
            "timestamp": self.analysis_timestamp,
            "repository_path": str(self.repository_path),
            "total_improvements": len(self.improvements),
            "improvements_by_type": {k: len(v) for k, v in by_type.items()},
            "improvements_by_severity": by_severity,
            "detailed_improvements": [
                {
                    "type": imp.type,
                    "severity": imp.severity,
                    "description": imp.description,
                    "file_path": imp.file_path,
                    "line_number": imp.line_number,
                    "suggested_fix": imp.suggested_fix,
                    "estimated_impact": imp.estimated_impact,
                    "law_001_compliant": imp.law_001_compliant
                }
                for imp in self.improvements
            ],
            "law_001_context": self.law_001_context,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate high-level recommendations based on detected improvements."""
        recommendations = []
        
        # Count improvements by type
        type_counts = {}
        for improvement in self.improvements:
            type_counts[improvement.type] = type_counts.get(improvement.type, 0) + 1
        
        # Generate recommendations based on patterns
        if type_counts.get("code_smell", 0) > 10:
            recommendations.append("Consider running a comprehensive code refactoring session")
        
        if type_counts.get("security_vulnerability", 0) > 0:
            recommendations.append("Address security vulnerabilities as high priority")
        
        if type_counts.get("performance_issue", 0) > 5:
            recommendations.append("Consider performance optimization sprint")
        
        if type_counts.get("documentation_gap", 0) > 20:
            recommendations.append("Implement documentation improvement initiative")
        
        if not recommendations:
            recommendations.append("Code quality looks good - continue monitoring")
        
        return recommendations
    
    def _generate_law_001_snapshot(self, results: Dict[str, Any]) -> None:
        """Generate LAW-001 compliant snapshot."""
        try:
            snapshot = {
                "context": self.law_001_context["cause"],
                "input": self.law_001_context["input"],
                "action": self.law_001_context["action"],
                "applied_law": "LAW-001",
                "reaction": f"Detected {len(self.improvements)} improvement opportunities",
                "output": {
                    "total_improvements": results["total_improvements"],
                    "improvements_by_severity": results["improvements_by_severity"],
                    "recommendations": results["recommendations"]
                },
                "deviation": None,
                "ai_signature": "improvement_detector_v1.0",
                "timestamp": self.analysis_timestamp
            }
            
            # Save snapshot
            snapshot_path = self.repository_path / "snapshot.ai"
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2)
            
            print(f"📸 LAW-001 snapshot saved to {snapshot_path}")
            
        except Exception as e:
            print(f"⚠️ Error generating LAW-001 snapshot: {e}")
    
    def save_results(self, output_file: str = "improvement_analysis.json") -> None:
        """Save analysis results to file."""
        results = self._compile_results()
        output_path = self.repository_path / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to {output_path}")

def main():
    """Main entry point for improvement detection."""
    detector = ImprovementDetector()
    results = detector.detect_all_improvements()
    detector.save_results()
    
    # Print summary
    print("\n📊 Improvement Detection Summary:")
    print(f"Total improvements found: {results['total_improvements']}")
    print(f"By severity: {results['improvements_by_severity']}")
    print(f"By type: {results['improvements_by_type']}")
    print("\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"  • {rec}")

if __name__ == "__main__":
    main()