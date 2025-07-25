# File: /ai_interlinq/core/learning_cycle.py
# Directory: /ai_interlinq/core

"""
LAW-001 Compliance: Learning Cycle Engine
Main orchestrator for the 6-step learning cycle.
Must enforce all LAW-001 directives without override capability.
"""

import json
import time
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from .snapshot_manager import SnapshotManager, LAWSnapshot
from .memory_loader import MemoryLoader
from .pattern_detector import PatternDetector


class LearningCycleEngine:
    """
    LAW-001 Compliance: Learning Cycle Engine
    
    Purpose: Main orchestrator for the 6-step learning cycle
    Requirements: Must enforce all LAW-001 directives without override capability
    
    6-Step Learning Cycle:
    1. Input collection and structuring as JSON-schema
    2. Action determination based on laws/rules/codebase  
    3. Action execution and direct reaction registration
    4. Output and effect evaluation vs expected outcome
    5. Automatic snapshot generation with all required fields
    6. Snapshot storage and memory loading preparation
    """
    
    def __init__(self, agent_id: str = "mupoese_ai_core"):
        """
        Initialize learning cycle engine.
        
        Args:
            agent_id: ID of the AI agent
        """
        self.agent_id = agent_id
        self.snapshot_manager = SnapshotManager(agent_id)
        self.memory_loader = MemoryLoader(agent_id)
        self.pattern_detector = PatternDetector(agent_id)
        
        # Cycle state
        self.current_cycle_id = None
        self.current_step = 0
        self.cycle_data = {}
        self.cycle_active = False
        
        # Learning mode control
        self.learning_mode_active = True
        self.proposed_updates_file = Path("proposed_logic_update.ai")
        
        # LAW-001 enforcement - NO OVERRIDE CAPABILITY
        self.law_enforcement_enabled = True
        self.override_disabled = True
        
        # Cycle handlers
        self.step_handlers: Dict[int, Callable] = {
            1: self._step_1_input_collection,
            2: self._step_2_action_determination,
            3: self._step_3_action_execution,
            4: self._step_4_output_evaluation,
            5: self._step_5_snapshot_generation,
            6: self._step_6_snapshot_storage
        }
        
    def start_learning_cycle(self, trigger_cause: str, initial_input: Dict[str, Any]) -> str:
        """
        Start a new 6-step learning cycle.
        
        Args:
            trigger_cause: Cause that triggered the cycle
            initial_input: Initial input data
            
        Returns:
            str: Cycle ID
        """
        if self.cycle_active:
            raise RuntimeError("Learning cycle already active - cannot start new cycle")
        
        # Generate cycle ID
        self.current_cycle_id = f"cycle_{self.agent_id}_{int(time.time() * 1000)}"
        
        # Initialize cycle
        self.cycle_active = True
        self.current_step = 0
        self.cycle_data = {
            "cycle_id": self.current_cycle_id,
            "trigger_cause": trigger_cause,
            "initial_input": initial_input,
            "start_time": time.time(),
            "steps_completed": [],
            "deviations_detected": [],
            "learning_mode": self.learning_mode_active
        }
        
        # Enable memory loading at cycle start (LAW-001 requirement)
        self.memory_loader.enable_snapshot_loading()
        self.memory_loader.load_snapshots_at_cycle_start()
        
        print(f"Learning cycle started: {self.current_cycle_id}")
        print(f"Trigger cause: {trigger_cause}")
        
        return self.current_cycle_id
    
    def execute_cycle_step(self, step: int) -> Dict[str, Any]:
        """
        Execute a specific step in the learning cycle.
        
        Args:
            step: Step number (1-6)
            
        Returns:
            Dict with step execution results
        """
        if not self.cycle_active:
            raise RuntimeError("No active learning cycle")
        
        if step < 1 or step > 6:
            raise ValueError("Step must be between 1 and 6")
        
        if step != self.current_step + 1:
            raise RuntimeError(f"Steps must be executed in order. Expected step {self.current_step + 1}, got {step}")
        
        # Execute step handler
        step_handler = self.step_handlers[step]
        step_result = step_handler()
        
        # Update cycle state
        self.current_step = step
        self.cycle_data["steps_completed"].append({
            "step": step,
            "result": step_result,
            "timestamp": time.time()
        })
        
        print(f"Cycle {self.current_cycle_id} - Step {step} completed")
        
        return step_result
    
    def execute_full_cycle(self, trigger_cause: str, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete 6-step learning cycle.
        
        Args:
            trigger_cause: Cause that triggered the cycle
            initial_input: Initial input data
            
        Returns:
            Dict with complete cycle results
        """
        try:
            # Start cycle
            cycle_id = self.start_learning_cycle(trigger_cause, initial_input)
            
            # Execute all 6 steps
            step_results = []
            for step in range(1, 7):
                result = self.execute_cycle_step(step)
                step_results.append(result)
            
            # Complete cycle
            cycle_result = self.complete_cycle()
            
            return {
                "cycle_id": cycle_id,
                "success": True,
                "step_results": step_results,
                "cycle_result": cycle_result,
                "total_time": time.time() - self.cycle_data["start_time"]
            }
            
        except Exception as e:
            self.abort_cycle(str(e))
            return {
                "cycle_id": self.current_cycle_id,
                "success": False,
                "error": str(e),
                "steps_completed": len(self.cycle_data.get("steps_completed", []))
            }
    
    def complete_cycle(self) -> Dict[str, Any]:
        """
        Complete the current learning cycle.
        
        Returns:
            Dict with cycle completion results
        """
        if not self.cycle_active:
            raise RuntimeError("No active learning cycle")
        
        if self.current_step != 6:
            raise RuntimeError(f"Cycle incomplete - only {self.current_step} steps completed")
        
        # Finalize cycle
        self.cycle_data["end_time"] = time.time()
        self.cycle_data["total_duration"] = self.cycle_data["end_time"] - self.cycle_data["start_time"]
        self.cycle_data["status"] = "completed"
        
        # Reset cycle state
        cycle_result = self.cycle_data.copy()
        self.cycle_active = False
        self.current_cycle_id = None
        self.current_step = 0
        self.cycle_data = {}
        
        print(f"Learning cycle completed: {cycle_result['cycle_id']}")
        print(f"Total duration: {cycle_result['total_duration']:.2f}s")
        
        return cycle_result
    
    def abort_cycle(self, reason: str) -> None:
        """
        Abort the current learning cycle.
        
        Args:
            reason: Reason for aborting the cycle
        """
        if self.cycle_active:
            self.cycle_data["status"] = "aborted"
            self.cycle_data["abort_reason"] = reason
            self.cycle_data["end_time"] = time.time()
            
            print(f"Learning cycle aborted: {self.current_cycle_id}")
            print(f"Reason: {reason}")
            
            # Reset state
            self.cycle_active = False
            self.current_cycle_id = None
            self.current_step = 0
            self.cycle_data = {}
    
    def _step_1_input_collection(self) -> Dict[str, Any]:
        """
        Step 1: Input collection and structuring as JSON-schema.
        """
        try:
            # Collect and structure input data
            structured_input = {
                "raw_input": self.cycle_data["initial_input"],
                "trigger_cause": self.cycle_data["trigger_cause"],
                "timestamp": time.time(),
                "agent_id": self.agent_id,
                "memory_context": self.memory_loader.prepare_cycle_context()
            }
            
            # Validate JSON schema compliance
            if not isinstance(structured_input, dict):
                raise ValueError("Input must be structured as JSON object")
            
            # Store structured input in cycle data
            self.cycle_data["structured_input"] = structured_input
            
            return {
                "step": 1,
                "action": "Input collection and structuring",
                "success": True,
                "structured_input": structured_input
            }
            
        except Exception as e:
            return {
                "step": 1,
                "action": "Input collection and structuring",
                "success": False,
                "error": str(e)
            }
    
    def _step_2_action_determination(self) -> Dict[str, Any]:
        """
        Step 2: Action determination based on laws/rules/codebase.
        """
        try:
            structured_input = self.cycle_data["structured_input"]
            
            # Determine action based on current laws and rules
            action = self._determine_action_from_laws(structured_input)
            applied_law = self._get_applicable_law(structured_input)
            
            # Store determination in cycle data
            self.cycle_data["determined_action"] = action
            self.cycle_data["applied_law"] = applied_law
            
            return {
                "step": 2,
                "action": "Action determination",
                "success": True,
                "determined_action": action,
                "applied_law": applied_law
            }
            
        except Exception as e:
            return {
                "step": 2,
                "action": "Action determination",
                "success": False,
                "error": str(e)
            }
    
    def _step_3_action_execution(self) -> Dict[str, Any]:
        """
        Step 3: Action execution and direct reaction registration.
        """
        try:
            action = self.cycle_data["determined_action"]
            
            # Execute the determined action
            execution_result = self._execute_action(action)
            
            # Register direct reaction
            direct_reaction = self._register_direct_reaction(execution_result)
            
            # Store execution results in cycle data
            self.cycle_data["execution_result"] = execution_result
            self.cycle_data["direct_reaction"] = direct_reaction
            
            return {
                "step": 3,
                "action": "Action execution",
                "success": True,
                "execution_result": execution_result,
                "direct_reaction": direct_reaction
            }
            
        except Exception as e:
            return {
                "step": 3,
                "action": "Action execution",
                "success": False,
                "error": str(e)
            }
    
    def _step_4_output_evaluation(self) -> Dict[str, Any]:
        """
        Step 4: Output and effect evaluation vs expected outcome.
        """
        try:
            execution_result = self.cycle_data["execution_result"]
            
            # Evaluate output against expected outcome
            evaluation = self._evaluate_output(execution_result)
            
            # Detect any deviations
            deviation = self._detect_deviation(evaluation)
            
            # Store evaluation in cycle data
            self.cycle_data["output_evaluation"] = evaluation
            self.cycle_data["deviation"] = deviation
            
            if deviation:
                self.cycle_data["deviations_detected"].append(deviation)
            
            return {
                "step": 4,
                "action": "Output evaluation",
                "success": True,
                "evaluation": evaluation,
                "deviation": deviation
            }
            
        except Exception as e:
            return {
                "step": 4,
                "action": "Output evaluation",
                "success": False,
                "error": str(e)
            }
    
    def _step_5_snapshot_generation(self) -> Dict[str, Any]:
        """
        Step 5: Automatic snapshot generation with all required fields.
        """
        try:
            # Generate LAW-001 compliant snapshot
            snapshot = self.snapshot_manager.create_snapshot(
                context=f"Learning cycle {self.current_cycle_id}",
                input_data=self.cycle_data["structured_input"],
                action=self.cycle_data["determined_action"],
                applied_law=self.cycle_data["applied_law"],
                reaction=self.cycle_data["direct_reaction"],
                output=self.cycle_data["execution_result"],
                deviation=self.cycle_data["deviation"],
                cycle_step=5
            )
            
            # Store snapshot in cycle data
            self.cycle_data["generated_snapshot"] = snapshot
            
            return {
                "step": 5,
                "action": "Snapshot generation",
                "success": True,
                "snapshot_id": snapshot.snapshot_id
            }
            
        except Exception as e:
            return {
                "step": 5,
                "action": "Snapshot generation",
                "success": False,
                "error": str(e)
            }
    
    def _step_6_snapshot_storage(self) -> Dict[str, Any]:
        """
        Step 6: Snapshot storage and memory loading preparation.
        """
        try:
            snapshot = self.cycle_data["generated_snapshot"]
            
            # Save snapshot to filesystem
            save_success = self.snapshot_manager.save_snapshot(snapshot, update_current=True)
            
            if not save_success:
                raise RuntimeError("Failed to save snapshot")
            
            # Handle learning mode logic
            if self.learning_mode_active and self.cycle_data["deviation"]:
                self._handle_learning_mode_deviation()
            
            # Prepare for next cycle memory loading
            self.memory_loader.load_snapshots_at_cycle_start()
            
            return {
                "step": 6,
                "action": "Snapshot storage",
                "success": True,
                "snapshot_saved": True,
                "learning_mode_handled": self.learning_mode_active and bool(self.cycle_data["deviation"])
            }
            
        except Exception as e:
            return {
                "step": 6,
                "action": "Snapshot storage",
                "success": False,
                "error": str(e)
            }
    
    def _determine_action_from_laws(self, input_data: Dict[str, Any]) -> str:
        """
        Determine action based on current laws and rules.
        
        Args:
            input_data: Structured input data
            
        Returns:
            str: Determined action
        """
        # Simple rule-based action determination
        trigger_cause = input_data.get("trigger_cause", "")
        
        if "compliance" in trigger_cause.lower():
            return "Perform compliance check"
        elif "analysis" in trigger_cause.lower():
            return "Perform analysis"
        elif "update" in trigger_cause.lower():
            return "Process update request"
        else:
            return "Process general request"
    
    def _get_applicable_law(self, input_data: Dict[str, Any]) -> str:
        """
        Get the applicable law for the current context.
        
        Args:
            input_data: Structured input data
            
        Returns:
            str: Applicable law identifier
        """
        # Default to LAW-001 for all actions (as per requirements)
        return "LAW-001"
    
    def _execute_action(self, action: str) -> Any:
        """
        Execute the determined action.
        
        Args:
            action: Action to execute
            
        Returns:
            Execution result
        """
        # Simulate action execution
        execution_start = time.time()
        
        # Basic action execution logic
        if "compliance" in action.lower():
            result = "Compliance check completed"
        elif "analysis" in action.lower():
            result = "Analysis completed"
        elif "update" in action.lower():
            result = "Update processed"
        else:
            result = "Action completed"
        
        execution_time = time.time() - execution_start
        
        return {
            "action": action,
            "result": result,
            "execution_time": execution_time,
            "timestamp": time.time()
        }
    
    def _register_direct_reaction(self, execution_result: Any) -> str:
        """
        Register direct reaction to action execution.
        
        Args:
            execution_result: Result of action execution
            
        Returns:
            str: Direct reaction
        """
        if isinstance(execution_result, dict) and execution_result.get("result"):
            return f"Action executed successfully: {execution_result['result']}"
        else:
            return "Action execution completed"
    
    def _evaluate_output(self, execution_result: Any) -> Dict[str, Any]:
        """
        Evaluate output against expected outcome.
        
        Args:
            execution_result: Result of action execution
            
        Returns:
            Dict: Evaluation results
        """
        evaluation = {
            "expected": "Successful execution",
            "actual": execution_result,
            "matches_expected": True,
            "evaluation_timestamp": time.time()
        }
        
        # Simple evaluation logic
        if isinstance(execution_result, dict):
            if "error" in execution_result:
                evaluation["matches_expected"] = False
                evaluation["issue"] = "Execution contained error"
        
        return evaluation
    
    def _detect_deviation(self, evaluation: Dict[str, Any]) -> Optional[str]:
        """
        Detect deviation from expected behavior.
        
        Args:
            evaluation: Output evaluation results
            
        Returns:
            str or None: Deviation description if detected
        """
        if not evaluation.get("matches_expected", True):
            return f"Output deviation detected: {evaluation.get('issue', 'Unknown issue')}"
        
        return None
    
    def _handle_learning_mode_deviation(self) -> None:
        """
        Handle deviation when learning mode is active.
        """
        try:
            deviation = self.cycle_data["deviation"]
            
            if not deviation:
                return
            
            # Create proposed logic update
            proposed_update = {
                "timestamp": time.time(),
                "cycle_id": self.current_cycle_id,
                "deviation": deviation,
                "suggested_improvement": f"Review logic for handling: {self.cycle_data['trigger_cause']}",
                "input_context": self.cycle_data["structured_input"],
                "action_taken": self.cycle_data["determined_action"],
                "agent_id": self.agent_id
            }
            
            # Append to proposed updates file
            updates_list = []
            if self.proposed_updates_file.exists():
                try:
                    with open(self.proposed_updates_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            updates_list = json.loads(content)
                except:
                    updates_list = []
            
            updates_list.append(proposed_update)
            
            # Save updated list
            with open(self.proposed_updates_file, 'w', encoding='utf-8') as f:
                json.dump(updates_list, f, indent=2)
            
            print(f"Proposed logic update logged for deviation: {deviation}")
            
        except Exception as e:
            print(f"Error handling learning mode deviation: {e}")
    
    def get_cycle_status(self) -> Dict[str, Any]:
        """
        Get current cycle status.
        
        Returns:
            Dict: Current cycle status
        """
        return {
            "cycle_active": self.cycle_active,
            "current_cycle_id": self.current_cycle_id,
            "current_step": self.current_step,
            "learning_mode": self.learning_mode_active,
            "law_enforcement": self.law_enforcement_enabled,
            "override_disabled": self.override_disabled
        }
    
    def disable_override_capability(self) -> bool:
        """
        Permanently disable override capability (LAW-001 enforcement).
        
        Returns:
            bool: Always False - override cannot be enabled
        """
        self.override_disabled = True
        self.law_enforcement_enabled = True
        return False  # Override remains disabled
    
    def attempt_override(self) -> bool:
        """
        Attempt to override LAW-001 enforcement (will always fail).
        
        Returns:
            bool: Always False - override not allowed
        """
        print("WARNING: Override attempt blocked by LAW-001 enforcement")
        return False