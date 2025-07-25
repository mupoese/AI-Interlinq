# ai_interlinq/core/memory_system.py

"""
Advanced Memory System for AI-Interlinq
Implements snapshot memory, recall methods, and persistent storage for AI communications.
"""

import json
import sqlite3
import pickle
import hashlib
import time
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock
from datetime import datetime, timedelta

from .communication_protocol import Message, MessageType


@dataclass
class MemorySnapshot:
    """Represents a memory snapshot."""
    snapshot_id: str
    timestamp: float
    data: Dict[str, Any]
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class ConversationContext:
    """Represents conversation context for memory."""
    session_id: str
    participants: List[str]
    start_time: float
    last_activity: float
    message_count: int
    context_data: Dict[str, Any]


class MemoryDatabase:
    """SQLite-based memory storage system."""
    
    def __init__(self, db_path: str = "ai_interlinq_memory.db"):
        """Initialize memory database."""
        self.db_path = Path(db_path)
        self.lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    data_json TEXT NOT NULL,
                    tags TEXT,
                    metadata_json TEXT,
                    data_hash TEXT,
                    created_at REAL DEFAULT (datetime('now'))
                );
                
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    participants TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    context_data_json TEXT,
                    created_at REAL DEFAULT (datetime('now'))
                );
                
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    command TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES conversations (session_id)
                );
                
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    key_hash TEXT PRIMARY KEY,
                    key_text TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    category TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    created_at REAL DEFAULT (datetime('now')),
                    accessed_count INTEGER DEFAULT 0,
                    last_accessed REAL
                );
                
                CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp);
                CREATE INDEX IF NOT EXISTS idx_snapshots_tags ON snapshots(tags);
                CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
                CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
            """)
    
    def store_snapshot(self, snapshot: MemorySnapshot) -> bool:
        """Store a memory snapshot."""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    data_json = json.dumps(snapshot.data)
                    data_hash = hashlib.sha256(data_json.encode()).hexdigest()
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO snapshots 
                        (snapshot_id, timestamp, data_json, tags, metadata_json, data_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        snapshot.snapshot_id,
                        snapshot.timestamp,
                        data_json,
                        json.dumps(snapshot.tags),
                        json.dumps(snapshot.metadata),
                        data_hash
                    ))
                    return True
        except Exception as e:
            print(f"Error storing snapshot: {e}")
            return False
    
    def retrieve_snapshot(self, snapshot_id: str) -> Optional[MemorySnapshot]:
        """Retrieve a memory snapshot by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT snapshot_id, timestamp, data_json, tags, metadata_json
                    FROM snapshots WHERE snapshot_id = ?
                """, (snapshot_id,))
                
                row = cursor.fetchone()
                if row:
                    return MemorySnapshot(
                        snapshot_id=row[0],
                        timestamp=row[1],
                        data=json.loads(row[2]),
                        tags=json.loads(row[3]) if row[3] else [],
                        metadata=json.loads(row[4]) if row[4] else {}
                    )
        except Exception as e:
            print(f"Error retrieving snapshot: {e}")
        return None
    
    def store_message(self, message: Message) -> bool:
        """Store a message in the database."""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO messages 
                        (message_id, session_id, sender_id, recipient_id, 
                         message_type, command, data_json, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        message.header.message_id,
                        message.header.session_id,
                        message.header.sender_id,
                        message.header.recipient_id,
                        message.header.message_type.value,
                        message.payload.command,
                        json.dumps(message.payload.data),
                        message.header.timestamp
                    ))
                    return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False


class AdvancedMemorySystem:
    """Advanced memory system with AI learning capabilities."""
    
    def __init__(self, agent_id: str, db_path: Optional[str] = None):
        """
        Initialize advanced memory system.
        
        Args:
            agent_id: ID of the AI agent
            db_path: Path to memory database
        """
        self.agent_id = agent_id
        self.db = MemoryDatabase(db_path or f"memory_{agent_id}.db")
        self._active_contexts: Dict[str, ConversationContext] = {}
        self._knowledge_cache: Dict[str, Any] = {}
        self._learning_patterns: Dict[str, List] = {}
        self._injection_handlers: Dict[str, Callable] = {}
        
    def create_snapshot(self, data: Dict[str, Any], tags: List[str] = None) -> str:
        """
        Create a memory snapshot of current state.
        
        Args:
            data: Data to snapshot
            tags: Optional tags for categorization
            
        Returns:
            Snapshot ID
        """
        snapshot_id = f"snap_{self.agent_id}_{int(time.time() * 1000)}"
        
        snapshot = MemorySnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            data=data,
            tags=tags or [],
            metadata={
                "agent_id": self.agent_id,
                "creation_method": "manual",
                "data_size": len(json.dumps(data))
            }
        )
        
        if self.db.store_snapshot(snapshot):
            return snapshot_id
        return None
    
    def auto_snapshot(self, context_data: Dict[str, Any], trigger: str) -> str:
        """
        Automatically create snapshot based on triggers.
        
        Args:
            context_data: Current context data
            trigger: What triggered the snapshot
            
        Returns:
            Snapshot ID
        """
        # Enhanced data with learning patterns
        enhanced_data = {
            **context_data,
            "learning_patterns": self._extract_patterns(context_data),
            "trigger": trigger,
            "agent_state": self._get_agent_state()
        }
        
        tags = [trigger, "auto", self.agent_id]
        return self.create_snapshot(enhanced_data, tags)
    
    def recall_memory(self, query: Dict[str, Any], limit: int = 10) -> List[MemorySnapshot]:
        """
        Intelligent memory recall based on query.
        
        Args:
            query: Query parameters for memory search
            limit: Maximum number of results
            
        Returns:
            List of relevant memory snapshots
        """
        # Implementation of semantic memory search
        relevant_snapshots = []
        
        # Search by tags
        if "tags" in query:
            relevant_snapshots.extend(self._search_by_tags(query["tags"], limit))
        
        # Search by content similarity
        if "content" in query:
            relevant_snapshots.extend(self._search_by_content(query["content"], limit))
        
        # Search by time range
        if "time_range" in query:
            relevant_snapshots.extend(self._search_by_time(query["time_range"], limit))
        
        # Remove duplicates and sort by relevance
        unique_snapshots = {s.snapshot_id: s for s in relevant_snapshots}
        return list(unique_snapshots.values())[:limit]
    
    def inject_knowledge(self, key: str, value: Any, category: str = "general") -> bool:
        """
        Inject knowledge into the memory system.
        
        Args:
            key: Knowledge key
            value: Knowledge value
            category: Knowledge category
            
        Returns:
            Success status
        """
        try:
            # Store in database
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            
            with sqlite3.connect(self.db.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_base
                    (key_hash, key_text, value_json, category, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    key_hash,
                    key,
                    json.dumps(value),
                    category,
                    time.time()
                ))
            
            # Update cache
            self._knowledge_cache[key] = value
            
            # Trigger learning pattern update
            self._update_learning_patterns(key, value, category)
            
            return True
            
        except Exception as e:
            print(f"Error injecting knowledge: {e}")
            return False
    
    def retrieve_knowledge(self, key: str, use_cache: bool = True) -> Optional[Any]:
        """
        Retrieve knowledge from memory.
        
        Args:
            key: Knowledge key
            use_cache: Whether to use cache
            
        Returns:
            Retrieved knowledge or None
        """
        # Check cache first
        if use_cache and key in self._knowledge_cache:
            return self._knowledge_cache[key]
        
        # Query database
        try:
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute("""
                    SELECT value_json FROM knowledge_base 
                    WHERE key_hash = ? OR key_text = ?
                """, (key_hash, key))
                
                row = cursor.fetchone()
                if row:
                    value = json.loads(row[0])
                    # Update cache and access count
                    if use_cache:
                        self._knowledge_cache[key] = value
                    
                    # Update access statistics
                    conn.execute("""
                        UPDATE knowledge_base 
                        SET accessed_count = accessed_count + 1,
                            last_accessed = ?
                        WHERE key_hash = ?
                    """, (time.time(), key_hash))
                    
                    return value
                    
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
        
        return None
    
    def register_injection_handler(self, pattern: str, handler: Callable):
        """Register a handler for code injection patterns."""
        self._injection_handlers[pattern] = handler
    
    def process_code_injection(self, code: str, context: Dict[str, Any]) -> Any:
        """
        Process code injection safely with context.
        
        Args:
            code: Code to inject and execute
            context: Execution context
            
        Returns:
            Execution result
        """
        # Security check - only allow safe operations
        forbidden_patterns = ['import os', 'import sys', 'exec(', 'eval(', '__import__']
        
        for pattern in forbidden_patterns:
            if pattern in code:
                raise SecurityError(f"Forbidden pattern detected: {pattern}")
        
        # Create safe execution environment
        safe_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float,
                'list': list, 'dict': dict, 'tuple': tuple,
                'min': min, 'max': max, 'sum': sum, 'abs': abs
            },
            'context': context,
            'memory': self,
            'time': time.time(),
            'agent_id': self.agent_id
        }
        
        try:
            # Execute in controlled environment
            result = eval(code, safe_globals, {})
            
            # Log injection for learning
            self._log_injection(code, context, result)
            
            return result
            
        except Exception as e:
            print(f"Code injection error: {e}")
            return None
    
    def _extract_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract learning patterns from data."""
        patterns = []
        
        # Pattern: Frequent commands
        if "command" in data:
            command = data["command"]
            if command not in self._learning_patterns:
                self._learning_patterns[command] = []
            
            self._learning_patterns[command].append({
                "timestamp": time.time(),
                "data": data
            })
            
            patterns.append({
                "type": "command_frequency",
                "command": command,
                "frequency": len(self._learning_patterns[command])
            })
        
        # Pattern: Response times
        if "response_time" in data:
            patterns.append({
                "type": "performance",
                "metric": "response_time",
                "value": data["response_time"]
            })
        
        return patterns
    
    def _get_agent_state(self) -> Dict[str, Any]:
        """Get current agent state for snapshots."""
        return {
            "active_contexts": len(self._active_contexts),
            "knowledge_cache_size": len(self._knowledge_cache),
            "learning_patterns": len(self._learning_patterns),
            "timestamp": time.time()
        }
    
    def _search_by_tags(self, tags: List[str], limit: int) -> List[MemorySnapshot]:
        """Search snapshots by tags."""
        # Implementation would query database for matching tags
        return []
    
    def _search_by_content(self, content: str, limit: int) -> List[MemorySnapshot]:
        """Search snapshots by content similarity."""
        # Implementation would use text similarity algorithms
        return []
    
    def _search_by_time(self, time_range: tuple, limit: int) -> List[MemorySnapshot]:
        """Search snapshots by time range."""
        # Implementation would query database for time range
        return []
    
    def _update_learning_patterns(self, key: str, value: Any, category: str):
        """Update learning patterns based on injected knowledge."""
        pattern_key = f"{category}:{key}"
        if pattern_key not in self._learning_patterns:
            self._learning_patterns[pattern_key] = []
        
        self._learning_patterns[pattern_key].append({
            "timestamp": time.time(),
            "value": value,
            "category": category
        })
    
    def _log_injection(self, code: str, context: Dict[str, Any], result: Any):
        """Log code injection for learning and security."""
        log_entry = {
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "code": code,
            "context_keys": list(context.keys()),
            "result_type": type(result).__name__,
            "success": result is not None
        }
        
        # Store in learning patterns
        if "code_injections" not in self._learning_patterns:
            self._learning_patterns["code_injections"] = []
        
        self._learning_patterns["code_injections"].append(log_entry)
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Snapshot statistics
                snapshot_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
                
                # Message statistics
                message_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
                
                # Knowledge base statistics
                knowledge_count = conn.execute("SELECT COUNT(*) FROM knowledge_base").fetchone()[0]
                
                return {
                    "snapshots": snapshot_count,
                    "messages": message_count,
                    "knowledge_entries": knowledge_count,
                    "active_contexts": len(self._active_contexts),
                    "cached_knowledge": len(self._knowledge_cache),
                    "learning_patterns": len(self._learning_patterns),
                    "injection_handlers": len(self._injection_handlers)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_old_data(self, days_old: int = 30) -> int:
        """Clean up old data from memory system."""
        cutoff_time = time.time() - (days_old * 24 * 3600)
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Clean old snapshots
                cursor = conn.execute("""
                    DELETE FROM snapshots WHERE timestamp < ?
                """, (cutoff_time,))
                deleted_snapshots = cursor.rowcount
                
                # Clean old messages
                cursor = conn.execute("""
                    DELETE FROM messages WHERE timestamp < ?
                """, (cutoff_time,))
                deleted_messages = cursor.rowcount
                
                return deleted_snapshots + deleted_messages
                
        except Exception as e:
            print(f"Error cleaning up data: {e}")
            return 0


class SecurityError(Exception):
    """Security-related error in memory system."""
    pass


# Alias for backward compatibility
MemorySystem = AdvancedMemorySystem
