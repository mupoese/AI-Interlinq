# Installation Guide

Complete installation and setup guide for AI-Interlinq with law.ai system integration and LAW-001 compliance.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Basic Installation](#basic-installation)
3. [law.ai System Setup](#lawai-system-setup)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Setup](#advanced-setup)

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512 MB available RAM
- **Storage**: 100 MB free disk space
- **Network**: Internet connection for initial installation

### Recommended Requirements

- **Python**: 3.10 or higher
- **Operating System**: Linux (preferred for production)
- **Memory**: 2 GB available RAM
- **Storage**: 1 GB free disk space (for snapshots and logs)
- **Network**: Stable internet connection

### Python Dependencies

Core dependencies (automatically installed):
- `cryptography>=3.4.0` - Encryption and security
- `msgpack>=1.0.0` - Message serialization

Development dependencies (optional):
- `pytest>=6.0` - Testing framework
- `pytest-asyncio>=0.18.0` - Async testing support
- `black>=21.0.0` - Code formatting
- `flake8>=3.9.0` - Code linting
- `mypy>=0.910` - Type checking
- `pytest-cov>=3.0.0` - Test coverage

## Basic Installation

### Standard Installation

Install AI-Interlinq from PyPI:

```bash
# Install core package
pip install ai-interlinq

# Verify installation
python -c "import ai_interlinq; print('AI-Interlinq installed successfully')"
```

### Development Installation

For development with all tools and law.ai features:

```bash
# Install with development dependencies
pip install ai-interlinq[dev]

# Or install from source
git clone https://github.com/mupoese/AI-Interlinq.git
cd AI-Interlinq
pip install -e .[dev]
```

### Installation Verification

```bash
# Check installed version
python -c "import ai_interlinq; print(f'Version: {ai_interlinq.__version__}')"

# Test basic import
python -c "from ai_interlinq import TokenManager, EncryptionHandler; print('Core modules imported successfully')"
```

## law.ai System Setup

### Prerequisites for law.ai

The law.ai system requires specific directory structure and permissions:

```bash
# Create required directories
mkdir -p memory/snapshots
mkdir -p governance

# Set appropriate permissions (Linux/macOS)
chmod 755 memory/snapshots
chmod 755 governance

# Verify directories exist
ls -la memory/
ls -la governance/
```

### law.ai Component Installation

Install and verify law.ai components:

```python
# Create setup script: setup_law_ai.py
import os
import json
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.snapshot_manager import SnapshotManager
from ai_interlinq.core.memory_loader import MemoryLoader

def setup_law_ai():
    """Setup law.ai system components"""
    
    print("Setting up law.ai system...")
    
    # Initialize components
    cycle = LearningCycle()
    snapshot_manager = SnapshotManager()
    memory_loader = MemoryLoader()
    
    # Create initial directories
    os.makedirs("memory/snapshots", exist_ok=True)
    os.makedirs("governance", exist_ok=True)
    
    # Initialize memory system
    memory_loader.initialize()
    
    # Verify setup
    compliance = cycle.verify_compliance()
    
    if compliance.get('compliant'):
        print("✅ law.ai system setup completed successfully")
        print(f"LAW-001 Status: {compliance['status']}")
    else:
        print("❌ law.ai setup failed")
        print(f"Issues: {compliance.get('issues', [])}")
    
    return compliance

if __name__ == "__main__":
    setup_law_ai()
```

Run the setup:

```bash
python setup_law_ai.py
```

### LAW-001 Compliance Verification

Verify LAW-001 implementation:

```bash
# Run compliance verification
python -c "
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.status_checker import StatusChecker

cycle = LearningCycle()
status_checker = StatusChecker()

print('LAW-001 Compliance Check:')
compliance = cycle.verify_compliance()
print(f'  Status: {compliance.get(\"status\", \"UNKNOWN\")}')
print(f'  Compliant: {compliance.get(\"compliant\", False)}')

print('\\nDependency Check:')
deps = status_checker.check_dependencies()
for dep, status in deps.items():
    print(f'  {dep}: {\"✅\" if status else \"❌\"}')
"
```

## Configuration

### Basic Configuration

Create a configuration file `ai_interlinq_config.json`:

```json
{
    "communication": {
        "default_ttl": 3600,
        "encryption_enabled": true,
        "message_queue_size": 1000,
        "performance_monitoring": true
    },
    "law_ai": {
        "learning_cycle": {
            "memory_loading_enabled": true,
            "pattern_detection_enabled": true,
            "governance_checks_enabled": true,
            "auto_snapshot_generation": true,
            "max_execution_time": 30.0,
            "debug_mode": false
        },
        "memory": {
            "max_snapshots_to_load": 1000,
            "memory_usage_limit_mb": 512,
            "auto_cleanup_enabled": true,
            "cleanup_age_days": 30,
            "compression_enabled": true
        },
        "pattern_detection": {
            "deviation_threshold": 0.1,
            "repetition_threshold": 5,
            "anomaly_threshold": 2.0,
            "performance_threshold": 1.5,
            "analysis_window_hours": 24
        },
        "governance": {
            "voting_enabled": true,
            "required_votes": 3,
            "voting_timeout_hours": 48,
            "auto_approval_threshold": 0.8
        }
    },
    "storage": {
        "snapshot_path": "./memory/snapshots/",
        "governance_path": "./governance/",
        "log_path": "./logs/",
        "backup_enabled": true
    },
    "logging": {
        "level": "INFO",
        "file_logging": true,
        "console_logging": true,
        "max_log_size_mb": 100
    }
}
```

### Load Configuration

```python
# Load configuration in your application
import json
from ai_interlinq.core.learning_cycle import LearningCycle

# Load configuration
with open('ai_interlinq_config.json', 'r') as f:
    config = json.load(f)

# Initialize with configuration
learning_cycle = LearningCycle(config=config['law_ai']['learning_cycle'])
```

### Environment Variables

Set environment variables for sensitive configuration:

```bash
# Linux/macOS
export AI_INTERLINQ_ENCRYPTION_KEY="your_secure_encryption_key"
export AI_INTERLINQ_GOVERNANCE_ADMIN="your_admin_id"
export AI_INTERLINQ_DEBUG="false"

# Windows
set AI_INTERLINQ_ENCRYPTION_KEY=your_secure_encryption_key
set AI_INTERLINQ_GOVERNANCE_ADMIN=your_admin_id
set AI_INTERLINQ_DEBUG=false
```

Access in Python:

```python
import os
from ai_interlinq import EncryptionHandler

# Use environment variable for encryption key
encryption_key = os.getenv('AI_INTERLINQ_ENCRYPTION_KEY')
if not encryption_key:
    raise ValueError("AI_INTERLINQ_ENCRYPTION_KEY environment variable required")

encryption = EncryptionHandler(encryption_key)
```

## Verification

### Complete System Verification

Create verification script `verify_installation.py`:

```python
import asyncio
import time
import os
from ai_interlinq import TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.snapshot_manager import SnapshotManager
from ai_interlinq.core.memory_loader import MemoryLoader
from ai_interlinq.core.pattern_detector import PatternDetector
from ai_interlinq.core.status_checker import StatusChecker
from ai_interlinq.governance.voting_system import VotingSystem

async def verify_complete_installation():
    """Comprehensive installation verification"""
    
    print("🔍 AI-Interlinq Installation Verification")
    print("=" * 50)
    
    # Test 1: Core Communication Components
    print("\n1. Testing Core Communication Components...")
    try:
        token_manager = TokenManager()
        encryption = EncryptionHandler()
        protocol = CommunicationProtocol("test_agent")
        
        # Test token generation
        token = token_manager.generate_token("test_session")
        assert token, "Token generation failed"
        
        # Test encryption
        shared_key = encryption.generate_shared_key()
        encryption_with_key = EncryptionHandler(shared_key)
        success, encrypted = encryption_with_key.encrypt_message("test message")
        assert success, "Encryption failed"
        
        success, decrypted = encryption_with_key.decrypt_message(encrypted)
        assert success and decrypted == "test message", "Decryption failed"
        
        print("   ✅ Core communication components working")
    except Exception as e:
        print(f"   ❌ Core communication test failed: {e}")
        return False
    
    # Test 2: law.ai System Components
    print("\n2. Testing law.ai System Components...")
    try:
        learning_cycle = LearningCycle()
        snapshot_manager = SnapshotManager()
        memory_loader = MemoryLoader()
        pattern_detector = PatternDetector()
        status_checker = StatusChecker()
        
        # Test learning cycle
        result = await learning_cycle.execute_cycle(
            cause="installation_verification",
            input_data={"test": True, "timestamp": time.time()}
        )
        assert result.get('cycle_completed'), "Learning cycle failed"
        
        # Test snapshot creation
        snapshot = snapshot_manager.create_snapshot(result)
        assert snapshot.get('snapshot_id'), "Snapshot creation failed"
        
        # Test memory loading
        snapshots = memory_loader.load_snapshots(limit=10)
        assert isinstance(snapshots, list), "Memory loading failed"
        
        # Test pattern detection
        patterns = pattern_detector.detect_patterns()
        assert isinstance(patterns, dict), "Pattern detection failed"
        
        # Test status checking
        dependencies = status_checker.check_dependencies()
        assert isinstance(dependencies, dict), "Status checking failed"
        
        print("   ✅ law.ai system components working")
    except Exception as e:
        print(f"   ❌ law.ai system test failed: {e}")
        return False
    
    # Test 3: Governance System
    print("\n3. Testing Governance System...")
    try:
        voting_system = VotingSystem()
        
        # Test governance status
        status = voting_system.get_governance_status()
        assert isinstance(status, dict), "Governance status check failed"
        
        print("   ✅ Governance system working")
    except Exception as e:
        print(f"   ❌ Governance system test failed: {e}")
        return False
    
    # Test 4: LAW-001 Compliance
    print("\n4. Testing LAW-001 Compliance...")
    try:
        compliance = learning_cycle.verify_compliance()
        if not compliance.get('compliant'):
            print(f"   ⚠️ LAW-001 compliance issues: {compliance.get('issues', [])}")
        else:
            print("   ✅ LAW-001 fully compliant")
    except Exception as e:
        print(f"   ❌ LAW-001 compliance check failed: {e}")
        return False
    
    # Test 5: Directory Structure
    print("\n5. Verifying Directory Structure...")
    required_dirs = [
        "memory/snapshots",
        "governance"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory} exists")
        else:
            print(f"   ❌ {directory} missing")
            return False
    
    # Test 6: Performance Test
    print("\n6. Performance Test...")
    try:
        start_time = time.time()
        for i in range(10):
            result = await learning_cycle.execute_cycle(
                cause=f"performance_test_{i}",
                input_data={"iteration": i}
            )
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"   ✅ Average cycle time: {avg_time:.4f} seconds")
        
        if avg_time > 1.0:
            print("   ⚠️ Performance seems slow - check configuration")
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ AI-Interlinq installation verification completed successfully!")
    print("The system is ready for production use.")
    return True

if __name__ == "__main__":
    success = asyncio.run(verify_complete_installation())
    exit(0 if success else 1)
```

Run verification:

```bash
python verify_installation.py
```

### Quick Verification

For a quick check:

```bash
# One-line verification
python -c "
import asyncio
from ai_interlinq.core.learning_cycle import LearningCycle

async def quick_test():
    cycle = LearningCycle()
    result = await cycle.execute_cycle('test', {'quick': True})
    print(f'✅ Quick test: {\"PASSED\" if result.get(\"cycle_completed\") else \"FAILED\"}')

asyncio.run(quick_test())
"
```

## Troubleshooting

### Common Installation Issues

#### Issue 1: Python Version Compatibility

**Error:**
```
ERROR: ai-interlinq requires Python '>=3.8' but the running Python is 3.7.x
```

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.8+ using pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.10.0
pyenv global 3.10.0

# Or use system package manager
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.10 python3.10-pip

# macOS with Homebrew:
brew install python@3.10
```

#### Issue 2: Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'memory/snapshots'
```

**Solution:**
```bash
# Fix directory permissions
chmod 755 memory/snapshots
chmod 755 governance

# Or create with proper permissions
mkdir -p memory/snapshots governance
chown -R $USER:$USER memory governance
```

#### Issue 3: Cryptography Installation Fails

**Error:**
```
Failed building wheel for cryptography
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# CentOS/RHEL
sudo yum install gcc openssl-devel libffi-devel python3-devel

# macOS
xcode-select --install
brew install openssl libffi

# Reinstall cryptography
pip install --upgrade pip
pip install cryptography
```

#### Issue 4: Import Errors

**Error:**
```
ImportError: No module named 'ai_interlinq'
```

**Solution:**
```bash
# Verify installation
pip list | grep ai-interlinq

# Reinstall if missing
pip uninstall ai-interlinq
pip install ai-interlinq

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue 5: law.ai Dependencies Not Met

**Error:**
```
LAW-001 compliance check failed: dependencies not met
```

**Solution:**
```python
# Run dependency diagnostic
from ai_interlinq.core.status_checker import StatusChecker

status_checker = StatusChecker()
issues = status_checker.diagnose_issues()

print("Diagnostic Results:")
for issue, recommendation in issues.items():
    print(f"Issue: {issue}")
    print(f"Recommendation: {recommendation}")
    print()
```

### Performance Issues

#### Slow Learning Cycles

```python
# Enable debug mode to identify bottlenecks
from ai_interlinq.core.learning_cycle import LearningCycle

cycle = LearningCycle(debug=True)

# Check configuration
config = {
    "memory_loading_enabled": True,  # Try setting to False temporarily
    "pattern_detection_enabled": False,  # Disable for faster execution
    "max_execution_time": 10.0  # Reduce timeout
}

cycle.configure(config)
```

#### Memory Usage Issues

```python
# Configure memory limits
from ai_interlinq.core.memory_loader import MemoryLoader

memory_loader = MemoryLoader()
memory_config = {
    "max_snapshots_to_load": 100,  # Reduce from default 1000
    "memory_usage_limit_mb": 256,  # Reduce from default 512
    "auto_cleanup_enabled": True
}

memory_loader.configure(memory_config)

# Manual cleanup
cleanup_result = memory_loader.cleanup_old_snapshots(max_age_days=7)
print(f"Cleaned up {cleanup_result['cleaned_count']} snapshots")
```

### Log Analysis

Enable detailed logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_interlinq_debug.log'),
        logging.StreamHandler()
    ]
)

# Set component-specific log levels
logging.getLogger('ai_interlinq.core.learning_cycle').setLevel(logging.DEBUG)
logging.getLogger('ai_interlinq.core.snapshot_manager').setLevel(logging.DEBUG)
```

## Advanced Setup

### Production Deployment

#### Docker Setup

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create required directories
RUN mkdir -p memory/snapshots governance logs

# Install AI-Interlinq
RUN pip install -e .

# Verify installation
RUN python -c "from ai_interlinq.core.learning_cycle import LearningCycle; print('Installation verified')"

# Expose port (if using web interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from ai_interlinq.core.status_checker import StatusChecker; StatusChecker().check_dependencies()"

# Run application
CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t ai-interlinq .
docker run -d --name ai-interlinq-app -p 8000:8000 ai-interlinq
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ai-interlinq:
    build: .
    container_name: ai-interlinq-app
    ports:
      - "8000:8000"
    volumes:
      - ./memory:/app/memory
      - ./governance:/app/governance
      - ./logs:/app/logs
    environment:
      - AI_INTERLINQ_DEBUG=false
      - AI_INTERLINQ_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "from ai_interlinq.core.status_checker import StatusChecker; StatusChecker().check_dependencies()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:alpine
    container_name: ai-interlinq-redis
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  ai_interlinq_data:
```

### Distributed Setup

For distributed law.ai deployments:

```python
# distributed_config.py
DISTRIBUTED_CONFIG = {
    "nodes": [
        {"id": "node_1", "host": "192.168.1.10", "port": 8001},
        {"id": "node_2", "host": "192.168.1.11", "port": 8001},
        {"id": "node_3", "host": "192.168.1.12", "port": 8001}
    ],
    "consensus": {
        "algorithm": "raft",
        "required_votes": 2,
        "election_timeout": 5000
    },
    "replication": {
        "snapshot_replication": True,
        "sync_interval": 60,
        "backup_nodes": 2
    }
}
```

### Security Hardening

#### Encryption Key Management

```python
# Use secure key management
import os
from cryptography.fernet import Fernet

# Generate and store secure key
def generate_secure_key():
    key = Fernet.generate_key()
    
    # Store securely (example with file - use proper key management in production)
    with open('/etc/ai-interlinq/encryption.key', 'wb') as f:
        f.write(key)
    
    # Set strict permissions
    os.chmod('/etc/ai-interlinq/encryption.key', 0o600)
    
    return key

# Load key securely
def load_secure_key():
    key_path = os.getenv('AI_INTERLINQ_KEY_PATH', '/etc/ai-interlinq/encryption.key')
    
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Encryption key not found at {key_path}")
    
    with open(key_path, 'rb') as f:
        return f.read()
```

#### Network Security

```python
# Configure secure communication
SECURITY_CONFIG = {
    "tls": {
        "enabled": True,
        "cert_file": "/etc/ai-interlinq/cert.pem",
        "key_file": "/etc/ai-interlinq/key.pem",
        "ca_file": "/etc/ai-interlinq/ca.pem"
    },
    "authentication": {
        "enabled": True,
        "method": "certificate",
        "token_expiry": 3600
    },
    "firewall": {
        "allowed_ips": ["192.168.1.0/24"],
        "allowed_ports": [8001, 8002]
    }
}
```

---

**Installation Guide** • Version 1.1.0 • LAW-001 Compliant ✅

For usage instructions, see [LAW_AI_USAGE_GUIDE.md](LAW_AI_USAGE_GUIDE.md)

For API details, see [API_REFERENCE.md](API_REFERENCE.md)
## Automation System Setup

### Version Control Automation

After basic installation, set up the automation system:

```bash
# Ensure scripts are executable
chmod +x scripts/version_control.py
chmod +x scripts/doc_updater.py

# Test automation system
python scripts/version_control.py --verify-only

# Run initial documentation sync
python scripts/doc_updater.py
```

### CI/CD Integration

For full CI/CD automation:

1. **Git Hooks Setup**:
```bash
# Copy pre-commit hook
cp .github/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

2. **GitHub Actions Configuration**:
- Ensure `mupoese_key` secret is configured in repository settings
- Verify all workflow files in `.github/workflows/` are present
- Test workflows with initial commit

3. **Automation Verification**:
```bash
# Test full automation cycle
python scripts/version_control.py --changes "Test automation setup"

# Verify LAW-001 compliance
python law001_verification.py

# Run functional tests
python law001_functional_test.py
```

### Environment Variables

For automation to work properly, set these environment variables:

```bash
export GITHUB_TOKEN="your_github_token"  # For GitHub integration
export LAW_COMPLIANCE="LAW-001"          # Compliance framework
export AUTO_VERSION="true"               # Enable version automation
```

### Troubleshooting Automation

Common issues and solutions:

1. **Version Control Issues**:
```bash
# Reset version control state
git checkout law.ai
python scripts/version_control.py --changes "Reset automation"
```

2. **Documentation Sync Problems**:
```bash
# Force documentation update
python scripts/doc_updater.py
git add . && git commit -m "docs: sync documentation"
```

3. **LAW-001 Compliance Failures**:
```bash
# Check compliance status
python law001_verification.py

# Fix common compliance issues
mkdir -p memory/snapshots
python -c "from ai_interlinq.core.learning_cycle import LearningCycle; LearningCycle().verify_compliance()"
```

Installation guide version: 1.2.0
Last updated: 2025-07-25 16:48:35 UTC
