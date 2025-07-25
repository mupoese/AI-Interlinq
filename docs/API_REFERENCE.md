# API Reference

Complete API documentation for all AI-Interlinq components, including core communication modules and law.ai system components.

## Table of Contents

1. [Core Communication API](#core-communication-api)
2. [law.ai System API](#lawai-system-api)
3. [Governance API](#governance-api)
4. [Utility APIs](#utility-apis)
5. [Error Handling](#error-handling)
6. [Type Definitions](#type-definitions)

## Core Communication API

### TokenManager

Handles secure token generation, validation, and lifecycle management.

#### Class: `TokenManager(default_ttl=3600)`

**Parameters:**
- `default_ttl` (int): Default token time-to-live in seconds

```python
from ai_interlinq import TokenManager

# Initialize
token_manager = TokenManager(default_ttl=7200)
```

#### Methods

##### `generate_token(session_id, ttl=None)`

Generate a secure token for a session.

**Parameters:**
- `session_id` (str): Unique session identifier
- `ttl` (int, optional): Token time-to-live, defaults to default_ttl

**Returns:**
- `str`: Generated token

**Example:**
```python
token = token_manager.generate_token("session_001", ttl=3600)
```

##### `validate_token(token, session_id)`

Validate a token for a specific session.

**Parameters:**
- `token` (str): Token to validate
- `session_id` (str): Session identifier

**Returns:**
- `bool`: True if token is valid

##### `revoke_token(token)`

Revoke a token before expiration.

**Parameters:**
- `token` (str): Token to revoke

**Returns:**
- `bool`: True if token was successfully revoked

##### `cleanup_expired_tokens()`

Remove expired tokens from memory.

**Returns:**
- `int`: Number of tokens cleaned up

### EncryptionHandler

Provides encryption/decryption using shared keys with industry-standard security.

#### Class: `EncryptionHandler(shared_key=None)`

**Parameters:**
- `shared_key` (str, optional): Shared encryption key

```python
from ai_interlinq import EncryptionHandler

# Initialize with shared key
encryption = EncryptionHandler("your_shared_key")

# Or generate new key
encryption = EncryptionHandler()
shared_key = encryption.generate_shared_key()
```

#### Methods

##### `generate_shared_key()`

Generate a cryptographically secure shared key.

**Returns:**
- `str`: Generated shared key

##### `encrypt_message(message)`

Encrypt a message using the shared key.

**Parameters:**
- `message` (str): Message to encrypt

**Returns:**
- `tuple`: (success: bool, encrypted_data: str)

##### `decrypt_message(encrypted_data)`

Decrypt an encrypted message.

**Parameters:**
- `encrypted_data` (str): Encrypted message data

**Returns:**
- `tuple`: (success: bool, decrypted_message: str)

##### `generate_message_hash(message)`

Generate SHA-256 hash for message integrity verification.

**Parameters:**
- `message` (str): Message to hash

**Returns:**
- `str`: SHA-256 hash

### CommunicationProtocol

Defines message structure, validation rules, and communication patterns.

#### Class: `CommunicationProtocol(agent_id)`

**Parameters:**
- `agent_id` (str): Unique identifier for the agent

#### Methods

##### `create_message(recipient_id, message_type, command, data, session_id, priority=Priority.NORMAL, metadata=None)`

Create a structured message.

**Parameters:**
- `recipient_id` (str): Target agent ID
- `message_type` (MessageType): Type of message (REQUEST, RESPONSE, NOTIFICATION, ERROR)
- `command` (str): Command or action to perform
- `data` (dict): Message payload data
- `session_id` (str): Session identifier
- `priority` (Priority): Message priority level
- `metadata` (dict, optional): Additional metadata

**Returns:**
- `dict`: Structured message object

##### `validate_message(message)`

Validate message structure and required fields.

**Parameters:**
- `message` (dict): Message to validate

**Returns:**
- `tuple`: (is_valid: bool, errors: list)

##### `create_error_response(original_message, error_code, error_description)`

Create error response message.

**Parameters:**
- `original_message` (dict): Original message that caused error
- `error_code` (str): Error code
- `error_description` (str): Human-readable error description

**Returns:**
- `dict`: Error response message

## law.ai System API

### LearningCycle

Main orchestrator for LAW-001 6-step CIALORE process.

#### Class: `LearningCycle(config=None, debug=False)`

**Parameters:**
- `config` (dict, optional): Configuration dictionary
- `debug` (bool): Enable debug logging

```python
from ai_interlinq.core.learning_cycle import LearningCycle

# Initialize with default config
cycle = LearningCycle()

# Initialize with custom config
config = {
    "memory_loading_enabled": True,
    "pattern_detection_enabled": True,
    "auto_snapshot_generation": True
}
cycle = LearningCycle(config=config, debug=True)
```

#### Methods

##### `async execute_cycle(cause, input_data, config=None)`

Execute the complete 6-step LAW-001 learning cycle.

**Parameters:**
- `cause` (str): Trigger that initiated the cycle
- `input_data` (dict): Input data for processing
- `config` (dict, optional): Override configuration for this cycle

**Returns:**
- `dict`: Complete cycle result including all LAW-001 required fields

**Example:**
```python
result = await cycle.execute_cycle(
    cause="user_input_detected",
    input_data={
        "user_id": "mupoese",
        "action": "process_data",
        "timestamp": time.time()
    }
)
```

##### `verify_compliance()`

Verify LAW-001 compliance status.

**Returns:**
- `dict`: Compliance verification result

##### `get_cycle_statistics()`

Get statistics about learning cycle executions.

**Returns:**
- `dict`: Statistics including cycle count, average execution time, compliance rate

##### `configure(config)`

Update learning cycle configuration.

**Parameters:**
- `config` (dict): New configuration settings

### SnapshotManager

Handles AI execution snapshots with all required LAW-001 fields.

#### Class: `SnapshotManager(storage_path="./memory/snapshots/", debug=False)`

**Parameters:**
- `storage_path` (str): Path to store snapshots
- `debug` (bool): Enable debug logging

#### Methods

##### `create_snapshot(cycle_result)`

Create a LAW-001 compliant snapshot from cycle result.

**Parameters:**
- `cycle_result` (dict): Result from learning cycle execution

**Returns:**
- `dict`: Created snapshot with unique ID

##### `get_snapshot_by_id(snapshot_id)`

Retrieve specific snapshot by ID.

**Parameters:**
- `snapshot_id` (str): Unique snapshot identifier

**Returns:**
- `dict` or `None`: Snapshot data if found

##### `get_latest_snapshot()`

Get the most recent snapshot.

**Returns:**
- `dict` or `None`: Latest snapshot data

##### `get_snapshots_by_date_range(start_date, end_date)`

Retrieve snapshots within date range.

**Parameters:**
- `start_date` (datetime): Start of date range
- `end_date` (datetime): End of date range

**Returns:**
- `list`: List of snapshots in date range

##### `validate_snapshot(snapshot)`

Validate snapshot structure and required fields.

**Parameters:**
- `snapshot` (dict): Snapshot to validate

**Returns:**
- `dict`: Validation result with 'valid' flag and 'errors' list

##### `create_error_snapshot(error_data)`

Create snapshot for error conditions.

**Parameters:**
- `error_data` (dict): Error information

**Returns:**
- `dict`: Error snapshot

##### `get_snapshot_statistics()`

Get statistics about stored snapshots.

**Returns:**
- `dict`: Statistics including count, storage size, oldest/newest dates

### MemoryLoader

Loads snapshots at cycle start for continuity between cycles.

#### Class: `MemoryLoader(snapshot_path="./memory/snapshots/", max_memory_mb=512)`

**Parameters:**
- `snapshot_path` (str): Path to snapshot storage
- `max_memory_mb` (int): Maximum memory usage in MB

#### Methods

##### `load_snapshots(limit=None)`

Load snapshots into memory for learning cycle access.

**Parameters:**
- `limit` (int, optional): Maximum number of snapshots to load

**Returns:**
- `list`: List of loaded snapshots

##### `get_memory_stats()`

Get current memory usage statistics.

**Returns:**
- `dict`: Memory statistics including usage, snapshot count, dates

##### `configure(config)`

Configure memory loader behavior.

**Parameters:**
- `config` (dict): Configuration settings

##### `cleanup_old_snapshots(max_age_days)`

Remove snapshots older than specified age.

**Parameters:**
- `max_age_days` (int): Maximum age in days

**Returns:**
- `dict`: Cleanup result with count of removed snapshots

##### `free_memory()`

Free loaded snapshots from memory.

**Returns:**
- `bool`: True if memory was freed successfully

### PatternDetector

Detects systematic deviations and repetitive patterns in AI behavior.

#### Class: `PatternDetector(config=None, debug=False)`

**Parameters:**
- `config` (dict, optional): Pattern detection configuration
- `debug` (bool): Enable debug logging

#### Methods

##### `detect_patterns(snapshots=None)`

Analyze patterns in snapshots.

**Parameters:**
- `snapshots` (list, optional): Snapshots to analyze, defaults to recent snapshots

**Returns:**
- `dict`: Pattern analysis results

##### `analyze_snapshot_patterns(snapshot)`

Analyze patterns in a specific snapshot.

**Parameters:**
- `snapshot` (dict): Snapshot to analyze

**Returns:**
- `dict`: Pattern analysis for the snapshot

##### `is_systematic_deviation(result)`

Check if a result represents systematic deviation.

**Parameters:**
- `result` (dict): Learning cycle result

**Returns:**
- `bool`: True if systematic deviation detected

##### `set_thresholds(thresholds)`

Configure pattern detection thresholds.

**Parameters:**
- `thresholds` (dict): Threshold configuration

##### `get_pattern_health()`

Get overall pattern health assessment.

**Returns:**
- `dict`: Pattern health metrics

##### `log_deviation(deviation_data)`

Log a detected deviation for governance review.

**Parameters:**
- `deviation_data` (dict): Deviation information

### StatusChecker

Verifies dependencies and compliance status.

#### Class: `StatusChecker(debug=False)`

**Parameters:**
- `debug` (bool): Enable debug logging

#### Methods

##### `check_dependencies()`

Check all required LAW-001 dependencies.

**Returns:**
- `dict`: Dictionary of dependency names and their status

##### `verify_law_compliance(law_id="LAW-001")`

Verify compliance with specific law.

**Parameters:**
- `law_id` (str): Law identifier to verify

**Returns:**
- `dict`: Compliance verification result

##### `get_system_status()`

Get comprehensive system status.

**Returns:**
- `dict`: Complete system status including all components

##### `diagnose_issues()`

Diagnose common system issues.

**Returns:**
- `dict`: Diagnostic results with recommendations

## Governance API

### VotingSystem

Handles democratic voting for law modifications and governance decisions.

#### Class: `VotingSystem(governance_file="./governance/law_control.governance")`

**Parameters:**
- `governance_file` (str): Path to governance control file

```python
from ai_interlinq.governance.voting_system import VotingSystem

voting_system = VotingSystem()
```

#### Methods

##### `create_proposal(proposal_data, proposer)`

Create a new governance proposal.

**Parameters:**
- `proposal_data` (dict): Proposal information
- `proposer` (str): ID of the proposer

**Returns:**
- `str`: Unique proposal ID

##### `cast_vote(proposal_id, voter, vote, reason=None)`

Cast a vote on a proposal.

**Parameters:**
- `proposal_id` (str): Proposal to vote on
- `voter` (str): Voter identifier
- `vote` (str): Vote choice ("approve", "reject", "abstain")
- `reason` (str, optional): Reason for the vote

**Returns:**
- `dict`: Vote result with success status

##### `get_proposal_status(proposal_id)`

Get current status of a proposal.

**Parameters:**
- `proposal_id` (str): Proposal identifier

**Returns:**
- `dict`: Proposal status including vote counts

##### `get_governance_status()`

Get overall governance system status.

**Returns:**
- `dict`: Governance system status

##### `get_stuck_proposals()`

Get proposals that are stuck in processing.

**Returns:**
- `list`: List of stuck proposal IDs

##### `reset_proposal(proposal_id)`

Reset a stuck proposal.

**Parameters:**
- `proposal_id` (str): Proposal to reset

**Returns:**
- `bool`: True if reset successful

## Utility APIs

### Performance Monitoring

#### Class: `PerformanceMonitor()`

```python
from ai_interlinq.utils.performance import PerformanceMonitor

monitor = PerformanceMonitor()
```

##### `start_timer(operation_name)`

Start timing an operation.

**Parameters:**
- `operation_name` (str): Name of the operation

**Returns:**
- `str`: Timer ID for ending the timer

##### `end_timer(timer_id)`

End timing and record duration.

**Parameters:**
- `timer_id` (str): Timer ID from start_timer

**Returns:**
- `float`: Duration in seconds

##### `record_metric(metric_name, value)`

Record a custom metric.

**Parameters:**
- `metric_name` (str): Name of the metric
- `value` (float): Metric value

##### `increment_counter(counter_name)`

Increment a counter metric.

**Parameters:**
- `counter_name` (str): Name of the counter

##### `get_all_stats()`

Get all recorded statistics.

**Returns:**
- `dict`: All performance statistics

##### `get_latency_percentiles(operation_name)`

Get latency percentiles for an operation.

**Parameters:**
- `operation_name` (str): Operation name

**Returns:**
- `dict`: Percentile data (50th, 90th, 95th, 99th)

## Error Handling

### Exception Classes

#### `LearningCycleError`

Raised when learning cycle execution fails.

```python
from ai_interlinq.exceptions import LearningCycleError

try:
    result = await cycle.execute_cycle(cause, input_data)
except LearningCycleError as e:
    print(f"Learning cycle failed: {e}")
```

#### `SnapshotError`

Raised when snapshot operations fail.

```python
from ai_interlinq.exceptions import SnapshotError

try:
    snapshot = snapshot_manager.create_snapshot(data)
except SnapshotError as e:
    print(f"Snapshot creation failed: {e}")
```

#### `GovernanceError`

Raised when governance operations fail.

```python
from ai_interlinq.exceptions import GovernanceError

try:
    proposal_id = voting_system.create_proposal(data, proposer)
except GovernanceError as e:
    print(f"Governance operation failed: {e}")
```

#### `ComplianceError`

Raised when LAW-001 compliance is violated.

```python
from ai_interlinq.exceptions import ComplianceError

try:
    compliance = cycle.verify_compliance()
except ComplianceError as e:
    print(f"Compliance violation: {e}")
```

### Error Response Format

All API methods that can fail return structured error information:

```python
{
    "success": False,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {
            "additional": "error details"
        },
        "timestamp": 1753452276.436633
    }
}
```

## Type Definitions

### Enumerations

#### MessageType

```python
from ai_interlinq.core.communication_protocol import MessageType

MessageType.REQUEST      # Request message
MessageType.RESPONSE     # Response message  
MessageType.NOTIFICATION # Notification message
MessageType.ERROR        # Error message
```

#### Priority

```python
from ai_interlinq.core.communication_protocol import Priority

Priority.LOW      # Low priority
Priority.NORMAL   # Normal priority (default)
Priority.HIGH     # High priority
Priority.CRITICAL # Critical priority
```

### Data Structures

#### LearningCycleResult

Structure returned by `execute_cycle()`:

```python
{
    "context": str,              # Description of the cycle
    "input": dict,               # Input data with cause and parameters
    "action": str,               # Action taken
    "applied_law": str,          # Law applied (typically "LAW-001")
    "reaction": str,             # System reaction
    "output": dict,              # Results and evaluation
    "deviation": dict | None,    # Deviation information if found
    "ai_signature": str,         # Authentication signature
    "timestamp": float,          # Execution timestamp
    "snapshot_id": str,          # Unique snapshot identifier
    "cycle_step": int,           # Current step (1-6)
    "compliance_verified": bool  # Compliance verification status
}
```

#### SnapshotData

Structure for snapshot storage:

```python
{
    "snapshot_id": str,          # Unique identifier
    "context": str,              # Execution context
    "input": dict,               # Complete input data
    "action": str,               # Action performed
    "applied_law": str,          # Applied law
    "reaction": str,             # System reaction
    "output": dict,              # Execution output
    "deviation": dict | None,    # Deviation data
    "ai_signature": str,         # Signature
    "timestamp": float,          # Creation timestamp
    "cycle_step": int,           # Cycle step
    "compliance_verified": bool, # Compliance status
    "file_path": str,           # Storage file path
    "file_size": int            # File size in bytes
}
```

#### PatternAnalysis

Structure returned by pattern detection:

```python
{
    "repetitive_count": int,        # Number of repetitive patterns
    "deviation_count": int,         # Number of deviations detected
    "anomaly_count": int,          # Number of anomalies found
    "deviation_detected": bool,     # Whether systematic deviation exists
    "patterns": list,              # List of detected patterns
    "recommendations": list,       # Recommended actions
    "severity": str,               # Overall severity level
    "requires_attention": bool     # Whether human attention is needed
}
```

#### GovernanceProposal

Structure for governance proposals:

```python
{
    "proposal_id": str,            # Unique identifier
    "title": str,                  # Proposal title
    "description": str,            # Detailed description
    "law_id": str,                 # Target law ID
    "proposed_changes": dict,      # Specific changes proposed
    "justification": str,          # Reason for the change
    "proposer": str,               # Proposer identifier
    "created_timestamp": float,    # Creation time
    "status": str,                 # Current status
    "votes_for": int,              # Number of approval votes
    "votes_against": int,          # Number of rejection votes
    "votes_abstain": int,          # Number of abstain votes
    "required_votes": int,         # Votes needed for approval
    "voting_deadline": float       # Deadline for voting
}
```

### Configuration Schemas

#### LearningCycleConfig

```python
{
    "memory_loading_enabled": bool,     # Enable automatic memory loading
    "pattern_detection_enabled": bool,  # Enable pattern detection
    "governance_checks_enabled": bool,  # Enable governance validation
    "auto_snapshot_generation": bool,   # Enable automatic snapshots
    "max_execution_time": float,        # Maximum cycle execution time
    "deviation_threshold": float,       # Threshold for deviation detection
    "debug_mode": bool                  # Enable debug logging
}
```

#### MemoryConfig

```python
{
    "max_snapshots_to_load": int,       # Maximum snapshots in memory
    "memory_usage_limit_mb": int,       # Memory usage limit
    "auto_cleanup_enabled": bool,       # Enable automatic cleanup
    "cleanup_age_days": int,            # Age threshold for cleanup
    "compression_enabled": bool,        # Enable snapshot compression
    "backup_enabled": bool              # Enable automatic backups
}
```

#### PatternDetectionConfig

```python
{
    "deviation_threshold": float,       # Deviation detection threshold
    "repetition_threshold": int,        # Repetition detection threshold
    "anomaly_threshold": float,         # Anomaly detection threshold
    "performance_threshold": float,     # Performance degradation threshold
    "analysis_window_hours": int,       # Time window for analysis
    "enable_ml_detection": bool         # Enable machine learning detection
}
```

---

**API Reference** • Version 1.1.0 • LAW-001 Compliant ✅

For implementation examples, see [LAW_AI_USAGE_GUIDE.md](LAW_AI_USAGE_GUIDE.md)

For system architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)
## Version Control Automation API

### LawVersionController

The `LawVersionController` class provides automated version management:

```python
from scripts.version_control import LawVersionController

# Initialize controller
controller = LawVersionController()

# Update law.ai version
controller.update_law_version("Changes summary", "minor")

# Update package version
controller.update_package_version()

# Verify LAW-001 compliance
controller.verify_law_compliance()

# Full automation run
controller.run_full_update(
    changes_summary="Your changes",
    increment_type="minor",
    commit_message="feat: your feature"
)
```

### DocumentationUpdater

The `DocumentationUpdater` class handles automatic documentation synchronization:

```python
from scripts.doc_updater import DocumentationUpdater

# Initialize updater
updater = DocumentationUpdater()

# Update all documentation
updater.update_all_documentation()

# Update specific files
updater.update_readme()
updater.update_api_reference()
updater.update_architecture()
```

### Automation Methods

#### Version Control
- `update_law_version(changes_summary, increment_type)`: Update law.ai version
- `update_package_version()`: Synchronize package version
- `verify_law_compliance()`: Run LAW-001 compliance checks
- `commit_changes(message)`: Automated git commits

#### Documentation Management
- `update_all_documentation()`: Update all markdown files
- `update_readme()`: Update README with latest features
- `update_api_reference()`: Update API documentation
- `update_architecture()`: Update architecture docs
- `update_law_ai_usage_guide()`: Update usage examples

Last updated: 2025-07-25 16:48:35 UTC
Version: 1.2.0
