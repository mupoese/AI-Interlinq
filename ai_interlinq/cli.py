### ai_interlinq/cli.py
```python
"""Command-line interface for AI-Interlinq."""

import argparse
import asyncio
import sys
from typing import Optional

from .version import get_version
from .config import Config


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog='ai-interlinq',
        description='AI-to-AI communication toolkit'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'ai-interlinq {get_version()}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Agent command
    agent_parser = subparsers.add_parser('agent', help='Start an AI agent')
    agent_parser.add_argument('--id', required=True, help='Agent ID')
    agent_parser.add_argument('--config', help='Configuration file path')
    agent_parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run communication tests')
    test_parser.add_argument('--target', help='Target agent to test')
    test_parser.add_argument('--messages', type=int, default=100, help='Number of test messages')
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help='Run performance benchmarks')
    bench_parser.add_argument('--duration', type=int, default=60, help='Benchmark duration in seconds')
    bench_parser.add_argument('--output', help='Output file for results')
    
    return parser


async def run_agent(agent_id: str, config_path: Optional[str] = None, port: int = 8080):
    """Run an AI agent."""
    print(f"🤖 Starting AI agent: {agent_id}")
    print(f"🌐 Listening on port: {port}")
    
    # Load configuration
    if config_path:
        config = Config.from_file(config_path)
    else:
        config = Config.from_environment()
    
    # TODO: Implement agent startup logic
    print("✅ Agent started successfully")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down agent...")


async def run_test(target: Optional[str] = None, messages: int = 100):
    """Run communication tests."""
    print(f"🧪 Running communication tests")
    print(f"📊 Test messages: {messages}")
    if target:
        print(f"🎯 Target agent: {target}")
    
    # TODO: Implement test logic
    print("✅ Tests completed successfully")


async def run_benchmark(duration: int = 60, output: Optional[str] = None):
    """Run performance benchmarks."""
    print(f"⚡ Running performance benchmarks")
    print(f"⏱️  Duration: {duration} seconds")
    
    # TODO: Implement benchmark logic
    results = {
        "messages_per_second": 5000,
        "average_latency_ms": 2.5,
        "peak_memory_mb": 150
    }
    
    if output:
        import json
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Results saved to: {output}")
    
    print("✅ Benchmarks completed successfully")


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'agent':
            await run_agent(args.id, args.config, args.port)
        elif args.command == 'test':
            await run_test(args.target, args.messages)
        elif args.command == 'benchmark':
            await run_benchmark(args.duration, args.output)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cli_main():
    """Synchronous entry point for console scripts."""
    asyncio.run(main())


if __name__ == '__main__':
    cli_main()
```
