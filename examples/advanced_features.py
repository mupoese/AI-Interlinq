# examples/advanced_features.py
"""Advanced features demonstration for AI-Interlinq."""

import asyncio
import time
from ai_interlinq import TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler
from ai_interlinq.core.communication_protocol import MessageType, Priority
from ai_interlinq.transport.websocket import WebSocketTransport, TransportConfig
from ai_interlinq.core.connection_manager import ConnectionManager
from ai_interlinq.plugins.load_balancer import LoadBalancer, LoadBalancingStrategy
from ai_interlinq.plugins.rate_limiter import RateLimiter, RateLimitConfig
from ai_interlinq.plugins.metrics import MetricsCollector
from ai_interlinq.utils.performance import PerformanceMonitor


async def advanced_communication_demo():
    """Demonstrate advanced AI-Interlinq features."""
    
    print("🚀 AI-Interlinq Advanced Features Demo")
    print("=" * 50)
    
    # Setup components
    shared_key = "advanced_demo_key_2024"
    
    # Agent A setup
    token_manager_a = TokenManager(default_ttl=3600)
    encryption_a = EncryptionHandler(shared_key)
    protocol_a = CommunicationProtocol("advanced_agent_a")
    message_handler_a = MessageHandler("advanced_agent_a", token_manager_a, encryption_a)
    
    # Agent B setup
    token_manager_b = TokenManager(default_ttl=3600)
    encryption_b = EncryptionHandler(shared_key)
    protocol_b = CommunicationProtocol("advanced_agent_b")
    message_handler_b = MessageHandler("advanced_agent_b", token_manager_b, encryption_b)
    
    # Setup WebSocket transport
    config = TransportConfig(host="localhost", port=8080)
    transport_a = WebSocketTransport(config)
    transport_a.set_message_handler(message_handler_a.receive_message)
    
    # Setup connection manager
    conn_manager = ConnectionManager(transport_a, "advanced_agent_a")
    await conn_manager.start()
    
    # Setup load balancer
    load_balancer = LoadBalancer(LoadBalancingStrategy.WEIGHTED_RANDOM)
    load_balancer.add_backend("agent_b_1", "localhost:8081", weight=1.0)
    load_balancer.add_backend("agent_b_2", "localhost:8082", weight=2.0)
    load_balancer.add_backend("agent_b_3", "localhost:8083", weight=1.5)
    
    # Setup rate limiter
    rate_limiter = RateLimiter()
    rate_limiter.set_agent_rate_limit(
        "advanced_agent_a",
        RateLimitConfig(requests_per_second=10.0, burst_size=20)
    )
    
    # Setup metrics collector
    metrics = MetricsCollector()
    
    # Setup performance monitor
    perf_monitor = PerformanceMonitor()
    
    print("✅ All components initialized")
    
    # Demo 1: Load-balanced message sending
    print("\n📡 Demo 1: Load-balanced Message Sending")
    
    for i in range(5):
        backend = load_balancer.select_backend()
        if backend:
            print(f"   Selected backend: {backend.agent_id} (weight: {backend.weight})")
            
            # Simulate response time
            response_time = 0.1 + (i * 0.02)
            load_balancer.update_backend_stats(backend.agent_id, response_time, True)
            
            # Update metrics
            metrics.increment_counter("messages_sent", tags={"backend": backend.agent_id})
            metrics.record_histogram("response_time", response_time, tags={"backend": backend.agent_id})
    
    # Demo 2: Rate limiting
    print("\n⏱️  Demo 2: Rate Limiting")
    
    allowed_count = 0
    denied_count = 0
    
    for i in range(15):  # Try to send 15 requests (limit is 10/sec)
        is_allowed = await rate_limiter.check_rate_limit("advanced_agent_a")
        if is_allowed:
            allowed_count += 1
            print(f"   Request {i+1}: ✅ Allowed")
        else:
            denied_count += 1
            print(f"   Request {i+1}: ❌ Rate limited")
    
    print(f"   Summary: {allowed_count} allowed, {denied_count} denied")
    
    # Demo 3: Performance monitoring
    print("\n📊 Demo 3: Performance Monitoring")
    
    # Simulate some operations
    for i in range(10):
        timer_id = perf_monitor.start_timer("message_processing")
        
        # Simulate work
        await asyncio.sleep(0.01)
        
        duration = perf_monitor.end_timer(timer_id)
        print(f"   Operation {i+1}: {duration*1000:.2f}ms")
    
    # Get performance stats
    stats = perf_monitor.get_metric_stats("message_processing_duration")
    if stats:
        print(f"   Average: {stats['mean']*1000:.2f}ms")
        print(f"   Min: {stats['min']*1000:.2f}ms")
        print(f"   Max: {stats['max']*1000:.2f}ms")
    
    # Demo 4: Advanced message patterns
    print("\n🔄 Demo 4: Advanced Message Patterns")
    
    session_id = "advanced_demo_session"
    
    # Request-Response pattern
    print("   Testing request-response pattern...")
    
    async def handle_data_request(message):
        """Handle data request."""
        print(f"   📥 Received data request: {message.payload.data}")
        
        # Send response
        response = protocol_b.create_message(
            recipient_id=message.header.sender_id,
            message_type=MessageType.RESPONSE,
            command="data_response",
            data={
                "processed_data": f"Processed: {message.payload.data['query']}",
                "timestamp": time.time(),
                "original_message_id": message.header.message_id
            },
            session_id=message.header.session_id
        )
        
        await message_handler_b.send_message(response)
    
    message_handler_b.register_command_handler("data_request", handle_data_request)
    
    # Create and send request
    request = protocol_a.create_message(
        recipient_id="advanced_agent_b",
        message_type=MessageType.REQUEST,
        command="data_request",
        data={"query": "get_user_data", "user_id": "12345"},
        session_id=session_id,
        priority=Priority.HIGH
    )
    
    # Use request-response pattern
    response = await message_handler_a.send_request_and_wait_response(request, timeout=5.0)
    
    if response:
        print(f"   📤 Received response: {response.payload.data['processed_data']}")
    else:
        print("   ❌ Request timed out")
    
    # Demo 5: Metrics export
    print("\n📈 Demo 5: Metrics Export")
    
    # Add some more metrics
    metrics.set_gauge("active_connections", 5)
    metrics.set_gauge("memory_usage_mb", 128.5)
    metrics.increment_counter("total_requests", 100)
    
    # Export in Prometheus format
    prometheus_metrics = metrics.export_prometheus_format()
    print("   Prometheus format export:")
    print("   " + "\n   ".join(prometheus_metrics.split("\n")[:10]) + "...")
    
    # Get metrics summary
    summary = metrics.get_metrics_summary()
    print(f"   Metrics summary: {summary}")
    
    # Cleanup
    await conn_manager.stop()
    
    print("\n✅ Advanced features demo completed!")


async def distributed_setup_demo():
    """Demonstrate distributed AI agent setup."""
    
    print("\n🌐 Distributed Setup Demo")
    print("=" * 30)
    
    # This would typically involve multiple processes/containers
    # For demo purposes, we'll simulate the setup
    
    agents = ["ai_agent_1", "ai_agent_2", "ai_agent_3"]
    load_balancer = LoadBalancer(LoadBalancingStrategy.LEAST_CONNECTIONS)
    
    # Register agents with load balancer
    for i, agent_id in enumerate(agents):
        address = f"localhost:{8080 + i}"
        load_balancer.add_backend(agent_id, address)
        print(f"   Registered {agent_id} at {address}")
    
    # Simulate traffic distribution
    print("\n   Simulating traffic distribution:")
    
    for i in range(10):
        backend = load_balancer.select_backend()
        if backend:
            load_balancer.increment_connections(backend.agent_id)
            print(f"   Request {i+1} -> {backend.agent_id} (connections: {backend.active_connections})")
            
            # Simulate request completion
            await asyncio.sleep(0.1)
            load_balancer.decrement_connections(backend.agent_id)
    
    # Show final stats
    stats = load_balancer.get_backend_stats()
    print("\n   Final backend statistics:")
    for agent_id, stat in stats.items():
        print(f"   {agent_id}: {stat}")
    
    print("\n✅ Distributed setup demo completed!")


if __name__ == "__main__":
    print("🎯 Starting AI-Interlinq Advanced Demos...")
    
    # Run advanced communication demo
    asyncio.run(advanced_communication_demo())
    
    # Run distributed setup demo
    asyncio.run(distributed_setup_demo())
    
    print("\n🎉 All advanced demos completed successfully!")
