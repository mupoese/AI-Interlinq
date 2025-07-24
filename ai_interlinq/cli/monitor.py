# ai_interlinq/cli/monitor.py
"""
Monitor CLI Command for AI-Interlinq
Real-time monitoring and health checking utilities.

File: ai_interlinq/cli/monitor.py
Directory: ai_interlinq/cli/
"""

import asyncio
import time
import json
import signal
import sys
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import click

from ..core.token_manager import TokenManager
from ..core.communication_protocol import CommunicationProtocol
from ..utils.performance import PerformanceMonitor
from ..plugins.metrics import MetricsCollector
from ..transport.websocket import WebSocketTransport
from ..transport.base import TransportConfig


@dataclass
class MonitorConfig:
    """Configuration for monitoring."""
    refresh_interval: float = 5.0  # seconds
    history_length: int = 100  # number of data points to keep
    alert_thresholds: Dict[str, float] = None
    export_metrics: bool = False
    export_interval: int = 60  # seconds
    dashboard_mode: bool = False
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "error_rate": 0.05,      # 5% error rate
                "latency_p99": 1000.0,   # 1000ms P99 latency
                "memory_usage": 512.0,   # 512MB memory usage
                "connection_failures": 10  # 10 connection failures
            }


@dataclass
class HealthStatus:
    """Health status of a component."""
    component: str
    status: str  # healthy, degraded, unhealthy
    message: str
    metrics: Dict[str, Any]
    last_check: float
    
    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"


class SystemMonitor:
    """Real-time system monitor for AI-Interlinq."""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.running = False
        self.start_time = time.time()
        
        # Monitoring data
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.health_status: Dict[str, HealthStatus] = {}
        
        # Components to monitor
        self.performance_monitor = PerformanceMonitor()
        self.metrics_collector = MetricsCollector()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        click.echo("\n🛑 Shutting down monitor...")
        self.running = False
    
    async def start_monitoring(self, targets: List[str] = None):
        """Start the monitoring system."""
        self.running = True
        click.echo("🔍 Starting AI-Interlinq System Monitor")
        click.echo("=" * 60)
        
        if self.config.dashboard_mode:
            await self._run_dashboard(targets)
        else:
            await self._run_console_monitor(targets)
    
    async def _run_console_monitor(self, targets: List[str] = None):
        """Run console-based monitoring."""
        targets = targets or ["local"]
        
        while self.running:
            try:
                # Clear screen for real-time updates
                click.clear()
                
                # Display header
                uptime = time.time() - self.start_time
                click.echo(f"🤖 AI-Interlinq System Monitor")
                click.echo(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Uptime: {uptime:.0f}s")
                click.echo("=" * 60)
                
                # Monitor each target
                for target in targets:
                    await self._monitor_target(target)
                
                # Display alerts
                await self._display_alerts()
                
                # Display system metrics
                await self._display_system_metrics()
                
                # Wait for next refresh
                await asyncio.sleep(self.config.refresh_interval)
                
            except Exception as e:
                click.echo(f"❌ Monitoring error: {e}")
                await asyncio.sleep(1)
    
    async def _run_dashboard(self, targets: List[str] = None):
        """Run web dashboard monitoring."""
        try:
            # This would typically start a web server
            # For now, we'll simulate with enhanced console output
            click.echo("📊 Dashboard mode - Enhanced monitoring")
            
            await self._run_enhanced_console_monitor(targets)
            
        except Exception as e:
            click.echo(f"❌ Dashboard error: {e}")
            await self._run_console_monitor(targets)
    
    async def _run_enhanced_console_monitor(self, targets: List[str] = None):
        """Enhanced console monitoring with more detailed output."""
        targets = targets or ["local"]
        
        while self.running:
            try:
                click.clear()
                
                # Enhanced header with system info
                uptime = time.time() - self.start_time
                click.echo("🚀 AI-Interlinq Enhanced Monitor Dashboard")
                click.echo(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Uptime: {uptime:.0f}s | Targets: {len(targets)}")
                click.echo("=" * 80)
                
                # System overview
                await self._display_system_overview()
                
                # Target monitoring
                for i, target in enumerate(targets):
                    click.echo(f"\n📡 Target {i+1}: {target}")
                    click.echo("-" * 40)
                    await self._monitor_target_detailed(target)
                
                # Performance metrics
                await self._display_performance_dashboard()
                
                # Health checks
                await self._display_health_dashboard()
                
                # Recent alerts
                await self._display_recent_alerts()
                
                await asyncio.sleep(self.config.refresh_interval)
                
            except Exception as e:
                click.echo(f"❌ Dashboard error: {e}")
                await asyncio.sleep(1)
    
    async def _monitor_target(self, target: str):
        """Monitor a specific target."""
        click.echo(f"🎯 Target: {target}")
        
        try:
            # Collect metrics for target
            metrics = await self._collect_target_metrics(target)
            
            # Update history
            if target not in self.metrics_history:
                self.metrics_history[target] = []
            
            self.metrics_history[target].append({
                "timestamp": time.time(),
                "metrics": metrics
            })
            
            # Keep history within limits
            if len(self.metrics_history[target]) > self.config.history_length:
                self.metrics_history[target] = self.metrics_history[target][-self.config.history_length:]
            
            # Display current metrics
            status = "🟢" if metrics.get("status") == "healthy" else "🔴"
            click.echo(f"   Status: {status} {metrics.get('status', 'unknown')}")
            click.echo(f"   Connections: {metrics.get('connections', 0)}")
            click.echo(f"   Messages/sec: {metrics.get('messages_per_second', 0):.1f}")
            click.echo(f"   Latency: {metrics.get('avg_latency', 0):.2f}ms")
            click.echo(f"   Errors: {metrics.get('error_count', 0)}")
            
            # Check for alerts
            await self._check_target_alerts(target, metrics)
            
        except Exception as e:
            click.echo(f"   ❌ Error monitoring {target}: {e}")
            await self._add_alert("monitor_error", f"Failed to monitor {target}: {e}")
    
    async def _monitor_target_detailed(self, target: str):
        """Detailed monitoring for dashboard mode."""
        try:
            metrics = await self._collect_target_metrics(target)
            
            # Connection status
            connection_status = metrics.get("connection_status", {})
            click.echo(f"   🔗 Connections: {connection_status.get('active', 0)}/{connection_status.get('max', 0)}")
            
            # Throughput metrics
            throughput = metrics.get("throughput", {})
            click.echo(f"   ⚡ Throughput: {throughput.get('messages_per_second', 0):.1f} msg/s")
            click.echo(f"   📊 Bandwidth: {throughput.get('bytes_per_second', 0)/1024:.1f} KB/s")
            
            # Latency breakdown
            latency = metrics.get("latency", {})
            click.echo(f"   ⏱️  Latency: avg={latency.get('average', 0):.2f}ms, p99={latency.get('p99', 0):.2f}ms")
            
            # Error statistics
            errors = metrics.get("errors", {})
            error_rate = errors.get("rate", 0) * 100
            click.echo(f"   ❌ Errors: {errors.get('count', 0)} ({error_rate:.2f}%)")
            
            # Resource usage
            resources = metrics.get("resources", {})
            click.echo(f"   💾 Memory: {resources.get('memory_mb', 0):.1f}MB")
            click.echo(f"   🖥️  CPU: {resources.get('cpu_percent', 0):.1f}%")
            
        except Exception as e:
            click.echo(f"   ❌ Detailed monitoring error: {e}")
    
    async def _collect_target_metrics(self, target: str) -> Dict[str, Any]:
        """Collect metrics for a target."""
        # This would typically connect to the target and collect real metrics
        # For demonstration, we'll simulate metrics
        
        import random
        
        # Simulate connection to target
        if target == "local":
            # Local metrics from performance monitor
            try:
                stats = self.performance_monitor.get_all_stats()
                collector_stats = self.metrics_collector.get_metrics_summary()
                
                return {
                    "status": "healthy",
                    "connections": random.randint(10, 50),
                    "messages_per_second": random.uniform(50, 200),
                    "avg_latency": random.uniform(1, 10),
                    "error_count": random.randint(0, 5),
                    "connection_status": {
                        "active": random.randint(10, 50),
                        "max": 100
                    },
                    "throughput": {
                        "messages_per_second": random.uniform(50, 200),
                        "bytes_per_second": random.uniform(10000, 50000)
                    },
                    "latency": {
                        "average": random.uniform(1, 10),
                        "p50": random.uniform(1, 8),
                        "p90": random.uniform(8, 15),
                        "p99": random.uniform(15, 30)
                    },
                    "errors": {
                        "count": random.randint(0, 5),
                        "rate": random.uniform(0, 0.05)
                    },
                    "resources": {
                        "memory_mb": random.uniform(50, 200),
                        "cpu_percent": random.uniform(10, 80)
                    },
                    "performance_stats": stats,
                    "collector_stats": collector_stats
                }
                
            except Exception:
                return {"status": "error", "error": "Failed to collect local metrics"}
        
        else:
            # Remote target - would use transport to connect
            try:
                # Simulate remote connection
                await asyncio.sleep(0.1)  # Simulate network delay
                
                # Simulate metrics from remote target
                return {
                    "status": random.choice(["healthy", "healthy", "healthy", "degraded"]),
                    "connections": random.randint(5, 30),
                    "messages_per_second": random.uniform(20, 100),
                    "avg_latency": random.uniform(5, 25),
                    "error_count": random.randint(0, 3),
                    "remote": True,
                    "target": target
                }
                
            except Exception as e:
                return {"status": "unreachable", "error": str(e)}
    
    async def _check_target_alerts(self, target: str, metrics: Dict[str, Any]):
        """Check for alert conditions on target metrics."""
        alerts_triggered = []
        
        # Error rate alert
        error_rate = metrics.get("errors", {}).get("rate", 0)
        if error_rate > self.config.alert_thresholds["error_rate"]:
            alerts_triggered.append({
                "type": "high_error_rate",
                "target": target,
                "value": error_rate,
                "threshold": self.config.alert_thresholds["error_rate"],
                "message": f"High error rate: {error_rate:.2%}"
            })
        
        # Latency alert
        p99_latency = metrics.get("latency", {}).get("p99", 0)
        if p99_latency > self.config.alert_thresholds["latency_p99"]:
            alerts_triggered.append({
                "type": "high_latency",
                "target": target,
                "value": p99_latency,
                "threshold": self.config.alert_thresholds["latency_p99"],
                "message": f"High P99 latency: {p99_latency:.2f}ms"
            })
        
        # Memory usage alert
        memory_usage = metrics.get("resources", {}).get("memory_mb", 0)
        if memory_usage > self.config.alert_thresholds["memory_usage"]:
            alerts_triggered.append({
                "type": "high_memory",
                "target": target,
                "value": memory_usage,
                "threshold": self.config.alert_thresholds["memory_usage"],
                "message": f"High memory usage: {memory_usage:.1f}MB"
            })
        
        # Add triggered alerts
        for alert in alerts_triggered:
            await self._add_alert(alert["type"], alert["message"], alert)
    
    async def _add_alert(self, alert_type: str, message: str, details: Dict[str, Any] = None):
        """Add an alert to the system."""
        alert = {
            "timestamp": time.time(),
            "type": alert_type,
            "message": message,
            "details": details or {},
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    async def _display_alerts(self):
        """Display active alerts."""
        active_alerts = [a for a in self.alerts if not a["acknowledged"]]
        
        if active_alerts:
            click.echo(f"\n🚨 Active Alerts ({len(active_alerts)}):")
            for alert in active_alerts[-5:]:  # Show last 5 alerts
                timestamp = datetime.fromtimestamp(alert["timestamp"]).strftime("%H:%M:%S")
                click.echo(f"   [{timestamp}] {alert['type']}: {alert['message']}")
        else:
            click.echo(f"\n✅ No active alerts")
    
    async def _display_recent_alerts(self):
        """Display recent alerts for dashboard."""
        recent_alerts = self.alerts[-10:] if self.alerts else []
        
        click.echo(f"\n🚨 Recent Alerts ({len(recent_alerts)}):")
        if recent_alerts:
            for alert in recent_alerts:
                timestamp = datetime.fromtimestamp(alert["timestamp"]).strftime("%H:%M:%S")
                status = "✅" if alert["acknowledged"] else "🔴"
                click.echo(f"   {status} [{timestamp}] {alert['type']}: {alert['message']}")
        else:
            click.echo("   No recent alerts")
    
    async def _display_system_metrics(self):
        """Display overall system metrics."""
        click.echo(f"\n📊 System Metrics:")
        
        # Calculate aggregate metrics
        total_connections = 0
        total_messages_per_sec = 0
        avg_latency_values = []
        total_errors = 0
        
        for target, history in self.metrics_history.items():
            if history:
                latest = history[-1]["metrics"]
                total_connections += latest.get("connections", 0)
                total_messages_per_sec += latest.get("messages_per_second", 0)
                if latest.get("avg_latency", 0) > 0:
                    avg_latency_values.append(latest["avg_latency"])
                total_errors += latest.get("error_count", 0)
        
        avg_latency = sum(avg_latency_values) / len(avg_latency_values) if avg_latency_values else 0
        
        click.echo(f"   Total Connections: {total_connections}")
        click.echo(f"   Total Throughput: {total_messages_per_sec:.1f} msg/s")
        click.echo(f"   Average Latency: {avg_latency:.2f}ms")
        click.echo(f"   Total Errors: {total_errors}")
    
    async def _display_system_overview(self):
        """Display system overview for dashboard."""
        click.echo("🏛️  System Overview:")
        
        # System uptime and basic info
        uptime = time.time() - self.start_time
        uptime_str = str(timedelta(seconds=int(uptime)))
        
        click.echo(f"   Uptime: {uptime_str}")
        click.echo(f"   Targets Monitored: {len(self.metrics_history)}")
        click.echo(f"   Total Alerts: {len(self.alerts)}")
        click.echo(f"   Active Alerts: {len([a for a in self.alerts if not a['acknowledged']])}")
    
    async def _display_performance_dashboard(self):
        """Display performance metrics dashboard."""
        click.echo(f"\n⚡ Performance Dashboard:")
        
        # Get performance stats
        perf_stats = self.performance_monitor.get_all_stats()
        
        if perf_stats:
            click.echo("   Performance Metrics:")
            for metric_name, stats in perf_stats.items():
                if isinstance(stats, dict) and 'mean' in stats:
                    click.echo(f"     {metric_name}: {stats['mean']:.2f} (min: {stats['min']:.2f}, max: {stats['max']:.2f})")
        else:
            click.echo("   No performance data available")
        
        # Metrics collector stats
        collector_stats = self.metrics_collector.get_metrics_summary()
        if collector_stats:
            click.echo(f"   Metrics: {collector_stats['total_metrics']} collected, {collector_stats['memory_usage_bytes']} bytes")
    
    async def _display_health_dashboard(self):
        """Display health check dashboard."""
        click.echo(f"\n🏥 Health Dashboard:")
        
        # Update health checks
        await self._update_health_checks()
        
        if self.health_status:
            for component, health in self.health_status.items():
                status_icon = "🟢" if health.is_healthy else "🔴"
                click.echo(f"   {status_icon} {component}: {health.status} - {health.message}")
        else:
            click.echo("   No health checks configured")
    
    async def _update_health_checks(self):
        """Update health status for all components."""
        components = {
            "token_manager": self._check_token_manager_health,
            "performance_monitor": self._check_performance_monitor_health,
            "metrics_collector": self._check_metrics_collector_health,
            "memory_usage": self._check_memory_health
        }
        
        for component, check_func in components.items():
            try:
                status = await check_func()
                self.health_status[component] = status
            except Exception as e:
                self.health_status[component] = HealthStatus(
                    component=component,
                    status="unhealthy",
                    message=f"Health check failed: {e}",
                    metrics={},
                    last_check=time.time()
                )
    
    async def _check_token_manager_health(self) -> HealthStatus:
        """Check token manager health."""
        # This would check actual token manager if available
        return HealthStatus(
            component="token_manager",
            status="healthy",
            message="Token operations normal",
            metrics={"tokens_active": 0},
            last_check=time.time()
        )
    
    async def _check_performance_monitor_health(self) -> HealthStatus:
        """Check performance monitor health."""
        stats = self.performance_monitor.get_all_stats()
        
        return HealthStatus(
            component="performance_monitor",
            status="healthy",
            message="Performance monitoring active",
            metrics={"metrics_count": len(stats)},
            last_check=time.time()
        )
    
    async def _check_metrics_collector_health(self) -> HealthStatus:
        """Check metrics collector health."""
        stats = self.metrics_collector.get_metrics_summary()
        
        return HealthStatus(
            component="metrics_collector",
            status="healthy",
            message="Metrics collection active",
            metrics=stats,
            last_check=time.time()
        )
    
    async def _check_memory_health(self) -> HealthStatus:
        """Check system memory health."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = "unhealthy"
                message = f"High memory usage: {memory.percent:.1f}%"
            elif memory.percent > 80:
                status = "degraded"
                message = f"Elevated memory usage: {memory.percent:.1f}%"
            else:
                status = "healthy"
                message = f"Memory usage normal: {memory.percent:.1f}%"
            
            return HealthStatus(
                component="memory_usage",
                status=status,
                message=message,
                metrics={
                    "percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3)
                },
                last_check=time.time()
            )
            
        except ImportError:
            return HealthStatus(
                component="memory_usage",
                status="unknown",
                message="psutil not available for memory monitoring",
                metrics={},
                last_check=time.time()
            )
    
    def export_metrics(self, output_file: str, format: str = "json"):
        """Export collected metrics to file."""
        try:
            if format.lower() == "json":
                data = {
                    "export_timestamp": time.time(),
                    "monitor_uptime": time.time() - self.start_time,
                    "metrics_history": self.metrics_history,
                    "alerts": self.alerts,
                    "health_status": {
                        name: asdict(health) for name, health in self.health_status.items()
                    },
                    "config": asdict(self.config)
                }
                
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif format.lower() == "prometheus":
                # Export in Prometheus format
                lines = []
                timestamp = int(time.time() * 1000)  # Prometheus uses milliseconds
                
                for target, history in self.metrics_history.items():
                    if history:
                        latest = history[-1]["metrics"]
                        target_clean = target.replace("-", "_").replace(".", "_")
                        
                        # Export key metrics
                        lines.append(f'ai_interlinq_connections{{target="{target}"}} {latest.get("connections", 0)} {timestamp}')
                        lines.append(f'ai_interlinq_messages_per_second{{target="{target}"}} {latest.get("messages_per_second", 0)} {timestamp}')
                        lines.append(f'ai_interlinq_latency_ms{{target="{target}"}} {latest.get("avg_latency", 0)} {timestamp}')
                        lines.append(f'ai_interlinq_errors_total{{target="{target}"}} {latest.get("error_count", 0)} {timestamp}')
                
                with open(output_file, 'w') as f:
                    f.write('\n'.join(lines))
            
            click.echo(f"📊 Metrics exported to {output_file}")
            
        except Exception as e:
            click.echo(f"❌ Export failed: {e}")


# CLI Commands
@click.group()
def monitor():
    """AI-Interlinq monitoring commands."""
    pass


@monitor.command()
@click.option('--targets', '-t', multiple=True, help='Targets to monitor (default: local)')
@click.option('--interval', '-i', default=5.0, help='Refresh interval in seconds')
@click.option('--dashboard/--console', default=False, help='Dashboard mode vs console mode')
@click.option('--export', help='Export metrics to file')
@click.option('--export-interval', default=60, help='Export interval in seconds')
@click.option('--alert-config', help='JSON file with alert thresholds')
def watch(targets, interval, dashboard, export, export_interval, alert_config):
    """Start real-time monitoring of AI-Interlinq systems."""
    
    # Load alert configuration
    alert_thresholds = None
    if alert_config:
        try:
            with open(alert_config, 'r') as f:
                alert_thresholds = json.load(f)
        except Exception as e:
            click.echo(f"⚠️  Warning: Could not load alert config: {e}")
    
    config = MonitorConfig(
        refresh_interval=interval,
        dashboard_mode=dashboard,
        export_metrics=bool(export),
        export_interval=export_interval,
        alert_thresholds=alert_thresholds
    )
    
    async def run_monitor():
        monitor_system = SystemMonitor(config)
        
        # Setup export task if requested
        export_task = None
        if export:
            async def export_periodically():
                while monitor_system.running:
                    await asyncio.sleep(export_interval)
                    if monitor_system.running:
                        monitor_system.export_metrics(export, "json")
            
            export_task = asyncio.create_task(export_periodically())
        
        try:
            # Start monitoring
            await monitor_system.start_monitoring(list(targets) if targets else None)
        finally:
            if export_task:
                export_task.cancel()
                try:
                    await export_task
                except asyncio.CancelledError:
                    pass
    
    try:
        asyncio.run(run_monitor())
    except KeyboardInterrupt:
        click.echo("\n👋 Monitoring stopped")


@monitor.command()
@click.option('--target', '-t', required=True, help='Target to health check')
@click.option('--timeout', default=10.0, help='Health check timeout')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def health(target, timeout, verbose):
    """Perform health check on AI-Interlinq target."""
    
    async def run_health_check():
        click.echo(f"🏥 Health checking target: {target}")
        
        try:
            # Create monitor for health check
            config = MonitorConfig(refresh_interval=1.0)
            monitor_system = SystemMonitor(config)
            
            # Collect metrics with timeout
            start_time = time.time()
            metrics = await asyncio.wait_for(
                monitor_system._collect_target_metrics(target),
                timeout=timeout
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Analyze health
            status = metrics.get("status", "unknown")
            
            if status == "healthy":
                click.echo(f"✅ Target {target} is healthy")
                click.echo(f"   Response time: {response_time:.2f}ms")
                
                if verbose:
                    click.echo(f"   Connections: {metrics.get('connections', 'N/A')}")
                    click.echo(f"   Messages/sec: {metrics.get('messages_per_second', 'N/A')}")
                    click.echo(f"   Latency: {metrics.get('avg_latency', 'N/A')}ms")
                    click.echo(f"   Errors: {metrics.get('error_count', 'N/A')}")
                
                sys.exit(0)
                
            elif status == "degraded":
                click.echo(f"⚠️  Target {target} is degraded")
                click.echo(f"   Response time: {response_time:.2f}ms")
                if verbose and "error" in metrics:
                    click.echo(f"   Issue: {metrics['error']}")
                sys.exit(1)
                
            else:
                click.echo(f"❌ Target {target} is unhealthy")
                click.echo(f"   Status: {status}")
                if "error" in metrics:
                    click.echo(f"   Error: {metrics['error']}")
                sys.exit(2)
                
        except asyncio.TimeoutError:
            click.echo(f"❌ Health check timed out after {timeout}s")
            sys.exit(3)
        except Exception as e:
            click.echo(f"❌ Health check failed: {e}")
            sys.exit(4)
    
    asyncio.run(run_health_check())


@monitor.command()
@click.option('--target', '-t', required=True, help='Target to get metrics from')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'prometheus', 'csv']), 
              help='Output format')
@click.option('--output', '-o', help='Output file (default: stdout)')
def metrics(target, format, output):
    """Get current metrics from AI-Interlinq target."""
    
    async def get_metrics():
        try:
            config = MonitorConfig()
            monitor_system = SystemMonitor(config)
            
            # Collect metrics
            metrics_data = await monitor_system._collect_target_metrics(target)
            
            # Format output
            if format == 'json':
                output_data = json.dumps(metrics_data, indent=2)
            elif format == 'prometheus':
                lines = []
                for key, value in metrics_data.items():
                    if isinstance(value, (int, float)):
                        lines.append(f'ai_interlinq_{key}{{target="{target}"}} {value}')
                output_data = '\n'.join(lines)
            elif format == 'csv':
                import csv
                import io
                
                output_buffer = io.StringIO()
                writer = csv.writer(output_buffer)
                writer.writerow(['metric', 'value'])
                
                for key, value in metrics_data.items():
                    if isinstance(value, (int, float, str)):
                        writer.writerow([key, value])
                
                output_data = output_buffer.getvalue()
            
            # Output results
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                click.echo(f"📊 Metrics written to {output}")
            else:
                click.echo(output_data)
                
        except Exception as e:
            click.echo(f"❌ Failed to get metrics: {e}")
            sys.exit(1)
    
    asyncio.run(get_metrics())


@monitor.command()
@click.option('--input', '-i', required=True, help='Metrics file to analyze')
@click.option('--timerange', '-r', help='Time range to analyze (e.g., "1h", "30m")')
@click.option('--alert-threshold', '-a', multiple=True, 
              help='Alert thresholds (format: metric:threshold)')
def analyze(input, timerange, alert_threshold):
    """Analyze historical monitoring data."""
    
    try:
        # Load metrics data
        with open(input, 'r') as f:
            data = json.load(f)
        
        click.echo(f"📈 Analyzing metrics from {input}")
        click.echo("=" * 50)
        
        # Basic statistics
        export_time = data.get("export_timestamp", 0)
        uptime = data.get("monitor_uptime", 0)
        
        click.echo(f"Export time: {datetime.fromtimestamp(export_time).strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Monitor uptime: {uptime:.0f}s")
        
        # Analyze metrics history
        metrics_history = data.get("metrics_history", {})
        click.echo(f"\nTargets analyzed: {len(metrics_history)}")
        
        for target, history in metrics_history.items():
            click.echo(f"\n🎯 Target: {target}")
            if history:
                # Calculate statistics
                throughput_values = [h["metrics"].get("messages_per_second", 0) for h in history]
                latency_values = [h["metrics"].get("avg_latency", 0) for h in history if h["metrics"].get("avg_latency", 0) > 0]
                
                if throughput_values:
                    avg_throughput = sum(throughput_values) / len(throughput_values)
                    max_throughput = max(throughput_values)
                    click.echo(f"   Throughput: avg={avg_throughput:.1f}, max={max_throughput:.1f} msg/s")
                
                if latency_values:
                    avg_latency = sum(latency_values) / len(latency_values)
                    max_latency = max(latency_values)
                    click.echo(f"   Latency: avg={avg_latency:.2f}, max={max_latency:.2f}ms")
        
        # Analyze alerts
        alerts = data.get("alerts", [])
        if alerts:
            click.echo(f"\n🚨 Alerts found: {len(alerts)}")
            alert_types = {}
            for alert in alerts:
                alert_type = alert.get("type", "unknown")
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            
            for alert_type, count in alert_types.items():
                click.echo(f"   {alert_type}: {count}")
        
        # Health status
        health_status = data.get("health_status", {})
        if health_status:
            click.echo(f"\n🏥 Health Status:")
            for component, health in health_status.items():
                status = health.get("status", "unknown")
                message = health.get("message", "")
                click.echo(f"   {component}: {status} - {message}")
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    monitor()
