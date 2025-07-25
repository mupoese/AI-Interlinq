# AI-Interlinq

A high-performance AI-to-AI communication library with shared token encryption and integrated **law.ai** governance system for fast, secure, and compliant communication between AI models and agents.

## 🎯 law.ai Integration - LAW-001 Compliance

AI-Interlinq implements the **law.ai** system with full **LAW-001** compliance, ensuring consistent, traceable, and governed AI behavior through automated learning cycles.

### What is law.ai?

law.ai is a comprehensive AI governance and learning framework that implements the **Cause-Input-Action-Law-Reaction-Output-Effect (CIALORE)** 6-step learning cycle. It ensures every AI operation is tracked, learned from, and compliant with defined governance rules.

### LAW-001 Overview
- **ID:** LAW-001
- **Title:** Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle
- **Severity:** CRITICAL
- **Enforceable:** TRUE
- **Version:** 1.1.0
- **Status:** FULLY IMPLEMENTED ✅

### Core law.ai Components
1. **🔄 Learning Cycle Engine** - 6-step CIALORE process
2. **📸 Snapshot Management** - Execution state tracking and history
3. **🔍 Pattern Detection** - Systematic deviation identification
4. **🏛️ Governance Framework** - Authorization and voting system
5. **🧠 Memory System** - Persistent state and knowledge management
6. **✅ Status Monitoring** - Dependencies and compliance verification

## 🚀 Features

### Core Communication Features
- **🔐 Shared Token Encryption**: Secure communication using shared encryption keys
- **⚡ High Performance**: Optimized for speed with minimal latency  
- **🏗️ Standardized Protocol**: Consistent message formats and communication patterns
- **🔄 Async Support**: Full asynchronous communication capabilities
- **📊 Performance Monitoring**: Built-in metrics and performance tracking
- **🛡️ Security First**: Industry-standard encryption and authentication
- **🔌 Easy Integration**: Simple API for quick AI system integration

### law.ai Governance Features
- **🎯 LAW-001 Compliance**: Automatic 6-step learning cycle enforcement
- **📸 Snapshot Generation**: Every AI operation creates traceable snapshots
- **🧠 Memory Loading**: Automatic loading of previous execution states
- **🔍 Pattern Detection**: Identifies systematic deviations and repetitive patterns
- **🏛️ Governance Controls**: Voting system for law modifications
- **📊 Compliance Monitoring**: Real-time LAW-001 compliance verification
- **🔐 Immutable Laws**: Core laws cannot be overridden without proper authorization


## 🔄 CI/CD Automation

AI-Interlinq includes comprehensive CI/CD automation with law.ai integration:

### Automated Systems
- **🤖 Auto-Commit Workflows**: Continuous integration with automatic commits
- **📊 Code Analysis**: Automated code quality and security analysis
- **🧪 Comprehensive Testing**: Full test suite execution with LAW-001 compliance
- **📈 Performance Monitoring**: Automated benchmarking and performance tracking
- **🚀 Release Automation**: Automated version management and releases
- **📝 Documentation Sync**: Automatic documentation updates with code changes

### Version Control Automation
The system includes automatic version control for law.ai updates:

```bash
# Manual version control execution
python scripts/version_control.py --changes "your changes" --increment minor

# Automatic documentation updates
python scripts/doc_updater.py

# Verify LAW-001 compliance
python scripts/version_control.py --verify-only
```

### CI/CD Workflows
- **Auto-Commit**: `.github/workflows/auto-commit.yml`
- **Code Analysis**: `.github/workflows/code-analysis.yml`
- **Comprehensive Testing**: `.github/workflows/comprehensive-testing.yml`
- **Monitoring**: `.github/workflows/monitoring.yml`
- **Benchmarking**: `.github/workflows/benchmark.yml`
- **Release**: `.github/workflows/release.yml`

All workflows maintain full LAW-001 compliance and integrate with the law.ai governance system.

## 📦 Installation

### Standard Installation

```bash
pip install ai-interlinq
```

For development with law.ai tools:
```bash
pip install ai-interlinq[dev]
```

### law.ai System Requirements

The law.ai system requires specific directory structure and dependencies:

```bash
# Install with law.ai compliance tools
pip install ai-interlinq[dev]

# Verify LAW-001 compliance after installation
python -c "from ai_interlinq.core.learning_cycle import LearningCycle; print('LAW-001 Status:', LearningCycle().verify_compliance())"
```

**System Requirements:**
- Python 3.8+
- `memory/snapshots/` directory (auto-created)
- `governance/` system (included)
- Write permissions for snapshot generation

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for complete setup instructions.

## 🎯 Quick Start

### Basic Communication with law.ai Integration

```python
import asyncio
from ai_interlinq import TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler
from ai_interlinq.core.communication_protocol import MessageType, Priority
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.snapshot_manager import SnapshotManager

async def law_ai_example():
    # Initialize law.ai learning cycle (LAW-001 compliance)
    learning_cycle = LearningCycle()
    snapshot_manager = SnapshotManager()
    
    # Setup shared encryption key
    shared_key = "your_shared_secret_key"
    
    # Initialize communication components
    token_manager = TokenManager(default_ttl=3600)
    encryption = EncryptionHandler(shared_key)
    protocol = CommunicationProtocol("agent_001")
    message_handler = MessageHandler("agent_001", token_manager, encryption)
    
    # Execute LAW-001 learning cycle for message sending
    cause = "user_request_message_send"
    input_data = {
        "recipient": "agent_002",
        "message_type": "request",
        "command": "process_data",
        "session_id": "session_001"
    }
    
    # LAW-001: 6-step learning cycle execution
    result = await learning_cycle.execute_cycle(
        cause=cause,
        input_data=input_data
    )
    
    # Create session and generate token
    session_id = input_data["session_id"]
    token = token_manager.generate_token(session_id)
    
    # Create message following CIALORE cycle
    message = protocol.create_message(
        recipient_id="agent_002",
        message_type=MessageType.REQUEST,
        command="process_data",
        data={"task": "analyze", "payload": "sample_data"},
        session_id=session_id,
        priority=Priority.HIGH
    )
    
    # Send message with automatic snapshot generation
    success = await message_handler.send_message(message)
    if success:
        print("✅ Message sent successfully with LAW-001 compliance!")
        
        # Automatic snapshot creation (LAW-001 requirement)
        snapshot = snapshot_manager.create_snapshot(result)
        print(f"📸 Snapshot generated: {snapshot['snapshot_id']}")

# Run example
asyncio.run(law_ai_example())
```

### law.ai Learning Cycle Usage

```python
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.memory_loader import MemoryLoader
from ai_interlinq.core.pattern_detector import PatternDetector

async def learning_cycle_example():
    # Initialize law.ai components
    cycle = LearningCycle()
    memory_loader = MemoryLoader()
    pattern_detector = PatternDetector()
    
    # Load previous snapshots (memory.load_snapshots=True)
    previous_snapshots = memory_loader.load_snapshots()
    print(f"Loaded {len(previous_snapshots)} previous snapshots")
    
    # Execute CIALORE learning cycle
    result = await cycle.execute_cycle(
        cause="ai_communication_initiated",
        input_data={
            "operation": "message_processing",
            "timestamp": time.time(),
            "agent_id": "ai_agent_001"
        }
    )
    
    # Check for patterns and deviations
    patterns = pattern_detector.detect_patterns(result)
    if patterns.get('deviation_detected'):
        print("⚠️ Pattern deviation detected - escalating for review")
    
    return result

# Execute with LAW-001 compliance
result = asyncio.run(learning_cycle_example())
```
```

### Message Handling

```python
async def setup_message_handler():
    # Register command handlers
    async def handle_process_data(message):
        data = message.payload.data
        print(f"Processing: {data['task']} - {data['payload']}")
        
        # Send response
        response = protocol.create_message(
            recipient_id=message.header.sender_id,
            message_type=MessageType.RESPONSE,
            command="process_complete",
            data={"result": "processed", "status": "success"},
            session_id=message.header.session_id
        )
        await message_handler.send_message(response)
    
    message_handler.register_command_handler("process_data", handle_process_data)
    
    # Process incoming messages
    processed = await message_handler.process_messages(session_id)
    print(f"Processed {processed} messages")
```

## 🏗️ Architecture

### Core Communication Components

- **TokenManager**: Handles secure token generation, validation, and lifecycle
- **EncryptionHandler**: Provides encryption/decryption using shared keys
- **CommunicationProtocol**: Defines message structure and validation rules
- **MessageHandler**: Manages message queuing, routing, and processing

### law.ai System Components

- **LearningCycle**: Main orchestrator for LAW-001 6-step CIALORE process
- **SnapshotManager**: Handles AI execution snapshots with all required LAW-001 fields
- **MemoryLoader**: Loads snapshots at cycle start (memory.load_snapshots=True)
- **PatternDetector**: Detects repetitive patterns and systematic deviations
- **StatusChecker**: Verifies dependencies and compliance status
- **Governance System**: Controls law modifications and voting procedures

### Directory Structure with law.ai

```
AI-Interlinq/
├── law.ai                          # Core law definition (LAW-001)
├── snapshot.ai                     # Current execution state
├── proposed_logic_update.ai         # Logic improvement suggestions
├── ai_interlinq/                   # Main package
│   ├── core/                       # Core communication + law.ai modules
│   │   ├── learning_cycle.py       # Main LAW-001 orchestrator
│   │   ├── snapshot_manager.py     # Snapshot handling
│   │   ├── memory_loader.py        # Memory management
│   │   ├── pattern_detector.py     # Pattern analysis
│   │   ├── status_checker.py       # Compliance verification
│   │   └── communication_protocol.py # Message protocols
│   ├── governance/                 # law.ai governance framework
│   ├── utils/                      # Utilities and helpers
│   └── transport/                  # Transport layers
├── governance/                     # Governance control files
│   ├── law_control.governance      # Law modification control
│   └── voting_system.py            # Voting and approval
├── memory/                         # law.ai memory and snapshots
│   └── snapshots/                  # Historical snapshots
└── docs/                           # Comprehensive documentation
    ├── LAW_AI_USAGE_GUIDE.md       # law.ai usage guide
    ├── API_REFERENCE.md            # Complete API documentation
    ├── INSTALLATION.md             # Setup instructions
    └── ARCHITECTURE.md             # System architecture
```

### Message Structure with law.ai Integration

#### Standard Communication Message
```python
{
    "header": {
        "message_id": "unique_id",
        "message_type": "request|response|notification|error",
        "sender_id": "agent_001", 
        "recipient_id": "agent_002",
        "timestamp": 1234567890.123,
        "priority": "low|normal|high|critical",
        "session_id": "session_001",
        "protocol_version": "1.0"
    },
    "payload": {
        "command": "process_data",
        "data": {"key": "value"},
        "metadata": {"optional": "metadata"}
    },
    "signature": "optional_signature"
}
```

#### law.ai Snapshot Structure (LAW-001 Compliant)
```python
{
    "context": "LAW-001 6-step learning cycle execution",
    "input": {
        "cause": "user_input_detected",
        "input_data": {"user": "mupoese", "action": "message_send"},
        "timestamp": 1753452276.436633,
        "agent_id": "ai_agent_001",
        "cycle_number": 1
    },
    "action": "Message processing with LAW-001 compliance",
    "applied_law": "LAW-001 - Cause-Input-Action-Law-Reaction-Output-Effect Learning Cycle",
    "reaction": "Cycle executed successfully",
    "output": {
        "cycle_completed": true,
        "execution_time": 0.00003695,
        "compliance_status": "COMPLIANT",
        "next_action": "snapshot_generation"
    },
    "deviation": null,  # or deviation details if found
    "ai_signature": "mupoese_ai_core/law_engine.kernel/memory.snapshot.validator",
    "timestamp": 1753452276.4366748,
    "snapshot_id": "cycle_1_1753452276",
    "cycle_step": 6,
    "compliance_verified": true
}
```

## 🔐 Security & Governance Features

### Traditional Security Features
#### Token-Based Authentication
- Secure token generation using cryptographically strong random values
- Configurable token expiration and automatic cleanup
- Session-based token management

#### Encryption
- Industry-standard AES encryption via Fernet
- PBKDF2 key derivation for enhanced security
- Message integrity verification with SHA-256 hashing

### law.ai Governance Security
#### LAW-001 Compliance Enforcement
- **Immutable Laws**: Core laws cannot be overridden without proper governance approval
- **Audit Trail**: Every AI operation creates traceable snapshots
- **Pattern Monitoring**: Automatic detection of systematic deviations
- **Governance Voting**: Democratic voting system for law modifications

#### Compliance Verification
- **Real-time Monitoring**: Continuous LAW-001 compliance verification
- **Dependency Checking**: Ensures all required components are active
- **Memory Integrity**: Validates snapshot consistency and authenticity
- **Signature Verification**: AI signatures for all operations

### Example: Secure law.ai Communication Setup

```python
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.snapshot_manager import SnapshotManager
from ai_interlinq import EncryptionHandler

# Initialize law.ai system with security
learning_cycle = LearningCycle()
snapshot_manager = SnapshotManager()

# Generate shared key for communication
encryption = EncryptionHandler()
shared_key = encryption.generate_shared_key()

# Setup encryption for multiple agents with law.ai compliance
agent_a_encryption = EncryptionHandler(shared_key)
agent_b_encryption = EncryptionHandler(shared_key)

# Execute secure communication with LAW-001 compliance
async def secure_law_ai_communication():
    # All communications automatically trigger learning cycle
    result = await learning_cycle.execute_cycle(
        cause="secure_communication_request",
        input_data={
            "encryption_enabled": True,
            "shared_key_length": len(shared_key),
            "governance_active": True
        }
    )
    
    # Both agents can now communicate securely with full audit trail
    success, encrypted = agent_a_encryption.encrypt_message("Hello Agent B!")
    success, decrypted = agent_b_encryption.decrypt_message(encrypted)
    
    # Automatic snapshot generation for audit trail
    snapshot = snapshot_manager.create_snapshot(result)
    print(f"🔐 Secure communication completed with snapshot: {snapshot['snapshot_id']}")

asyncio.run(secure_law_ai_communication())
```

## ⚡ Performance

AI-Interlinq is optimized for high-throughput, low-latency communication:

- **Message Creation**: 10,000+ messages/second
- **Serialization**: 8,000+ messages/second  
- **Encryption**: 5,000+ messages/second
- **End-to-End Latency**: < 10ms for standard messages

### Performance Monitoring

```python
from ai_interlinq.utils.performance import PerformanceMonitor

monitor = PerformanceMonitor()

# Time operations
timer_id = monitor.start_timer("message_processing")
# ... process message ...
duration = monitor.end_timer(timer_id)

# Record custom metrics
monitor.record_metric("queue_size", 42)
monitor.increment_counter("messages_processed")

# Get statistics
stats = monitor.get_all_stats()
latency_percentiles = monitor.get_latency_percentiles("message_processing")
```

## 📚 Documentation

### Complete Documentation
- **[LAW_AI_USAGE_GUIDE.md](docs/LAW_AI_USAGE_GUIDE.md)** - Comprehensive law.ai system usage guide
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API documentation for all components
- **[INSTALLATION.md](docs/INSTALLATION.md)** - Installation and setup instructions
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines with LAW-001 compliance requirements

### Quick Reference
- **Getting Started**: [docs/getting_started.md](docs/getting_started.md)
- **Advanced Usage**: [docs/advanced_usage.md](docs/advanced_usage.md)
- **Examples**: [docs/examples/](docs/examples/)
- **LAW-001 Compliance**: [LAW001_COMPLIANCE_REPORT.md](LAW001_COMPLIANCE_REPORT.md)

## 📚 Advanced Usage Examples

### LAW-001 Learning Cycle Integration

### Priority-Based Message Queuing with law.ai

```python
from ai_interlinq.core.learning_cycle import LearningCycle

# Initialize learning cycle for priority handling
learning_cycle = LearningCycle()

# Execute learning cycle for priority message processing
result = await learning_cycle.execute_cycle(
    cause="priority_message_queue_processing",
    input_data={
        "high_priority_count": 5,
        "normal_priority_count": 10,
        "processing_strategy": "priority_first"
    }
)

# Messages are automatically queued by priority with LAW-001 compliance
message_high = protocol.create_message(..., priority=Priority.HIGH)
message_normal = protocol.create_message(..., priority=Priority.NORMAL)

# High priority messages are processed first with full audit trail
await message_handler.process_messages(session_id)
```

### Request-Response Pattern

```python
# Send request and wait for response
request = protocol.create_message(
    recipient_id="agent_002",
    message_type=MessageType.REQUEST,
    command="get_status",
    data={},
    session_id=session_id
)

response = await message_handler.send_request_and_wait_response(
    request, timeout=30.0
)

if response:
    print(f"Status: {response.payload.data['status']}")
```

### Error Handling

```python
# Automatic error responses
try:
    # Process message
    result = process_data(message.payload.data)
except Exception as e:
    error_response = protocol.create_error_response(
        original_message=message,
        error_code="PROCESSING_ERROR", 
        error_description=str(e)
    )
    await message_handler.send_message(error_response)
```

## 🧪 Testing

### Standard Tests
Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=ai_interlinq tests/
```

### LAW-001 Compliance Testing
Run law.ai compliance verification:
```bash
python law001_verification.py
```

Run comprehensive LAW-001 functional tests:
```bash
python law001_functional_test.py
```

Verify learning cycle functionality:
```bash
python -m pytest tests/test_core/test_learning_cycle.py -v
```

### Performance Benchmarks
Performance benchmarks with law.ai overhead:
```bash
python examples/performance_benchmark.py
```

### Compliance Verification
Verify complete LAW-001 implementation:
```bash
python law001_runner.py --verify-compliance
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## 🛣️ Roadmap

### Communication Features
- [ ] WebSocket transport layer
- [ ] Redis pub/sub integration  
- [ ] Message persistence and replay
- [ ] Load balancing and failover
- [ ] Multi-language bindings

### law.ai System Enhancements
- [x] LAW-001 Implementation (COMPLETE ✅)
- [x] 6-step CIALORE Learning Cycle (COMPLETE ✅)
- [x] Snapshot Management System (COMPLETE ✅)
- [x] Pattern Detection Engine (COMPLETE ✅)
- [x] Governance Framework (COMPLETE ✅)
- [ ] Advanced Pattern Recognition with ML
- [ ] Distributed Governance Voting
- [ ] Multi-law Support (LAW-002, LAW-003, etc.)
- [ ] Visual Learning Cycle Dashboard
- [ ] Snapshot Analytics and Insights
- [ ] Cross-Agent Learning Networks

### Monitoring & Tools
- [ ] Metrics dashboard with law.ai integration
- [ ] CLI tools for law.ai monitoring
- [ ] Governance voting interface
- [ ] Compliance reporting tools

## 📞 Support

- 📧 Issues: [GitHub Issues](https://github.com/mupoese/AI-Interlinq/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/mupoese/AI-Interlinq/discussions)

---

## 📄 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

### law.ai Compliance

This software implements LAW-001 compliance as defined in [law.ai](law.ai). The law.ai system is an integral part of this software and cannot be disabled or modified without proper governance approval.

## 📞 Support

- 📧 Issues: [GitHub Issues](https://github.com/mupoese/AI-Interlinq/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/mupoese/AI-Interlinq/discussions)
- 📖 Documentation: [Complete Docs](docs/)
- 🏛️ Governance: [law_control.governance](governance/law_control.governance)

---

Built with ❤️ for the AI community • Powered by law.ai • LAW-001 Compliant ✅
