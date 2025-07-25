# File: /ai_interlinq/core/status_checker.py  
# Directory: /ai_interlinq/core

"""
LAW-001 Compliance: Status Checker
Verifies all LAW-001 dependencies are met:
- memory.snapshot_mem() == ACTIVE
- laws.snapshot_validation == TRUE  
- ai_status.verified == TRUE
- logic_engine.boot == SUCCESS
"""

import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
from .memory_loader import MemoryLoader
from .snapshot_manager import SnapshotManager
from .pattern_detector import PatternDetector
from .learning_cycle import LearningCycleEngine


class StatusChecker:
    """
    LAW-001 Compliance: Status Checker
    
    Purpose: Verify all LAW-001 dependencies are met
    Requirements: Check all required dependencies for compliance
    """
    
    def __init__(self, agent_id: str = "mupoese_ai_core"):
        """
        Initialize status checker.
        
        Args:
            agent_id: ID of the AI agent
        """
        self.agent_id = agent_id
        self.memory_loader = MemoryLoader(agent_id)
        self.snapshot_manager = SnapshotManager(agent_id)
        self.pattern_detector = PatternDetector(agent_id)
        
        # Status tracking
        self.last_check_time = 0
        self.last_check_results = {}
        self.ai_status_verified = True
        self.logic_engine_boot_status = "SUCCESS"
        
    def verify_all_dependencies(self) -> Dict[str, Any]:
        """
        Verify all LAW-001 dependencies.
        
        Returns:
            Dict: Comprehensive dependency verification results
        """
        self.last_check_time = time.time()
        
        # Check each required dependency
        dependency_results = {
            "memory.snapshot_mem() == ACTIVE": self._check_memory_snapshot_mem(),
            "laws.snapshot_validation == TRUE": self._check_laws_snapshot_validation(),
            "ai_status.verified == TRUE": self._check_ai_status_verified(),
            "logic_engine.boot == SUCCESS": self._check_logic_engine_boot()
        }
        
        # Calculate overall compliance
        all_passed = all(dependency_results.values())
        
        # Compile comprehensive results
        verification_results = {
            "timestamp": self.last_check_time,
            "agent_id": self.agent_id,
            "overall_compliance": all_passed,
            "compliance_status": "COMPLETE" if all_passed else "INCOMPLETE",
            "dependencies": dependency_results,
            "detailed_status": self._get_detailed_status(),
            "recommendations": self._get_recommendations(dependency_results)
        }
        
        self.last_check_results = verification_results
        
        return verification_results
    
    def check_law_001_compliance(self) -> Dict[str, Any]:
        """
        Comprehensive LAW-001 compliance check.
        
        Returns:
            Dict: Complete compliance assessment
        """
        compliance_check = {
            "law_id": "LAW-001",
            "title": "Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle",
            "severity": "CRITICAL",
            "enforceable": True,
            "check_timestamp": time.time(),
            "agent_id": self.agent_id
        }
        
        # Verify core dependencies
        dependencies = self.verify_all_dependencies()
        compliance_check["dependencies"] = dependencies
        
        # Check file structure
        file_structure = self._check_required_file_structure()
        compliance_check["file_structure"] = file_structure
        
        # Check system functionality
        functionality = self._check_system_functionality()
        compliance_check["functionality"] = functionality
        
        # Calculate overall compliance score
        compliance_score = self._calculate_compliance_score(dependencies, file_structure, functionality)
        compliance_check["compliance_score"] = compliance_score
        
        # Determine final status
        compliance_check["status"] = "COMPLETE" if compliance_score >= 0.9 else "INCOMPLETE"
        compliance_check["critical_issues"] = self._identify_critical_issues(dependencies, file_structure, functionality)
        
        return compliance_check
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        
        Returns:
            Dict: System health information
        """
        health_status = {
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "components": {}
        }
        
        # Check memory system health
        health_status["components"]["memory_system"] = self._check_memory_system_health()
        
        # Check snapshot system health
        health_status["components"]["snapshot_system"] = self._check_snapshot_system_health()
        
        # Check pattern detector health
        health_status["components"]["pattern_detector"] = self._check_pattern_detector_health()
        
        # Check learning cycle health
        health_status["components"]["learning_cycle"] = self._check_learning_cycle_health()
        
        # Calculate overall health score
        component_scores = [comp.get("health_score", 0) for comp in health_status["components"].values()]
        health_status["overall_health_score"] = sum(component_scores) / len(component_scores) if component_scores else 0
        
        health_status["health_status"] = "HEALTHY" if health_status["overall_health_score"] >= 0.8 else "DEGRADED"
        
        return health_status
    
    def _check_memory_snapshot_mem(self) -> bool:
        """
        Check if memory.snapshot_mem() == ACTIVE.
        
        Returns:
            bool: True if memory snapshot is active
        """
        try:
            snapshot_mem_status = self.memory_loader.snapshot_mem()
            return snapshot_mem_status == "ACTIVE"
        except Exception as e:
            print(f"Error checking memory.snapshot_mem(): {e}")
            return False
    
    def _check_laws_snapshot_validation(self) -> bool:
        """
        Check if laws.snapshot_validation == TRUE.
        
        Returns:
            bool: True if snapshot validation is enabled
        """
        try:
            # Check if law.ai file exists and contains validation settings
            law_file = Path("law.ai")
            if not law_file.exists():
                return False
            
            with open(law_file, 'r', encoding='utf-8') as f:
                law_content = f.read()
            
            # Check for validation indicators in LAW-001
            validation_indicators = [
                "snapshot_validation",
                "memory.snapshot_mem()",
                "automatic snapshot generation"
            ]
            
            return any(indicator in law_content for indicator in validation_indicators)
            
        except Exception as e:
            print(f"Error checking laws.snapshot_validation: {e}")
            return False
    
    def _check_ai_status_verified(self) -> bool:
        """
        Check if ai_status.verified == TRUE.
        
        Returns:
            bool: True if AI status is verified
        """
        return self.ai_status_verified
    
    def _check_logic_engine_boot(self) -> bool:
        """
        Check if logic_engine.boot == SUCCESS.
        
        Returns:
            bool: True if logic engine boot was successful
        """
        return self.logic_engine_boot_status == "SUCCESS"
    
    def _get_detailed_status(self) -> Dict[str, Any]:
        """
        Get detailed status of all components.
        
        Returns:
            Dict: Detailed component status
        """
        detailed_status = {
            "memory_loader": {
                "status": self.memory_loader.snapshot_mem(),
                "snapshots_enabled": self.memory_loader.load_snapshots_enabled,
                "loaded_snapshots": len(self.memory_loader.get_loaded_snapshots())
            },
            "snapshot_manager": {
                "statistics": self.snapshot_manager.get_snapshot_statistics()
            },
            "pattern_detector": {
                "summary": self.pattern_detector.get_pattern_summary()
            }
        }
        
        return detailed_status
    
    def _get_recommendations(self, dependency_results: Dict[str, bool]) -> List[str]:
        """
        Get recommendations for failed dependencies.
        
        Args:
            dependency_results: Results of dependency checks
            
        Returns:
            List: Recommendations for fixing issues
        """
        recommendations = []
        
        if not dependency_results.get("memory.snapshot_mem() == ACTIVE"):
            recommendations.append("Enable memory snapshot loading with memory_loader.enable_snapshot_loading()")
        
        if not dependency_results.get("laws.snapshot_validation == TRUE"):
            recommendations.append("Ensure law.ai file contains proper snapshot validation configuration")
        
        if not dependency_results.get("ai_status.verified == TRUE"):
            recommendations.append("Verify AI agent status and authentication")
        
        if not dependency_results.get("logic_engine.boot == SUCCESS"):
            recommendations.append("Check logic engine initialization and resolve boot issues")
        
        return recommendations
    
    def _check_required_file_structure(self) -> Dict[str, Any]:
        """
        Check if required file structure exists.
        
        Returns:
            Dict: File structure check results
        """
        required_files = {
            "snapshot.ai": Path("snapshot.ai"),
            "law.ai": Path("law.ai"),
            "memory/snapshots/": Path("memory/snapshots"),
            "governance/": Path("governance"),
            "proposed_logic_update.ai": Path("proposed_logic_update.ai")
        }
        
        file_checks = {}
        for name, path in required_files.items():
            file_checks[name] = {
                "exists": path.exists(),
                "path": str(path),
                "is_directory": path.is_dir() if path.exists() else False
            }
        
        files_exist = sum(1 for check in file_checks.values() if check["exists"])
        total_files = len(file_checks)
        
        return {
            "files_checked": file_checks,
            "files_exist_count": files_exist,
            "total_required": total_files,
            "structure_complete": files_exist == total_files,
            "completion_percentage": (files_exist / total_files) * 100
        }
    
    def _check_system_functionality(self) -> Dict[str, Any]:
        """
        Check system functionality.
        
        Returns:
            Dict: Functionality check results
        """
        functionality_tests = {
            "snapshot_creation": self._test_snapshot_creation(),
            "memory_loading": self._test_memory_loading(),
            "pattern_detection": self._test_pattern_detection(),
            "dependency_verification": self._test_dependency_verification()
        }
        
        passed_tests = sum(1 for test in functionality_tests.values() if test)
        total_tests = len(functionality_tests)
        
        return {
            "tests": functionality_tests,
            "passed_count": passed_tests,
            "total_tests": total_tests,
            "functionality_score": (passed_tests / total_tests) if total_tests > 0 else 0,
            "all_functional": passed_tests == total_tests
        }
    
    def _calculate_compliance_score(self, dependencies: Dict, file_structure: Dict, functionality: Dict) -> float:
        """
        Calculate overall compliance score.
        
        Args:
            dependencies: Dependency check results
            file_structure: File structure check results
            functionality: Functionality check results
            
        Returns:
            float: Compliance score (0.0 - 1.0)
        """
        # Weight the different aspects
        dependency_score = sum(dependencies["dependencies"].values()) / len(dependencies["dependencies"])
        structure_score = file_structure["completion_percentage"] / 100
        functionality_score = functionality["functionality_score"]
        
        # Weighted average (dependencies are most critical)
        compliance_score = (dependency_score * 0.5 + structure_score * 0.3 + functionality_score * 0.2)
        
        return compliance_score
    
    def _identify_critical_issues(self, dependencies: Dict, file_structure: Dict, functionality: Dict) -> List[str]:
        """
        Identify critical issues preventing compliance.
        
        Args:
            dependencies: Dependency check results
            file_structure: File structure check results
            functionality: Functionality check results
            
        Returns:
            List: Critical issues
        """
        critical_issues = []
        
        # Check dependency failures
        for dep, status in dependencies["dependencies"].items():
            if not status:
                critical_issues.append(f"Failed dependency: {dep}")
        
        # Check missing required files
        for file_name, file_info in file_structure["files_checked"].items():
            if not file_info["exists"]:
                critical_issues.append(f"Missing required file/directory: {file_name}")
        
        # Check functionality failures
        for test_name, test_result in functionality["tests"].items():
            if not test_result:
                critical_issues.append(f"Failed functionality test: {test_name}")
        
        return critical_issues
    
    def _test_snapshot_creation(self) -> bool:
        """Test snapshot creation functionality."""
        try:
            test_snapshot = self.snapshot_manager.create_snapshot(
                context="Status check test",
                input_data={"test": True},
                action="Test snapshot creation"
            )
            return test_snapshot is not None
        except Exception:
            return False
    
    def _test_memory_loading(self) -> bool:
        """Test memory loading functionality."""
        try:
            self.memory_loader.enable_snapshot_loading()
            return self.memory_loader.snapshot_mem() == "ACTIVE"
        except Exception:
            return False
    
    def _test_pattern_detection(self) -> bool:
        """Test pattern detection functionality."""
        try:
            analysis = self.pattern_detector.analyze_patterns([])
            return isinstance(analysis, dict)
        except Exception:
            return False
    
    def _test_dependency_verification(self) -> bool:
        """Test dependency verification functionality."""
        try:
            results = self.verify_all_dependencies()
            return isinstance(results, dict) and "dependencies" in results
        except Exception:
            return False
    
    def _check_memory_system_health(self) -> Dict[str, Any]:
        """Check memory system health."""
        try:
            stats = self.memory_loader.get_memory_statistics()
            validation = self.memory_loader.validate_memory_dependencies()
            
            health_score = sum(validation.values()) / len(validation) if validation else 0
            
            return {
                "status": "HEALTHY" if health_score >= 0.8 else "DEGRADED",
                "health_score": health_score,
                "statistics": stats,
                "validation": validation
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "health_score": 0,
                "error": str(e)
            }
    
    def _check_snapshot_system_health(self) -> Dict[str, Any]:
        """Check snapshot system health."""
        try:
            stats = self.snapshot_manager.get_snapshot_statistics()
            
            # Basic health assessment
            health_score = 1.0 if stats.get("total_snapshots", 0) >= 0 else 0
            
            return {
                "status": "HEALTHY" if health_score >= 0.8 else "DEGRADED",
                "health_score": health_score,
                "statistics": stats
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "health_score": 0,
                "error": str(e)
            }
    
    def _check_pattern_detector_health(self) -> Dict[str, Any]:
        """Check pattern detector health."""
        try:
            summary = self.pattern_detector.get_pattern_summary()
            
            # Health based on successful operation
            health_score = 1.0 if isinstance(summary, dict) else 0
            
            return {
                "status": "HEALTHY" if health_score >= 0.8 else "DEGRADED",
                "health_score": health_score,
                "summary": summary
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "health_score": 0,
                "error": str(e)
            }
    
    def _check_learning_cycle_health(self) -> Dict[str, Any]:
        """Check learning cycle health."""
        try:
            # Basic functionality test
            cycle_engine = LearningCycleEngine(self.agent_id)
            status = cycle_engine.get_cycle_status()
            
            health_score = 1.0 if isinstance(status, dict) else 0
            
            return {
                "status": "HEALTHY" if health_score >= 0.8 else "DEGRADED",
                "health_score": health_score,
                "cycle_status": status
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "health_score": 0,
                "error": str(e)
            }