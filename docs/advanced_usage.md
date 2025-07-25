# Advanced Usage

Advanced features and patterns for AI-Interlinq with law.ai governance system integration.

## Table of Contents

1. [Advanced Learning Cycle Patterns](#advanced-learning-cycle-patterns)
2. [Complex Message Handling](#complex-message-handling)
3. [Performance Optimization](#performance-optimization)
4. [Security Hardening](#security-hardening)
5. [Governance Automation](#governance-automation)
6. [Distributed Deployments](#distributed-deployments)
7. [Custom Extensions](#custom-extensions)
8. [Production Patterns](#production-patterns)

## Advanced Learning Cycle Patterns

### Conditional Learning Cycles

Execute different learning paths based on conditions:

```python
import asyncio
from ai_interlinq.core.learning_cycle import LearningCycle
from ai_interlinq.core.pattern_detector import PatternDetector

async def conditional_learning_cycle(operation_type, data):
    """Execute learning cycle with conditional logic"""
    
    learning_cycle = LearningCycle()
    pattern_detector = PatternDetector()
    
    # Configure cycle based on operation type
    if operation_type == "critical":
        config = {
            "memory_loading_enabled": True,
            "pattern_detection_enabled": True,
            "governance_checks_enabled": True,
            "max_execution_time": 10.0
        }
    elif operation_type == "performance":
        config = {
            "memory_loading_enabled": False,  # Faster execution
            "pattern_detection_enabled": False,
            "governance_checks_enabled": False,
            "max_execution_time": 1.0
        }
    else:
        config = {}  # Default configuration
    
    # Execute with configuration
    result = await learning_cycle.execute_cycle(
        cause=f"conditional_operation_{operation_type}",
        input_data={
            "operation_type": operation_type,
            "data": data,
            "configuration": config
        },
        config=config
    )
    
    # Post-process based on patterns
    patterns = pattern_detector.analyze_snapshot_patterns(result)
    if patterns.get('requires_attention'):
        await escalate_for_review(result, patterns)
    
    return result

async def escalate_for_review(result, patterns):
    """Escalate concerning patterns for governance review"""
    
    from ai_interlinq.governance.voting_system import VotingSystem
    
    voting_system = VotingSystem()
    
    # Create urgent review proposal
    proposal = {
        "title": f"Pattern Review: {patterns.get('severity', 'UNKNOWN')}",
        "description": f"Systematic pattern detected in snapshot {result['snapshot_id']}",
        "law_id": "LAW-001",
        "proposed_changes": {
            "review_required": True,
            "pattern_data": patterns
        },
        "justification": "Automated pattern detection flagged for human review"
    }
    
    proposal_id = voting_system.create_proposal(proposal, "automated_system")
    print(f"🏛️ Escalated to governance: {proposal_id}")
```

### Chained Learning Cycles

Chain multiple learning cycles for complex operations:

```python
async def chained_learning_cycles():
    """Execute multiple related learning cycles in sequence"""
    
    learning_cycle = LearningCycle()
    snapshot_manager = SnapshotManager()
    
    # Phase 1: Data preparation
    phase1_result = await learning_cycle.execute_cycle(
        cause="chained_operation_phase1",
        input_data={
            "phase": "data_preparation",
            "operation": "complex_ai_task"
        }
    )
    
    # Phase 2: Processing (using phase 1 results)
    phase2_result = await learning_cycle.execute_cycle(
        cause="chained_operation_phase2",
        input_data={
            "phase": "processing",
            "previous_snapshot": phase1_result['snapshot_id'],
            "input_from_phase1": phase1_result['output']
        }
    )
    
    # Phase 3: Finalization
    phase3_result = await learning_cycle.execute_cycle(
        cause="chained_operation_phase3",
        input_data={
            "phase": "finalization",
            "previous_snapshots": [
                phase1_result['snapshot_id'],
                phase2_result['snapshot_id']
            ],
            "combined_results": {
                "phase1": phase1_result['output'],
                "phase2": phase2_result['output']
            }
        }
    )
    
    # Create master snapshot linking all phases
    master_snapshot = {
        "context": "Chained learning cycle operation completed",
        "input": {
            "operation": "complex_ai_task",
            "phases": ["data_preparation", "processing", "finalization"]
        },
        "action": "Execute multi-phase learning cycle chain",
        "applied_law": "LAW-001",
        "reaction": "All phases completed successfully",
        "output": {
            "phase_snapshots": [
                phase1_result['snapshot_id'],
                phase2_result['snapshot_id'],
                phase3_result['snapshot_id']
            ],
            "final_result": phase3_result['output'],
            "chain_completed": True
        },
        "deviation": None,
        "ai_signature": "chained_operation_controller"
    }
    
    master_snapshot_result = snapshot_manager.create_snapshot(master_snapshot)
    
    return {
        "master_snapshot": master_snapshot_result,
        "phase_results": [phase1_result, phase2_result, phase3_result]
    }
```

## Complex Message Handling

### Batch Message Processing

Process multiple messages with law.ai compliance:

```python
from ai_interlinq import MessageHandler, TokenManager, EncryptionHandler
from ai_interlinq.core.communication_protocol import MessageType, Priority

class BatchMessageProcessor:
    """Process multiple messages efficiently with LAW-001 compliance"""
    
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.learning_cycle = LearningCycle()
        self.token_manager = TokenManager()
        self.encryption = EncryptionHandler()
        self.message_handler = MessageHandler(agent_id, self.token_manager, self.encryption)
        
    async def process_message_batch(self, messages, batch_config=None):
        """Process a batch of messages with learning cycle compliance"""
        
        batch_id = f"batch_{int(time.time())}"
        
        # Execute learning cycle for batch processing
        batch_result = await self.learning_cycle.execute_cycle(
            cause="batch_message_processing",
            input_data={
                "batch_id": batch_id,
                "message_count": len(messages),
                "batch_config": batch_config or {},
                "agent_id": self.agent_id
            }
        )
        
        results = []
        for i, message in enumerate(messages):
            try:
                # Process individual message
                message_result = await self._process_single_message(
                    message, batch_id, i, batch_result['snapshot_id']
                )
                results.append(message_result)
                
            except Exception as e:
                # Handle individual message failure
                error_result = await self._handle_message_error(
                    message, e, batch_id, i
                )
                results.append(error_result)
        
        # Complete batch processing cycle
        completion_result = await self.learning_cycle.execute_cycle(
            cause="batch_processing_completion",
            input_data={
                "batch_id": batch_id,
                "processed_count": len([r for r in results if r['success']]),
                "failed_count": len([r for r in results if not r['success']]),
                "batch_snapshot": batch_result['snapshot_id']
            }
        )
        
        return {
            "batch_id": batch_id,
            "batch_snapshot": batch_result['snapshot_id'],
            "completion_snapshot": completion_result['snapshot_id'],
            "results": results,
            "summary": {
                "total": len(messages),
                "successful": len([r for r in results if r['success']]),
                "failed": len([r for r in results if not r['success']])
            }
        }
    
    async def _process_single_message(self, message, batch_id, index, batch_snapshot):
        """Process a single message within a batch"""
        
        # Execute learning cycle for individual message
        message_result = await self.learning_cycle.execute_cycle(
            cause="batch_message_individual",
            input_data={
                "batch_id": batch_id,
                "message_index": index,
                "message_id": message.get('header', {}).get('message_id'),
                "batch_snapshot": batch_snapshot
            }
        )
        
        # Process the message
        success = await self.message_handler.send_message(message)
        
        return {
            "success": success,
            "message_id": message.get('header', {}).get('message_id'),
            "snapshot_id": message_result['snapshot_id'],
            "index": index
        }
    
    async def _handle_message_error(self, message, error, batch_id, index):
        """Handle error in message processing"""
        
        error_result = await self.learning_cycle.execute_cycle(
            cause="batch_message_error",
            input_data={
                "batch_id": batch_id,
                "message_index": index,
                "error": str(error),
                "message_id": message.get('header', {}).get('message_id')
            }
        )
        
        return {
            "success": False,
            "error": str(error),
            "message_id": message.get('header', {}).get('message_id'),
            "snapshot_id": error_result['snapshot_id'],
            "index": index
        }
```

### Message Routing with Governance

Implement intelligent message routing with governance controls:

```python
class GovernanceAwareRouter:
    """Message router with governance integration"""
    
    def __init__(self):
        self.learning_cycle = LearningCycle()
        self.voting_system = VotingSystem()
        self.pattern_detector = PatternDetector()
        self.routes = {}
        
    async def register_route(self, pattern, handler, governance_level="NORMAL"):
        """Register a message route with governance level"""
        
        # Execute learning cycle for route registration
        registration_result = await self.learning_cycle.execute_cycle(
            cause="route_registration",
            input_data={
                "pattern": pattern,
                "handler": handler.__name__,
                "governance_level": governance_level
            }
        )
        
        # Check if governance approval required
        if governance_level == "CRITICAL":
            proposal = {
                "title": f"Register critical route: {pattern}",
                "description": f"Register new message route with handler {handler.__name__}",
                "law_id": "LAW-001",
                "proposed_changes": {
                    "new_route": {
                        "pattern": pattern,
                        "handler": handler.__name__,
                        "governance_level": governance_level
                    }
                },
                "justification": "Critical route requires governance approval"
            }
            
            proposal_id = self.voting_system.create_proposal(proposal, "route_manager")
            
            # Wait for approval (in production, this would be asynchronous)
            print(f"🏛️ Route registration requires governance approval: {proposal_id}")
            return False
        
        # Register route
        self.routes[pattern] = {
            "handler": handler,
            "governance_level": governance_level,
            "registration_snapshot": registration_result['snapshot_id']
        }
        
        return True
    
    async def route_message(self, message):
        """Route message with governance compliance"""
        
        # Find matching route
        route_pattern = self._find_route_pattern(message)
        if not route_pattern:
            return await self._handle_unrouted_message(message)
        
        route_info = self.routes[route_pattern]
        
        # Execute learning cycle for routing
        routing_result = await self.learning_cycle.execute_cycle(
            cause="message_routing",
            input_data={
                "message_id": message['header']['message_id'],
                "route_pattern": route_pattern,
                "handler": route_info['handler'].__name__,
                "governance_level": route_info['governance_level']
            }
        )
        
        # Check for routing patterns
        patterns = self.pattern_detector.analyze_snapshot_patterns(routing_result)
        if patterns.get('deviation_detected'):
            await self._handle_routing_deviation(message, patterns, routing_result)
        
        # Execute handler
        try:
            result = await route_info['handler'](message)
            
            # Log successful routing
            completion_result = await self.learning_cycle.execute_cycle(
                cause="message_routing_completion",
                input_data={
                    "message_id": message['header']['message_id'],
                    "routing_snapshot": routing_result['snapshot_id'],
                    "success": True,
                    "result": result
                }
            )
            
            return {
                "success": True,
                "result": result,
                "routing_snapshot": routing_result['snapshot_id'],
                "completion_snapshot": completion_result['snapshot_id']
            }
            
        except Exception as e:
            # Handle routing error
            error_result = await self.learning_cycle.execute_cycle(
                cause="message_routing_error",
                input_data={
                    "message_id": message['header']['message_id'],
                    "routing_snapshot": routing_result['snapshot_id'],
                    "error": str(e)
                }
            )
            
            return {
                "success": False,
                "error": str(e),
                "routing_snapshot": routing_result['snapshot_id'],
                "error_snapshot": error_result['snapshot_id']
            }
    
    def _find_route_pattern(self, message):
        """Find matching route pattern for message"""
        command = message.get('payload', {}).get('command', '')
        
        # Simple pattern matching (extend as needed)
        for pattern in self.routes:
            if pattern in command or pattern == "*":
                return pattern
        
        return None
    
    async def _handle_unrouted_message(self, message):
        """Handle message with no matching route"""
        
        result = await self.learning_cycle.execute_cycle(
            cause="unrouted_message",
            input_data={
                "message_id": message['header']['message_id'],
                "command": message.get('payload', {}).get('command'),
                "available_routes": list(self.routes.keys())
            }
        )
        
        return {
            "success": False,
            "error": "No matching route found",
            "snapshot_id": result['snapshot_id']
        }
    
    async def _handle_routing_deviation(self, message, patterns, routing_result):
        """Handle deviation in routing patterns"""
        
        deviation_result = await self.learning_cycle.execute_cycle(
            cause="routing_deviation_detected",
            input_data={
                "message_id": message['header']['message_id'],
                "patterns": patterns,
                "routing_snapshot": routing_result['snapshot_id'],
                "severity": patterns.get('severity', 'UNKNOWN')
            }
        )
        
        if patterns.get('severity') == 'HIGH':
            # Escalate to governance
            proposal = {
                "title": "Routing Pattern Deviation - High Severity",
                "description": f"High severity routing deviation detected for message {message['header']['message_id']}",
                "law_id": "LAW-001",
                "proposed_changes": {
                    "investigate_routing": True,
                    "deviation_data": patterns
                },
                "justification": "High severity deviation requires immediate review"
            }
            
            proposal_id = self.voting_system.create_proposal(proposal, "routing_monitor")
            print(f"🚨 High severity routing deviation escalated: {proposal_id}")
```

## Performance Optimization

### Caching Strategies

Implement intelligent caching with law.ai compliance:

```python
from functools import wraps
import hashlib
import json

class LAWCompliantCache:
    """Caching system that maintains LAW-001 compliance"""
    
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.learning_cycle = LearningCycle()
        self.pattern_detector = PatternDetector()
        
    def cache_with_compliance(self, ttl=3600):
        """Decorator for caching function results with LAW-001 compliance"""
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Check cache first
                cached_result = await self._check_cache(cache_key, func.__name__)
                if cached_result:
                    return cached_result['data']
                
                # Execute function with learning cycle
                execution_result = await self.learning_cycle.execute_cycle(
                    cause="cached_function_execution",
                    input_data={
                        "function": func.__name__,
                        "cache_key": cache_key,
                        "cache_hit": False,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                )
                
                # Execute actual function
                result = await func(*args, **kwargs)
                
                # Store in cache with compliance data
                await self._store_in_cache(
                    cache_key, result, ttl, execution_result['snapshot_id']
                )
                
                return result
            
            return wrapper
        return decorator
    
    async def _check_cache(self, cache_key, function_name):
        """Check cache with compliance logging"""
        
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            
            # Check if expired
            if time.time() > cached_item['expires_at']:
                del self.cache[cache_key]
                return None
            
            # Log cache hit
            hit_result = await self.learning_cycle.execute_cycle(
                cause="cache_hit",
                input_data={
                    "function": function_name,
                    "cache_key": cache_key,
                    "cached_at": cached_item['cached_at'],
                    "original_snapshot": cached_item['snapshot_id']
                }
            )
            
            return cached_item
        
        return None
    
    async def _store_in_cache(self, cache_key, data, ttl, snapshot_id):
        """Store data in cache with compliance tracking"""
        
        # Clean cache if needed
        if len(self.cache) >= self.max_size:
            await self._cleanup_cache()
        
        # Store with metadata
        self.cache[cache_key] = {
            "data": data,
            "cached_at": time.time(),
            "expires_at": time.time() + ttl,
            "snapshot_id": snapshot_id,
            "access_count": 0
        }
        
        # Log caching action
        cache_result = await self.learning_cycle.execute_cycle(
            cause="cache_store",
            input_data={
                "cache_key": cache_key,
                "ttl": ttl,
                "data_size": len(str(data)),
                "original_snapshot": snapshot_id
            }
        )
    
    async def _cleanup_cache(self):
        """Clean up expired cache entries"""
        
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if current_time > item['expires_at']
        ]
        
        # Remove expired items
        for key in expired_keys:
            del self.cache[key]
        
        # If still too large, remove least recently used
        if len(self.cache) >= self.max_size:
            # Sort by access count and remove oldest
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: (x[1]['access_count'], x[1]['cached_at'])
            )
            
            items_to_remove = len(self.cache) - self.max_size + 1
            for i in range(items_to_remove):
                key = sorted_items[i][0]
                del self.cache[key]
        
        # Log cleanup
        cleanup_result = await self.learning_cycle.execute_cycle(
            cause="cache_cleanup",
            input_data={
                "expired_count": len(expired_keys),
                "current_size": len(self.cache),
                "max_size": self.max_size
            }
        )
    
    def _generate_cache_key(self, func_name, args, kwargs):
        """Generate deterministic cache key"""
        
        key_data = {
            "function": func_name,
            "args": str(args),
            "kwargs": sorted(kwargs.items())
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

# Usage example
cache = LAWCompliantCache()

@cache.cache_with_compliance(ttl=1800)
async def expensive_ai_operation(data, config):
    """Expensive AI operation that benefits from caching"""
    
    # Simulate expensive computation
    await asyncio.sleep(2)
    
    # Process data
    result = {
        "processed_data": f"processed_{data}",
        "config": config,
        "timestamp": time.time()
    }
    
    return result
```

### Async Optimization Patterns

Optimize async operations with law.ai compliance:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncOptimizer:
    """Optimize async operations while maintaining LAW-001 compliance"""
    
    def __init__(self, max_workers=10):
        self.learning_cycle = LearningCycle()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
        
    async def parallel_learning_cycles(self, operations):
        """Execute multiple learning cycles in parallel"""
        
        # Start parallel execution tracking
        parallel_result = await self.learning_cycle.execute_cycle(
            cause="parallel_learning_cycles_start",
            input_data={
                "operation_count": len(operations),
                "max_workers": self.executor._max_workers
            }
        )
        
        # Execute operations in parallel with semaphore control
        async def execute_with_semaphore(operation):
            async with self.semaphore:
                return await self._execute_single_operation(
                    operation, parallel_result['snapshot_id']
                )
        
        # Run all operations
        results = await asyncio.gather(
            *[execute_with_semaphore(op) for op in operations],
            return_exceptions=True
        )
        
        # Complete parallel execution tracking
        completion_result = await self.learning_cycle.execute_cycle(
            cause="parallel_learning_cycles_completion",
            input_data={
                "parallel_snapshot": parallel_result['snapshot_id'],
                "completed_count": len([r for r in results if not isinstance(r, Exception)]),
                "failed_count": len([r for r in results if isinstance(r, Exception)]),
                "results_summary": self._summarize_results(results)
            }
        )
        
        return {
            "parallel_snapshot": parallel_result['snapshot_id'],
            "completion_snapshot": completion_result['snapshot_id'],
            "results": results,
            "summary": {
                "total": len(operations),
                "successful": len([r for r in results if not isinstance(r, Exception)]),
                "failed": len([r for r in results if isinstance(r, Exception)])
            }
        }
    
    async def _execute_single_operation(self, operation, parent_snapshot):
        """Execute single operation with learning cycle"""
        
        result = await self.learning_cycle.execute_cycle(
            cause="parallel_operation_individual",
            input_data={
                "operation": operation,
                "parent_snapshot": parent_snapshot,
                "worker_id": asyncio.current_task().get_name()
            }
        )
        
        # Execute the actual operation
        if callable(operation):
            return await operation()
        else:
            return operation
    
    def _summarize_results(self, results):
        """Create summary of parallel execution results"""
        
        return {
            "success_rate": len([r for r in results if not isinstance(r, Exception)]) / len(results),
            "error_types": [type(r).__name__ for r in results if isinstance(r, Exception)],
            "execution_pattern": "parallel"
        }
    
    async def optimized_message_pipeline(self, messages, batch_size=10):
        """Process messages in optimized batches with law.ai compliance"""
        
        pipeline_result = await self.learning_cycle.execute_cycle(
            cause="optimized_message_pipeline",
            input_data={
                "total_messages": len(messages),
                "batch_size": batch_size,
                "pipeline_strategy": "batched_parallel"
            }
        )
        
        # Split messages into batches
        batches = [
            messages[i:i + batch_size]
            for i in range(0, len(messages), batch_size)
        ]
        
        all_results = []
        
        # Process batches sequentially, messages within batch in parallel
        for batch_idx, batch in enumerate(batches):
            batch_result = await self.learning_cycle.execute_cycle(
                cause="pipeline_batch_processing",
                input_data={
                    "batch_index": batch_idx,
                    "batch_size": len(batch),
                    "pipeline_snapshot": pipeline_result['snapshot_id']
                }
            )
            
            # Process batch in parallel
            batch_results = await asyncio.gather(
                *[self._process_message_optimized(msg, batch_result['snapshot_id']) 
                  for msg in batch],
                return_exceptions=True
            )
            
            all_results.extend(batch_results)
        
        # Complete pipeline
        completion_result = await self.learning_cycle.execute_cycle(
            cause="pipeline_completion",
            input_data={
                "pipeline_snapshot": pipeline_result['snapshot_id'],
                "total_processed": len(all_results),
                "batch_count": len(batches)
            }
        )
        
        return {
            "pipeline_snapshot": pipeline_result['snapshot_id'],
            "completion_snapshot": completion_result['snapshot_id'],
            "results": all_results,
            "batches_processed": len(batches)
        }
    
    async def _process_message_optimized(self, message, batch_snapshot):
        """Process single message with optimization"""
        
        # Use thread pool for CPU-intensive work if needed
        loop = asyncio.get_event_loop()
        
        # CPU-intensive processing in thread pool
        processed_message = await loop.run_in_executor(
            self.executor,
            self._cpu_intensive_processing,
            message
        )
        
        # I/O operations remain async
        result = await self.learning_cycle.execute_cycle(
            cause="optimized_message_processing",
            input_data={
                "message_id": message.get('header', {}).get('message_id'),
                "batch_snapshot": batch_snapshot,
                "optimization": "thread_pool_cpu"
            }
        )
        
        return {
            "message_id": message.get('header', {}).get('message_id'),
            "processed": processed_message,
            "snapshot_id": result['snapshot_id']
        }
    
    def _cpu_intensive_processing(self, message):
        """CPU-intensive processing that runs in thread pool"""
        
        # Simulate CPU-intensive work
        import hashlib
        
        data = str(message)
        for _ in range(1000):
            data = hashlib.sha256(data.encode()).hexdigest()
        
        return {
            "original": message,
            "processed_hash": data,
            "cpu_work_completed": True
        }
```

This advanced usage documentation provides sophisticated patterns for using AI-Interlinq with law.ai governance while maintaining high performance and compliance. The patterns shown demonstrate how to handle complex scenarios while preserving the mandatory LAW-001 learning cycle requirements.

---

**Advanced Usage Guide** • Version 1.1.0 • LAW-001 Compliant ✅

These advanced patterns enable sophisticated AI communication systems while maintaining strict governance compliance and high performance standards.