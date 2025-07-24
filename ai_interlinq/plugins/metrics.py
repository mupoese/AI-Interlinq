# ai_interlinq/plugins/metrics.py
"""Metrics collection plugin for AI-Interlinq."""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from ..utils.logging import get_logger


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """A single metric data point."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


class MetricsCollector:
    """Collects and aggregates metrics for AI-Interlinq."""
    
    def __init__(self, max_samples: int = 10000):
        self.max_samples = max_samples
        self.logger = get_logger("metrics_collector")
        
        # Thread-safe storage
        self._lock = threading.RLock()
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        
        # Histogram buckets
        self._histogram_buckets = [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._histograms: Dict[str, Dict[float, int]] = defaultdict(lambda: defaultdict(int))
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        with self._lock:
            metric_key = self._create_metric_key(name, tags)
            self._counters[metric_key] += value
            
            metric = Metric(
                name=name,
                value=value,
                timestamp=time.time(),
                tags=tags or {},
                metric_type=MetricType.COUNTER
            )
            self._metrics[metric_key].append(metric)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        with self._lock:
            metric_key = self._create_metric_key(name, tags)
            self._gauges[metric_key] = value
            
            metric = Metric(
                name=name,
                value=value,
                timestamp=time.time(),
                tags=tags or {},
                metric_type=MetricType.GAUGE
            )
            self._metrics[metric_key].append(metric)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a value in a histogram."""
        with self._lock:
            metric_key = self._create_metric_key(name, tags)
            
            # Find appropriate bucket
            for bucket in self._histogram_buckets:
                if value <= bucket:
                    self._histograms[metric_key][bucket] += 1
            
            # Also record in +Inf bucket
            self._histograms[metric_key][float('inf')] += 1
            
            metric = Metric(
                name=name,
                value=value,
                timestamp=time.time(),
                tags=tags or {},
                metric_type=MetricType.HISTOGRAM
            )
            self._metrics[metric_key].append(metric)
    
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Start a timer and return timer ID."""
        timer_id = f"{name}_{id(threading.current_thread())}_{time.time()}"
        
        with self._lock:
            if not hasattr(self, '_active_timers'):
                self._active_timers = {}
            
            self._active_timers[timer_id] = {
                'name': name,
                'start_time': time.time(),
                'tags': tags or {}
            }
        
        return timer_id
    
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """Stop a timer and record the duration."""
        with self._lock:
            if not hasattr(self, '_active_timers') or timer_id not in self._active_timers:
                return None
            
            timer_info = self._active_timers.pop(timer_id)
            duration = time.time() - timer_info['start_time']
            
            # Record as histogram
            self.record_histogram(f"{timer_info['name']}_duration", duration, timer_info['tags'])
            
            return duration
    
    def get_counter_value(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        metric_key = self._create_metric_key(name, tags)
        with self._lock:
            return self._counters.get(metric_key, 0.0)
    
    def get_gauge_value(self, name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get current gauge value."""
        metric_key = self._create_metric_key(name, tags)
        with self._lock:
            return self._gauges.get(metric_key)
    
    def get_histogram_buckets(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[float, int]:
        """Get histogram bucket counts."""
        metric_key = self._create_metric_key(name, tags)
        with self._lock:
            return dict(self._histograms.get(metric_key, {}))
    
    def get_all_metrics(self) -> Dict[str, List[Dict]]:
        """Get all metrics in Prometheus-like format."""
        with self._lock:
            result = {}
            
            # Counters
            for key, value in self._counters.items():
                if key not in result:
                    result[key] = []
                result[key].append({
                    'type': 'counter',
                    'value': value,
                    'timestamp': time.time()
                })
            
            # Gauges
            for key, value in self._gauges.items():
                if key not in result:
                    result[key] = []
                result[key].append({
                    'type': 'gauge',
                    'value': value,
                    'timestamp': time.time()
                })
            
            # Histograms
            for key, buckets in self._histograms.items():
                if key not in result:
                    result[key] = []
                result[key].append({
                    'type': 'histogram',
                    'buckets': dict(buckets),
                    'timestamp': time.time()
                })
            
            return result
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        with self._lock:
            # Export counters
            for key, value in self._counters.items():
                name, tags_str = self._parse_metric_key(key)
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name}{tags_str} {value}")
            
            # Export gauges
            for key, value in self._gauges.items():
                name, tags_str = self._parse_metric_key(key)
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name}{tags_str} {value}")
            
            # Export histograms
            for key, buckets in self._histograms.items():
                name, tags_str = self._parse_metric_key(key)
                lines.append(f"# TYPE {name} histogram")
                
                for bucket, count in sorted(buckets.items()):
                    if bucket == float('inf'):
                        bucket_str = '+Inf'
                    else:
                        bucket_str = str(bucket)
                    
                    bucket_tags = tags_str.rstrip('}') + f',le="{bucket_str}"}}' if tags_str else f'{{le="{bucket_str}"}}'
                    lines.append(f"{name}_bucket{bucket_tags} {count}")
        
        return '\n'.join(lines)
    
    def clear_metrics(self) -> None:
        """Clear all metrics."""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            if hasattr(self, '_active_timers'):
                self._active_timers.clear()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._lock:
            return {
                'total_metrics': len(self._metrics),
                'counters': len(self._counters),
                'gauges': len(self._gauges),
                'histograms': len(self._histograms),
                'active_timers': len(getattr(self, '_active_timers', {})),
                'memory_usage_bytes': sum(len(deque_) for deque_ in self._metrics.values()) * 64  # Rough estimate
            }
    
    def _create_metric_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for the metric."""
        if not tags:
            return name
        
        tag_parts = [f"{k}={v}" for k, v in sorted(tags.items())]
        return f"{name}{{{','.join(tag_parts)}}}"
    
    def _parse_metric_key(self, key: str) -> tuple[str, str]:
        """Parse metric key back into name and tags string."""
        if '{' not in key:
            return key, ''
        
        name, tags_part = key.split('{', 1)
        return name, '{' + tags_part
