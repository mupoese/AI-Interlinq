# Getting Started with AI-Interlinq

Welcome to AI-Interlinq! This guide will help you get started with the high-performance AI communication library with integrated law.ai governance system.

## Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher
- Basic understanding of async/await programming
- Familiarity with AI agent concepts
- Understanding of the importance of governance in AI systems

## Installation

### Quick Installation

```bash
# Install AI-Interlinq
pip install ai-interlinq

# Verify installation
python -c "import ai_interlinq; print('AI-Interlinq installed successfully!')"
```

### Development Installation

For development with law.ai compliance tools:

```bash
# Install with development dependencies
pip install ai-interlinq[dev]

# Or install from source
git clone https://github.com/mupoese/AI-Interlinq.git
cd AI-Interlinq
pip install -e .[dev]
```

## LAW-001 Compliance Setup

AI-Interlinq requires LAW-001 compliance for all AI operations. Let's set this up:

### 1. Initialize law.ai System

```python
# setup_law_ai.py
import os
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.status_checker import StatusChecker

def setup_law_ai():
    """Initialize law.ai system for LAW-001 compliance"""
    
    # Create required directories
    os.makedirs("memory/snapshots", exist_ok=True)
    os.makedirs("governance", exist_ok=True)
    
    # Initialize components
    learning_cycle = LearningCycle()
    status_checker = StatusChecker()
    
    # Verify compliance
    compliance = learning_cycle.verify_compliance()
    dependencies = status_checker.check_dependencies()
    
    print("LAW-001 Setup Results:")
    print(f"  Compliance Status: {compliance.get('status', 'UNKNOWN')}")
    print(f"  All Dependencies: {'✅' if all(dependencies.values()) else '❌'}")
    
    for dep, status in dependencies.items():
        print(f"    {dep}: {'✅' if status else '❌'}")
    
    return all(dependencies.values()) and compliance.get('compliant', False)

if __name__ == "__main__":
    success = setup_law_ai()
    print(f"\nSetup {'completed successfully' if success else 'failed'}!")
```

Run the setup:

```bash
python setup_law_ai.py
```

### 2. Verify Installation

```python
# verify_setup.py
import asyncio
from ai_interlinq.core.learning_cycle import LearningCycle

async def verify_law_ai():
    """Verify LAW-001 compliance is working"""
    
    learning_cycle = LearningCycle()
    
    # Execute a test learning cycle
    result = await learning_cycle.execute_cycle(
        cause="setup_verification",
        input_data={
            "test": True,
            "setup_phase": "verification"
        }
    )
    
    # Check results
    success = (
        result.get('cycle_completed') == True and
        result.get('compliance_verified') == True and
        'snapshot_id' in result
    )
    
    print(f"LAW-001 Verification: {'✅ PASSED' if success else '❌ FAILED'}")
    if success:
        print(f"  Snapshot ID: {result['snapshot_id']}")
        print(f"  Execution Time: {result['output'].get('execution_time', 'N/A')} seconds")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(verify_law_ai())
    print(f"Verification {'passed' if success else 'failed'}!")
```

## Your First AI Communication

Let's create your first LAW-001 compliant AI communication:

### Basic Communication Example

```python
# first_communication.py
import asyncio
import time
from ai_interlinq import TokenManager, EncryptionHandler, CommunicationProtocol
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.communication_protocol import MessageType, Priority

async def first_ai_communication():
    """Your first LAW-001 compliant AI communication"""
    
    print("🚀 Starting first AI communication with LAW-001 compliance...")
    
    # Step 1: Initialize law.ai learning cycle
    learning_cycle = LearningCycle()
    print("✅ Learning cycle initialized")
    
    # Step 2: Execute learning cycle for communication setup
    setup_result = await learning_cycle.execute_cycle(
        cause="first_communication_setup",
        input_data={
            "action": "initialize_communication",
            "agent_id": "my_first_agent",
            "timestamp": time.time()
        }
    )
    
    print(f"✅ Learning cycle completed - Snapshot: {setup_result['snapshot_id']}")
    
    # Step 3: Initialize communication components
    token_manager = TokenManager(default_ttl=3600)
    encryption = EncryptionHandler()
    protocol = CommunicationProtocol("my_first_agent")
    
    # Generate shared key for encryption
    shared_key = encryption.generate_shared_key()
    encryption_with_key = EncryptionHandler(shared_key)
    
    print("✅ Communication components initialized")
    
    # Step 4: Create and process a message
    session_id = "first_session"
    token = token_manager.generate_token(session_id)
    
    # Create message
    message = protocol.create_message(
        recipient_id="target_agent",
        message_type=MessageType.REQUEST,
        command="hello_world",
        data={
            "message": "Hello from my first LAW-001 compliant AI agent!",
            "timestamp": time.time(),
            "compliance_verified": True
        },
        session_id=session_id,
        priority=Priority.HIGH
    )
    
    # Validate message
    is_valid, errors = protocol.validate_message(message)
    if not is_valid:
        print(f"❌ Message validation failed: {errors}")
        return False
    
    print("✅ Message created and validated")
    
    # Step 5: Encrypt message
    success, encrypted_message = encryption_with_key.encrypt_message(str(message))
    if not success:
        print("❌ Message encryption failed")
        return False
    
    print("✅ Message encrypted successfully")
    
    # Step 6: Execute learning cycle for message sending
    send_result = await learning_cycle.execute_cycle(
        cause="first_message_send",
        input_data={
            "action": "send_encrypted_message",
            "message_id": message['header']['message_id'],
            "recipient": message['header']['recipient_id'],
            "encrypted": True,
            "compliance_check": "passed"
        }
    )
    
    print(f"✅ Message sending cycle completed - Snapshot: {send_result['snapshot_id']}")
    
    # Step 7: Simulate receiving and decrypting
    success, decrypted_message = encryption_with_key.decrypt_message(encrypted_message)
    if success:
        print("✅ Message decrypted successfully at recipient")
        print(f"📨 Decrypted content preview: {decrypted_message[:100]}...")
    
    print("\n🎉 First AI communication completed successfully!")
    print(f"   📸 Snapshots generated: 2")
    print(f"   🏛️ LAW-001 compliance: VERIFIED")
    print(f"   🔐 Encryption: AES-256-GCM")
    print(f"   ⏱️ Total execution: Complete")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(first_ai_communication())
    if success:
        print("\n✅ Congratulations! You've successfully created your first LAW-001 compliant AI communication.")
        print("   Next steps: Explore advanced features in docs/advanced_usage.md")
    else:
        print("\n❌ Communication setup failed. Check the error messages above.")
```

Run your first communication:

```bash
python first_communication.py
```

## Understanding law.ai Integration

### The Learning Cycle

Every AI operation in AI-Interlinq follows the LAW-001 6-step learning cycle:

1. **Cause Detection**: Identify what triggered the AI operation
2. **Input Collection**: Gather and structure input data  
3. **Action Determination**: Decide what action to take
4. **Law Application**: Apply LAW-001 rules
5. **Reaction Registration**: Record the system's response
6. **Output & Effect Evaluation**: Assess results and generate snapshot

### Snapshots

Snapshots are complete records of each learning cycle execution:

```python
# View your snapshots
from ai_interlinq.core.snapshot_manager import SnapshotManager

snapshot_manager = SnapshotManager()

# Get latest snapshot
latest = snapshot_manager.get_latest_snapshot()
if latest:
    print(f"Latest snapshot: {latest['snapshot_id']}")
    print(f"Context: {latest['context']}")
    print(f"Compliance: {'✅' if latest['compliance_verified'] else '❌'}")
```

### Governance

The governance system ensures democratic control:

```python
# Check governance status
from ai_interlinq.governance.voting_system import VotingSystem

voting_system = VotingSystem()
status = voting_system.get_governance_status()

print(f"Governance active: {status['active']}")
print(f"Pending proposals: {status.get('pending_votes', 0)}")
```

## Common Patterns

### Pattern 1: Simple Message Exchange

```python
async def simple_message_exchange():
    """Simple pattern for message exchange with law.ai compliance"""
    
    learning_cycle = LearningCycle()
    
    # Always wrap AI operations in learning cycles
    result = await learning_cycle.execute_cycle(
        cause="simple_message_exchange",
        input_data={
            "operation": "send_message",
            "message": "Hello, AI world!"
        }
    )
    
    # Process the result
    if result['cycle_completed']:
        print(f"✅ Message processed - Snapshot: {result['snapshot_id']}")
    
    return result
```

### Pattern 2: Error Handling

```python
async def error_handling_pattern():
    """Pattern for proper error handling with law.ai compliance"""
    
    learning_cycle = LearningCycle()
    
    try:
        result = await learning_cycle.execute_cycle(
            cause="error_handling_demo",
            input_data={"test_error": False}
        )
        
        # Check for deviations
        if result.get('deviation'):
            print(f"⚠️ Deviation detected: {result['deviation']}")
            # Handle deviation appropriately
        
        return result
        
    except Exception as e:
        print(f"❌ Error in learning cycle: {e}")
        # Error will be logged automatically by law.ai system
        raise
```

### Pattern 3: Performance Monitoring

```python
from ai_interlinq.utils.performance import PerformanceMonitor

def performance_monitoring_pattern():
    """Pattern for monitoring performance with law.ai integration"""
    
    monitor = PerformanceMonitor()
    
    # Start timing
    timer_id = monitor.start_timer("ai_operation")
    
    # Your AI operation here
    # ... (wrapped in learning cycle)
    
    # End timing
    duration = monitor.end_timer(timer_id)
    
    print(f"⏱️ Operation completed in {duration:.4f} seconds")
    
    # Record custom metrics
    monitor.record_metric("messages_processed", 1)
```

## Next Steps

Now that you have AI-Interlinq working with law.ai compliance:

1. **Explore Advanced Features**: See [advanced_usage.md](advanced_usage.md)
2. **Read the Architecture**: Understand the system in [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Study the API**: Complete reference in [API_REFERENCE.md](API_REFERENCE.md)
4. **Join Governance**: Learn about governance in [LAW_AI_USAGE_GUIDE.md](LAW_AI_USAGE_GUIDE.md)
5. **Contribute**: Follow the guide in [../CONTRIBUTING.md](../CONTRIBUTING.md)

## Troubleshooting

### Common Issues

#### Issue: "Dependencies not met" error
**Solution:**
```bash
# Check dependencies
python -c "
from ai_interlinq.core.status_checker import StatusChecker
status_checker = StatusChecker()
deps = status_checker.check_dependencies()
for dep, status in deps.items():
    print(f'{dep}: {\"✅\" if status else \"❌\"}')
"
```

#### Issue: Learning cycle fails to start
**Solution:**
```bash
# Verify directory structure
mkdir -p memory/snapshots
mkdir -p governance

# Check permissions
ls -la memory/
ls -la governance/
```

#### Issue: Snapshots not being created
**Solution:**
```python
# Test snapshot creation
from ai_interlinq.core.snapshot_manager import SnapshotManager

snapshot_manager = SnapshotManager()
test_data = {
    "context": "test",
    "input": {"test": True},
    "action": "test",
    "applied_law": "LAW-001",
    "reaction": "test",
    "output": {"status": "test"},
    "deviation": None,
    "ai_signature": "test_signature",
    "timestamp": time.time(),
    "snapshot_id": "test_001",
    "cycle_step": 6,
    "compliance_verified": True
}

snapshot = snapshot_manager.create_snapshot(test_data)
print(f"Test snapshot created: {snapshot['snapshot_id']}")
```

## Getting Help

- **Documentation**: [docs/](.)
- **Issues**: [GitHub Issues](https://github.com/mupoese/AI-Interlinq/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mupoese/AI-Interlinq/discussions)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)

---

**Getting Started Guide** • Version 1.1.0 • LAW-001 Compliant ✅

Congratulations on taking your first steps with AI-Interlinq! The combination of high-performance communication and law.ai governance provides a solid foundation for building reliable, compliant AI systems.