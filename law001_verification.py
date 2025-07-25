#!/usr/bin/env python3
# File: /law001_verification.py
# Directory: /

"""
LAW-001 Compliance Verification Script
Verifies all LAW-001 requirements are met without importing problematic modules.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists."""
    path = Path(filepath)
    exists = path.exists()
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"{status}: {description} ({filepath})")
    return exists


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a required directory exists."""
    path = Path(dirpath)
    exists = path.is_dir()
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"{status}: {description} ({dirpath})")
    return exists


def validate_json_file(filepath: str, required_fields: List[str] = None) -> bool:
    """Validate that a JSON file exists and has required fields."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"❌ Missing required fields in {filepath}: {missing_fields}")
                return False
        
        print(f"✅ Valid JSON structure in {filepath}")
        return True
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating {filepath}: {e}")
        return False


def validate_law_ai_file() -> bool:
    """Validate law.ai file contains LAW-001."""
    try:
        with open("law.ai", 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_elements = [
            "LAW-001",
            "Cause-Input-Action-Law-Reaction-Output-Effect",
            "Severity: CRITICAL",
            "Enforceable: TRUE",
            "memory.snapshot_mem()",
            "governance.vote"
        ]
        
        missing = [elem for elem in required_elements if elem not in content]
        if missing:
            print(f"❌ LAW-001 missing required elements: {missing}")
            return False
        
        print("✅ LAW-001 definition complete and valid")
        return True
    except Exception as e:
        print(f"❌ Error validating law.ai: {e}")
        return False


def check_core_modules() -> Dict[str, bool]:
    """Check if core modules exist and are syntactically valid."""
    core_modules = {
        "snapshot_manager.py": "ai_interlinq/core/snapshot_manager.py",
        "memory_loader.py": "ai_interlinq/core/memory_loader.py", 
        "pattern_detector.py": "ai_interlinq/core/pattern_detector.py",
        "learning_cycle.py": "ai_interlinq/core/learning_cycle.py",
        "status_checker.py": "ai_interlinq/core/status_checker.py"
    }
    
    results = {}
    print("\n🔍 Checking Core Modules:")
    
    for module_name, module_path in core_modules.items():
        exists = check_file_exists(module_path, f"Core module: {module_name}")
        
        # Basic syntax check
        if exists:
            try:
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, module_path, 'exec')
                print(f"✅ Syntax valid: {module_name}")
                results[module_name] = True
            except SyntaxError as e:
                print(f"❌ Syntax error in {module_name}: {e}")
                results[module_name] = False
            except Exception as e:
                print(f"❌ Error checking {module_name}: {e}")
                results[module_name] = False
        else:
            results[module_name] = False
    
    return results


def verify_snapshot_ai_structure() -> bool:
    """Verify snapshot.ai has proper LAW-001 structure."""
    required_fields = [
        "context", "input", "action", "applied_law", 
        "reaction", "output", "ai_signature"
    ]
    return validate_json_file("snapshot.ai", required_fields)


def verify_governance_system() -> bool:
    """Verify governance system is complete."""
    governance_files = [
        ("governance/law_control.governance", "Governance control system"),
        ("governance/voting_system.py", "Voting system implementation")
    ]
    
    all_exist = True
    for filepath, description in governance_files:
        exists = check_file_exists(filepath, description)
        all_exist = all_exist and exists
    
    return all_exist


def run_law001_verification() -> Dict[str, Any]:
    """Run complete LAW-001 verification."""
    print("🚀 Starting LAW-001 Compliance Verification")
    print("=" * 50)
    
    results = {
        "overall_status": "UNKNOWN",
        "root_files": {},
        "directories": {},
        "core_modules": {},
        "governance": False,
        "law_definition": False
    }
    
    # Check root level files
    print("\n📁 Checking Root Level Files:")
    results["root_files"]["snapshot.ai"] = verify_snapshot_ai_structure()
    results["root_files"]["proposed_logic_update.ai"] = check_file_exists(
        "proposed_logic_update.ai", "Proposed logic update file"
    )
    results["root_files"]["law.ai"] = validate_law_ai_file()
    results["root_files"]["main.py"] = check_file_exists("main.py", "Main integration file")
    
    # Check directory structure
    print("\n📂 Checking Directory Structure:")
    results["directories"]["memory/snapshots"] = check_directory_exists(
        "memory/snapshots", "Snapshot history storage"
    )
    results["directories"]["governance"] = check_directory_exists(
        "governance", "Governance system directory"
    )
    results["directories"]["ai_interlinq/core"] = check_directory_exists(
        "ai_interlinq/core", "Core modules directory"
    )
    
    # Check core modules
    results["core_modules"] = check_core_modules()
    
    # Check governance system
    print("\n🏛️ Checking Governance System:")
    results["governance"] = verify_governance_system()
    
    # Check LAW-001 definition
    print("\n⚖️ Checking LAW-001 Definition:")
    results["law_definition"] = results["root_files"]["law.ai"]
    
    # Calculate overall status
    all_root_files = all(results["root_files"].values())
    all_directories = all(results["directories"].values())
    all_core_modules = all(results["core_modules"].values())
    governance_ok = results["governance"]
    law_definition_ok = results["law_definition"]
    
    if all([all_root_files, all_directories, all_core_modules, governance_ok, law_definition_ok]):
        results["overall_status"] = "COMPLETE"
    elif any([all_root_files, all_directories, all_core_modules, governance_ok, law_definition_ok]):
        results["overall_status"] = "PARTIAL"
    else:
        results["overall_status"] = "INCOMPLETE"
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    status_emoji = {
        "COMPLETE": "✅",
        "PARTIAL": "⚠️", 
        "INCOMPLETE": "❌"
    }
    
    print(f"{status_emoji[results['overall_status']]} Overall LAW-001 Status: {results['overall_status']}")
    print(f"✅ Root Files: {sum(results['root_files'].values())}/{len(results['root_files'])}")
    print(f"✅ Directories: {sum(results['directories'].values())}/{len(results['directories'])}")
    print(f"✅ Core Modules: {sum(results['core_modules'].values())}/{len(results['core_modules'])}")
    print(f"✅ Governance: {'YES' if results['governance'] else 'NO'}")
    print(f"✅ LAW Definition: {'YES' if results['law_definition'] else 'NO'}")
    
    return results


if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Run verification
    results = run_law001_verification()
    
    # Exit with appropriate code
    exit_code = 0 if results["overall_status"] == "COMPLETE" else 1
    sys.exit(exit_code)