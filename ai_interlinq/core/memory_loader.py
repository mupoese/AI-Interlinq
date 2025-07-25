# File: /ai_interlinq/core/memory_loader.py
# Directory: /ai_interlinq/core

"""
LAW-001 Compliance: Memory Loading System
Loads snapshots at start of each cycle (memory.load_snapshots=True)
Must implement memory.snapshot_mem() functionality.
"""

import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from .snapshot_manager import LAWSnapshot, SnapshotManager


class MemoryLoader:
    """
    LAW-001 Compliance: Memory Loading System
    
    Purpose: Load snapshots at start of each cycle (memory.load_snapshots=True)
    Requirements: Must implement memory.snapshot_mem() functionality
    """
    
    def __init__(self, agent_id: str = "mupoese_ai_core"):
        """
        Initialize memory loader.
        
        Args:
            agent_id: ID of the AI agent
        """
        self.agent_id = agent_id
        self.snapshot_manager = SnapshotManager(agent_id)
        self.loaded_snapshots: List[LAWSnapshot] = []
        self.snapshot_memory: Dict[str, Any] = {}
        self.memory_status = "INACTIVE"
        self.load_snapshots_enabled = False
        
    def enable_snapshot_loading(self) -> bool:
        """
        Enable snapshot loading (memory.load_snapshots=True).
        
        Returns:
            bool: Success status
        """
        try:
            self.load_snapshots_enabled = True
            self.memory_status = "ACTIVE"
            return True
        except Exception as e:
            print(f"Error enabling snapshot loading: {e}")
            return False
    
    def disable_snapshot_loading(self) -> bool:
        """
        Disable snapshot loading (memory.load_snapshots=False).
        
        Returns:
            bool: Success status
        """
        try:
            self.load_snapshots_enabled = False
            self.memory_status = "INACTIVE"
            return True
        except Exception as e:
            print(f"Error disabling snapshot loading: {e}")
            return False
    
    def snapshot_mem(self) -> str:
        """
        LAW-001 Required: memory.snapshot_mem() functionality.
        
        Returns:
            str: Memory status (ACTIVE/INACTIVE)
        """
        return self.memory_status
    
    def load_snapshots_at_cycle_start(self, max_snapshots: int = 10) -> bool:
        """
        Load snapshots at the start of each learning cycle.
        
        Args:
            max_snapshots: Maximum number of recent snapshots to load
            
        Returns:
            bool: Success status
        """
        if not self.load_snapshots_enabled:
            return False
        
        try:
            # Load current snapshot
            current_snapshot = self.snapshot_manager.load_current_snapshot()
            
            # Load recent snapshots for context
            recent_snapshots = self.snapshot_manager.list_recent_snapshots(max_snapshots)
            
            # Clear existing loaded snapshots
            self.loaded_snapshots.clear()
            self.snapshot_memory.clear()
            
            # Add current snapshot if it exists
            if current_snapshot:
                self.loaded_snapshots.append(current_snapshot)
                self._add_to_memory(current_snapshot)
            
            # Add recent snapshots
            for snapshot in recent_snapshots:
                if snapshot not in self.loaded_snapshots:
                    self.loaded_snapshots.append(snapshot)
                    self._add_to_memory(snapshot)
            
            # Update memory status
            self.memory_status = "ACTIVE" if self.loaded_snapshots else "INACTIVE"
            
            return True
            
        except Exception as e:
            print(f"Error loading snapshots at cycle start: {e}")
            self.memory_status = "INACTIVE"
            return False
    
    def get_loaded_snapshots(self) -> List[LAWSnapshot]:
        """
        Get list of currently loaded snapshots.
        
        Returns:
            List of loaded snapshots
        """
        return self.loaded_snapshots.copy()
    
    def get_snapshot_memory(self) -> Dict[str, Any]:
        """
        Get the snapshot memory dictionary.
        
        Returns:
            Dict containing processed snapshot data
        """
        return self.snapshot_memory.copy()
    
    def search_memory_by_context(self, context_query: str) -> List[LAWSnapshot]:
        """
        Search loaded snapshots by context.
        
        Args:
            context_query: Context to search for
            
        Returns:
            List of matching snapshots
        """
        matching_snapshots = []
        
        for snapshot in self.loaded_snapshots:
            if context_query.lower() in snapshot.context.lower():
                matching_snapshots.append(snapshot)
        
        return matching_snapshots
    
    def search_memory_by_law(self, law_name: str) -> List[LAWSnapshot]:
        """
        Search loaded snapshots by applied law.
        
        Args:
            law_name: Law name to search for
            
        Returns:
            List of matching snapshots
        """
        matching_snapshots = []
        
        for snapshot in self.loaded_snapshots:
            if law_name in snapshot.applied_law:
                matching_snapshots.append(snapshot)
        
        return matching_snapshots
    
    def search_memory_by_deviation(self) -> List[LAWSnapshot]:
        """
        Search loaded snapshots that contain deviations.
        
        Returns:
            List of snapshots with deviations
        """
        deviation_snapshots = []
        
        for snapshot in self.loaded_snapshots:
            if snapshot.deviation is not None:
                deviation_snapshots.append(snapshot)
        
        return deviation_snapshots
    
    def get_memory_patterns(self) -> Dict[str, Any]:
        """
        Analyze loaded snapshots for patterns.
        
        Returns:
            Dict containing identified patterns
        """
        if not self.loaded_snapshots:
            return {}
        
        patterns = {
            "total_snapshots": len(self.loaded_snapshots),
            "law_frequency": {},
            "action_frequency": {},
            "deviation_count": 0,
            "cycle_step_distribution": {},
            "time_range": {}
        }
        
        timestamps = []
        
        for snapshot in self.loaded_snapshots:
            # Count law applications
            law = snapshot.applied_law
            patterns["law_frequency"][law] = patterns["law_frequency"].get(law, 0) + 1
            
            # Count action types
            action = snapshot.action
            patterns["action_frequency"][action] = patterns["action_frequency"].get(action, 0) + 1
            
            # Count deviations
            if snapshot.deviation is not None:
                patterns["deviation_count"] += 1
            
            # Count cycle steps
            step = snapshot.cycle_step
            patterns["cycle_step_distribution"][step] = patterns["cycle_step_distribution"].get(step, 0) + 1
            
            # Collect timestamps
            timestamps.append(snapshot.timestamp)
        
        # Calculate time range
        if timestamps:
            patterns["time_range"] = {
                "earliest": min(timestamps),
                "latest": max(timestamps),
                "span_seconds": max(timestamps) - min(timestamps)
            }
        
        return patterns
    
    def get_last_action_context(self) -> Optional[Dict[str, Any]]:
        """
        Get context from the last action for continuity.
        
        Returns:
            Dict with last action context or None
        """
        if not self.loaded_snapshots:
            return None
        
        # Sort by timestamp to get the most recent
        recent_snapshot = max(self.loaded_snapshots, key=lambda s: s.timestamp)
        
        return {
            "context": recent_snapshot.context,
            "action": recent_snapshot.action,
            "output": recent_snapshot.output,
            "applied_law": recent_snapshot.applied_law,
            "timestamp": recent_snapshot.timestamp,
            "cycle_step": recent_snapshot.cycle_step
        }
    
    def prepare_cycle_context(self) -> Dict[str, Any]:
        """
        Prepare context for the next learning cycle based on loaded memory.
        
        Returns:
            Dict with prepared context
        """
        patterns = self.get_memory_patterns()
        last_context = self.get_last_action_context()
        deviations = self.search_memory_by_deviation()
        
        cycle_context = {
            "memory_status": self.memory_status,
            "loaded_snapshots_count": len(self.loaded_snapshots),
            "patterns": patterns,
            "last_action": last_context,
            "pending_deviations": len(deviations),
            "requires_attention": len(deviations) > 0,
            "memory_load_time": time.time()
        }
        
        return cycle_context
    
    def validate_memory_dependencies(self) -> Dict[str, bool]:
        """
        Validate LAW-001 memory dependencies.
        
        Returns:
            Dict with validation results for each dependency
        """
        validation_results = {
            "memory.snapshot_mem() == ACTIVE": self.snapshot_mem() == "ACTIVE",
            "memory.load_snapshots_enabled": self.load_snapshots_enabled,
            "snapshots_loaded": len(self.loaded_snapshots) > 0,
            "snapshot_memory_available": len(self.snapshot_memory) > 0
        }
        
        return validation_results
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive memory loading statistics.
        
        Returns:
            Dict with memory statistics
        """
        stats = {
            "memory_status": self.memory_status,
            "load_snapshots_enabled": self.load_snapshots_enabled,
            "loaded_snapshots_count": len(self.loaded_snapshots),
            "memory_entries": len(self.snapshot_memory),
            "agent_id": self.agent_id
        }
        
        if self.loaded_snapshots:
            timestamps = [s.timestamp for s in self.loaded_snapshots]
            stats.update({
                "oldest_loaded_snapshot": min(timestamps),
                "newest_loaded_snapshot": max(timestamps),
                "memory_span_seconds": max(timestamps) - min(timestamps)
            })
        
        return stats
    
    def _add_to_memory(self, snapshot: LAWSnapshot) -> None:
        """
        Add snapshot data to the memory dictionary.
        
        Args:
            snapshot: Snapshot to add to memory
        """
        memory_key = f"{snapshot.snapshot_id}"
        
        self.snapshot_memory[memory_key] = {
            "context": snapshot.context,
            "action": snapshot.action,
            "applied_law": snapshot.applied_law,
            "output": snapshot.output,
            "deviation": snapshot.deviation,
            "timestamp": snapshot.timestamp,
            "cycle_step": snapshot.cycle_step
        }
        
        # Also add indexed entries for quick lookup
        law_key = f"law_{snapshot.applied_law}"
        if law_key not in self.snapshot_memory:
            self.snapshot_memory[law_key] = []
        
        self.snapshot_memory[law_key].append(memory_key)
        
        # Add step-based indexing
        step_key = f"step_{snapshot.cycle_step}"
        if step_key not in self.snapshot_memory:
            self.snapshot_memory[step_key] = []
        
        self.snapshot_memory[step_key].append(memory_key)
    
    def clear_memory(self) -> bool:
        """
        Clear all loaded memory.
        
        Returns:
            bool: Success status
        """
        try:
            self.loaded_snapshots.clear()
            self.snapshot_memory.clear()
            if not self.load_snapshots_enabled:
                self.memory_status = "INACTIVE"
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False