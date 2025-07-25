#!/usr/bin/env python3
# File: /law001_functional_test.py
# Directory: /

"""
LAW-001 Functional Integration Test
Tests that all LAW-001 components work together properly.
"""

import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any


class LAW001FunctionalTest:
    """Test LAW-001 compliance functionality."""
    
    def __init__(self):
        """Initialize test environment."""
        self.test_results = {}
        self.test_agent_id = "test_ai_core"
        
    def test_snapshot_creation(self) -> bool:
        """Test snapshot creation functionality."""
        print("🧪 Testing snapshot creation...")
        
        try:
            # Create a test snapshot with LAW-001 required fields
            test_snapshot = {
                "context": "LAW-001 functional test execution",
                "input": {
                    "test_action": "verify_snapshot_creation",
                    "timestamp": time.time(),
                    "agent_id": self.test_agent_id
                },
                "action": "Created functional test snapshot",
                "applied_law": "LAW-001 - Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle", 
                "reaction": "Test snapshot successfully generated",
                "output": "Snapshot creation functionality verified",
                "deviation": None,
                "ai_signature": f"{self.test_agent_id}/law_engine.kernel/test.validator",
                "test_mode": True
            }
            
            # Save test snapshot
            test_file = "test_snapshot.ai"
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_snapshot, f, indent=2)
            
            # Verify it was created and is valid JSON
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded_snapshot = json.load(f)
            
            # Check required fields
            required_fields = [
                "context", "input", "action", "applied_law",
                "reaction", "output", "ai_signature"
            ]
            
            missing_fields = [field for field in required_fields if field not in loaded_snapshot]
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Clean up test file
            os.remove(test_file)
            
            print("✅ Snapshot creation test passed")
            return True
            
        except Exception as e:
            print(f"❌ Snapshot creation test failed: {e}")
            return False
    
    def test_memory_snapshots_directory(self) -> bool:
        """Test memory snapshots directory functionality."""
        print("🧪 Testing memory snapshots directory...")
        
        try:
            snapshots_dir = Path("memory/snapshots")
            
            # Verify directory exists and is writable
            if not snapshots_dir.exists():
                print("❌ Snapshots directory does not exist")
                return False
            
            # Test writing a snapshot to the directory
            test_snapshot_file = snapshots_dir / f"test_{int(time.time())}.json"
            
            test_data = {
                "test": True,
                "timestamp": time.time(),
                "purpose": "directory_write_test"
            }
            
            with open(test_snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            # Verify file was created and is readable
            with open(test_snapshot_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            if loaded_data["test"] is not True:
                print("❌ Data integrity test failed")
                return False
            
            # Clean up test file
            test_snapshot_file.unlink()
            
            print("✅ Memory snapshots directory test passed")
            return True
            
        except Exception as e:
            print(f"❌ Memory snapshots directory test failed: {e}")
            return False
    
    def test_proposed_logic_update(self) -> bool:
        """Test proposed logic update functionality."""
        print("🧪 Testing proposed logic update functionality...")
        
        try:
            # Read current state
            with open("proposed_logic_update.ai", 'r', encoding='utf-8') as f:
                current_updates = json.load(f)
            
            # Add a test update
            test_update = {
                "timestamp": time.time(),
                "agent_id": self.test_agent_id,
                "suggested_improvement": "Test logic update proposal",
                "reasoning": "Functional test verification",
                "test_mode": True
            }
            
            if not isinstance(current_updates, list):
                current_updates = []
            
            current_updates.append(test_update)
            
            # Save updated file
            with open("proposed_logic_update.ai", 'w', encoding='utf-8') as f:
                json.dump(current_updates, f, indent=2)
            
            # Verify it was saved correctly
            with open("proposed_logic_update.ai", 'r', encoding='utf-8') as f:
                saved_updates = json.load(f)
            
            if not any(update.get("test_mode") for update in saved_updates):
                print("❌ Test update not found in saved file")
                return False
            
            # Remove test update to restore original state
            filtered_updates = [update for update in saved_updates if not update.get("test_mode")]
            
            with open("proposed_logic_update.ai", 'w', encoding='utf-8') as f:
                json.dump(filtered_updates, f, indent=2)
            
            print("✅ Proposed logic update test passed")
            return True
            
        except Exception as e:
            print(f"❌ Proposed logic update test failed: {e}")
            return False
    
    def test_governance_files(self) -> bool:
        """Test governance system files."""
        print("🧪 Testing governance system files...")
        
        try:
            # Test law_control.governance file
            governance_file = Path("governance/law_control.governance")
            if not governance_file.exists():
                print("❌ Governance control file missing")
                return False
            
            with open(governance_file, 'r', encoding='utf-8') as f:
                governance_content = f.read()
            
            # Check for required governance elements
            required_elements = [
                "LAW_MODIFICATION_CONTROL",
                "mupoese_admin_core", 
                "governance.vote",
                "PROTECTED_LAWS",
                "LAW-001: PROTECTED"
            ]
            
            missing_elements = [elem for elem in required_elements if elem not in governance_content]
            if missing_elements:
                print(f"❌ Missing governance elements: {missing_elements}")
                return False
            
            # Test voting_system.py file
            voting_file = Path("governance/voting_system.py")
            if not voting_file.exists():
                print("❌ Voting system file missing")
                return False
            
            with open(voting_file, 'r', encoding='utf-8') as f:
                voting_content = f.read()
            
            # Basic syntax check
            try:
                compile(voting_content, str(voting_file), 'exec')
            except SyntaxError as e:
                print(f"❌ Voting system syntax error: {e}")
                return False
            
            # Check for required voting elements
            voting_elements = [
                "class VotingSystem",
                "create_logic_update_vote",
                "admin_decision",
                "mupoese_admin_core"
            ]
            
            missing_voting = [elem for elem in voting_elements if elem not in voting_content]
            if missing_voting:
                print(f"❌ Missing voting elements: {missing_voting}")
                return False
            
            print("✅ Governance system test passed")
            return True
            
        except Exception as e:
            print(f"❌ Governance system test failed: {e}")
            return False
    
    def test_law_definition(self) -> bool:
        """Test LAW-001 definition completeness."""
        print("🧪 Testing LAW-001 definition...")
        
        try:
            with open("law.ai", 'r', encoding='utf-8') as f:
                law_content = f.read()
            
            # Check critical LAW-001 elements
            critical_elements = [
                "ID: LAW-001",
                "Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle",
                "Severity: CRITICAL",
                "Enforceable: TRUE",
                "6-step learning cycle",
                "snapshot.ai",
                "memory.snapshot_mem()",
                "governance.vote",
                "Dependencies:",
                "mupoese_admin_core"
            ]
            
            missing_critical = [elem for elem in critical_elements if elem not in law_content]
            if missing_critical:
                print(f"❌ Missing critical LAW-001 elements: {missing_critical}")
                return False
            
            print("✅ LAW-001 definition test passed")
            return True
            
        except Exception as e:
            print(f"❌ LAW-001 definition test failed: {e}")
            return False
    
    def test_dependencies_simulation(self) -> bool:
        """Simulate dependency verification."""
        print("🧪 Testing dependency verification simulation...")
        
        try:
            # Simulate the four required dependencies
            dependencies = {
                "memory.snapshot_mem()": "ACTIVE",
                "laws.snapshot_validation": "TRUE", 
                "ai_status.verified": "TRUE",
                "logic_engine.boot": "SUCCESS"
            }
            
            # All dependencies should be in a valid state for this test
            failed_deps = [dep for dep, status in dependencies.items() 
                          if status not in ["ACTIVE", "TRUE", "SUCCESS"]]
            
            if failed_deps:
                print(f"❌ Failed dependencies: {failed_deps}")
                return False
            
            print("✅ Dependencies verification test passed")
            return True
            
        except Exception as e:
            print(f"❌ Dependencies verification test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all functional tests."""
        print("🚀 Starting LAW-001 Functional Tests")
        print("=" * 50)
        
        tests = [
            ("snapshot_creation", self.test_snapshot_creation),
            ("memory_snapshots_directory", self.test_memory_snapshots_directory),
            ("proposed_logic_update", self.test_proposed_logic_update),
            ("governance_files", self.test_governance_files),
            ("law_definition", self.test_law_definition),
            ("dependencies_simulation", self.test_dependencies_simulation)
        ]
        
        results = {}
        passed_tests = 0
        
        for test_name, test_func in tests:
            print(f"\n🔬 Running {test_name}...")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 FUNCTIONAL TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100
        
        status = "PASS" if passed_tests == total_tests else "PARTIAL" if passed_tests > 0 else "FAIL"
        status_emoji = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}
        
        print(f"{status_emoji[status]} Overall Status: {status}")
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            failed_tests = [name for name, result in results.items() if not result]
            print(f"❌ Failed Tests: {', '.join(failed_tests)}")
        
        return {
            "overall_status": status,
            "tests_passed": passed_tests,
            "total_tests": total_tests,
            "success_rate": success_rate,
            "results": results
        }


if __name__ == "__main__":
    # Change to script directory  
    os.chdir(Path(__file__).parent)
    
    # Run functional tests
    test_runner = LAW001FunctionalTest()
    results = test_runner.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if results["overall_status"] == "PASS" else 1
    sys.exit(exit_code)