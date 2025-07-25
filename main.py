# File: /main.py
# Directory: /

"""
LAW-001 Compliance: Main Integration Module
Integrates all components and ensures LAW-001 compliance at startup.
Must automatically load snapshots and verify dependencies.
"""

import sys
import time
import json
from pathlib import Path

# Direct imports to avoid dependency issues with full ai_interlinq package
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import LAW-001 compliance components directly
from ai_interlinq.core.snapshot_manager import SnapshotManager
from ai_interlinq.core.memory_loader import MemoryLoader  
from ai_interlinq.core.pattern_detector import PatternDetector
from ai_interlinq.core.learning_cycle import LearningCycleEngine
from ai_interlinq.core.status_checker import StatusChecker
from governance.voting_system import VotingSystem


class AIInterlinqLAW001System:
    """
    LAW-001 Compliance Main System
    
    Purpose: Main integration point for AI-Interlinq with LAW-001 compliance
    Requirements: Must automatically load snapshots and verify dependencies at startup
    """
    
    def __init__(self, agent_id: str = "mupoese_ai_core"):
        """
        Initialize LAW-001 compliant AI-Interlinq system.
        
        Args:
            agent_id: ID of the AI agent
        """
        self.agent_id = agent_id
        print(f"🤖 Initializing AI-Interlinq LAW-001 System - Agent: {agent_id}")
        
        # Initialize core components
        self.snapshot_manager = SnapshotManager(agent_id)
        self.memory_loader = MemoryLoader(agent_id)
        self.pattern_detector = PatternDetector(agent_id)
        self.learning_cycle = LearningCycleEngine(agent_id)
        self.status_checker = StatusChecker(agent_id)
        self.voting_system = VotingSystem()
        
        # System state
        self.law_001_compliant = False
        self.system_initialized = False
        self.dependencies_verified = False
        
    def startup(self) -> bool:
        """
        Perform LAW-001 compliant startup sequence.
        
        Returns:
            bool: True if startup successful and compliant
        """
        print("🚀 Starting LAW-001 compliance startup sequence...")
        
        try:
            # Step 1: Verify LAW-001 dependencies
            print("📋 Step 1: Verifying LAW-001 dependencies...")
            if not self._verify_dependencies():
                print("❌ Dependency verification failed")
                return False
            
            # Step 2: Initialize memory loading system
            print("💾 Step 2: Initializing memory loading system...")
            if not self._initialize_memory_system():
                print("❌ Memory system initialization failed")
                return False
            
            # Step 3: Load snapshots at startup (LAW-001 requirement)
            print("📸 Step 3: Loading snapshots at startup...")
            if not self._load_startup_snapshots():
                print("❌ Snapshot loading failed")
                return False
            
            # Step 4: Initialize pattern detection
            print("🔍 Step 4: Initializing pattern detection...")
            if not self._initialize_pattern_detection():
                print("❌ Pattern detection initialization failed")
                return False
            
            # Step 5: Initialize governance system
            print("🏛️ Step 5: Initializing governance system...")
            if not self._initialize_governance():
                print("❌ Governance system initialization failed")
                return False
            
            # Step 6: Final compliance verification
            print("✅ Step 6: Final LAW-001 compliance verification...")
            compliance_result = self._verify_final_compliance()
            
            if compliance_result["overall_compliance"]:
                self.law_001_compliant = True
                self.system_initialized = True
                print("🎉 LAW-001 compliance achieved - System ready!")
                return True
            else:
                print("❌ Final compliance verification failed")
                print(f"Missing: {compliance_result.get('critical_issues', [])}")
                return False
                
        except Exception as e:
            print(f"💥 Startup error: {e}")
            return False
    
    def execute_learning_cycle(self, trigger_cause: str, input_data: dict) -> dict:
        """
        Execute a complete LAW-001 learning cycle.
        
        Args:
            trigger_cause: What triggered this cycle
            input_data: Input data for the cycle
            
        Returns:
            dict: Cycle execution results
        """
        if not self.law_001_compliant:
            raise RuntimeError("System not LAW-001 compliant - cannot execute learning cycle")
        
        print(f"🔄 Executing LAW-001 learning cycle: {trigger_cause}")
        
        return self.learning_cycle.execute_full_cycle(trigger_cause, input_data)
    
    def get_system_status(self) -> dict:
        """
        Get comprehensive system status.
        
        Returns:
            dict: System status information
        """
        status = {
            "agent_id": self.agent_id,
            "law_001_compliant": self.law_001_compliant,
            "system_initialized": self.system_initialized,
            "dependencies_verified": self.dependencies_verified,
            "timestamp": time.time()
        }
        
        if self.system_initialized:
            # Get component status
            status.update({
                "memory_status": self.memory_loader.get_memory_statistics(),
                "pattern_analysis": self.pattern_detector.get_pattern_summary(),
                "learning_cycle_status": self.learning_cycle.get_cycle_status(),
                "governance_stats": self.voting_system.get_voting_statistics()
            })
            
            # Get compliance check
            compliance_check = self.status_checker.check_law_001_compliance()
            status["compliance_check"] = compliance_check
        
        return status
    
    def _verify_dependencies(self) -> bool:
        """Verify all LAW-001 dependencies."""
        try:
            verification_result = self.status_checker.verify_all_dependencies()
            self.dependencies_verified = verification_result["overall_compliance"]
            
            if not self.dependencies_verified:
                print("⚠️ Some dependencies failed:")
                for dep, status in verification_result["dependencies"].items():
                    status_icon = "✅" if status else "❌"
                    print(f"   {status_icon} {dep}")
                
                # Print recommendations
                if verification_result.get("recommendations"):
                    print("💡 Recommendations:")
                    for rec in verification_result["recommendations"]:
                        print(f"   • {rec}")
            
            return self.dependencies_verified
            
        except Exception as e:
            print(f"Error verifying dependencies: {e}")
            return False
    
    def _initialize_memory_system(self) -> bool:
        """Initialize memory loading system."""
        try:
            # Enable snapshot loading (LAW-001 requirement)
            success = self.memory_loader.enable_snapshot_loading()
            
            if success:
                memory_status = self.memory_loader.snapshot_mem()
                print(f"   Memory system status: {memory_status}")
                return memory_status == "ACTIVE"
            
            return False
            
        except Exception as e:
            print(f"Error initializing memory system: {e}")
            return False
    
    def _load_startup_snapshots(self) -> bool:
        """Load snapshots at startup (LAW-001 requirement)."""
        try:
            # Load snapshots at cycle start
            success = self.memory_loader.load_snapshots_at_cycle_start()
            
            if success:
                loaded_snapshots = self.memory_loader.get_loaded_snapshots()
                print(f"   Loaded {len(loaded_snapshots)} snapshots")
                
                # Prepare cycle context
                context = self.memory_loader.prepare_cycle_context()
                print(f"   Memory status: {context['memory_status']}")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error loading startup snapshots: {e}")
            return False
    
    def _initialize_pattern_detection(self) -> bool:
        """Initialize pattern detection system."""
        try:
            # Analyze current snapshots for patterns
            loaded_snapshots = self.memory_loader.get_loaded_snapshots()
            analysis = self.pattern_detector.analyze_patterns(loaded_snapshots)
            
            print(f"   Patterns detected: {analysis.get('patterns_detected', 0)}")
            print(f"   Deviations detected: {analysis.get('deviations_detected', 0)}")
            
            return isinstance(analysis, dict)
            
        except Exception as e:
            print(f"Error initializing pattern detection: {e}")
            return False
    
    def _initialize_governance(self) -> bool:
        """Initialize governance system."""
        try:
            # Process any pending proposed updates
            vote_ids = self.voting_system.process_proposed_updates()
            
            if vote_ids:
                print(f"   Created {len(vote_ids)} governance votes for pending updates")
            
            # Get voting statistics
            stats = self.voting_system.get_voting_statistics()
            print(f"   Active votes: {stats['active_votes']}")
            print(f"   Total votes: {stats['total_votes']}")
            
            return True
            
        except Exception as e:
            print(f"Error initializing governance: {e}")
            return False
    
    def _verify_final_compliance(self) -> dict:
        """Perform final LAW-001 compliance verification."""
        try:
            return self.status_checker.check_law_001_compliance()
        except Exception as e:
            return {
                "overall_compliance": False,
                "error": str(e),
                "critical_issues": [f"Compliance verification failed: {e}"]
            }


def main():
    """Main entry point for LAW-001 compliant AI-Interlinq system."""
    print("=" * 60)
    print("🤖 AI-Interlinq LAW-001 Compliance System")
    print("   Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle")
    print("=" * 60)
    
    # Initialize system
    system = AIInterlinqLAW001System()
    
    # Perform startup
    startup_success = system.startup()
    
    if startup_success:
        print("\n✨ System startup completed successfully!")
        print("🏛️ LAW-001 compliance: COMPLETE")
        
        # Display system status
        status = system.get_system_status()
        print(f"\n📊 System Status:")
        print(f"   Agent ID: {status['agent_id']}")
        print(f"   Compliance Status: {'COMPLETE' if status['law_001_compliant'] else 'INCOMPLETE'}")
        print(f"   Dependencies: {'VERIFIED' if status['dependencies_verified'] else 'FAILED'}")
        
        # Example learning cycle execution
        print("\n🔄 Executing example learning cycle...")
        try:
            cycle_result = system.execute_learning_cycle(
                trigger_cause="System startup demonstration",
                input_data={
                    "startup_time": time.time(),
                    "compliance_status": "COMPLETE",
                    "example": True
                }
            )
            
            if cycle_result["success"]:
                print(f"✅ Learning cycle completed successfully!")
                print(f"   Cycle ID: {cycle_result['cycle_id']}")
                print(f"   Duration: {cycle_result['total_time']:.2f}s")
            else:
                print(f"❌ Learning cycle failed: {cycle_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Learning cycle error: {e}")
        
        # System ready for operation
        print("\n🎯 System ready for AI-Interlinq operations!")
        print("   All LAW-001 requirements satisfied")
        print("   Learning cycle operational")
        print("   Governance system active")
        print("   Memory loading enabled")
        
        return True
        
    else:
        print("\n💥 System startup FAILED!")
        print("❌ LAW-001 compliance: INCOMPLETE")
        print("⚠️ System cannot operate without compliance")
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)