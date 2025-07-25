#!/usr/bin/env python3
"""
Automatic Documentation Updater
- Synchronizes all *.md files after code changes
- Updates version references
- Maintains documentation consistency

This script ensures all documentation stays synchronized with code changes
and version updates, maintaining consistency across the entire project.
"""

import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class DocumentationUpdater:
    """
    Handles automatic updates to all markdown documentation files.
    
    This class provides:
    - Version reference synchronization
    - Timestamp updates
    - Feature documentation updates
    - Architecture documentation maintenance
    - API reference updates
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the documentation updater."""
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.current_version = self._get_current_version()
        self.timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Define documentation files to update
        self.md_files = [
            "README.md",
            "CHANGELOG.md", 
            "docs/API_REFERENCE.md",
            "docs/ARCHITECTURE.md",
            "docs/LAW_AI_USAGE_GUIDE.md",
            "docs/INSTALLATION.md",
            "CONTRIBUTING.md"
        ]
        
        # Version patterns to update
        self.version_patterns = [
            (r'Version:\s*\d+\.\d+\.\d+', f'Version: {self.current_version}'),
            (r'v\d+\.\d+\.\d+', f'v{self.current_version}'),
            (r'ai-interlinq==\d+\.\d+\.\d+', f'ai-interlinq=={self.current_version}'),
        ]
    
    def _get_current_version(self) -> str:
        """Get current version from law.ai file."""
        try:
            law_file = self.repo_root / "law.ai"
            with open(law_file, 'r') as f:
                content = f.read()
                version_match = re.search(r'Version:\s*(\d+\.\d+\.\d+)', content)
                if version_match:
                    return version_match.group(1)
                return "1.2.0"
        except FileNotFoundError:
            return "1.2.0"
    
    def update_readme(self) -> bool:
        """Update README.md with CI/CD automation documentation."""
        try:
            readme_path = self.repo_root / "README.md"
            if not readme_path.exists():
                print(f"⚠️ README.md not found: {readme_path}")
                return False
            
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Update version references
            for pattern, replacement in self.version_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Add/update CI/CD automation section if needed
            cicd_section = """
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
"""
            
            # Insert CI/CD section after features if not present
            if "CI/CD Automation" not in content:
                # Find a good insertion point after the features section
                features_end = content.find("## 📦 Installation")
                if features_end > 0:
                    content = content[:features_end] + cicd_section + "\n" + content[features_end:]
                else:
                    # Append at the end if we can't find a good spot
                    content += cicd_section
            
            with open(readme_path, 'w') as f:
                f.write(content)
            
            print("✅ README.md updated with CI/CD automation documentation")
            return True
            
        except Exception as e:
            print(f"❌ Error updating README.md: {e}")
            return False
    
    def update_api_reference(self) -> bool:
        """Update API_REFERENCE.md with automation APIs."""
        try:
            api_ref_path = self.repo_root / "docs" / "API_REFERENCE.md"
            if not api_ref_path.exists():
                print(f"⚠️ API_REFERENCE.md not found: {api_ref_path}")
                return True  # Not critical
            
            with open(api_ref_path, 'r') as f:
                content = f.read()
            
            # Update version references
            for pattern, replacement in self.version_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Add automation API section if not present
            automation_api_section = f"""
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

Last updated: {self.timestamp}
Version: {self.current_version}
"""
            
            # Add automation API section if not present
            if "Version Control Automation API" not in content:
                content += automation_api_section
            
            with open(api_ref_path, 'w') as f:
                f.write(content)
            
            print("✅ API_REFERENCE.md updated with automation APIs")
            return True
            
        except Exception as e:
            print(f"❌ Error updating API_REFERENCE.md: {e}")
            return False
    
    def update_architecture(self) -> bool:
        """Update ARCHITECTURE.md with CI/CD pipeline architecture."""
        try:
            arch_path = self.repo_root / "docs" / "ARCHITECTURE.md"
            if not arch_path.exists():
                print(f"⚠️ ARCHITECTURE.md not found: {arch_path}")
                return True  # Not critical
            
            with open(arch_path, 'r') as f:
                content = f.read()
            
            # Update version references
            for pattern, replacement in self.version_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Add CI/CD architecture section
            cicd_architecture = f"""
## CI/CD Pipeline Architecture

### Automation System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Code Changes  │───▶│  Version Control │───▶│  Documentation  │
│                 │    │   Automation     │    │  Synchronization│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  LAW-001        │◀───│   CI/CD Pipeline │───▶│   Deployment    │
│  Compliance     │    │   Execution      │    │   Automation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

#### 1. Version Control Automation
- **LawVersionController**: Manages law.ai version updates
- **Git Integration**: Automated commit and push operations
- **Semantic Versioning**: Automatic version increments
- **Change Tracking**: Comprehensive change documentation

#### 2. Documentation Pipeline
- **DocumentationUpdater**: Synchronizes all *.md files
- **Version References**: Updates version numbers across docs
- **API Documentation**: Auto-generates API references
- **Architecture Updates**: Maintains system documentation

#### 3. CI/CD Workflows
- **Auto-Commit**: `.github/workflows/auto-commit.yml`
- **Testing Pipeline**: Comprehensive test execution
- **Code Analysis**: Quality and security checks
- **Performance Monitoring**: Automated benchmarking
- **Release Management**: Version-based releases

#### 4. LAW-001 Integration
- **Compliance Verification**: Automatic LAW-001 checks
- **Governance Workflow**: Integration with law.ai governance
- **Snapshot Management**: Execution state tracking
- **Pattern Detection**: Systematic deviation monitoring

### Workflow Execution

#### Standard Development Cycle
1. **Code Change Detection**: Git hooks trigger automation
2. **Version Analysis**: Determine version increment type
3. **Law.ai Update**: Update version and timestamp
4. **Documentation Sync**: Update all markdown files
5. **Compliance Check**: Verify LAW-001 requirements
6. **Automated Commit**: Commit with proper versioning
7. **CI/CD Pipeline**: Execute comprehensive testing
8. **Deployment**: Automated release if tests pass

#### Emergency Updates
1. **Manual Trigger**: `python scripts/version_control.py`
2. **Immediate Compliance**: Skip some checks for urgent fixes
3. **Post-Update Verification**: Complete compliance check
4. **Documentation Catch-up**: Sync documentation after emergency

### Integration Points

#### GitHub Actions
- Secure authentication with mupoese_key
- Automated workflow triggers
- Status reporting and notifications
- Failure handling and rollback

#### Law.ai Governance
- Automatic governance compliance
- Vote tracking for major changes
- Audit trail maintenance
- Pattern detection integration

#### Monitoring Systems
- Performance metrics collection
- Error tracking and alerting
- Usage analytics
- Compliance reporting

Last updated: {self.timestamp}
Architecture version: {self.current_version}
"""
            
            # Add CI/CD architecture if not present
            if "CI/CD Pipeline Architecture" not in content:
                content += cicd_architecture
            
            with open(arch_path, 'w') as f:
                f.write(content)
            
            print("✅ ARCHITECTURE.md updated with CI/CD pipeline documentation")
            return True
            
        except Exception as e:
            print(f"❌ Error updating ARCHITECTURE.md: {e}")
            return False
    
    def update_law_ai_usage_guide(self) -> bool:
        """Update LAW_AI_USAGE_GUIDE.md with automation features."""
        try:
            usage_path = self.repo_root / "docs" / "LAW_AI_USAGE_GUIDE.md"
            if not usage_path.exists():
                print(f"⚠️ LAW_AI_USAGE_GUIDE.md not found: {usage_path}")
                return True  # Not critical
            
            with open(usage_path, 'r') as f:
                content = f.read()
            
            # Update version references
            for pattern, replacement in self.version_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Add automation usage section
            automation_usage = f"""
## Automation and Version Control Usage

### Automatic Version Control

The law.ai system includes comprehensive automation for version management:

#### Basic Usage
```bash
# Run full automation update
python scripts/version_control.py

# Custom changes summary
python scripts/version_control.py --changes "Add new feature X"

# Specify version increment type
python scripts/version_control.py --increment major --changes "Breaking changes"

# Custom commit message
python scripts/version_control.py --message "feat: add amazing feature"

# Verify compliance only
python scripts/version_control.py --verify-only
```

#### Documentation Synchronization
```bash
# Update all documentation
python scripts/doc_updater.py

# The system automatically:
# - Updates version references in all *.md files
# - Synchronizes API documentation
# - Updates architecture diagrams
# - Maintains usage examples
```

### CI/CD Integration with LAW-001

#### Automated Workflows
The system provides several automated workflows:

```yaml
# .github/workflows/auto-version-commit.yml
# Triggers on code changes and automatically:
# 1. Updates law.ai version
# 2. Synchronizes documentation
# 3. Commits changes with proper versioning
# 4. Maintains LAW-001 compliance
```

#### Example Integration
```python
from ai_interlinq.core.learning_cycle import LearningCycle
from scripts.version_control import LawVersionController

async def automated_development_cycle():
    # Initialize systems
    learning_cycle = LearningCycle()
    version_controller = LawVersionController()
    
    # Execute LAW-001 compliant development cycle
    result = await learning_cycle.execute_cycle(
        cause="code_change_detected",
        input_data={{
            "changes": "New feature implementation",
            "automation_enabled": True,
            "version_control": True
        }}
    )
    
    # Automatic version management
    version_controller.run_full_update(
        changes_summary="Implement new feature with LAW-001 compliance",
        increment_type="minor"
    )
    
    return result
```

### Best Practices for Automation

#### Version Control
1. **Semantic Versioning**:
   - `major`: Breaking changes requiring governance approval
   - `minor`: New features maintaining backward compatibility
   - `patch`: Bug fixes and minor improvements

2. **Change Documentation**:
   - Always provide meaningful change summaries
   - Document impact on LAW-001 compliance
   - Include governance considerations

3. **Compliance Verification**:
   - Run verification before major changes
   - Address compliance issues immediately
   - Maintain audit trail integrity

#### Governance Integration
```python
# Example: Major change requiring governance approval
from governance.voting_system import VotingSystem

async def major_change_with_governance():
    voting_system = VotingSystem()
    
    # Propose major change
    proposal = await voting_system.create_proposal(
        title="Major Architecture Change",
        description="Implement new automation system",
        change_type="major",
        requires_approval=True
    )
    
    # Wait for approval before proceeding
    if await voting_system.wait_for_approval(proposal.id):
        # Proceed with automated version control
        controller = LawVersionController()
        success = controller.run_full_update(
            changes_summary="Major architecture update with governance approval",
            increment_type="major"
        )
        
        if success:
            await voting_system.mark_proposal_implemented(proposal.id)
```

### Monitoring and Maintenance

#### Automated Monitoring
The system continuously monitors:
- LAW-001 compliance status
- Version synchronization across components
- Documentation consistency
- Automation system health

#### Maintenance Commands
```bash
# Check system status
python scripts/version_control.py --verify-only

# Full system health check
python law001_verification.py

# Run functional tests
python law001_functional_test.py

# Performance monitoring
python -m ai_interlinq.cli.monitor --automation-status
```

Last updated: {self.timestamp}
Usage guide version: {self.current_version}
LAW-001 Status: COMPLIANT ✅
"""
            
            # Add automation usage if not present
            if "Automation and Version Control Usage" not in content:
                content += automation_usage
            
            with open(usage_path, 'w') as f:
                f.write(content)
            
            print("✅ LAW_AI_USAGE_GUIDE.md updated with automation usage instructions")
            return True
            
        except Exception as e:
            print(f"❌ Error updating LAW_AI_USAGE_GUIDE.md: {e}")
            return False
    
    def update_installation_guide(self) -> bool:
        """Update INSTALLATION.md with automation setup instructions."""
        try:
            install_path = self.repo_root / "docs" / "INSTALLATION.md"
            if not install_path.exists():
                print(f"⚠️ INSTALLATION.md not found: {install_path}")
                return True  # Not critical
            
            with open(install_path, 'r') as f:
                content = f.read()
            
            # Update version references
            for pattern, replacement in self.version_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Add automation setup section
            automation_setup = f"""
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

Installation guide version: {self.current_version}
Last updated: {self.timestamp}
"""
            
            # Add automation setup if not present
            if "Automation System Setup" not in content:
                content += automation_setup
            
            with open(install_path, 'w') as f:
                f.write(content)
            
            print("✅ INSTALLATION.md updated with automation setup instructions")
            return True
            
        except Exception as e:
            print(f"❌ Error updating INSTALLATION.md: {e}")
            return False
    
    def update_file_versions(self, file_path: Path) -> int:
        """Update version references in a specific file."""
        try:
            if not file_path.exists():
                return 0
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Apply version updates
            for pattern, replacement in self.version_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                return 1
            
            return 0
            
        except Exception as e:
            print(f"⚠️ Error updating {file_path}: {e}")
            return 0
    
    def update_all_documentation(self) -> bool:
        """Update all markdown files with latest information."""
        print("📚 Starting Documentation Synchronization")
        print("=" * 50)
        
        total_updated = 0
        success_count = 0
        
        # Update specific files with custom logic
        updates = [
            ("README.md", self.update_readme),
            ("API_REFERENCE.md", self.update_api_reference),
            ("ARCHITECTURE.md", self.update_architecture),
            ("LAW_AI_USAGE_GUIDE.md", self.update_law_ai_usage_guide),
            ("INSTALLATION.md", self.update_installation_guide),
        ]
        
        for file_name, update_func in updates:
            print(f"📝 Updating {file_name}...")
            if update_func():
                success_count += 1
                total_updated += 1
        
        # Update version references in remaining files
        for md_file in self.md_files:
            file_path = self.repo_root / md_file
            if file_path.exists() and md_file not in [u[0] for u in updates]:
                print(f"🔄 Updating version references in {md_file}...")
                if self.update_file_versions(file_path):
                    total_updated += 1
        
        print("=" * 50)
        print(f"✅ Documentation synchronization completed!")
        print(f"📊 Files updated: {total_updated}")
        print(f"🎯 Custom updates successful: {success_count}/{len(updates)}")
        print(f"📅 Timestamp: {self.timestamp}")
        print(f"🔖 Version: {self.current_version}")
        
        return success_count == len(updates)

def main():
    """Main entry point for documentation updates."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatic Documentation Updater')
    parser.add_argument('--file', '-f', 
                       help='Update specific file only')
    parser.add_argument('--version-only', action='store_true',
                       help='Only update version references')
    
    args = parser.parse_args()
    
    updater = DocumentationUpdater()
    
    if args.file:
        # Update specific file
        file_path = Path(args.file)
        success = updater.update_file_versions(file_path)
        print(f"✅ Updated {success} version references in {args.file}")
    else:
        # Update all documentation
        success = updater.update_all_documentation()
        exit(0 if success else 1)

if __name__ == "__main__":
    main()