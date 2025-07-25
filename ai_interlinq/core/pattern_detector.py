# File: /ai_interlinq/core/pattern_detector.py
# Directory: /ai_interlinq/core

"""
LAW-001 Compliance: Pattern Detection Module
Detects repetitive patterns and systematic deviations.
Must trigger escalation when deviation > threshold.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from .snapshot_manager import LAWSnapshot
from .memory_loader import MemoryLoader


@dataclass
class Pattern:
    """Represents a detected pattern."""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    first_seen: float
    last_seen: float
    examples: List[str]
    deviation_indicator: bool


@dataclass
class Deviation:
    """Represents a detected deviation."""
    deviation_id: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    pattern_reference: Optional[str]
    timestamp: float
    snapshot_id: str
    escalation_required: bool


class PatternDetector:
    """
    LAW-001 Compliance: Pattern Detection Module
    
    Purpose: Detect repetitive patterns and systematic deviations
    Requirements: Must trigger escalation when deviation > threshold
    """
    
    def __init__(self, agent_id: str = "mupoese_ai_core", deviation_threshold: float = 0.3):
        """
        Initialize pattern detector.
        
        Args:
            agent_id: ID of the AI agent
            deviation_threshold: Threshold for escalation (0.0-1.0)
        """
        self.agent_id = agent_id
        self.deviation_threshold = deviation_threshold
        self.memory_loader = MemoryLoader(agent_id)
        
        # Pattern storage
        self.detected_patterns: Dict[str, Pattern] = {}
        self.detected_deviations: Dict[str, Deviation] = {}
        
        # Pattern analysis cache
        self._pattern_cache: Dict[str, Any] = {}
        self._analysis_timestamp = 0
        
        # Escalation tracking
        self.escalation_count = 0
        self.last_escalation_time = 0
        
    def analyze_patterns(self, snapshots: Optional[List[LAWSnapshot]] = None) -> Dict[str, Any]:
        """
        Analyze patterns in snapshots.
        
        Args:
            snapshots: List of snapshots to analyze, or None to use loaded memory
            
        Returns:
            Dict with analysis results
        """
        if snapshots is None:
            snapshots = self.memory_loader.get_loaded_snapshots()
        
        if not snapshots:
            return {"error": "No snapshots available for analysis"}
        
        analysis_results = {
            "total_snapshots": len(snapshots),
            "patterns_detected": 0,
            "deviations_detected": 0,
            "escalations_required": 0,
            "analysis_timestamp": time.time()
        }
        
        # Detect different types of patterns
        action_patterns = self._detect_action_patterns(snapshots)
        temporal_patterns = self._detect_temporal_patterns(snapshots)
        law_patterns = self._detect_law_application_patterns(snapshots)
        deviation_patterns = self._detect_deviation_patterns(snapshots)
        
        # Store detected patterns
        all_patterns = {
            **action_patterns,
            **temporal_patterns,
            **law_patterns,
            **deviation_patterns
        }
        
        for pattern_id, pattern in all_patterns.items():
            self.detected_patterns[pattern_id] = pattern
            if pattern.deviation_indicator:
                analysis_results["deviations_detected"] += 1
        
        analysis_results["patterns_detected"] = len(all_patterns)
        
        # Check for escalation requirements
        escalations = self._check_escalation_requirements()
        analysis_results["escalations_required"] = len(escalations)
        
        # Update cache
        self._pattern_cache = analysis_results
        self._analysis_timestamp = time.time()
        
        return analysis_results
    
    def detect_systematic_deviations(self, snapshots: Optional[List[LAWSnapshot]] = None) -> List[Deviation]:
        """
        Detect systematic deviations that require attention.
        
        Args:
            snapshots: List of snapshots to analyze
            
        Returns:
            List of detected deviations
        """
        if snapshots is None:
            snapshots = self.memory_loader.get_loaded_snapshots()
        
        deviations = []
        
        if not snapshots:
            return deviations
        
        # Analyze deviation frequency and patterns
        deviation_snapshots = [s for s in snapshots if s.deviation is not None]
        
        if not deviation_snapshots:
            return deviations
        
        # Calculate deviation rate
        deviation_rate = len(deviation_snapshots) / len(snapshots)
        
        # Create systematic deviation if rate exceeds threshold
        if deviation_rate > self.deviation_threshold:
            deviation = Deviation(
                deviation_id=self._generate_deviation_id(),
                severity="HIGH" if deviation_rate > 0.5 else "MEDIUM",
                description=f"Systematic deviation detected: {deviation_rate:.2%} of snapshots contain deviations",
                pattern_reference=None,
                timestamp=time.time(),
                snapshot_id="multiple",
                escalation_required=True
            )
            
            deviations.append(deviation)
            self.detected_deviations[deviation.deviation_id] = deviation
        
        # Analyze specific deviation patterns
        deviation_types = {}
        for snapshot in deviation_snapshots:
            dev_type = self._categorize_deviation(snapshot.deviation)
            deviation_types[dev_type] = deviation_types.get(dev_type, 0) + 1
        
        # Create deviations for frequent types
        for dev_type, count in deviation_types.items():
            if count >= 3:  # Pattern threshold
                deviation = Deviation(
                    deviation_id=self._generate_deviation_id(),
                    severity="MEDIUM",
                    description=f"Repeated deviation pattern: {dev_type} (occurred {count} times)",
                    pattern_reference=dev_type,
                    timestamp=time.time(),
                    snapshot_id="pattern",
                    escalation_required=count >= 5
                )
                
                deviations.append(deviation)
                self.detected_deviations[deviation.deviation_id] = deviation
        
        return deviations
    
    def trigger_escalation(self, deviation: Deviation) -> bool:
        """
        Trigger escalation for a deviation that exceeds threshold.
        
        Args:
            deviation: Deviation that requires escalation
            
        Returns:
            bool: Success status
        """
        try:
            self.escalation_count += 1
            self.last_escalation_time = time.time()
            
            # Create escalation log
            escalation_data = {
                "escalation_id": f"esc_{self.agent_id}_{int(time.time())}",
                "deviation_id": deviation.deviation_id,
                "severity": deviation.severity,
                "description": deviation.description,
                "timestamp": time.time(),
                "agent_id": self.agent_id,
                "escalation_count": self.escalation_count
            }
            
            # Save escalation log
            escalation_path = Path("memory/snapshots") / f"escalation_{escalation_data['escalation_id']}.json"
            with open(escalation_path, 'w', encoding='utf-8') as f:
                json.dump(escalation_data, f, indent=2)
            
            print(f"ESCALATION TRIGGERED: {deviation.severity} - {deviation.description}")
            
            return True
            
        except Exception as e:
            print(f"Error triggering escalation: {e}")
            return False
    
    def check_repetitive_patterns(self, window_size: int = 10) -> List[Pattern]:
        """
        Check for repetitive patterns in recent snapshots.
        
        Args:
            window_size: Number of recent snapshots to analyze
            
        Returns:
            List of repetitive patterns found
        """
        snapshots = self.memory_loader.get_loaded_snapshots()
        
        if len(snapshots) < window_size:
            window_size = len(snapshots)
        
        # Get recent snapshots
        recent_snapshots = sorted(snapshots, key=lambda s: s.timestamp)[-window_size:]
        
        repetitive_patterns = []
        
        # Check for repeated actions
        action_sequence = [s.action for s in recent_snapshots]
        action_repetitions = self._find_sequence_repetitions(action_sequence)
        
        for sequence, count in action_repetitions.items():
            if count >= 3:  # Repetition threshold
                pattern = Pattern(
                    pattern_id=self._generate_pattern_id(),
                    pattern_type="repetitive_action",
                    description=f"Action sequence repeated {count} times: {sequence}",
                    frequency=count,
                    confidence=min(count / window_size, 1.0),
                    first_seen=recent_snapshots[0].timestamp,
                    last_seen=recent_snapshots[-1].timestamp,
                    examples=[sequence],
                    deviation_indicator=count >= 5
                )
                repetitive_patterns.append(pattern)
        
        return repetitive_patterns
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Get summary of all detected patterns and deviations.
        
        Returns:
            Dict with pattern summary
        """
        summary = {
            "total_patterns": len(self.detected_patterns),
            "total_deviations": len(self.detected_deviations),
            "escalation_count": self.escalation_count,
            "last_escalation": self.last_escalation_time,
            "deviation_threshold": self.deviation_threshold,
            "patterns_by_type": {},
            "deviations_by_severity": {},
            "escalation_required_count": 0
        }
        
        # Categorize patterns
        for pattern in self.detected_patterns.values():
            pattern_type = pattern.pattern_type
            summary["patterns_by_type"][pattern_type] = summary["patterns_by_type"].get(pattern_type, 0) + 1
        
        # Categorize deviations
        for deviation in self.detected_deviations.values():
            severity = deviation.severity
            summary["deviations_by_severity"][severity] = summary["deviations_by_severity"].get(severity, 0) + 1
            
            if deviation.escalation_required:
                summary["escalation_required_count"] += 1
        
        return summary
    
    def _detect_action_patterns(self, snapshots: List[LAWSnapshot]) -> Dict[str, Pattern]:
        """Detect patterns in action sequences."""
        patterns = {}
        
        # Count action frequencies
        action_counts = {}
        for snapshot in snapshots:
            action = snapshot.action
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Create patterns for frequent actions
        total_snapshots = len(snapshots)
        for action, count in action_counts.items():
            frequency_ratio = count / total_snapshots
            
            if frequency_ratio > 0.1:  # 10% threshold
                pattern_id = f"action_{hashlib.md5(action.encode()).hexdigest()[:8]}"
                
                patterns[pattern_id] = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="frequent_action",
                    description=f"Frequent action: {action} ({frequency_ratio:.1%})",
                    frequency=count,
                    confidence=frequency_ratio,
                    first_seen=min(s.timestamp for s in snapshots if s.action == action),
                    last_seen=max(s.timestamp for s in snapshots if s.action == action),
                    examples=[action],
                    deviation_indicator=frequency_ratio > 0.5
                )
        
        return patterns
    
    def _detect_temporal_patterns(self, snapshots: List[LAWSnapshot]) -> Dict[str, Pattern]:
        """Detect temporal patterns in snapshots."""
        patterns = {}
        
        if len(snapshots) < 2:
            return patterns
        
        # Sort by timestamp
        sorted_snapshots = sorted(snapshots, key=lambda s: s.timestamp)
        
        # Calculate time intervals
        intervals = []
        for i in range(1, len(sorted_snapshots)):
            interval = sorted_snapshots[i].timestamp - sorted_snapshots[i-1].timestamp
            intervals.append(interval)
        
        # Find regular intervals
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            
            # Check for regular timing patterns
            regular_count = sum(1 for interval in intervals if abs(interval - avg_interval) < avg_interval * 0.1)
            
            if regular_count > len(intervals) * 0.7:  # 70% regularity
                pattern_id = "temporal_regular"
                
                patterns[pattern_id] = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="temporal_regularity",
                    description=f"Regular timing pattern: {avg_interval:.1f}s average interval",
                    frequency=regular_count,
                    confidence=regular_count / len(intervals),
                    first_seen=sorted_snapshots[0].timestamp,
                    last_seen=sorted_snapshots[-1].timestamp,
                    examples=[f"{avg_interval:.1f}s"],
                    deviation_indicator=False
                )
        
        return patterns
    
    def _detect_law_application_patterns(self, snapshots: List[LAWSnapshot]) -> Dict[str, Pattern]:
        """Detect patterns in law applications."""
        patterns = {}
        
        # Count law applications
        law_counts = {}
        for snapshot in snapshots:
            law = snapshot.applied_law
            law_counts[law] = law_counts.get(law, 0) + 1
        
        # Create patterns for law usage
        total_snapshots = len(snapshots)
        for law, count in law_counts.items():
            frequency_ratio = count / total_snapshots
            
            pattern_id = f"law_{hashlib.md5(law.encode()).hexdigest()[:8]}"
            
            patterns[pattern_id] = Pattern(
                pattern_id=pattern_id,
                pattern_type="law_application",
                description=f"Law application: {law} ({frequency_ratio:.1%})",
                frequency=count,
                confidence=frequency_ratio,
                first_seen=min(s.timestamp for s in snapshots if s.applied_law == law),
                last_seen=max(s.timestamp for s in snapshots if s.applied_law == law),
                examples=[law],
                deviation_indicator=law != "LAW-001" and frequency_ratio > 0.3
            )
        
        return patterns
    
    def _detect_deviation_patterns(self, snapshots: List[LAWSnapshot]) -> Dict[str, Pattern]:
        """Detect patterns in deviations."""
        patterns = {}
        
        deviation_snapshots = [s for s in snapshots if s.deviation is not None]
        
        if not deviation_snapshots:
            return patterns
        
        # Categorize deviations
        deviation_types = {}
        for snapshot in deviation_snapshots:
            dev_type = self._categorize_deviation(snapshot.deviation)
            if dev_type not in deviation_types:
                deviation_types[dev_type] = []
            deviation_types[dev_type].append(snapshot)
        
        # Create patterns for deviation types
        for dev_type, dev_snapshots in deviation_types.items():
            if len(dev_snapshots) >= 2:
                pattern_id = f"deviation_{hashlib.md5(dev_type.encode()).hexdigest()[:8]}"
                
                patterns[pattern_id] = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="deviation_pattern",
                    description=f"Deviation pattern: {dev_type}",
                    frequency=len(dev_snapshots),
                    confidence=len(dev_snapshots) / len(snapshots),
                    first_seen=min(s.timestamp for s in dev_snapshots),
                    last_seen=max(s.timestamp for s in dev_snapshots),
                    examples=[dev_type],
                    deviation_indicator=True
                )
        
        return patterns
    
    def _check_escalation_requirements(self) -> List[str]:
        """Check which patterns/deviations require escalation."""
        escalation_required = []
        
        for pattern in self.detected_patterns.values():
            if pattern.deviation_indicator and pattern.confidence > self.deviation_threshold:
                escalation_required.append(pattern.pattern_id)
        
        for deviation in self.detected_deviations.values():
            if deviation.escalation_required:
                escalation_required.append(deviation.deviation_id)
        
        return escalation_required
    
    def _categorize_deviation(self, deviation_text: str) -> str:
        """Categorize a deviation based on its text."""
        if deviation_text is None:
            return "unknown"
        
        text_lower = deviation_text.lower()
        
        if "timeout" in text_lower or "time" in text_lower:
            return "timing_deviation"
        elif "error" in text_lower or "fail" in text_lower:
            return "execution_error"
        elif "unexpected" in text_lower or "anomal" in text_lower:
            return "unexpected_behavior"
        elif "threshold" in text_lower or "limit" in text_lower:
            return "threshold_violation"
        else:
            return "general_deviation"
    
    def _find_sequence_repetitions(self, sequence: List[str]) -> Dict[str, int]:
        """Find repetitions in a sequence."""
        repetitions = {}
        
        for i in range(len(sequence)):
            for j in range(i + 1, len(sequence)):
                if sequence[i] == sequence[j]:
                    key = sequence[i]
                    repetitions[key] = repetitions.get(key, 0) + 1
        
        return repetitions
    
    def _generate_pattern_id(self) -> str:
        """Generate unique pattern ID."""
        timestamp = int(time.time() * 1000)
        return f"pat_{self.agent_id}_{timestamp}"
    
    def _generate_deviation_id(self) -> str:
        """Generate unique deviation ID."""
        timestamp = int(time.time() * 1000)
        return f"dev_{self.agent_id}_{timestamp}"