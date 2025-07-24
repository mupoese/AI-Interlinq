# examples/advanced_communication.py

"""
Advanced AI-Interlinq Communication Example
Demonstrates advanced features including memory system, code injection, and learning.
"""

import asyncio
import time
import json
from typing import Dict, Any

from ai_interlinq import (
    TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler,
    AdvancedMemorySystem, PerformanceMonitor, MessageSerializer, MessageParser
)
from ai_interlinq.core.communication_protocol import MessageType, Priority


class IntelligentAgent:
    """An intelligent AI agent with advanced memory and learning capabilities."""
    
    def __init__(self, agent_id: str, shared_key: str):
        """Initialize intelligent agent."""
        self.agent_id = agent_id
        self.token_manager = TokenManager(default_ttl=7200)
        self.encryption = EncryptionHandler(shared_key)
        self.protocol = CommunicationProtocol(agent_id)
        self.message_handler = MessageHandler(agent_id, self.token_manager, self.encryption)
        self.memory_system = AdvancedMemorySystem(agent_id)
        self.performance_monitor = PerformanceMonitor()
        self.serializer = MessageSerializer()
        self.parser = MessageParser()
        
        # Learning state
        self.conversation_history = []
        self.learned_patterns = {}
        self.active_sessions = {}
        
        # Register command handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message command handlers."""
        handlers = {
            "learn_pattern": self._handle_learn_pattern,
            "query_knowledge": self._handle_query_knowledge,
            "execute_code": self._handle_execute_code,
            "create_memory": self._handle_create_memory,
            "recall_memory": self._handle_recall_memory,
            "get_stats": self._handle_get_stats,
            "collaborate": self._handle_collaborate
        }
        
        for command, handler in handlers.items():
            self.message_handler.register_command_handler(command, handler)
    
    async def _handle_learn_pattern(self, message):
        """Handle learning pattern requests."""
        timer_id = self.performance_monitor.start_timer("learn_pattern")
        
        try:
            data = message.payload.data
            pattern_name = data.get("pattern_name")
            pattern_data = data.get("pattern_data")
            
            # Store pattern in memory
            self.memory_system.inject_knowledge(
                key=f"pattern:{pattern_name}",
                value=pattern_data,
                category="learned_patterns"
            )
            
            # Create memory snapshot
            snapshot_data = {
                "pattern_name": pattern_name,
                "pattern_data": pattern_data,
                "learning_context": data.get("context", {}),
                "timestamp": time.time()
            }
            
            snapshot_id = self.memory_system.create_snapshot(
                snapshot_data, 
                tags=["learning", "pattern", pattern_name]
            )
            
            # Send response
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="pattern_learned",
                data={
                    "pattern_name": pattern_name,
                    "snapshot_id": snapshot_id,
                    "status": "success",
                    "message": f"Pattern '{pattern_name}' learned successfully"
                },
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "LEARNING_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _handle_query_knowledge(self, message):
        """Handle knowledge query requests."""
        timer_id = self.performance_monitor.start_timer("query_knowledge")
        
        try:
            data = message.payload.data
            query = data.get("query")
            
            # Search memory for relevant information
            memory_results = self.memory_system.recall_memory({
                "content": query,
                "tags": data.get("tags", [])
            }, limit=5)
            
            # Query knowledge base
            knowledge_key = f"knowledge:{query}"
            direct_knowledge = self.memory_system.retrieve_knowledge(knowledge_key)
            
            # Compile response
            response_data = {
                "query": query,
                "direct_knowledge": direct_knowledge,
                "memory_results": [
                    {
                        "snapshot_id": snap.snapshot_id,
                        "timestamp": snap.timestamp,
                        "tags": snap.tags,
                        "relevance": self._calculate_relevance(snap, query)
                    }
                    for snap in memory_results
                ],
                "total_results": len(memory_results)
            }
            
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="knowledge_response",
                data=response_data,
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "QUERY_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _handle_execute_code(self, message):
        """Handle safe code execution requests."""
        timer_id = self.performance_monitor.start_timer("execute_code")
        
        try:
            data = message.payload.data
            code = data.get("code")
            context = data.get("context", {})
            
            # Add agent context
            execution_context = {
                **context,
                "agent_id": self.agent_id,
                "session_id": message.header.session_id,
                "memory_stats": self.memory_system.get_memory_statistics(),
                "performance_stats": self.performance_monitor.get_all_stats()
            }
            
            # Execute code safely
            result = self.memory_system.process_code_injection(code, execution_context)
            
            # Create memory snapshot of execution
            execution_snapshot = {
                "code": code,
                "context": execution_context,
                "result": result,
                "execution_time": time.time(),
                "success": result is not None
            }
            
            snapshot_id = self.memory_system.create_snapshot(
                execution_snapshot,
                tags=["code_execution", "injection", self.agent_id]
            )
            
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="code_executed",
                data={
                    "result": result,
                    "snapshot_id": snapshot_id,
                    "execution_context": execution_context,
                    "success": result is not None
                },
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "EXECUTION_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _handle_create_memory(self, message):
        """Handle memory creation requests."""
        timer_id = self.performance_monitor.start_timer("create_memory")
        
        try:
            data = message.payload.data
            memory_data = data.get("memory_data")
            tags = data.get("tags", [])
            trigger = data.get("trigger", "manual")
            
            # Create memory snapshot
            snapshot_id = self.memory_system.auto_snapshot(memory_data, trigger)
            
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="memory_created",
                data={
                    "snapshot_id": snapshot_id,
                    "trigger": trigger,
                    "data_size": len(json.dumps(memory_data)),
                    "tags": tags
                },
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "MEMORY_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _handle_recall_memory(self, message):
        """Handle memory recall requests."""
        timer_id = self.performance_monitor.start_timer("recall_memory")
        
        try:
            data = message.payload.data
            query = data.get("query", {})
            limit = data.get("limit", 10)
            
            # Recall memories
            memories = self.memory_system.recall_memory(query, limit)
            
            # Format response
            memory_data = []
            for memory in memories:
                memory_data.append({
                    "snapshot_id": memory.snapshot_id,
                    "timestamp": memory.timestamp,
                    "tags": memory.tags,
                    "metadata": memory.metadata,
                    "data_preview": str(memory.data)[:200] + "..." if len(str(memory.data)) > 200 else str(memory.data)
                })
            
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="memory_recalled",
                data={
                    "query": query,
                    "memories": memory_data,
                    "total_found": len(memories)
                },
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "RECALL_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _handle_get_stats(self, message):
        """Handle statistics requests."""
        timer_id = self.performance_monitor.start_timer("get_stats")
        
        try:
            # Gather comprehensive statistics
            stats = {
                "agent_id": self.agent_id,
                "timestamp": time.time(),
                "memory_stats": self.memory_system.get_memory_statistics(),
                "performance_stats": self.performance_monitor.get_all_stats(),
                "message_stats": self.message_handler.get_statistics(),
                "conversation_history": len(self.conversation_history),
                "learned_patterns": len(self.learned_patterns),
                "active_sessions": len(self.active_sessions)
            }
            
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="stats_response",
                data=stats,
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "STATS_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _handle_collaborate(self, message):
        """Handle collaboration requests between agents."""
        timer_id = self.performance_monitor.start_timer("collaborate")
        
        try:
            data = message.payload.data
            collaboration_type = data.get("type")
            task_data = data.get("task_data")
            
            # Process based on collaboration type
            if collaboration_type == "knowledge_share":
                result = await self._share_knowledge(task_data)
            elif collaboration_type == "joint_learning":
                result = await self._joint_learning(task_data)
            elif collaboration_type == "task_delegation":
                result = await self._delegate_task(task_data)
            else:
                result = {"error": f"Unknown collaboration type: {collaboration_type}"}
            
            # Create collaboration memory
            collaboration_memory = {
                "collaboration_type": collaboration_type,
                "partner_agent": message.header.sender_id,
                "task_data": task_data,
                "result": result,
                "timestamp": time.time()
            }
            
            snapshot_id = self.memory_system.create_snapshot(
                collaboration_memory,
                tags=["collaboration", collaboration_type, message.header.sender_id]
            )
            
            response = self.protocol.create_message(
                recipient_id=message.header.sender_id,
                message_type=MessageType.RESPONSE,
                command="collaboration_result",
                data={
                    "collaboration_type": collaboration_type,
                    "result": result,
                    "snapshot_id": snapshot_id
                },
                session_id=message.header.session_id
            )
            
            await self.message_handler.send_message(response)
            
        except Exception as e:
            await self._send_error_response(message, "COLLABORATION_ERROR", str(e))
        finally:
            self.performance_monitor.end_timer(timer_id)
    
    async def _share_knowledge(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Share knowledge with another agent."""
        knowledge_keys = task_data.get("knowledge_keys", [])
        shared_knowledge = {}
        
        for key in knowledge_keys:
            knowledge = self.memory_system.retrieve_knowledge(key)
            if knowledge:
                shared_knowledge[key] = knowledge
        
        return {
            "shared_knowledge": shared_knowledge,
            "total_shared": len(shared_knowledge)
        }
    
    async def _joint_learning(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Participate in joint learning with another agent."""
        learning_data = task_data.get("learning_data")
        learning_type = task_data.get("learning_type", "pattern")
        
        # Process learning data
        if learning_type == "pattern":
            pattern_name = f"joint_pattern_{int(time.time())}"
            self.memory_system.inject_knowledge(
                key=f"pattern:{pattern_name}",
                value=learning_data,
                category="joint_learning"
            )
            
            return {
                "pattern_name": pattern_name,
                "status": "learned",
                "learning_type": learning_type
            }
        
        return {"status": "processed", "learning_type": learning_type}
    
    async def _delegate_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task delegation."""
        task_type = task_data.get("task_type")
        task_params = task_data.get("params", {})
        
        # Process different task types
        if task_type == "data_analysis":
            return await self._analyze_data(task_params)
        elif task_type == "pattern_recognition":
            return await self._recognize_patterns(task_params)
        elif task_type == "memory_consolidation":
            return await self._consolidate_memory(task_params)
        
        return {"status": "unknown_task", "task_type": task_type}
    
    async def _analyze_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data for another agent."""
        data = params.get("data", [])
        analysis_type = params.get("analysis_type", "basic")
        
        if analysis_type == "basic":
            return {
                "data_size": len(data),
                "data_type": type(data).__name__,
                "analysis_type": analysis_type,
                "summary": f"Analyzed {len(data)} data points"
            }
        
        return {"status": "analyzed", "analysis_type": analysis_type}
    
    async def _recognize_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize patterns in data."""
        data = params.get("data", [])
        
        # Simple pattern recognition
        patterns = {
            "data_length": len(data),
            "unique_types": len(set(type(item).__name__ for item in data)),
            "patterns_found": []
        }
        
        return patterns
    
    async def _consolidate_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate memory for optimization."""
        cleanup_days = params.get("cleanup_days", 7)
        
        # Clean up old data
        cleaned_count = self.memory_system.cleanup_old_data(cleanup_days)
        
        return {
            "cleaned_items": cleaned_count,
            "cleanup_days": cleanup_days,
            "status": "consolidated"
        }
    
    def _calculate_relevance(self, snapshot, query: str) -> float:
        """Calculate relevance score for memory snapshot."""
        # Simple relevance calculation based on tag matching and content
        relevance = 0.0
        
        # Tag matching
        query_words = query.lower().split()
        for tag in snapshot.tags:
            if any(word in tag.lower() for word in query_words):
                relevance += 0.3
        
        # Content matching
        snapshot_text = str(snapshot.data).lower()
        for word in query_words:
            if word in snapshot_text:
                relevance += 0.1
        
        return min(relevance, 1.0)  # Cap at 1.0
    
    async def _send_error_response(self, original_message, error_code: str, error_description: str):
        """Send error response to original sender."""
        error_response = self.protocol.create_error_response(
            original_message, error_code, error_description
        )
        await self.message_handler.send_message(error_response)


async def advanced_communication_demo():
    """Demonstrate advanced AI-to-AI communication features."""
    
    print("🤖 AI-Interlinq Advanced Communication Demo")
    print("=" * 60)
    
    # Setup agents
    shared_key = "advanced_ai_communication_key_2024"
    
    agent_alpha = IntelligentAgent("agent_alpha", shared_key)
    agent_beta = IntelligentAgent("agent_beta", shared_key)
    
    session_id = "advanced_session_001"
    
    # Generate tokens
    token_alpha = agent_alpha.token_manager.generate_token(session_id)
    token_beta = agent_beta.token_manager.generate_token(session_id)
    
    print(f"🔑 Agent Alpha token: {token_alpha[:20]}...")
    print(f"🔑 Agent Beta token: {token_beta[:20]}...")
    
    # Demo 1: Knowledge Learning and Sharing
    print(f"\n📚 Demo 1: Knowledge Learning and Sharing")
    print("-" * 40)
    
    # Agent Alpha learns a pattern
    learn_message = agent_alpha.protocol.create_message(
        recipient_id="agent_beta",
        message_type=MessageType.REQUEST,
        command="learn_pattern",
        data={
            "pattern_name": "fibonacci_sequence",
            "pattern_data": {
                "description": "Fibonacci sequence generation algorithm",
                "algorithm": "F(n) = F(n-1) + F(n-2)",
                "base_cases": {"F(0)": 0, "F(1)": 1},
                "examples": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
            },
            "context": {"learning_source": "mathematical_patterns", "difficulty": "intermediate"}
        },
        session_id=session_id,
        priority=Priority.HIGH
    )
    
    # Simulate message transmission and processing
    serialized = agent_alpha.serializer.serialize(learn_message)
    success, encrypted = agent_alpha.encryption.encrypt_message(serialized.decode('utf-8'))
    
    if success:
        await agent_beta.message_handler.receive_message(encrypted, encrypted=True)
        processed = await agent_beta.message_handler.process_messages(session_id)
        print(f"✅ Learning message processed: {processed} messages")
    
    await asyncio.sleep(0.1)  # Allow processing
    
    # Demo 2: Code Execution and Injection
    print(f"\n💻 Demo 2: Safe Code Execution")
    print("-" * 40)
    
    code_message = agent_beta.protocol.create_message(
        recipient_id="agent_alpha",
        message_type=MessageType.REQUEST,
        command="execute_code",
        data={
            "code": "sum([1, 2, 3, 4, 5]) * len(context.get('test_data', []))",
            "context": {
                "test_data": [10, 20, 30],
                "operation": "sum_and_multiply"
            }
        },
        session_id=session_id
    )
    
    serialized = agent_beta.serializer.serialize(code_message)
    success, encrypted = agent_beta.encryption.encrypt_message(serialized.decode('utf-8'))
    
    if success:
        await agent_alpha.message_handler.receive_message(encrypted, encrypted=True)
        processed = await agent_alpha.message_handler.process_messages(session_id)
        print(f"✅ Code execution processed: {processed} messages")
    
    await asyncio.sleep(0.1)
    
    # Demo 3: Memory Management
    print(f"\n🧠 Demo 3: Advanced Memory Management")
    print("-" * 40)
    
    memory_message = agent_alpha.protocol.create_message(
        recipient_id="agent_beta",
        message_type=MessageType.REQUEST,
        command="create_memory",
        data={
            "memory_data": {
                "conversation_summary": "Discussion about Fibonacci sequences and code execution",
                "key_insights": [
                    "Fibonacci patterns can be learned and applied",
                    "Safe code execution enables dynamic computation",
                    "Memory snapshots preserve important interactions"
                ],
                "participants": ["agent_alpha", "agent_beta"],
                "interaction_quality": "high"
            },
            "tags": ["conversation", "learning", "fibonacci", "collaboration"],
            "trigger": "conversation_end"
        },
        session_id=session_id
    )
    
    serialized = agent_alpha.serializer.serialize(memory_message)
    success, encrypted = agent_alpha.encryption.encrypt_message(serialized.decode('utf-8'))
    
    if success:
        await agent_beta.message_handler.receive_message(encrypted, encrypted=True)
        processed = await agent_beta.message_handler.process_messages(session_id)
        print(f"✅ Memory creation processed: {processed} messages")
    
    await asyncio.sleep(0.1)
    
    # Demo 4: Collaboration
    print(f"\n🤝 Demo 4: Agent Collaboration")
    print("-" * 40)
    
    collaboration_message = agent_beta.protocol.create_message(
        recipient_id="agent_alpha",
        message_type=MessageType.REQUEST,
        command="collaborate",
        data={
            "type": "joint_learning",
            "task_data": {
                "learning_data": {
                    "prime_numbers": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
                    "algorithm": "Sieve of Eratosthenes",
                    "complexity": "O(n log log n)"
                },
                "learning_type": "pattern"
            }
        },
        session_id=session_id,
        priority=Priority.HIGH
    )
    
    serialized = agent_beta.serializer.serialize(collaboration_message)
    success, encrypted = agent_beta.encryption.encrypt_message(serialized.decode('utf-8'))
    
    if success:
        await agent_alpha.message_handler.receive_message(encrypted, encrypted=True)
        processed = await agent_alpha.message_handler.process_messages(session_id)
        print(f"✅ Collaboration processed: {processed} messages")
    
    await asyncio.sleep(0.1)
    
    # Demo 5: Statistics and Performance Analysis
    print(f"\n📊 Demo 5: Statistics and Performance")
    print("-" * 40)
    
    stats_message = agent_alpha.protocol.create_message(
        recipient_id="agent_beta",
        message_type=MessageType.REQUEST,
        command="get_stats",
        data={},
        session_id=session_id
    )
    
    serialized = agent_alpha.serializer.serialize(stats_message)
    success, encrypted = agent_alpha.encryption.encrypt_message(serialized.decode('utf-8'))
    
    if success:
        await agent_beta.message_handler.receive_message(encrypted, encrypted=True)
        processed = await agent_beta.message_handler.process_messages(session_id)
        print(f"✅ Statistics request processed: {processed} messages")
    
    await asyncio.sleep(0.1)
    
    # Display final statistics
    print(f"\n📈 Final Performance Statistics")
    print("-" * 40)
    
    alpha_stats = agent_alpha.message_handler.get_statistics()
    beta_stats = agent_beta.message_handler.get_statistics()
    
    print(f"Agent Alpha - Sent: {alpha_stats['messages_sent']}, Received: {alpha_stats['messages_received']}")
    print(f"Agent Beta - Sent: {beta_stats['messages_sent']}, Received: {beta_stats['messages_received']}")
    
    # Memory statistics
    alpha_memory = agent_alpha.memory_system.get_memory_statistics()
    beta_memory = agent_beta.memory_system.get_memory_statistics()
    
    print(f"Agent Alpha Memory - Snapshots: {alpha_memory.get('snapshots', 0)}, Knowledge: {alpha_memory.get('knowledge_entries', 0)}")
    print(f"Agent Beta Memory - Snapshots: {beta_memory.get('snapshots', 0)}, Knowledge: {beta_memory.get('knowledge_entries', 0)}")
    
    print(f"\n✅ Advanced communication demo completed successfully!")


if __name__ == "__main__":
    print("🚀 Starting Advanced AI-Interlinq Demo...")
    asyncio.run(advanced_communication_demo())
    print(f"\n🎉 Demo completed successfully!")
