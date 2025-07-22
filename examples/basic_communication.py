"""
Basic AI-Interlinq Communication Example
Demonstrates simple AI-to-AI communication using shared tokens.
"""

import asyncio
import time
from ai_interlinq import TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler
from ai_interlinq.core.communication_protocol import MessageType, Priority


async def basic_communication_example():
    """Demonstrate basic communication between two AI agents."""
    
    print("🤖 AI-Interlinq Basic Communication Example")
    print("=" * 50)
    
    # Setup shared encryption key
    shared_key = "ai_communication_secret_key_2024"
    print(f"📡 Using shared key: {shared_key[:10]}...")
    
    # Initialize components for Agent A
    token_manager_a = TokenManager(default_ttl=3600)
    encryption_a = EncryptionHandler(shared_key)
    protocol_a = CommunicationProtocol("agent_a")
    message_handler_a = MessageHandler("agent_a", token_manager_a, encryption_a)
    
    # Initialize components for Agent B
    token_manager_b = TokenManager(default_ttl=3600)
    encryption_b = EncryptionHandler(shared_key)
    protocol_b = CommunicationProtocol("agent_b")
    message_handler_b = MessageHandler("agent_b", token_manager_b, encryption_b)
    
    # Create communication session
    session_id = "session_001"
    
    # Generate tokens for both agents
    token_a = token_manager_a.generate_token(session_id)
    token_b = token_manager_b.generate_token(session_id)
    
    print(f"🔑 Generated token for Agent A: {token_a[:20]}...")
    print(f"🔑 Generated token for Agent B: {token_b[:20]}...")
    
    # Register message handlers
    async def handle_greeting(message):
        print(f"👋 Agent B received greeting: {message.payload.data['text']}")
        
        # Send response
        response = protocol_b.create_message(
            recipient_id=message.header.sender_id,
            message_type=MessageType.RESPONSE,
            command="greeting_response",
            data={
                "text": "Hello Agent A! Nice to communicate with you!",
                "original_message_id": message.header.message_id
            },
            session_id=session_id
        )
        
        await message_handler_b.send_message(response)
    
    async def handle_greeting_response(message):
        print(f"💬 Agent A received response: {message.payload.data['text']}")
    
    # Register handlers
    message_handler_b.register_command_handler("greeting", handle_greeting)
    message_handler_a.register_command_handler("greeting_response", handle_greeting_response)
    
    # Create and send a greeting message from Agent A to Agent B
    greeting_message = protocol_a.create_message(
        recipient_id="agent_b",
        message_type=MessageType.REQUEST,
        command="greeting",
        data={
            "text": "Hello Agent B! This is Agent A speaking.",
            "timestamp": time.time()
        },
        session_id=session_id,
        priority=Priority.NORMAL
    )
    
    print(f"\n📤 Agent A sending greeting message...")
    
    # Simulate message transmission (normally would go over network)
    serialized = protocol_a.serialize_message(greeting_message)
    success, encrypted = encryption_a.encrypt_message(serialized)
    
    if success:
        print(f"🔒 Message encrypted successfully")
        
        # Agent B receives the message
        await message_handler_b.receive_message(encrypted, encrypted=True)
        
        # Process messages for Agent B
        processed = await message_handler_b.process_messages(session_id)
        print(f"⚡ Agent B processed {processed} messages")
        
        # Small delay to simulate async processing
        await asyncio.sleep(0.1)
        
        # Process response for Agent A
        # In a real scenario, Agent A would receive the response over network
        # For this example, we'll simulate it
        
        print(f"\n📊 Communication Statistics:")
        stats_a = message_handler_a.get_statistics()
        stats_b = message_handler_b.get_statistics()
        
        print(f"   Agent A - Sent: {stats_a['messages_sent']}, Received: {stats_a['messages_received']}")
        print(f"   Agent B - Sent: {stats_b['messages_sent']}, Received: {stats_b['messages_received']}")
        
    else:
        print(f"❌ Failed to encrypt message: {encrypted}")
    
    print(f"\n✅ Basic communication example completed!")


async def performance_test():
    """Test communication performance."""
    
    print(f"\n🚀 Performance Test")
    print("=" * 30)
    
    # Setup
    shared_key = "performance_test_key"
    token_manager = TokenManager()
    encryption = EncryptionHandler(shared_key)
    protocol = CommunicationProtocol("test_agent")
    
    session_id = "perf_test"
    token = token_manager.generate_token(session_id)
    
    # Test message creation speed
    start_time = time.time()
    messages = []
    
    for i in range(1000):
        message = protocol.create_message(
            recipient_id="target_agent",
            message_type=MessageType.REQUEST,
            command="test_command",
            data={"index": i, "payload": "x" * 100},  # 100 char payload
            session_id=session_id
        )
        messages.append(message)
    
    creation_time = time.time() - start_time
    print(f"📈 Created 1000 messages in {creation_time:.4f}s ({1000/creation_time:.0f} msg/s)")
    
    # Test serialization speed
    start_time = time.time()
    serialized_messages = []
    
    for message in messages:
        serialized = protocol.serialize_message(message)
        serialized_messages.append(serialized)
    
    serialization_time = time.time() - start_time
    print(f"📈 Serialized 1000 messages in {serialization_time:.4f}s ({1000/serialization_time:.0f} msg/s)")
    
    # Test encryption speed
    start_time = time.time()
    encrypted_messages = []
    
    for serialized in serialized_messages:
        success, encrypted = encryption.encrypt_message(serialized)
        if success:
            encrypted_messages.append(encrypted)
    
    encryption_time = time.time() - start_time
    print(f"🔒 Encrypted {len(encrypted_messages)} messages in {encryption_time:.4f}s ({len(encrypted_messages)/encryption_time:.0f} msg/s)")
    
    # Test decryption speed
    start_time = time.time()
    decrypted_count = 0
    
    for encrypted in encrypted_messages[:100]:  # Test subset for speed
        success, decrypted = encryption.decrypt_message(encrypted)
        if success:
            decrypted_count += 1
    
    decryption_time = time.time() - start_time
    print(f"🔓 Decrypted {decrypted_count} messages in {decryption_time:.4f}s ({decrypted_count/decryption_time:.0f} msg/s)")
    
    # Average message size
    avg_size = sum(len(s.encode()) for s in serialized_messages) / len(serialized_messages)
    print(f"📏 Average message size: {avg_size:.0f} bytes")


if __name__ == "__main__":
    print("🚀 Starting AI-Interlinq Examples...")
    
    # Run basic communication example
    asyncio.run(basic_communication_example())
    
    # Run performance test
    asyncio.run(performance_test())
    
    print(f"\n🎉 All examples completed successfully!")
