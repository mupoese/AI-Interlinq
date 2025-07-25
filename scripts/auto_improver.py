#!/usr/bin/env python3
"""
AI-Interlinq Auto-Improver System

Intelligent code improvement system with LAW-001 integration.
- Analyzes codebase for improvement opportunities
- Implements enhancements automatically
- Maintains compliance with governance rules
- Integrates with learning cycle framework

Author: AI-Interlinq Auto-Improvement System
LAW-001 Compliant: Yes
Version: 1.1.0
"""

import os
import sys
import json
import ast
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImprovementType(Enum):
    """Types of improvements that can be made."""
    CODE_QUALITY = "code_quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    LAW_COMPLIANCE = "law_compliance"
    ARCHITECTURE = "architecture"

class Priority(Enum):
    """Priority levels for improvements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ImprovementSuggestion:
    """Represents a single improvement suggestion."""
    type: ImprovementType
    priority: Priority
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    suggested_fix: str
    auto_fixable: bool
    requires_testing: bool
    law_compliance_impact: bool
    estimated_effort: str
    confidence_score: float

@dataclass
class AnalysisResult:
    """Results from code analysis."""
    timestamp: str
    total_files_analyzed: int
    suggestions: List[ImprovementSuggestion]
    metrics: Dict[str, Any]
    overall_health_score: float
    law_compliance_status: bool

class AutoImprover:
    """
    Intelligent code improvement system with LAW-001 integration.
    
    This class analyzes the AI-Interlinq codebase and implements
    improvements while maintaining LAW-001 compliance.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.law_compliance = True
        self.improvement_engine = None
        self.commit_manager = None
        self.analysis_results: Optional[AnalysisResult] = None
        
        # LAW-001 integration
        self.law_file = self.project_root / "law.ai"
        self.snapshot_manager = None
        self.learning_cycle = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize auto-improvement components."""
        logger.info("🤖 Initializing Auto-Improvement System...")
        
        # Verify LAW-001 compliance
        if not self._verify_law_compliance():
            logger.error("❌ LAW-001 compliance verification failed")
            raise RuntimeError("Cannot proceed without LAW-001 compliance")
        
        # Initialize core components
        try:
            sys.path.insert(0, str(self.project_root))
            from ai_interlinq.core import learning_cycle, snapshot_manager
            
            self.snapshot_manager = snapshot_manager.SnapshotManager()
            self.learning_cycle = learning_cycle.LearningCycleEngine()
            
            logger.info("✅ Core components initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Core components not available: {e}")
        except AttributeError as e:
            logger.warning(f"⚠️ Core component attribute error: {e}")
            # Continue without core components for basic analysis
    
    def _verify_law_compliance(self) -> bool:
        """Verify LAW-001 compliance before proceeding."""
        if not self.law_file.exists():
            logger.error("❌ LAW-001 file not found")
            return False
        
        try:
            with open(self.law_file, 'r') as f:
                law_content = f.read()
            
            if 'LAW-001' not in law_content:
                logger.error("❌ LAW-001 identifier not found in law file")
                return False
            
            logger.info("✅ LAW-001 compliance verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reading LAW-001 file: {e}")
            return False
    
    def analyze_code(self) -> AnalysisResult:
        """
        Analyze codebase for improvement opportunities.
        
        Returns:
            AnalysisResult: Comprehensive analysis with suggestions
        """
        logger.info("🔍 Starting comprehensive code analysis...")
        
        start_time = time.time()
        suggestions = []
        metrics = {}
        
        # Analyze Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not any(
            part.startswith('.') or part == '__pycache__' 
            for part in f.parts
        )]
        
        logger.info(f"📁 Analyzing {len(python_files)} Python files...")
        
        for py_file in python_files:
            file_suggestions = self._analyze_file(py_file)
            suggestions.extend(file_suggestions)
        
        # Analyze project structure
        structure_suggestions = self._analyze_project_structure()
        suggestions.extend(structure_suggestions)
        
        # Analyze LAW-001 compliance
        compliance_suggestions = self._analyze_law_compliance()
        suggestions.extend(compliance_suggestions)
        
        # Calculate metrics
        metrics = self._calculate_metrics(suggestions, python_files)
        
        # Calculate overall health score
        health_score = self._calculate_health_score(suggestions, metrics)
        
        # Check LAW-001 compliance status
        law_compliance_status = len([s for s in suggestions 
                                   if s.type == ImprovementType.LAW_COMPLIANCE]) == 0
        
        analysis_time = time.time() - start_time
        
        self.analysis_results = AnalysisResult(
            timestamp=datetime.utcnow().isoformat(),
            total_files_analyzed=len(python_files),
            suggestions=suggestions,
            metrics=metrics,
            overall_health_score=health_score,
            law_compliance_status=law_compliance_status
        )
        
        logger.info(f"📊 Analysis completed in {analysis_time:.2f}s")
        logger.info(f"   Files analyzed: {len(python_files)}")
        logger.info(f"   Suggestions: {len(suggestions)}")
        logger.info(f"   Health score: {health_score:.1f}/100")
        
        return self.analysis_results
    
    def _analyze_file(self, file_path: Path) -> List[ImprovementSuggestion]:
        """Analyze a single Python file for improvements."""
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                suggestions.append(ImprovementSuggestion(
                    type=ImprovementType.CODE_QUALITY,
                    priority=Priority.CRITICAL,
                    title="Syntax Error",
                    description=f"Syntax error in file: {e}",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=getattr(e, 'lineno', None),
                    suggested_fix="Fix syntax error",
                    auto_fixable=False,
                    requires_testing=True,
                    law_compliance_impact=True,
                    estimated_effort="30min",
                    confidence_score=1.0
                ))
                return suggestions
            
            # Code quality analysis
            suggestions.extend(self._analyze_code_quality(file_path, tree, content))
            
            # Performance analysis
            suggestions.extend(self._analyze_performance(file_path, tree, content))
            
            # Security analysis
            suggestions.extend(self._analyze_security(file_path, tree, content))
            
            # Documentation analysis
            suggestions.extend(self._analyze_documentation(file_path, tree, content))
            
        except Exception as e:
            logger.warning(f"⚠️ Error analyzing {file_path}: {e}")
        
        return suggestions
    
    def _analyze_code_quality(self, file_path: Path, tree: ast.AST, content: str) -> List[ImprovementSuggestion]:
        """Analyze code quality issues."""
        suggestions = []
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = len([line for line in content.split('\n')[node.lineno-1:node.end_lineno] if line.strip()])
                
                if func_lines > 50:
                    suggestions.append(ImprovementSuggestion(
                        type=ImprovementType.CODE_QUALITY,
                        priority=Priority.MEDIUM,
                        title="Long Function",
                        description=f"Function '{node.name}' is {func_lines} lines long",
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        suggested_fix="Consider breaking into smaller functions",
                        auto_fixable=False,
                        requires_testing=True,
                        law_compliance_impact=False,
                        estimated_effort="2h",
                        confidence_score=0.8
                    ))
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    suggestions.append(ImprovementSuggestion(
                        type=ImprovementType.DOCUMENTATION,
                        priority=Priority.LOW,
                        title="Missing Docstring",
                        description=f"{type(node).__name__} '{node.name}' lacks documentation",
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        suggested_fix="Add comprehensive docstring",
                        auto_fixable=True,
                        requires_testing=False,
                        law_compliance_impact=False,
                        estimated_effort="15min",
                        confidence_score=0.9
                    ))
        
        # Check for complex conditions
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Count boolean operators in condition
                bool_ops = len([n for n in ast.walk(node.test) if isinstance(n, (ast.BoolOp, ast.Compare))])
                if bool_ops > 3:
                    suggestions.append(ImprovementSuggestion(
                        type=ImprovementType.CODE_QUALITY,
                        priority=Priority.MEDIUM,
                        title="Complex Condition",
                        description="Condition has multiple boolean operations",
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=node.lineno,
                        suggested_fix="Extract condition to separate function or variables",
                        auto_fixable=False,
                        requires_testing=True,
                        law_compliance_impact=False,
                        estimated_effort="30min",
                        confidence_score=0.7
                    ))
        
        return suggestions
    
    def _analyze_performance(self, file_path: Path, tree: ast.AST, content: str) -> List[ImprovementSuggestion]:
        """Analyze performance issues."""
        suggestions = []
        
        # Check for inefficient loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Look for list comprehensions inside loops
                for child in ast.walk(node):
                    if isinstance(child, ast.ListComp) and child != node:
                        suggestions.append(ImprovementSuggestion(
                            type=ImprovementType.PERFORMANCE,
                            priority=Priority.MEDIUM,
                            title="Inefficient Loop Pattern",
                            description="List comprehension inside loop can be optimized",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            suggested_fix="Move list comprehension outside loop or use generator",
                            auto_fixable=False,
                            requires_testing=True,
                            law_compliance_impact=False,
                            estimated_effort="30min",
                            confidence_score=0.8
                        ))
        
        # Check for string concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            suggestions.append(ImprovementSuggestion(
                                type=ImprovementType.PERFORMANCE,
                                priority=Priority.HIGH,
                                title="String Concatenation in Loop",
                                description="String concatenation in loop is inefficient",
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=node.lineno,
                                suggested_fix="Use list.join() or f-strings instead",
                                auto_fixable=True,
                                requires_testing=True,
                                law_compliance_impact=False,
                                estimated_effort="15min",
                                confidence_score=0.9
                            ))
        
        return suggestions
    
    def _analyze_security(self, file_path: Path, tree: ast.AST, content: str) -> List[ImprovementSuggestion]:
        """Analyze security issues."""
        suggestions = []
        
        # Check for potential SQL injection (basic check)
        if 'execute(' in content and any(op in content.lower() for op in ['select', 'insert', 'update', 'delete']):
            suggestions.append(ImprovementSuggestion(
                type=ImprovementType.SECURITY,
                priority=Priority.HIGH,
                title="Potential SQL Injection",
                description="SQL queries found - verify parameterization",
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=None,
                suggested_fix="Use parameterized queries",
                auto_fixable=False,
                requires_testing=True,
                law_compliance_impact=True,
                estimated_effort="1h",
                confidence_score=0.6
            ))
        
        # Check for hardcoded secrets
        sensitive_patterns = ['password', 'api_key', 'secret_key', 'token']
        for pattern in sensitive_patterns:
            if f'{pattern}=' in content.lower() or f'"{pattern}"' in content.lower():
                suggestions.append(ImprovementSuggestion(
                    type=ImprovementType.SECURITY,
                    priority=Priority.CRITICAL,
                    title="Potential Hardcoded Secret",
                    description=f"Potential hardcoded {pattern} found",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=None,
                    suggested_fix="Move sensitive data to environment variables",
                    auto_fixable=False,
                    requires_testing=True,
                    law_compliance_impact=True,
                    estimated_effort="30min",
                    confidence_score=0.7
                ))
        
        return suggestions
    
    def _analyze_documentation(self, file_path: Path, tree: ast.AST, content: str) -> List[ImprovementSuggestion]:
        """Analyze documentation issues."""
        suggestions = []
        
        # Check for TODO/FIXME comments
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if any(marker in line.upper() for marker in ['TODO', 'FIXME', 'BUG', 'HACK']):
                suggestions.append(ImprovementSuggestion(
                    type=ImprovementType.CODE_QUALITY,
                    priority=Priority.LOW,
                    title="TODO/FIXME Comment",
                    description="Unresolved TODO or FIXME comment",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=i,
                    suggested_fix="Resolve the TODO/FIXME or create an issue",
                    auto_fixable=False,
                    requires_testing=False,
                    law_compliance_impact=False,
                    estimated_effort="varies",
                    confidence_score=1.0
                ))
        
        return suggestions
    
    def _analyze_project_structure(self) -> List[ImprovementSuggestion]:
        """Analyze project structure improvements."""
        suggestions = []
        
        # Check for missing important files
        important_files = {
            'README.md': 'Project documentation',
            'requirements.txt': 'Python dependencies',
            '.gitignore': 'Git ignore rules',
            'setup.py': 'Package setup',
            'LICENSE': 'License information'
        }
        
        for file_name, description in important_files.items():
            if not (self.project_root / file_name).exists():
                suggestions.append(ImprovementSuggestion(
                    type=ImprovementType.DOCUMENTATION,
                    priority=Priority.MEDIUM,
                    title=f"Missing {file_name}",
                    description=f"Missing {description} file",
                    file_path=".",
                    line_number=None,
                    suggested_fix=f"Create {file_name} file",
                    auto_fixable=True,
                    requires_testing=False,
                    law_compliance_impact=False,
                    estimated_effort="30min",
                    confidence_score=1.0
                ))
        
        return suggestions
    
    def _analyze_law_compliance(self) -> List[ImprovementSuggestion]:
        """Analyze LAW-001 compliance issues."""
        suggestions = []
        
        # Check for proper snapshot integration
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if 'core/' not in str(py_file):  # Skip core files
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for snapshot patterns without LAW-001 reference
                if ('snapshot' in content.lower() and 
                    'create' in content.lower() and 
                    'LAW-001' not in content and 
                    'law.ai' not in content):
                    
                    suggestions.append(ImprovementSuggestion(
                        type=ImprovementType.LAW_COMPLIANCE,
                        priority=Priority.HIGH,
                        title="Missing LAW-001 Reference",
                        description="Snapshot creation without LAW-001 compliance reference",
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=None,
                        suggested_fix="Add LAW-001 compliance reference to snapshot operations",
                        auto_fixable=False,
                        requires_testing=True,
                        law_compliance_impact=True,
                        estimated_effort="1h",
                        confidence_score=0.9
                    ))
                
            except Exception as e:
                logger.warning(f"⚠️ Error checking LAW compliance in {py_file}: {e}")
        
        # Check memory/snapshots directory
        snapshots_dir = self.project_root / "memory" / "snapshots"
        if not snapshots_dir.exists():
            suggestions.append(ImprovementSuggestion(
                type=ImprovementType.LAW_COMPLIANCE,
                priority=Priority.CRITICAL,
                title="Missing Snapshots Directory",
                description="LAW-001 requires memory/snapshots directory",
                file_path=".",
                line_number=None,
                suggested_fix="Create memory/snapshots directory structure",
                auto_fixable=True,
                requires_testing=False,
                law_compliance_impact=True,
                estimated_effort="5min",
                confidence_score=1.0
            ))
        
        return suggestions
    
    def _calculate_metrics(self, suggestions: List[ImprovementSuggestion], files: List[Path]) -> Dict[str, Any]:
        """Calculate code quality metrics."""
        
        metrics = {
            'total_files': len(files),
            'total_suggestions': len(suggestions),
            'suggestions_by_type': {},
            'suggestions_by_priority': {},
            'auto_fixable_count': 0,
            'law_compliance_issues': 0,
            'estimated_effort_hours': 0
        }
        
        # Count by type
        for suggestion_type in ImprovementType:
            count = len([s for s in suggestions if s.type == suggestion_type])
            metrics['suggestions_by_type'][suggestion_type.value] = count
        
        # Count by priority
        for priority in Priority:
            count = len([s for s in suggestions if s.priority == priority])
            metrics['suggestions_by_priority'][priority.value] = count
        
        # Count auto-fixable
        metrics['auto_fixable_count'] = len([s for s in suggestions if s.auto_fixable])
        
        # Count LAW compliance issues
        metrics['law_compliance_issues'] = len([s for s in suggestions 
                                              if s.type == ImprovementType.LAW_COMPLIANCE])
        
        # Estimate total effort (simplified)
        effort_mapping = {
            '5min': 0.08, '15min': 0.25, '30min': 0.5, 
            '1h': 1.0, '2h': 2.0, 'varies': 1.0
        }
        
        total_effort = 0
        for suggestion in suggestions:
            effort = effort_mapping.get(suggestion.estimated_effort, 1.0)
            total_effort += effort
        
        metrics['estimated_effort_hours'] = round(total_effort, 1)
        
        return metrics
    
    def _calculate_health_score(self, suggestions: List[ImprovementSuggestion], metrics: Dict[str, Any]) -> float:
        """Calculate overall codebase health score (0-100)."""
        
        base_score = 100.0
        
        # Deduct points based on suggestion priorities
        priority_weights = {
            Priority.CRITICAL: 20,
            Priority.HIGH: 10,
            Priority.MEDIUM: 5,
            Priority.LOW: 1
        }
        
        for suggestion in suggestions:
            deduction = priority_weights.get(suggestion.priority, 1)
            base_score -= deduction
        
        # Extra deduction for LAW compliance issues
        law_issues = metrics.get('law_compliance_issues', 0)
        if law_issues > 0:
            base_score -= law_issues * 15  # Extra penalty for compliance issues
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, base_score))
    
    def implement_improvements(self, max_auto_fixes: int = 10) -> Dict[str, Any]:
        """
        Implement automatic improvements.
        
        Args:
            max_auto_fixes: Maximum number of automatic fixes to apply
            
        Returns:
            Dict with implementation results
        """
        if not self.analysis_results:
            raise RuntimeError("Must run analyze_code() first")
        
        logger.info("🔧 Starting automatic improvement implementation...")
        
        # Filter auto-fixable suggestions
        auto_fixable = [s for s in self.analysis_results.suggestions if s.auto_fixable]
        auto_fixable.sort(key=lambda x: (x.priority.value, -x.confidence_score))
        
        # Limit number of fixes
        fixes_to_apply = auto_fixable[:max_auto_fixes]
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_suggestions': len(self.analysis_results.suggestions),
            'auto_fixable': len(auto_fixable),
            'applied_fixes': [],
            'skipped_fixes': [],
            'errors': []
        }
        
        for suggestion in fixes_to_apply:
            try:
                if self._apply_fix(suggestion):
                    results['applied_fixes'].append({
                        'type': suggestion.type.value,
                        'title': suggestion.title,
                        'file': suggestion.file_path,
                        'confidence': suggestion.confidence_score
                    })
                    logger.info(f"✅ Applied: {suggestion.title}")
                else:
                    results['skipped_fixes'].append({
                        'type': suggestion.type.value,
                        'title': suggestion.title,
                        'reason': 'Implementation failed'
                    })
                    logger.warning(f"⚠️ Skipped: {suggestion.title}")
                    
            except Exception as e:
                results['errors'].append({
                    'suggestion': suggestion.title,
                    'error': str(e)
                })
                logger.error(f"❌ Error applying {suggestion.title}: {e}")
        
        logger.info(f"🔧 Implementation completed: {len(results['applied_fixes'])} fixes applied")
        
        return results
    
    def _apply_fix(self, suggestion: ImprovementSuggestion) -> bool:
        """Apply a specific improvement fix."""
        
        if suggestion.type == ImprovementType.DOCUMENTATION:
            if "Missing" in suggestion.title and suggestion.file_path == ".":
                return self._create_missing_file(suggestion)
            elif "Missing Docstring" in suggestion.title:
                return self._add_docstring(suggestion)
        
        elif suggestion.type == ImprovementType.LAW_COMPLIANCE:
            if "Missing Snapshots Directory" in suggestion.title:
                return self._create_snapshots_directory()
        
        elif suggestion.type == ImprovementType.PERFORMANCE:
            if "String Concatenation" in suggestion.title:
                return self._fix_string_concatenation(suggestion)
        
        return False
    
    def _create_missing_file(self, suggestion: ImprovementSuggestion) -> bool:
        """Create missing project files."""
        
        if "Missing .gitignore" in suggestion.title:
            gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
*.egg-info/
.installed.cfg
*.egg

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""
            try:
                with open(self.project_root / ".gitignore", 'w') as f:
                    f.write(gitignore_content)
                return True
            except Exception as e:
                logger.error(f"Failed to create .gitignore: {e}")
                return False
        
        return False
    
    def _add_docstring(self, suggestion: ImprovementSuggestion) -> bool:
        """Add basic docstring to functions/classes."""
        # This would require more sophisticated AST manipulation
        # For now, return False to indicate manual intervention needed
        return False
    
    def _create_snapshots_directory(self) -> bool:
        """Create LAW-001 compliant snapshots directory."""
        try:
            snapshots_dir = self.project_root / "memory" / "snapshots"
            snapshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Create README in snapshots directory
            readme_content = """# LAW-001 Snapshots Directory

This directory contains LAW-001 compliant snapshots generated by the learning cycle system.

## Structure
- `*.json` - Learning cycle snapshots
- Each snapshot contains: context, input, action, applied_law, reaction, output, ai_signature

## Compliance
All snapshots in this directory are LAW-001 compliant and part of the automated learning cycle.
"""
            with open(snapshots_dir / "README.md", 'w') as f:
                f.write(readme_content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to create snapshots directory: {e}")
            return False
    
    def _fix_string_concatenation(self, suggestion: ImprovementSuggestion) -> bool:
        """Fix string concatenation performance issues."""
        # This would require sophisticated code transformation
        # For now, return False to indicate manual intervention needed
        return False
    
    def commit_changes(self, commit_message: Optional[str] = None) -> bool:
        """
        Commit improvements using LAW-001 compliant process.
        
        Args:
            commit_message: Custom commit message
            
        Returns:
            bool: True if commit successful
        """
        if not commit_message:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            commit_message = f"""🤖 Auto-improvement: {timestamp}

- Automated code analysis and improvements
- LAW-001 compliance maintained
- Health score optimization applied

LAW-001-Compliant: Yes
AI-Signature: mupoese_ai_auto_improver_v1.1.0

Co-authored-by: mupoese <31779778+mupoese@users.noreply.github.com>"""
        
        try:
            # Create LAW-001 snapshot before committing
            if self.snapshot_manager:
                snapshot_data = {
                    'context': 'auto_improvement_commit',
                    'analysis_results': asdict(self.analysis_results) if self.analysis_results else {},
                    'timestamp': datetime.utcnow().isoformat(),
                    'commit_message': commit_message
                }
                self.snapshot_manager.create_snapshot(snapshot_data)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if not result.stdout.strip():
                logger.info("ℹ️ No changes to commit")
                return True
            
            # Stage changes
            subprocess.run(['git', 'add', '.'], cwd=self.project_root, check=True)
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], 
                          cwd=self.project_root, check=True)
            
            logger.info("✅ Changes committed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Commit failed: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive improvement report."""
        if not self.analysis_results:
            raise RuntimeError("Must run analyze_code() first")
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'law_compliance': 'LAW-001',
            'analysis': self._serialize_analysis_results(self.analysis_results),
            'summary': {
                'total_files': self.analysis_results.total_files_analyzed,
                'total_suggestions': len(self.analysis_results.suggestions),
                'health_score': self.analysis_results.overall_health_score,
                'law_compliant': self.analysis_results.law_compliance_status,
                'auto_fixable': len([s for s in self.analysis_results.suggestions if s.auto_fixable])
            },
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        if self.analysis_results.overall_health_score < 70:
            report['recommendations'].append({
                'priority': 'high',
                'action': 'Immediate code quality improvements needed',
                'details': 'Health score below 70% indicates significant issues'
            })
        
        critical_suggestions = [s for s in self.analysis_results.suggestions 
                              if s.priority == Priority.CRITICAL]
        if critical_suggestions:
            report['recommendations'].append({
                'priority': 'critical',
                'action': f'Address {len(critical_suggestions)} critical issues immediately',
                'details': 'Critical issues may impact system stability'
            })
        
        if not self.analysis_results.law_compliance_status:
            report['recommendations'].append({
                'priority': 'critical',
                'action': 'Fix LAW-001 compliance violations',
                'details': 'System must maintain LAW-001 compliance at all times'
            })
        
        return report
    
    def _serialize_analysis_results(self, results: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to JSON-serializable format."""
        serialized_suggestions = []
        for suggestion in results.suggestions:
            serialized_suggestions.append({
                'type': suggestion.type.value,
                'priority': suggestion.priority.value,
                'title': suggestion.title,
                'description': suggestion.description,
                'file_path': suggestion.file_path,
                'line_number': suggestion.line_number,
                'suggested_fix': suggestion.suggested_fix,
                'auto_fixable': suggestion.auto_fixable,
                'requires_testing': suggestion.requires_testing,
                'law_compliance_impact': suggestion.law_compliance_impact,
                'estimated_effort': suggestion.estimated_effort,
                'confidence_score': suggestion.confidence_score
            })
        
        return {
            'timestamp': results.timestamp,
            'total_files_analyzed': results.total_files_analyzed,
            'suggestions': serialized_suggestions,
            'metrics': results.metrics,
            'overall_health_score': results.overall_health_score,
            'law_compliance_status': results.law_compliance_status
        }


def main():
    """Main entry point for auto-improver."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Interlinq Auto-Improvement System')
    parser.add_argument('--project-root', default='.',
                      help='Root directory of the project')
    parser.add_argument('--analyze-only', action='store_true',
                      help='Only analyze, do not implement fixes')
    parser.add_argument('--max-fixes', type=int, default=10,
                      help='Maximum number of automatic fixes to apply')
    parser.add_argument('--commit', action='store_true',
                      help='Commit changes after implementing fixes')
    parser.add_argument('--report-file', 
                      help='Save report to specified file')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize auto-improver
        improver = AutoImprover(args.project_root)
        
        # Analyze code
        logger.info("🚀 Starting AI-Interlinq Auto-Improvement System...")
        analysis_results = improver.analyze_code()
        
        # Generate report
        report = improver.generate_report()
        
        if args.report_file:
            with open(args.report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📄 Report saved to {args.report_file}")
        
        # Print summary
        print(f"\n📊 Auto-Improvement Analysis Summary:")
        print(f"   Files Analyzed: {analysis_results.total_files_analyzed}")
        print(f"   Suggestions: {len(analysis_results.suggestions)}")
        print(f"   Health Score: {analysis_results.overall_health_score:.1f}/100")
        print(f"   LAW-001 Compliant: {'✅' if analysis_results.law_compliance_status else '❌'}")
        
        # Show top suggestions
        if analysis_results.suggestions:
            print(f"\n🔍 Top Suggestions:")
            for i, suggestion in enumerate(analysis_results.suggestions[:5], 1):
                priority_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(suggestion.priority.value, '⚪')
                auto_icon = '🤖' if suggestion.auto_fixable else '👤'
                print(f"   {i}. {priority_icon} {auto_icon} {suggestion.title}")
                print(f"      {suggestion.description}")
        
        # Implement fixes if requested
        if not args.analyze_only:
            implementation_results = improver.implement_improvements(args.max_fixes)
            
            print(f"\n🔧 Implementation Results:")
            print(f"   Fixes Applied: {len(implementation_results['applied_fixes'])}")
            print(f"   Fixes Skipped: {len(implementation_results['skipped_fixes'])}")
            print(f"   Errors: {len(implementation_results['errors'])}")
            
            # Commit if requested
            if args.commit and implementation_results['applied_fixes']:
                if improver.commit_changes():
                    print(f"✅ Changes committed successfully")
                else:
                    print(f"❌ Failed to commit changes")
        
        print(f"\n🎯 Auto-improvement cycle completed!")
        
    except Exception as e:
        logger.error(f"❌ Auto-improvement failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()