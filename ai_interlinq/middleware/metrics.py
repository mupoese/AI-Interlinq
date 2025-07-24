
# File: /ai_interlinq/middleware/metrics.py
# Directory: /ai_interlinq/middleware

"""
Metrics middleware for AI-Interlinq framework.
Provides comprehensive metrics collection, monitoring, and export capabilities.
"""

import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class MetricPoint:
    """Individual metric measurement."""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

@dataclass
class HistogramBucket:
    """Histogram bucket for latency measurements."""
    upper_bound: float
    count: int = 0

class MetricsCollector:
    """Thread-safe metrics collector."""
    
    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()
        
    def increment(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.counters[key] += value
            self._add_metric_point(name, self.counters[key], MetricType.COUNTER, labels)
            
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value."""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.gauges[key] = value
            self._add_metric_point(name, value, MetricType.GAUGE, labels)
            
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a value for histogram metric."""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.histograms[key].append(value)
            self._add_metric_point(name, value, MetricType.HISTOGRAM, labels)
            
    def time_operation(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        return TimerContext(self, name, labels)
        
    def _add_metric_point(self, name: str, value: float, metric_type: MetricType, labels: Optional[Dict[str, str]]):
        """Add metric point to time series."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type=metric_type
        )
        self.metrics[name].append(point)
        
    def _get_metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Generate unique key for metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{label_str}}"
        
    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        with self.lock:
            if name not in self.metrics:
                return {}
                
            points = list(self.metrics[name])
            if not points:
                return {}
                
            values = [p.value for p in points]
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "last_updated": points[-1].timestamp.isoformat()
            }

class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: Optional[Dict[str, str]]):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.observe_histogram(f"{self.name}_duration", duration, self.labels)

class MetricsMiddleware:
    """
    Comprehensive metrics middleware for AI communication monitoring.
    
    Features:
    - Message processing metrics
    - Performance monitoring
    - Error tracking
    - Custom metric collection
    - Export capabilities
    """
    
    def __init__(
        self,
        enable_detailed_metrics: bool = True,
        histogram_buckets: Optional[List[float]] = None,
        export_interval: int = 60
    ):
        """
        Initialize metrics middleware.
        
        Args:
            enable_detailed_metrics: Enable detailed per-message metrics
            histogram_buckets: Custom histogram buckets for latency
            export_interval: Metrics export interval in seconds
        """
        self.enable_detailed = enable_detailed_metrics
        self.export_interval = export_interval
        
        # Default histogram buckets for latency (in seconds)
        self.histogram_buckets = histogram_buckets or [
            0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0
        ]
        
        # Metrics collector
        self.collector = MetricsCollector()
        
        # System metrics
        self.system_metrics = {
            "messages_processed": 0,
            "messages_failed": 0, 
            "bytes_processed": 0,
            "active_connections": 0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0
        }
        
        # Performance tracking
        self.performance_stats = {
            "avg_processing_time": 0.0,
            "min_processing_time": float('inf'),
            "max_processing_time": 0.0,
            "p95_processing_time": 0.0,
            "p99_processing_time": 0.0
        }
        
        # Error tracking
        self.error_stats = defaultdict(int)
        self.error_history = deque(maxlen=1000)
        
        # Export handlers
        self.export_handlers = []
        self.export_task = None
        
    def record_message_processed(
        self,
        message_type: str,
        processing_time: float,
        message_size: int,
        success: bool = True,
        error_type: Optional[str] = None
    ):
        """
        Record message processing metrics.
        
        Args:
            message_type: Type of message processed
            processing_time: Time taken to process message
            message_size: Size of message in bytes
            success: Whether processing was successful
            error_type: Type of error if failed
        """
        labels = {"message_type": message_type}
        
        # Record basic metrics
        self.collector.increment("messages_total", labels=labels)
        self.collector.observe_histogram("message_processing_time", processing_time, labels)
        self.collector.observe_histogram("message_size_bytes", message_size, labels)
        
        if success:
            self.collector.increment("messages_success", labels=labels)
            self.system_metrics["messages_processed"] += 1
        else:
            self.collector.increment("messages_failed", labels=labels)
            self.system_metrics["messages_failed"] += 1
            
            if error_type:
                error_labels = {**labels, "error_type": error_type}
                self.collector.increment("errors_total", labels=error_labels)
                self.error_stats[error_type] += 1
                self.error_history.append({
                    "timestamp": datetime.utcnow(),
                    "error_type": error_type,
                    "message_type": message_type
                })
                
        # Update system metrics
        self.system_metrics["bytes_processed"] += message_size
        
        # Update performance stats
        self._update_performance_stats(processing_time)
        
    def record_connection_event(self, event_type: str, connection_id: str):
        """
        Record connection-related events.
        
        Args:
            event_type: Type of event (connect, disconnect, error)
            connection_id: Unique connection identifier
        """
        labels = {"event_type": event_type, "connection_id": connection_id}
        self.collector.increment("connection_events", labels=labels)
        
        if event_type == "connect":
            self.system_metrics["active_connections"] += 1
            self.collector.set_gauge("active_connections", self.system_metrics["active_connections"])
        elif event_type == "disconnect":
            self.system_metrics["active_connections"] = max(0, self.system_metrics["active_connections"] - 1)
            self.collector.set_gauge("active_connections", self.system_metrics["active_connections"])
            
    def record_custom_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Record custom metric.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            labels: Optional labels
        """
        if metric_type == MetricType.COUNTER:
            self.collector.increment(name, int(value), labels)
        elif metric_type == MetricType.GAUGE:
            self.collector.set_gauge(name, float(value), labels)
        elif metric_type == MetricType.HISTOGRAM:
            self.collector.observe_histogram(name, float(value), labels)
            
    async def middleware_handler(
        self,
        message: Dict[str, Any],
        next_handler: Callable
    ) -> Dict[str, Any]:
        """
        Middleware handler for metrics collection.
        
        Args:
            message: Message to process
            next_handler: Next middleware in chain
            
        Returns:
            Processed message with metrics metadata
        """
        start_time = time.time()
        message_type = message.get("type", "unknown")
        message_size = len(json.dumps(message).encode('utf-8'))
        
        # Record incoming message
        if self.enable_detailed:
            self.collector.increment("messages_incoming", labels={"type": message_type})
            
        try:
            # Process message through next handler
            with self.collector.time_operation("message_processing", {"type": message_type}):
                response = await next_handler(message)
                
            processing_time = time.time() - start_time
            
            # Record successful processing
            self.record_message_processed(
                message_type=message_type,
                processing_time=processing_time,
                message_size=message_size,
                success=True
            )
            
            # Add metrics metadata to response
            if isinstance(response, dict) and self.enable_detailed:
                response["metrics"] = {
                    "processing_time": processing_time,
                    "message_size": message_size,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_type = type(e).__name__
            
            # Record failed processing
            self.record_message_processed(
                message_type=message_type,
                processing_time=processing_time,
                message_size=message_size,
                success=False,
                error_type=error_type
            )
            
            # Re-raise exception
            raise
            
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            "system_metrics": self.system_metrics.copy(),
            "performance_stats": self.performance_stats.copy(),
            "error_stats": dict(self.error_stats),
            "recent_errors": list(self.error_history)[-10:],  # Last 10 errors
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        metrics_lines = []
        
        # System metrics
        for name, value in self.system_metrics.items():
            metrics_lines.append(f"ai_interlinq_{name} {value}")
            
        # Performance metrics
        for name, value in self.performance_stats.items():
            if value != float('inf'):
                metrics_lines.append(f"ai_interlinq_{name} {value}")
                
        # Error metrics
        for error_type, count in self.error_stats.items():
            metrics_lines.append(f'ai_interlinq_errors{{type="{error_type}"}} {count}')
            
        return "\n".join(metrics_lines) + "\n"
        
    def export_to_json(self) -> str:
        """Export metrics as JSON."""
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": self.system_metrics,
            "performance_stats": self.performance_stats,
            "error_stats": dict(self.error_stats),
            "histogram_data": self._get_histogram_data()
        }
        return json.dumps(export_data, indent=2)
        
    def add_export_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add custom export handler."""
        self.export_handlers.append(handler)
        
    async def start_export_task(self):
        """Start periodic metrics export task."""
        if self.export_task:
            return
            
        self.export_task = asyncio.create_task(self._export_loop())
        
    async def stop_export_task(self):
        """Stop metrics export task."""
        if self.export_task:
            self.export_task.cancel()
            try:
                await self.export_task
            except asyncio.CancelledError:
                pass
            self.export_task = None
            
    async def _export_loop(self):
        """Periodic metrics export loop."""
        while True:
            try:
                await asyncio.sleep(self.export_interval)
                
                # Export to all registered handlers
                metrics_data = self.get_metrics_summary()
                for handler in self.export_handlers:
                    try:
                        handler(metrics_data)
                    except Exception as e:
                        logger.error(f"Metrics export handler failed: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics export loop error: {e}")
                
    def _update_performance_stats(self, processing_time: float):
        """Update performance statistics."""
        stats = self.performance_stats
        
        # Update min/max
        stats["min_processing_time"] = min(stats["min_processing_time"], processing_time)
        stats["max_processing_time"] = max(stats["max_processing_time"], processing_time)
        
        # Update average (simplified running average)
        if stats["avg_processing_time"] == 0.0:
            stats["avg_processing_time"] = processing_time
        else:
            stats["avg_processing_time"] = (stats["avg_processing_time"] * 0.9 + processing_time * 0.1)
            
    def _get_histogram_data(self) -> Dict[str, Any]:
        """Get histogram data for export."""
        histogram_data = {}
        
        for name, values in self.collector.histograms.items():
            if values:
                histogram_data[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "p50": statistics.median(values),
                    "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                    "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
                }
                
        return histogram_data
        
    def reset_metrics(self):
        """Reset all metrics."""
        self.collector = MetricsCollector()
        self.system_metrics = {k: 0 if isinstance(v, (int, float)) else v for k, v in self.system_metrics.items()}
        self.performance_stats = {
            "avg_processing_time": 0.0,
            "min_processing_time": float('inf'),
            "max_processing_time": 0.0,
            "p95_processing_time": 0.0,
            "p99_processing_time": 0.0
        }
        self.error_stats.clear()
        self.error_history.clear()
