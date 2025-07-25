# File: /ai_interlinq/core/snapshot_manager.py
# Directory: /ai_interlinq/core

"""
LAW-001 Compliance: Snapshot Management System
Handles creation and management of AI execution snapshots per LAW-001 requirements.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict


@dataclass
class LAWSnapshot:
    """LAW-001 compliant snapshot structure."""
    context: str
    input: Dict[str, Any]
    action: str
    applied_law: str
    reaction: str
    output: Any
    deviation: Optional[str]
    ai_signature: str
    timestamp: float
    snapshot_id: str
    cycle_step: int  # 1-6 for the 6-step learning cycle
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary format."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert snapshot to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class SnapshotManager:
    """
    LAW-001 Compliance: Snapshot Management System
    
    Purpose: Handle creation and management of AI execution snapshots
    Requirements: Must implement snapshot.ai generation with all required fields
    """
    
    def __init__(self, agent_id: str = "mupoese_ai_core"):
        """
        Initialize snapshot manager.
        
        Args:
            agent_id: ID of the AI agent creating snapshots
        """
        self.agent_id = agent_id
        self.snapshots_dir = Path("memory/snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.current_snapshot_path = Path("snapshot.ai")
        
    def create_snapshot(
        self,
        context: str,
        input_data: Dict[str, Any],
        action: str,
        applied_law: str = "LAW-001",
        reaction: str = "",
        output: Any = None,
        deviation: Optional[str] = None,
        cycle_step: int = 1
    ) -> LAWSnapshot:
        """
        Create a new LAW-001 compliant snapshot.
        
        Args:
            context: Description of the execution context
            input_data: Input data that triggered the action
            action: Action taken by the AI
            applied_law: Law/rule applied (default LAW-001)
            reaction: Direct reaction to the action
            output: Output produced by the action
            deviation: Any deviation from expected behavior
            cycle_step: Current step in the 6-step learning cycle
            
        Returns:
            LAWSnapshot: Created snapshot
        """
        snapshot_id = self._generate_snapshot_id()
        
        # Generate AI signature
        ai_signature = self._generate_ai_signature(
            context, input_data, action, applied_law
        )
        
        snapshot = LAWSnapshot(
            context=context,
            input=input_data,
            action=action,
            applied_law=applied_law,
            reaction=reaction,
            output=output,
            deviation=deviation,
            ai_signature=ai_signature,
            timestamp=time.time(),
            snapshot_id=snapshot_id,
            cycle_step=cycle_step
        )
        
        return snapshot
    
    def save_snapshot(self, snapshot: LAWSnapshot, update_current: bool = True) -> bool:
        """
        Save snapshot to filesystem.
        
        Args:
            snapshot: Snapshot to save
            update_current: Whether to update the current snapshot.ai file
            
        Returns:
            bool: Success status
        """
        try:
            # Save to snapshots directory with timestamp
            timestamp_str = datetime.fromtimestamp(
                snapshot.timestamp, tz=timezone.utc
            ).strftime("%Y%m%d_%H%M%S")
            
            snapshot_filename = f"snapshot_{timestamp_str}_{snapshot.snapshot_id}.ai"
            snapshot_path = self.snapshots_dir / snapshot_filename
            
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                f.write(snapshot.to_json())
            
            # Update current snapshot.ai if requested
            if update_current:
                with open(self.current_snapshot_path, 'w', encoding='utf-8') as f:
                    f.write(snapshot.to_json())
            
            return True
            
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False
    
    def load_current_snapshot(self) -> Optional[LAWSnapshot]:
        """
        Load the current snapshot.ai file.
        
        Returns:
            LAWSnapshot or None if not found/invalid
        """
        try:
            if not self.current_snapshot_path.exists():
                return None
                
            with open(self.current_snapshot_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return LAWSnapshot(**data)
            
        except Exception as e:
            print(f"Error loading current snapshot: {e}")
            return None
    
    def load_snapshot_by_id(self, snapshot_id: str) -> Optional[LAWSnapshot]:
        """
        Load a specific snapshot by ID from the snapshots directory.
        
        Args:
            snapshot_id: ID of snapshot to load
            
        Returns:
            LAWSnapshot or None if not found
        """
        try:
            # Search for snapshot file with matching ID
            for snapshot_file in self.snapshots_dir.glob(f"*_{snapshot_id}.ai"):
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return LAWSnapshot(**data)
            
            return None
            
        except Exception as e:
            print(f"Error loading snapshot {snapshot_id}: {e}")
            return None
    
    def list_recent_snapshots(self, limit: int = 10) -> List[LAWSnapshot]:
        """
        List recent snapshots from the snapshots directory.
        
        Args:
            limit: Maximum number of snapshots to return
            
        Returns:
            List of recent snapshots sorted by timestamp (newest first)
        """
        snapshots = []
        
        try:
            # Get all snapshot files
            snapshot_files = list(self.snapshots_dir.glob("snapshot_*.ai"))
            
            # Sort by modification time (newest first)
            snapshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Load snapshots up to limit
            for snapshot_file in snapshot_files[:limit]:
                try:
                    with open(snapshot_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    snapshots.append(LAWSnapshot(**data))
                except Exception as e:
                    print(f"Error loading snapshot {snapshot_file}: {e}")
                    continue
            
            return snapshots
            
        except Exception as e:
            print(f"Error listing snapshots: {e}")
            return []
    
    def generate_cycle_snapshot(
        self,
        cycle_data: Dict[str, Any],
        step: int,
        deviation_detected: bool = False
    ) -> LAWSnapshot:
        """
        Generate snapshot for a specific step in the 6-step learning cycle.
        
        Args:
            cycle_data: Data from the current learning cycle
            step: Current step (1-6) in the learning cycle
            deviation_detected: Whether deviation was detected
            
        Returns:
            LAWSnapshot: Generated snapshot
        """
        step_actions = {
            1: "Input collection and structuring",
            2: "Action determination based on laws/rules/codebase", 
            3: "Action execution and reaction registration",
            4: "Output and effect evaluation",
            5: "Automatic snapshot generation",
            6: "Snapshot storage and memory loading preparation"
        }
        
        context = f"LAW-001 Learning Cycle Step {step}"
        action = step_actions.get(step, f"Unknown step {step}")
        
        deviation = None
        if deviation_detected:
            deviation = f"Deviation detected during step {step}"
        
        snapshot = self.create_snapshot(
            context=context,
            input_data=cycle_data,
            action=action,
            applied_law="LAW-001",
            reaction=f"Step {step} completed",
            output=f"Cycle step {step} executed successfully",
            deviation=deviation,
            cycle_step=step
        )
        
        return snapshot
    
    def _generate_snapshot_id(self) -> str:
        """Generate unique snapshot ID."""
        timestamp = int(time.time() * 1000)
        return f"snap_{self.agent_id}_{timestamp}"
    
    def _generate_ai_signature(
        self,
        context: str,
        input_data: Dict[str, Any],
        action: str,
        applied_law: str
    ) -> str:
        """
        Generate AI signature for the snapshot.
        
        Args:
            context: Execution context
            input_data: Input data
            action: Action taken
            applied_law: Law applied
            
        Returns:
            str: AI signature
        """
        # Create hash of key components for signature
        signature_data = f"{context}:{json.dumps(input_data, sort_keys=True)}:{action}:{applied_law}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()[:16]
        
        return f"{self.agent_id}/law_engine.kernel/memory.snapshot.validator/{signature_hash}"
    
    def cleanup_old_snapshots(self, days_old: int = 30) -> int:
        """
        Clean up old snapshot files.
        
        Args:
            days_old: Number of days after which snapshots are considered old
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            cutoff_time = time.time() - (days_old * 24 * 3600)
            deleted_count = 0
            
            for snapshot_file in self.snapshots_dir.glob("snapshot_*.ai"):
                if snapshot_file.stat().st_mtime < cutoff_time:
                    snapshot_file.unlink()
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up snapshots: {e}")
            return 0
    
    def get_snapshot_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored snapshots.
        
        Returns:
            Dict with snapshot statistics
        """
        try:
            snapshot_files = list(self.snapshots_dir.glob("snapshot_*.ai"))
            
            if not snapshot_files:
                return {
                    "total_snapshots": 0,
                    "oldest_snapshot": None,
                    "newest_snapshot": None,
                    "storage_size_bytes": 0
                }
            
            # Calculate statistics
            total_size = sum(f.stat().st_size for f in snapshot_files)
            modification_times = [f.stat().st_mtime for f in snapshot_files]
            
            return {
                "total_snapshots": len(snapshot_files),
                "oldest_snapshot": datetime.fromtimestamp(min(modification_times)),
                "newest_snapshot": datetime.fromtimestamp(max(modification_times)),
                "storage_size_bytes": total_size
            }
            
        except Exception as e:
            return {"error": str(e)}