"""
Performance Monitoring for AI-Interlinq
Tracks and analyzes communication performance metrics.
"""

import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import deque, defaultdict


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitors and analyzes AI communication performance."""
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            max_samples: Maximum number of samples to keep for each metric
        """
        self.max_samples = max_samples
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self._start_times: Dict[str, float] = {}
        self._counters: Dict[str, int] = defaultdict(int)
    
    def start_timer(self, operation: str) -> str:
        """
        Start timing an operation.
        
        Args:
            operation: Name of the operation
            
        Returns:
            Timer ID for this specific timing
        """
        timer_id = f"{operation}_{int(time.time() * 1000000)}"
        self._start_times[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        End timing an operation and record the duration.
        
        Args:
            timer_id: Timer ID from start_timer
            metadata: Optional metadata to include
            
        Returns:
            Duration in seconds
        """
        if timer_id not in self._start_times:
            return 0.0
        
        duration = time.time() - self._start_times.pop(timer_id)
        operation = timer_id.rsplit('_', 1)[0]
        
        metric = PerformanceMetric(
            name=f"{operation}_duration",
            value=duration,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        self._metrics[metric.name].append(metric)
        return duration
    
    def record_metric(
        self,
        name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a performance metric.
        
        Args:
            name: Metric name
            value: Metric value
            metadata: Optional metadata
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        self._metrics[name].append(metric)
    
    def increment_counter(self, name: str, amount: int = 1) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Counter name
            amount: Amount to increment by
        """
        self._counters[name] += amount
    
    def get_metric_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a metric.
        
        Args:
            name: Metric name
            
        Returns:
            Dictionary with metric statistics
        """
        if name not in self._metrics or not self._metrics[name]:
            return {}
        
        values = [m.value for m in self._metrics[name]]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "latest": values[-1],
            "latest_timestamp": self._metrics[name][-1].timestamp
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all metrics."""
        stats = {}
        
        # Metric statistics
        for metric_name in self._metrics:
            stats[metric_name] = self.get_metric_stats(metric_name)
        
        # Counter values
        for counter_name, value in self._counters.items():
            stats[counter_name] = {"count": value}
        
        return stats
    
    def get_throughput(self, metric_name: str, window_seconds: int = 60) -> float:
        """
        Calculate throughput for a metric over a time window.
        
        Args:
            metric_name: Name of the metric
            window_seconds: Time window in seconds
            
        Returns:
            Throughput (events per second)
        """
        if metric_name not in self._metrics:
            return 0.0
        
        now = time.time()
        cutoff = now - window_seconds
        
        recent_metrics = [
            m for m in self._metrics[metric_name]
            if m.timestamp >= cutoff
        ]
        
        return len(recent_metrics) / window_seconds
    
    def get_latency_percentiles(
        self,
        metric_name: str,
        percentiles: List[float] = [50, 90, 95, 99]
    ) -> Dict[float, float]:
        """
        Calculate latency percentiles for a metric.
        
        Args:
            metric_name: Name of the latency metric
            percentiles: List of percentiles to calculate
            
        Returns:
            Dictionary mapping percentile to value
        """
        if metric_name not in self._metrics or not self._metrics[metric_name]:
            return {p: 0.0 for p in percentiles}
        
        values = sorted([m.value for m in self._metrics[metric_name]])
        result = {}
        
        for percentile in percentiles:
            index = int((percentile / 100.0) * len(values))
            if index >= len(values):
                index = len(values) - 1
            result[percentile] = values[index]
        
        return result
    
    def clear_metrics(self, metric_name: Optional[str] = None) -> None:
        """
        Clear metrics.
        
        Args:
            metric_name: Specific metric to clear, or None to clear all
        """
        if metric_name:
            if metric_name in self._metrics:
                self._metrics[metric_name].clear()
            if metric_name in self._counters:
                self._counters[metric_name] = 0
        else:
            self._metrics.clear()
            self._counters.clear()
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in the specified format.
        
        Args:
            format: Export format ("json" or "csv")
            
        Returns:
            Exported metrics as string
        """
        if format.lower() == "json":
            import json
            data = {
                "metrics": {},
                "counters": dict(self._counters),
                "exported_at": time.time()
            }
            
            for metric_name, metrics in self._metrics.items():
                data["metrics"][metric_name] = [
                    {
                        "value": m.value,
                        "timestamp": m.timestamp,
                        "metadata": m.metadata
                    }
                    for m in metrics
                ]
            
            return json.dumps(data, indent=2)
        
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["metric_name", "value", "timestamp", "metadata"])
            
            # Write metrics
            for metric_name, metrics in self._metrics.items():
                for m in metrics:
                    writer.writerow([
                        metric_name,
                        m.value,
                        m.timestamp,
                        str(m.metadata)
                    ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
