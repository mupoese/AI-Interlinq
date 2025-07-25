# File: /governance/voting_system.py
# Directory: /governance

"""
LAW-001 Compliance: Voting System
Handles governance votes for logic updates.
Must implement mupoese_admin_core approval system.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class VoteType(Enum):
    """Types of votes."""
    LOGIC_UPDATE = "logic_update"
    LAW_MODIFICATION = "law_modification"
    GOVERNANCE_CHANGE = "governance_change"
    EMERGENCY_DECISION = "emergency_decision"


class VoteStatus(Enum):
    """Vote status options."""
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Vote:
    """Represents a governance vote."""
    vote_id: str
    vote_type: VoteType
    title: str
    description: str
    proposed_by: str
    created_timestamp: float
    voting_deadline: float
    required_approvals: int
    approval_threshold: float
    status: VoteStatus
    votes_cast: Dict[str, bool]  # voter_id -> True/False
    approved_by: List[str]
    denied_by: List[str]
    admin_decision: Optional[bool]
    admin_decision_timestamp: Optional[float]
    final_result: Optional[bool]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert vote to dictionary."""
        data = asdict(self)
        data["vote_type"] = self.vote_type.value
        data["status"] = self.status.value
        return data


class VotingSystem:
    """
    LAW-001 Compliance: Voting System
    
    Purpose: Handle governance votes for logic updates
    Requirements: Must implement mupoese_admin_core approval system
    """
    
    def __init__(self, admin_id: str = "mupoese_admin_core"):
        """
        Initialize voting system.
        
        Args:
            admin_id: Administrator ID with final decision authority
        """
        self.admin_id = admin_id
        self.governance_dir = Path("governance")
        self.votes_file = self.governance_dir / "votes.json"
        self.governance_log = self.governance_dir / "governance_log.json"
        
        # Ensure governance directory exists
        self.governance_dir.mkdir(exist_ok=True)
        
        # Voting configuration
        self.default_voting_duration = 7 * 24 * 3600  # 7 days in seconds
        self.required_approvals = 3
        self.approval_threshold = 0.667  # 66.7%
        
        # Load existing votes
        self.active_votes: Dict[str, Vote] = {}
        self.vote_history: List[Vote] = []
        self._load_votes()
        
        # Authorized voters
        self.authorized_voters = {
            "mupoese_admin_core",
            "law_engine.kernel", 
            "memory.snapshot.validator",
            "governance.validator",
            "ai_interlinq.core"
        }
    
    def create_logic_update_vote(self, proposal_data: Dict[str, Any]) -> str:
        """
        Create a vote for a logic update proposal.
        
        Args:
            proposal_data: Proposal data from proposed_logic_update.ai
            
        Returns:
            str: Vote ID
        """
        vote_id = self._generate_vote_id()
        
        vote = Vote(
            vote_id=vote_id,
            vote_type=VoteType.LOGIC_UPDATE,
            title=f"Logic Update Proposal",
            description=f"Proposed update: {proposal_data.get('suggested_improvement', 'Unspecified')}",
            proposed_by=proposal_data.get("agent_id", "unknown"),
            created_timestamp=time.time(),
            voting_deadline=time.time() + self.default_voting_duration,
            required_approvals=self.required_approvals,
            approval_threshold=self.approval_threshold,
            status=VoteStatus.ACTIVE,
            votes_cast={},
            approved_by=[],
            denied_by=[],
            admin_decision=None,
            admin_decision_timestamp=None,
            final_result=None
        )
        
        self.active_votes[vote_id] = vote
        self._save_votes()
        self._log_governance_activity(f"Logic update vote created: {vote_id}")
        
        print(f"Logic update vote created: {vote_id}")
        print(f"Proposal: {vote.description}")
        
        return vote_id
    
    def create_law_modification_vote(self, law_id: str, modification_details: str) -> str:
        """
        Create a vote for law modification.
        
        Args:
            law_id: ID of the law to be modified
            modification_details: Details of proposed modification
            
        Returns:
            str: Vote ID
        """
        vote_id = self._generate_vote_id()
        
        vote = Vote(
            vote_id=vote_id,
            vote_type=VoteType.LAW_MODIFICATION,
            title=f"Law Modification: {law_id}",
            description=modification_details,
            proposed_by=self.admin_id,
            created_timestamp=time.time(),
            voting_deadline=time.time() + self.default_voting_duration,
            required_approvals=self.required_approvals,
            approval_threshold=self.approval_threshold,
            status=VoteStatus.ACTIVE,
            votes_cast={},
            approved_by=[],
            denied_by=[],
            admin_decision=None,
            admin_decision_timestamp=None,
            final_result=None
        )
        
        self.active_votes[vote_id] = vote
        self._save_votes()
        self._log_governance_activity(f"Law modification vote created: {vote_id} for {law_id}")
        
        return vote_id
    
    def cast_vote(self, vote_id: str, voter_id: str, approval: bool) -> bool:
        """
        Cast a vote on an active proposal.
        
        Args:
            vote_id: ID of the vote
            voter_id: ID of the voter
            approval: True for approval, False for denial
            
        Returns:
            bool: Success status
        """
        if vote_id not in self.active_votes:
            print(f"Vote {vote_id} not found or not active")
            return False
        
        vote = self.active_votes[vote_id]
        
        # Check if voter is authorized
        if voter_id not in self.authorized_voters:
            print(f"Voter {voter_id} is not authorized")
            return False
        
        # Check if vote is still active
        if vote.status != VoteStatus.ACTIVE:
            print(f"Vote {vote_id} is not active (status: {vote.status.value})")
            return False
        
        # Check if voting deadline has passed
        if time.time() > vote.voting_deadline:
            print(f"Voting deadline has passed for vote {vote_id}")
            vote.status = VoteStatus.FAILED
            self._save_votes()
            return False
        
        # Cast the vote
        vote.votes_cast[voter_id] = approval
        
        if approval:
            if voter_id not in vote.approved_by:
                vote.approved_by.append(voter_id)
            if voter_id in vote.denied_by:
                vote.denied_by.remove(voter_id)
        else:
            if voter_id not in vote.denied_by:
                vote.denied_by.append(voter_id)
            if voter_id in vote.approved_by:
                vote.approved_by.remove(voter_id)
        
        # Check if vote should be concluded
        self._check_vote_conclusion(vote)
        
        self._save_votes()
        self._log_governance_activity(f"Vote cast by {voter_id} on {vote_id}: {'APPROVE' if approval else 'DENY'}")
        
        print(f"Vote cast by {voter_id} on {vote_id}: {'APPROVED' if approval else 'DENIED'}")
        
        return True
    
    def admin_decision(self, vote_id: str, decision: bool, reason: str = "") -> bool:
        """
        Administrator final decision on a vote.
        
        Args:
            vote_id: ID of the vote
            decision: True for approval, False for denial
            reason: Reason for the decision
            
        Returns:
            bool: Success status
        """
        if vote_id not in self.active_votes:
            print(f"Vote {vote_id} not found")
            return False
        
        vote = self.active_votes[vote_id]
        
        # Record admin decision
        vote.admin_decision = decision
        vote.admin_decision_timestamp = time.time()
        vote.final_result = decision
        
        # Update vote status
        if decision:
            vote.status = VoteStatus.PASSED
        else:
            vote.status = VoteStatus.FAILED
        
        # Move to history
        self.vote_history.append(vote)
        del self.active_votes[vote_id]
        
        self._save_votes()
        self._log_governance_activity(f"Admin decision on {vote_id}: {'APPROVED' if decision else 'DENIED'} - {reason}")
        
        print(f"Administrator decision on vote {vote_id}: {'APPROVED' if decision else 'DENIED'}")
        if reason:
            print(f"Reason: {reason}")
        
        return True
    
    def get_active_votes(self) -> List[Dict[str, Any]]:
        """
        Get list of active votes.
        
        Returns:
            List of active vote dictionaries
        """
        return [vote.to_dict() for vote in self.active_votes.values()]
    
    def get_vote_status(self, vote_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific vote.
        
        Args:
            vote_id: ID of the vote
            
        Returns:
            Dict with vote status or None if not found
        """
        # Check active votes
        if vote_id in self.active_votes:
            vote = self.active_votes[vote_id]
            status = vote.to_dict()
            status["votes_needed"] = max(0, vote.required_approvals - len(vote.approved_by))
            status["approval_percentage"] = (len(vote.approved_by) / len(self.authorized_voters)) * 100
            return status
        
        # Check vote history
        for vote in self.vote_history:
            if vote.vote_id == vote_id:
                return vote.to_dict()
        
        return None
    
    def process_proposed_updates(self) -> List[str]:
        """
        Process proposed logic updates and create votes.
        
        Returns:
            List of created vote IDs
        """
        proposed_updates_file = Path("proposed_logic_update.ai")
        
        if not proposed_updates_file.exists():
            return []
        
        try:
            with open(proposed_updates_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                
                updates = json.loads(content)
            
            created_votes = []
            
            # Create votes for each proposed update
            for update in updates:
                if isinstance(update, dict):
                    vote_id = self.create_logic_update_vote(update)
                    created_votes.append(vote_id)
            
            # Clear processed updates
            with open(proposed_updates_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            
            return created_votes
            
        except Exception as e:
            print(f"Error processing proposed updates: {e}")
            return []
    
    def get_voting_statistics(self) -> Dict[str, Any]:
        """
        Get voting system statistics.
        
        Returns:
            Dict with voting statistics
        """
        total_votes = len(self.active_votes) + len(self.vote_history)
        passed_votes = sum(1 for vote in self.vote_history if vote.final_result is True)
        failed_votes = sum(1 for vote in self.vote_history if vote.final_result is False)
        
        return {
            "active_votes": len(self.active_votes),
            "total_votes": total_votes,
            "passed_votes": passed_votes,
            "failed_votes": failed_votes,
            "pass_rate": (passed_votes / len(self.vote_history)) * 100 if self.vote_history else 0,
            "authorized_voters": len(self.authorized_voters),
            "admin_id": self.admin_id
        }
    
    def _check_vote_conclusion(self, vote: Vote) -> None:
        """
        Check if a vote should be concluded based on current votes.
        
        Args:
            vote: Vote to check
        """
        total_votes = len(vote.votes_cast)
        approvals = len(vote.approved_by)
        
        # Check if enough approvals reached
        if approvals >= vote.required_approvals:
            approval_percentage = approvals / len(self.authorized_voters)
            
            if approval_percentage >= vote.approval_threshold:
                vote.status = VoteStatus.PASSED
                vote.final_result = True
                self.vote_history.append(vote)
                if vote.vote_id in self.active_votes:
                    del self.active_votes[vote.vote_id]
                self._log_governance_activity(f"Vote {vote.vote_id} concluded: PASSED")
                print(f"Vote {vote.vote_id} has PASSED")
                return
        
        # Check if impossible to reach threshold
        remaining_voters = len(self.authorized_voters) - total_votes
        max_possible_approvals = approvals + remaining_voters
        
        if max_possible_approvals < vote.required_approvals:
            vote.status = VoteStatus.FAILED
            vote.final_result = False
            self.vote_history.append(vote)
            if vote.vote_id in self.active_votes:
                del self.active_votes[vote.vote_id]
            self._log_governance_activity(f"Vote {vote.vote_id} concluded: FAILED")
            print(f"Vote {vote.vote_id} has FAILED")
    
    def _generate_vote_id(self) -> str:
        """Generate unique vote ID."""
        timestamp = int(time.time() * 1000)
        return f"vote_{timestamp}"
    
    def _save_votes(self) -> None:
        """Save votes to file."""
        try:
            votes_data = {
                "active_votes": {vid: vote.to_dict() for vid, vote in self.active_votes.items()},
                "vote_history": [vote.to_dict() for vote in self.vote_history],
                "last_updated": time.time()
            }
            
            with open(self.votes_file, 'w', encoding='utf-8') as f:
                json.dump(votes_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving votes: {e}")
    
    def _load_votes(self) -> None:
        """Load votes from file."""
        try:
            if not self.votes_file.exists():
                return
            
            with open(self.votes_file, 'r', encoding='utf-8') as f:
                votes_data = json.load(f)
            
            # Load active votes
            for vote_id, vote_dict in votes_data.get("active_votes", {}).items():
                vote_dict["vote_type"] = VoteType(vote_dict["vote_type"])
                vote_dict["status"] = VoteStatus(vote_dict["status"])
                self.active_votes[vote_id] = Vote(**vote_dict)
            
            # Load vote history
            for vote_dict in votes_data.get("vote_history", []):
                vote_dict["vote_type"] = VoteType(vote_dict["vote_type"])
                vote_dict["status"] = VoteStatus(vote_dict["status"])
                self.vote_history.append(Vote(**vote_dict))
                
        except Exception as e:
            print(f"Error loading votes: {e}")
    
    def _log_governance_activity(self, activity: str) -> None:
        """
        Log governance activity.
        
        Args:
            activity: Activity description
        """
        try:
            log_entry = {
                "timestamp": time.time(),
                "activity": activity,
                "admin_id": self.admin_id
            }
            
            # Load existing log
            log_entries = []
            if self.governance_log.exists():
                with open(self.governance_log, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        log_entries = json.loads(content)
            
            # Add new entry
            log_entries.append(log_entry)
            
            # Keep only last 1000 entries
            if len(log_entries) > 1000:
                log_entries = log_entries[-1000:]
            
            # Save log
            with open(self.governance_log, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, indent=2)
                
        except Exception as e:
            print(f"Error logging governance activity: {e}")