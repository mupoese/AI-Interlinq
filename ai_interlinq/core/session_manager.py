# ai_interlinq/core/session_manager.py
"""Session management for AI-Interlinq."""

import asyncio
import time
from typing import Dict, Optional, Set, List
from dataclasses import dataclass
from enum import Enum

from ..utils.logging import get_logger
from ..exceptions import SessionError


class SessionStatus(Enum):
    """Session status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class SessionInfo:
    """Information about a communication session."""
    session_id: str
    participants: Set[str]
    created_at: float
    expires_at: float
    status: SessionStatus
    metadata: Dict[str, any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SessionManager:
    """Manages communication sessions between AI agents."""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self.logger = get_logger("session_manager")
        
        # Session storage
        self._sessions: Dict[str, SessionInfo] = {}
        self._agent_sessions: Dict[str, Set[str]] = {}  # agent_id -> session_ids
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start(self):
        """Start the session manager."""
        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        self.logger.info("Session manager started")
    
    async def stop(self):
        """Stop the session manager."""
        self._is_running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Session manager stopped")
    
    def create_session(
        self, 
        session_id: str, 
        participants: List[str], 
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> SessionInfo:
        """Create a new communication session."""
        
        if session_id in self._sessions:
            raise SessionError(f"Session {session_id} already exists")
        
        ttl = ttl or self.default_ttl
        now = time.time()
        
        session_info = SessionInfo(
            session_id=session_id,
            participants=set(participants),
            created_at=now,
            expires_at=now + ttl,
            status=SessionStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        # Store session
        self._sessions[session_id] = session_info
        
        # Update agent session mapping
        for agent_id in participants:
            if agent_id not in self._agent_sessions:
                self._agent_sessions[agent_id] = set()
            self._agent_sessions[agent_id].add(session_id)
        
        self.logger.info(f"Created session {session_id} with participants: {participants}")
        return session_info
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information."""
        session = self._sessions.get(session_id)
        
        if session and self._is_session_expired(session):
            session.status = SessionStatus.EXPIRED
        
        return session
    
    def extend_session(self, session_id: str, additional_ttl: int = None) -> bool:
        """Extend session expiration time."""
        session = self._sessions.get(session_id)
        
        if not session:
            return False
        
        if session.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            return False
        
        additional_ttl = additional_ttl or self.default_ttl
        session.expires_at = time.time() + additional_ttl
        
        self.logger.info(f"Extended session {session_id} by {additional_ttl} seconds")
        return True
    
    def pause_session(self, session_id: str) -> bool:
        """Pause a session."""
        session = self._sessions.get(session_id)
        
        if not session or session.status != SessionStatus.ACTIVE:
            return False
        
        session.status = SessionStatus.PAUSED
        self.logger.info(f"Paused session {session_id}")
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session."""
        session = self._sessions.get(session_id)
        
        if not session or session.status != SessionStatus.PAUSED:
            return False
        
        if self._is_session_expired(session):
            session.status = SessionStatus.EXPIRED
            return False
        
        session.status = SessionStatus.ACTIVE
        self.logger.info(f"Resumed session {session_id}")
        return True
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a session."""
        session = self._sessions.get(session_id)
        
        if not session:
            return False
        
        session.status = SessionStatus.TERMINATED
        
        # Remove from agent mappings
        for agent_id in session.participants:
            if agent_id in self._agent_sessions:
                self._agent_sessions[agent_id].discard(session_id)
                if not self._agent_sessions[agent_id]:
                    del self._agent_sessions[agent_id]
        
        self.logger.info(f"Terminated session {session_id}")
        return True
    
    def add_participant(self, session_id: str, agent_id: str) -> bool:
        """Add a participant to an existing session."""
        session = self._sessions.get(session_id)
        
        if not session or session.status != SessionStatus.ACTIVE:
            return False
        
        session.participants.add(agent_id)
        
        # Update agent mapping
        if agent_id not in self._agent_sessions:
            self._agent_sessions[agent_id] = set()
        self._agent_sessions[agent_id].add(session_id)
        
        self.logger.info(f"Added participant {agent_id} to session {session_id}")
        return True
    
    def remove_participant(self, session_id: str, agent_id: str) -> bool:
        """Remove a participant from a session."""
        session = self._sessions.get(session_id)
        
        if not session:
            return False
        
        session.participants.discard(agent_id)
        
        # Update agent mapping
        if agent_id in self._agent_sessions:
            self._agent_sessions[agent_id].discard(session_id)
            if not self._agent_sessions[agent_id]:
                del self._agent_sessions[agent_id]
        
        # Terminate session if no participants left
        if not session.participants:
            self.terminate_session(session_id)
        
        self.logger.info(f"Removed participant {agent_id} from session {session_id}")
        return True
    
    def get_agent_sessions(self, agent_id: str) -> List[str]:
        """Get all active sessions for an agent."""
        return list(self._agent_sessions.get(agent_id, set()))
    
    def get_active_sessions(self) -> List[str]:
        """Get all active session IDs."""
        return [
            session_id for session_id, session in self._sessions.items()
            if session.status == SessionStatus.ACTIVE and not self._is_session_expired(session)
        ]
    
    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        stats = {
            "total": len(self._sessions),
            "active": 0,
            "paused": 0,
            "expired": 0,
            "terminated": 0
        }
        
        for session in self._sessions.values():
            if self._is_session_expired(session):
                session.status = SessionStatus.EXPIRED
            
            if session.status == SessionStatus.ACTIVE:
                stats["active"] += 1
            elif session.status == SessionStatus.PAUSED:
                stats["paused"] += 1
            elif session.status == SessionStatus.EXPIRED:
                stats["expired"] += 1
            elif session.status == SessionStatus.TERMINATED:
                stats["terminated"] += 1
        
        return stats
    
    def _is_session_expired(self, session: SessionInfo) -> bool:
        """Check if a session is expired."""
        return time.time() > session.expires_at
    
    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions."""
        while self._is_running:
            try:
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session in self._sessions.items():
                    if session.status == SessionStatus.ACTIVE and current_time > session.expires_at:
                        expired_sessions.append(session_id)
                
                # Mark sessions as expired
                for session_id in expired_sessions:
                    session = self._sessions[session_id]
                    session.status = SessionStatus.EXPIRED
                    self.logger.info(f"Session {session_id} expired")
                
                # Remove old terminated/expired sessions after 24 hours
                cleanup_threshold = current_time - (24 * 3600)
                sessions_to_remove = []
                
                for session_id, session in self._sessions.items():
                    if (session.status in [SessionStatus.EXPIRED, SessionStatus.TERMINATED] and
                        session.created_at < cleanup_threshold):
                        sessions_to_remove.append(session_id)
                
                for session_id in sessions_to_remove:
                    session = self._sessions.pop(session_id)
                    # Clean up agent mappings
                    for agent_id in session.participants:
                        if agent_id in self._agent_sessions:
                            self._agent_sessions[agent_id].discard(session_id)
                            if not self._agent_sessions[agent_id]:
                                del self._agent_sessions[agent_id]
                    
                    self.logger.debug(f"Cleaned up old session {session_id}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)
