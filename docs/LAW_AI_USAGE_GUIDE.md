# law.ai System Usage Guide

Complete guide for using the law.ai system within AI-Interlinq, including LAW-001 compliance, learning cycles, and governance procedures.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [LAW-001 Learning Cycle](#law-001-learning-cycle)
4. [Snapshot Management](#snapshot-management)
5. [Memory System](#memory-system)
6. [Pattern Detection](#pattern-detection)
7. [Governance Framework](#governance-framework)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

### What is law.ai?

law.ai is a comprehensive AI governance and learning framework that implements the **Cause-Input-Action-Law-Reaction-Output-Effect (CIALORE)** learning cycle. It ensures consistent, traceable, and governed AI behavior through automated snapshot generation, pattern detection, and governance controls.

### LAW-001 Specification

- **ID:** LAW-001
- **Title:** Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle
- **Severity:** CRITICAL
- **Enforceable:** TRUE
- **Version:** 1.1.0
- **Scope:** Global AI Execution Layer

### Core Principles

1. **Every AI operation must trigger a 6-step learning cycle**
2. **All executions must be tracked through snapshots**
3. **Pattern deviations must be detected and reported**
4. **Law modifications require governance approval**
5. **Memory loading ensures continuity between cycles**

## Getting Started

### Basic Setup

```python
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.snapshot_manager import SnapshotManager
from ai_interlinq.core.memory_loader import MemoryLoader
from ai_interlinq.core.pattern_detector import PatternDetector
from ai_interlinq.core.status_checker import StatusChecker

# Initialize all law.ai components
learning_cycle = LearningCycle()
snapshot_manager = SnapshotManager()
memory_loader = MemoryLoader()
pattern_detector = PatternDetector()
status_checker = StatusChecker()

# Verify LAW-001 compliance
compliance_status = learning_cycle.verify_compliance()
print(f"LAW-001 Compliance Status: {compliance_status}")
```

### Verification of Dependencies

```python
# Check all required dependencies
dependencies = status_checker.check_dependencies()
print("Dependency Status:")
for dep, status in dependencies.items():
    print(f"  {dep}: {'✅' if status else '❌'}")
```

## LAW-001 Learning Cycle

### The 6-Step CIALORE Process

The learning cycle follows these mandatory steps:

1. **Cause Detection**: Identify the trigger for AI operation
2. **Input Collection**: Gather and structure data as JSON schema
3. **Action Determination**: Decide action based on laws, ruleset, codebase
4. **Law Application**: Apply relevant laws and execute action
5. **Reaction Registration**: Capture immediate response
6. **Output & Effect Evaluation**: Assess results and generate snapshot

### Basic Learning Cycle Execution

```python
import asyncio

async def execute_basic_cycle():
    """Execute a basic LAW-001 learning cycle"""
    
    # Initialize learning cycle
    cycle = LearningCycle()
    
    # Execute the 6-step cycle
    result = await cycle.execute_cycle(
        cause="user_input_detected",
        input_data={
            "user_id": "mupoese",
            "action": "process_data",
            "payload": {"task": "analysis", "data": "sample_data"},
            "timestamp": time.time()
        }
    )
    
    print(f"Learning cycle completed: {result['cycle_completed']}")
    print(f"Compliance status: {result['output']['compliance_status']}")
    print(f"Execution time: {result['output']['execution_time']}")
    
    return result

# Run the cycle
result = asyncio.run(execute_basic_cycle())
```

### Advanced Learning Cycle with Custom Parameters

```python
async def execute_advanced_cycle():
    """Execute advanced learning cycle with custom configuration"""
    
    cycle = LearningCycle()
    
    # Configure learning parameters
    config = {
        "memory_loading_enabled": True,
        "pattern_detection_enabled": True,
        "governance_checks_enabled": True,
        "auto_snapshot_generation": True
    }
    
    result = await cycle.execute_cycle(
        cause="ai_communication_request",
        input_data={
            "operation": "message_processing",
            "message_type": "priority_request",
            "sender": "agent_001",
            "recipient": "agent_002",
            "encryption_enabled": True,
            "governance_level": "HIGH"
        },
        config=config
    )
    
    # Check for deviations
    if result.get('deviation'):
        print(f"⚠️ Deviation detected: {result['deviation']}")
    
    return result
```

## Snapshot Management

### Understanding Snapshots

Snapshots are complete records of each learning cycle execution, containing all required LAW-001 fields:

- **context**: Description of the learning cycle execution
- **input**: Complete input data including cause and parameters
- **action**: Action taken during the cycle
- **applied_law**: Which law was applied (typically LAW-001)
- **reaction**: Immediate response from the system
- **output**: Results and evaluation data
- **deviation**: Any deviations from expected behavior
- **ai_signature**: Authentication signature
- **timestamp**: Execution timestamp
- **snapshot_id**: Unique identifier
- **cycle_step**: Current step in the cycle
- **compliance_verified**: Compliance verification flag

### Manual Snapshot Creation

```python
# Create snapshot manually
snapshot_data = {
    "context": "Manual snapshot creation for testing",
    "input": {
        "cause": "manual_test",
        "input_data": {"test": True},
        "timestamp": time.time()
    },
    "action": "Test snapshot generation",
    "applied_law": "LAW-001",
    "reaction": "Snapshot created successfully",
    "output": {"status": "success"},
    "deviation": None
}

snapshot = snapshot_manager.create_snapshot(snapshot_data)
print(f"Created snapshot: {snapshot['snapshot_id']}")
```

### Retrieving Snapshots

```python
# Get latest snapshot
latest = snapshot_manager.get_latest_snapshot()
if latest:
    print(f"Latest snapshot: {latest['snapshot_id']}")
    print(f"Compliance: {latest['compliance_verified']}")

# Get snapshot by ID
specific_snapshot = snapshot_manager.get_snapshot_by_id("cycle_1_1753452276")
if specific_snapshot:
    print(f"Found snapshot: {specific_snapshot['context']}")

# Get snapshots by date range
import datetime
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
recent_snapshots = snapshot_manager.get_snapshots_by_date_range(
    start_date=yesterday,
    end_date=datetime.datetime.now()
)
print(f"Recent snapshots: {len(recent_snapshots)}")
```

### Snapshot Validation

```python
# Validate snapshot integrity
validation_result = snapshot_manager.validate_snapshot(snapshot)
if validation_result['valid']:
    print("✅ Snapshot is valid")
else:
    print(f"❌ Snapshot validation failed: {validation_result['errors']}")
```

## Memory System

### Loading Previous Snapshots

The memory system automatically loads previous snapshots at the start of each learning cycle:

```python
# Initialize memory loader
memory_loader = MemoryLoader()

# Load all snapshots (automatic on cycle start)
snapshots = memory_loader.load_snapshots()
print(f"Loaded {len(snapshots)} snapshots from memory")

# Get memory statistics
stats = memory_loader.get_memory_stats()
print(f"Memory usage: {stats['memory_usage_mb']} MB")
print(f"Total snapshots: {stats['total_snapshots']}")
print(f"Oldest snapshot: {stats['oldest_snapshot_date']}")
```

### Memory Configuration

```python
# Configure memory loading behavior
memory_config = {
    "max_snapshots_to_load": 1000,
    "memory_usage_limit_mb": 512,
    "auto_cleanup_enabled": True,
    "cleanup_age_days": 30
}

memory_loader.configure(memory_config)
```

### Memory Cleanup

```python
# Manual memory cleanup
cleanup_result = memory_loader.cleanup_old_snapshots(max_age_days=7)
print(f"Cleaned up {cleanup_result['cleaned_count']} old snapshots")

# Free memory
memory_loader.free_memory()
print("Memory freed")
```

## Pattern Detection

### Understanding Pattern Detection

The pattern detector identifies:
- **Repetitive Patterns**: Same inputs producing same outputs
- **Systematic Deviations**: Consistent differences from expected behavior
- **Anomalies**: Unusual or unexpected patterns
- **Performance Trends**: Changes in execution performance

### Basic Pattern Detection

```python
# Initialize pattern detector
pattern_detector = PatternDetector()

# Analyze patterns in recent snapshots
patterns = pattern_detector.detect_patterns()

print("Pattern Analysis Results:")
print(f"  Repetitive patterns: {patterns.get('repetitive_count', 0)}")
print(f"  Deviations detected: {patterns.get('deviation_count', 0)}")
print(f"  Anomalies found: {patterns.get('anomaly_count', 0)}")

if patterns.get('deviation_detected'):
    print("⚠️ Systematic deviation detected - review required")
```

### Advanced Pattern Analysis

```python
# Analyze specific snapshot for patterns
result = await learning_cycle.execute_cycle(
    cause="pattern_analysis_test",
    input_data={"test_pattern": True}
)

pattern_analysis = pattern_detector.analyze_snapshot_patterns(result)

print("Detailed Pattern Analysis:")
for pattern_type, details in pattern_analysis.items():
    print(f"  {pattern_type}: {details}")
```

### Setting Pattern Thresholds

```python
# Configure pattern detection thresholds
thresholds = {
    "deviation_threshold": 0.1,  # 10% deviation triggers alert
    "repetition_threshold": 5,   # 5 identical patterns trigger alert
    "anomaly_threshold": 2.0,    # 2 standard deviations from mean
    "performance_threshold": 1.5  # 50% performance degradation
}

pattern_detector.set_thresholds(thresholds)
```

## Governance Framework

### Understanding Governance

The governance system controls:
- **Law Modifications**: Changes to core laws require approval
- **Voting Procedures**: Democratic decision making
- **Authorization Levels**: Different permission levels
- **Audit Trails**: Complete record of governance actions

### Checking Governance Status

```python
from ai_interlinq.governance.voting_system import VotingSystem

# Initialize governance system
voting_system = VotingSystem()

# Check governance status
governance_status = voting_system.get_governance_status()
print(f"Governance active: {governance_status['active']}")
print(f"Pending votes: {governance_status['pending_votes']}")
```

### Proposing Law Changes

```python
# Propose a new law or modification
proposal = {
    "title": "Update pattern detection threshold",
    "description": "Increase deviation threshold from 0.1 to 0.15",
    "law_id": "LAW-001",
    "proposed_changes": {
        "deviation_threshold": 0.15
    },
    "justification": "Reduce false positive alerts while maintaining security"
}

proposal_id = voting_system.create_proposal(
    proposal_data=proposal,
    proposer="mupoese_admin"
)

print(f"Proposal created: {proposal_id}")
```

### Voting on Proposals

```python
# Vote on a proposal
vote_result = voting_system.cast_vote(
    proposal_id=proposal_id,
    voter="admin_user",
    vote="approve",  # or "reject" or "abstain"
    reason="Justified change to reduce false positives"
)

if vote_result['success']:
    print("✅ Vote cast successfully")
else:
    print(f"❌ Vote failed: {vote_result['error']}")
```

### Checking Vote Results

```python
# Get proposal status
proposal_status = voting_system.get_proposal_status(proposal_id)
print(f"Proposal status: {proposal_status['status']}")
print(f"Votes for: {proposal_status['votes_for']}")
print(f"Votes against: {proposal_status['votes_against']}")

# Check if proposal passed
if proposal_status['status'] == 'approved':
    print("✅ Proposal approved - changes can be implemented")
```

## Best Practices

### 1. Always Use Learning Cycles

```python
# ✅ CORRECT: Always use learning cycles for AI operations
async def correct_ai_operation():
    cycle = LearningCycle()
    result = await cycle.execute_cycle(
        cause="ai_operation_request",
        input_data={"operation": "data_processing"}
    )
    return result

# ❌ INCORRECT: Direct operation without learning cycle
def incorrect_ai_operation():
    # This bypasses LAW-001 compliance
    return process_data_directly()
```

### 2. Handle Deviations Properly

```python
async def handle_deviations_correctly():
    cycle = LearningCycle()
    result = await cycle.execute_cycle(
        cause="operation_with_deviation_handling",
        input_data={"data": "test"}
    )
    
    # Always check for deviations
    if result.get('deviation'):
        print(f"⚠️ Deviation detected: {result['deviation']}")
        
        # Log for governance review
        pattern_detector.log_deviation(result['deviation'])
        
        # Consider escalation if systematic
        if pattern_detector.is_systematic_deviation(result):
            voting_system.create_urgent_review(result)
    
    return result
```

### 3. Regular Compliance Verification

```python
# Regular compliance checks
def daily_compliance_check():
    """Run daily compliance verification"""
    
    # Check LAW-001 compliance
    cycle = LearningCycle()
    compliance = cycle.verify_compliance()
    
    # Check dependencies
    status_checker = StatusChecker()
    deps = status_checker.check_dependencies()
    
    # Check pattern health
    pattern_detector = PatternDetector()
    patterns = pattern_detector.get_pattern_health()
    
    report = {
        "law_compliance": compliance,
        "dependencies": deps,
        "pattern_health": patterns,
        "timestamp": time.time()
    }
    
    return report
```

### 4. Proper Error Handling

```python
async def robust_learning_cycle():
    """Learning cycle with proper error handling"""
    
    cycle = LearningCycle()
    
    try:
        result = await cycle.execute_cycle(
            cause="error_handling_example",
            input_data={"test": True}
        )
        
        # Validate result
        if not result.get('cycle_completed'):
            raise Exception("Learning cycle did not complete properly")
        
        return result
        
    except Exception as e:
        # Log error for governance review
        error_data = {
            "error": str(e),
            "timestamp": time.time(),
            "cycle_stage": "execution"
        }
        
        # Create error snapshot
        snapshot_manager = SnapshotManager()
        error_snapshot = snapshot_manager.create_error_snapshot(error_data)
        
        # Re-raise for handling at higher level
        raise
```

## Troubleshooting

### Common Issues

#### 1. Learning Cycle Not Starting

**Symptoms:**
- Learning cycle fails to initialize
- "Dependencies not met" error

**Solutions:**
```python
# Check dependencies
status_checker = StatusChecker()
deps = status_checker.check_dependencies()

for dep, status in deps.items():
    if not status:
        print(f"❌ Missing dependency: {dep}")
        
# Fix common dependency issues
if not deps.get('memory.snapshot_mem'):
    # Initialize memory system
    memory_loader = MemoryLoader()
    memory_loader.initialize()

if not deps.get('laws.snapshot_validation'):
    # Enable snapshot validation
    snapshot_manager = SnapshotManager()
    snapshot_manager.enable_validation()
```

#### 2. Snapshot Generation Failures

**Symptoms:**
- Snapshots not being created
- Invalid snapshot errors

**Solutions:**
```python
# Validate snapshot data before creation
def create_safe_snapshot(data):
    snapshot_manager = SnapshotManager()
    
    # Pre-validate data
    validation = snapshot_manager.validate_snapshot_data(data)
    if not validation['valid']:
        print(f"Invalid snapshot data: {validation['errors']}")
        return None
    
    # Create snapshot
    try:
        snapshot = snapshot_manager.create_snapshot(data)
        return snapshot
    except Exception as e:
        print(f"Snapshot creation failed: {e}")
        return None
```

#### 3. Pattern Detection Issues

**Symptoms:**
- False positive pattern alerts
- Missing pattern detections

**Solutions:**
```python
# Adjust pattern detection sensitivity
pattern_detector = PatternDetector()

# For false positives - increase thresholds
pattern_detector.set_thresholds({
    "deviation_threshold": 0.2,  # Increase from 0.1
    "repetition_threshold": 10   # Increase from 5
})

# For missed detections - decrease thresholds
pattern_detector.set_thresholds({
    "deviation_threshold": 0.05,  # Decrease from 0.1
    "anomaly_threshold": 1.5      # Decrease from 2.0
})
```

#### 4. Governance System Issues

**Symptoms:**
- Votes not being recorded
- Proposals stuck in pending

**Solutions:**
```python
voting_system = VotingSystem()

# Check governance system status
status = voting_system.diagnose_system()
print(f"Governance system status: {status}")

# Reset stuck proposals
stuck_proposals = voting_system.get_stuck_proposals()
for proposal_id in stuck_proposals:
    voting_system.reset_proposal(proposal_id)
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug mode for all components
cycle = LearningCycle(debug=True)
snapshot_manager = SnapshotManager(debug=True)
pattern_detector = PatternDetector(debug=True)
```

### Getting Help

If you encounter issues not covered here:

1. Check the [API Reference](API_REFERENCE.md) for detailed function documentation
2. Review the [Architecture](ARCHITECTURE.md) documentation for system understanding
3. Examine the [LAW001_COMPLIANCE_REPORT.md](../LAW001_COMPLIANCE_REPORT.md) for implementation details
4. Open an issue on [GitHub Issues](https://github.com/mupoese/AI-Interlinq/issues)

---

**law.ai System Usage Guide** • Version 1.1.0 • LAW-001 Compliant ✅