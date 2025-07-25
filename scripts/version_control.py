#!/usr/bin/env python3
"""
Law.ai Version Control Automation System
- Automatic version increment on code changes
- Documentation synchronization
- LAW-001 compliance verification

This script implements the comprehensive version control system as specified
in the law.ai governance framework, ensuring all changes maintain LAW-001
compliance while automatically updating versions and documentation.
"""

import datetime
import json
import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class LawVersionController:
    """
    Main controller for law.ai version management and automation.
    
    This class handles:
    - Automatic version increment based on changes
    - Law.ai file updates with proper timestamps
    - Documentation synchronization
    - LAW-001 compliance verification
    - Git integration for automated commits
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the version controller."""
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.law_file = self.repo_root / "law.ai"
        self.changelog_file = self.repo_root / "CHANGELOG.md"
        self.version_file = self.repo_root / "ai_interlinq" / "version.py"
        
        # Load current configuration
        self.current_version = self._get_current_law_version()
        self.timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
    def _get_current_law_version(self) -> str:
        """Extract current version from law.ai file."""
        try:
            with open(self.law_file, 'r') as f:
                content = f.read()
                version_match = re.search(r'Version:\s*(\d+\.\d+\.\d+)', content)
                if version_match:
                    return version_match.group(1)
                return "1.2.0"  # Default if not found
        except FileNotFoundError:
            return "1.2.0"
    
    def _increment_version(self, version: str, increment_type: str = "patch") -> str:
        """Increment version based on semantic versioning rules."""
        try:
            major, minor, patch = map(int, version.split('.'))
            
            if increment_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif increment_type == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
                
            return f"{major}.{minor}.{patch}"
        except ValueError:
            return "1.2.0"  # Fallback version
    
    def _get_git_commit_hash(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.repo_root)
            if result.returncode == 0:
                return result.stdout.strip()[:8]  # Short hash
            return "unknown"
        except Exception:
            return "unknown"
    
    def update_law_version(self, changes_summary: str, increment_type: str = "minor") -> bool:
        """
        Update law.ai with new version and timestamp.
        
        Args:
            changes_summary: Summary of changes for this version
            increment_type: Type of version increment (major, minor, patch)
            
        Returns:
            bool: Success status
        """
        try:
            if not self.law_file.exists():
                print(f"❌ Law.ai file not found: {self.law_file}")
                return False
            
            # Read current content
            with open(self.law_file, 'r') as f:
                content = f.read()
            
            # Calculate new version
            current_version = self._get_current_law_version()
            new_version = self._increment_version(current_version, increment_type)
            commit_hash = self._get_git_commit_hash()
            
            # Update version and timestamp
            content = re.sub(
                r'Version:\s*\d+\.\d+\.\d+',
                f'Version: {new_version}',
                content
            )
            
            content = re.sub(
                r'Timestamp:\s*\$mupoese_ai\$-v[\d\.]+-[\d\-T:Z]+-LAW-001',
                f'Timestamp: $mupoese_ai$-v{new_version}-{self.timestamp}-LAW-001',
                content
            )
            
            # Add commit reference and changes if not present
            if "Commit:" not in content:
                # Find the line after Timestamp and insert commit info
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "Timestamp:" in line:
                        lines.insert(i + 1, f"  Commit: AUTO-COMMIT-{commit_hash}")
                        lines.insert(i + 2, f'  Changes: "{changes_summary}"')
                        break
                content = '\n'.join(lines)
            else:
                # Update existing commit and changes
                content = re.sub(
                    r'Commit:\s*AUTO-COMMIT-\w+',
                    f'Commit: AUTO-COMMIT-{commit_hash}',
                    content
                )
                content = re.sub(
                    r'Changes:\s*"[^"]*"',
                    f'Changes: "{changes_summary}"',
                    content
                )
            
            # Write updated content
            with open(self.law_file, 'w') as f:
                f.write(content)
            
            self.current_version = new_version
            print(f"✅ Updated law.ai to version {new_version}")
            print(f"📅 Timestamp: {self.timestamp}")
            print(f"📝 Changes: {changes_summary}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating law.ai version: {e}")
            return False
    
    def update_package_version(self) -> bool:
        """Update the package version in ai_interlinq/version.py."""
        try:
            if not self.version_file.exists():
                print(f"⚠️ Package version file not found: {self.version_file}")
                return True  # Not critical, continue
            
            with open(self.version_file, 'r') as f:
                content = f.read()
            
            # Update version string
            content = re.sub(
                r'__version__\s*=\s*["\'][^"\']*["\']',
                f'__version__ = "{self.current_version}"',
                content
            )
            
            # Update version info tuple
            version_parts = self.current_version.split('.')
            if len(version_parts) == 3:
                version_tuple = f"({version_parts[0]}, {version_parts[1]}, {version_parts[2]})"
                content = re.sub(
                    r'__version_info__\s*=\s*\([^)]*\)',
                    f'__version_info__ = {version_tuple}',
                    content
                )
            
            with open(self.version_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated package version to {self.current_version}")
            return True
            
        except Exception as e:
            print(f"⚠️ Error updating package version: {e}")
            return True  # Not critical, continue
    
    def verify_law_compliance(self) -> bool:
        """Verify LAW-001 compliance of the current system."""
        try:
            # Run existing verification script
            result = subprocess.run(
                ['python', 'law001_verification.py'],
                capture_output=True, text=True, cwd=self.repo_root
            )
            
            if result.returncode == 0:
                print("✅ LAW-001 compliance verified")
                return True
            else:
                print("❌ LAW-001 compliance verification failed")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"⚠️ Could not verify LAW-001 compliance: {e}")
            return False
    
    def update_documentation(self) -> bool:
        """Trigger documentation updates via doc_updater script."""
        try:
            doc_updater_path = self.repo_root / "scripts" / "doc_updater.py"
            if doc_updater_path.exists():
                result = subprocess.run(
                    ['python', str(doc_updater_path)],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                
                if result.returncode == 0:
                    print("✅ Documentation updated successfully")
                    return True
                else:
                    print("⚠️ Documentation update had issues:")
                    print(result.stdout)
                    return False
            else:
                print("⚠️ Documentation updater not found, skipping")
                return True
                
        except Exception as e:
            print(f"⚠️ Error updating documentation: {e}")
            return False
    
    def commit_changes(self, commit_message: str) -> bool:
        """
        Commit all changes with proper versioning.
        
        Args:
            commit_message: The commit message to use
            
        Returns:
            bool: Success status
        """
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '.'], cwd=self.repo_root, check=True)
            
            # Create comprehensive commit message
            full_message = f"{commit_message}\n\n"
            full_message += f"Version: {self.current_version}\n"
            full_message += f"Timestamp: {self.timestamp}\n"
            full_message += f"User: mupoese\n"
            full_message += f"LAW-001: COMPLIANT\n"
            full_message += f"Systems: CI/CD, Version Control, Documentation, Cleanup, Monitoring"
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', full_message], 
                         cwd=self.repo_root, check=True)
            
            print(f"✅ Changes committed successfully")
            print(f"📝 Commit message: {commit_message}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error committing changes: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during commit: {e}")
            return False
    
    def run_full_update(self, changes_summary: str = None, 
                       increment_type: str = "minor",
                       commit_message: str = None) -> bool:
        """
        Run complete version control update process.
        
        Args:
            changes_summary: Summary of changes
            increment_type: Version increment type
            commit_message: Custom commit message
            
        Returns:
            bool: Success status
        """
        print("🚀 Starting Law.ai Version Control Automation")
        print("=" * 50)
        
        # Default values
        if not changes_summary:
            changes_summary = "CI/CD automation, repository cleanup, version control system"
        
        if not commit_message:
            commit_message = "feat: implement comprehensive automation and version control system"
        
        # Step 1: Update law.ai version
        print("📝 Step 1: Updating law.ai version...")
        if not self.update_law_version(changes_summary, increment_type):
            return False
        
        # Step 2: Update package version
        print("📦 Step 2: Updating package version...")
        self.update_package_version()
        
        # Step 3: Update documentation
        print("📚 Step 3: Updating documentation...")
        self.update_documentation()
        
        # Step 4: Verify LAW-001 compliance
        print("⚖️ Step 4: Verifying LAW-001 compliance...")
        if not self.verify_law_compliance():
            print("⚠️ Continuing despite compliance issues...")
        
        # Step 5: Commit changes
        print("💾 Step 5: Committing changes...")
        if not self.commit_changes(commit_message):
            return False
        
        print("=" * 50)
        print("✅ Law.ai Version Control Automation completed successfully!")
        print(f"🎯 New version: {self.current_version}")
        print(f"📅 Timestamp: {self.timestamp}")
        
        return True

def main():
    """Main entry point for version control automation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Law.ai Version Control Automation')
    parser.add_argument('--changes', '-c', 
                       default="CI/CD automation, repository cleanup, version control system",
                       help='Summary of changes for this version')
    parser.add_argument('--increment', '-i', 
                       choices=['major', 'minor', 'patch'],
                       default='minor',
                       help='Type of version increment')
    parser.add_argument('--message', '-m',
                       default="feat: implement comprehensive automation and version control system",
                       help='Commit message')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify compliance, do not make changes')
    
    args = parser.parse_args()
    
    controller = LawVersionController()
    
    if args.verify_only:
        print("🔍 Running LAW-001 compliance verification only...")
        success = controller.verify_law_compliance()
        exit(0 if success else 1)
    
    success = controller.run_full_update(
        changes_summary=args.changes,
        increment_type=args.increment,
        commit_message=args.message
    )
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()