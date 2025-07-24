# ai_interlinq/middleware/compression.py
"""
Compression Middleware for AI-Interlinq
Provides intelligent compression and decompression for AI communication messages.

File: ai_interlinq/middleware/compression.py
Directory: ai_interlinq/middleware/
"""

import gzip
import zlib
import bz2
import lzma
import time
from typing import Dict, Optional, Tuple, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..core.communication_protocol import Message
from ..utils.logging import get_logger
from ..utils.performance import PerformanceMonitor


class CompressionAlgorithm(Enum):
    """Supported compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    BZ2 = "bz2"
    LZMA = "lzma"


class CompressionLevel(Enum):
    """Compression levels for performance vs ratio trade-off."""
    FAST = 1      # Fastest compression, lower ratio
    BALANCED = 6  # Balanced performance and ratio
    BEST = 9      # Best compression ratio, slower


@dataclass
class CompressionConfig:
    """Configuration for compression middleware."""
    algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP
    level: CompressionLevel = CompressionLevel.BALANCED
    min_size_threshold: int = 1024  # Only compress messages larger than 1KB
    max_size_threshold: int = 10 * 1024 * 1024  # Don't compress messages larger than 10MB
    adaptive_compression: bool = True  # Automatically choose best algorithm
    cache_compressed: bool = True  # Cache compressed results
    enable_async: bool = True  # Use async processing for large messages


@dataclass
class CompressionStats:
    """Statistics for compression operations."""
    total_compressed: int = 0
    total_decompressed: int = 0
    bytes_saved: int = 0
    compression_time: float = 0.0
    decompression_time: float = 0.0
    algorithm_usage: Dict[str, int] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0


class CompressionMiddleware:
    """Advanced compression middleware with intelligent algorithm selection."""
    
    def __init__(self, 
                 config: Optional[CompressionConfig] = None,
                 max_workers: int = 4):
        """
        Initialize compression middleware.
        
        Args:
            config: Compression configuration
            max_workers: Maximum worker threads for async compression
        """
        self.config = config or CompressionConfig()
        self.logger = get_logger("compression_middleware")
        self.performance_monitor = PerformanceMonitor()
        
        # Statistics tracking
        self.stats = CompressionStats()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=max_workers) if config.enable_async else None
        
        # Compression cache
        self._compression_cache: Dict[str, Tuple[bytes, CompressionAlgorithm]] = {}
        self._cache_max_size = 1000
        
        # Algorithm performance tracking
        self._algorithm_performance: Dict[CompressionAlgorithm, Dict[str, float]] = {
            alg: {"avg_ratio": 0.0, "avg_time": 0.0, "count": 0}
            for alg in CompressionAlgorithm
        }
        
        # Setup compression functions
        self._compressors = {
            CompressionAlgorithm.GZIP: self._compress_gzip,
            CompressionAlgorithm.ZLIB: self._compress_zlib,
            CompressionAlgorithm.BZ2: self._compress_bz2,
            CompressionAlgorithm.LZMA: self._compress_lzma,
        }
        
        self._decompressors = {
            CompressionAlgorithm.GZIP: self._decompress_gzip,
            CompressionAlgorithm.ZLIB: self._decompress_zlib,
            CompressionAlgorithm.BZ2: self._decompress_bz2,
            CompressionAlgorithm.LZMA: self._decompress_lzma,
        }
    
    async def compress_message(self, 
                             data: Union[str, bytes], 
                             algorithm: Optional[CompressionAlgorithm] = None) -> Tuple[bytes, CompressionAlgorithm, Dict[str, Any]]:
        """
        Compress message data with intelligent algorithm selection.
        
        Args:
            data: Data to compress (string or bytes)
            algorithm: Specific algorithm to use (None for auto-selection)
            
        Returns:
            Tuple of (compressed_data, algorithm_used, metadata)
        """
        timer_id = self.performance_monitor.start_timer("message_compression")
        
        try:
            # Convert to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            original_size = len(data_bytes)
            
            # Check size thresholds
            if original_size < self.config.min_size_threshold:
                self.performance_monitor.end_timer(timer_id)
                return data_bytes, CompressionAlgorithm.NONE, {
                    "original_size": original_size,
                    "compressed_size": original_size,
                    "compression_ratio": 1.0,
                    "reason": "Below minimum threshold"
                }
            
            if original_size > self.config.max_size_threshold:
                self.performance_monitor.end_timer(timer_id)
                return data_bytes, CompressionAlgorithm.NONE, {
                    "original_size": original_size,
                    "compressed_size": original_size,
                    "compression_ratio": 1.0,
                    "reason": "Above maximum threshold"
                }
            
            # Check cache first
            cache_key = self._get_cache_key(data_bytes, algorithm)
            if self.config.cache_compressed and cache_key in self._compression_cache:
                cached_data, cached_algorithm = self._compression_cache[cache_key]
                self.stats.cache_hits += 1
                
                metadata = {
                    "original_size": original_size,
                    "compressed_size": len(cached_data),
                    "compression_ratio": original_size / len(cached_data),
                    "cached": True
                }
                
                self.performance_monitor.end_timer(timer_id)
                return cached_data, cached_algorithm, metadata
            
            self.stats.cache_misses += 1
            
            # Select compression algorithm
            if algorithm is None:
                if self.config.adaptive_compression:
                    algorithm = await self._select_best_algorithm(data_bytes)
                else:
                    algorithm = self.config.algorithm
            
            # Perform compression
            if self.config.enable_async and original_size > 50000:  # Use async for large messages
                compressed_data = await self._compress_async(data_bytes, algorithm)
            else:
                compressed_data = await self._compress_sync(data_bytes, algorithm)
            
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            # Update statistics
            self.stats.total_compressed += 1
            self.stats.bytes_saved += (original_size - compressed_size)
            self.stats.algorithm_usage[algorithm.value] = self.stats.algorithm_usage.get(algorithm.value, 0) + 1
            
            # Update algorithm performance tracking
            compression_time = self.performance_monitor.end_timer(timer_id)
            self._update_algorithm_performance(algorithm, compression_ratio, compression_time)
            
            # Cache result if beneficial
            if (self.config.cache_compressed and 
                compression_ratio > 1.2 and  # Only cache if good compression
                len(self._compression_cache) < self._cache_max_size):
                self._compression_cache[cache_key] = (compressed_data, algorithm)
            
            metadata = {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "algorithm": algorithm.value,
                "compression_time": compression_time,
                "cached": False
            }
            
            self.logger.debug(
                f"Compressed {original_size} bytes to {compressed_size} bytes "
                f"({compression_ratio:.2f}x) using {algorithm.value}"
            )
            
            return compressed_data, algorithm, metadata
            
        except Exception as e:
            self.performance_monitor.end_timer(timer_id)
            self.logger.error(f"Compression failed: {e}")
            # Return original data on compression failure
            return data_bytes, CompressionAlgorithm.NONE, {
                "original_size": len(data_bytes),
                "compressed_size": len(data_bytes),
                "compression_ratio": 1.0,
                "error": str(e)
            }
    
    async def decompress_message(self, 
                               compressed_data: bytes, 
                               algorithm: CompressionAlgorithm) -> Tuple[bytes, Dict[str, Any]]:
        """
        Decompress message data.
        
        Args:
            compressed_data: Compressed data
            algorithm: Algorithm used for compression
            
        Returns:
            Tuple of (decompressed_data, metadata)
        """
        if algorithm == CompressionAlgorithm.NONE:
            return compressed_data, {
                "original_size": len(compressed_data),
                "decompressed_size": len(compressed_data),
                "decompression_time": 0.0
            }
        
        timer_id = self.performance_monitor.start_timer("message_decompression")
        
        try:
            compressed_size = len(compressed_data)
            
            # Perform decompression
            if self.config.enable_async and compressed_size > 50000:
                decompressed_data = await self._decompress_async(compressed_data, algorithm)
            else:
                decompressed_data = await self._decompress_sync(compressed_data, algorithm)
            
            decompressed_size = len(decompressed_data)
            decompression_time = self.performance_monitor.end_timer(timer_id)
            
            # Update statistics
            self.stats.total_decompressed += 1
            self.stats.decompression_time += decompression_time
            
            metadata = {
                "compressed_size": compressed_size,
                "decompressed_size": decompressed_size,
                "decompression_time": decompression_time,
                "algorithm": algorithm.value
            }
            
            self.logger.debug(
                f"Decompressed {compressed_size} bytes to {decompressed_size} bytes "
                f"using {algorithm.value}"
            )
            
            return decompressed_data, metadata
            
        except Exception as e:
            self.performance_monitor.end_timer(timer_id)
            self.logger.error(f"Decompression failed: {e}")
            raise ValueError(f"Decompression failed with {algorithm.value}: {e}")
    
    async def _select_best_algorithm(self, data: bytes) -> CompressionAlgorithm:
        """
        Intelligently select the best compression algorithm based on data characteristics.
        
        Args:
            data: Data to analyze
            
        Returns:
            Best compression algorithm for the data
        """
        data_size = len(data)
        
        # For small data, use fast compression
        if data_size < 5000:
            return CompressionAlgorithm.GZIP
        
        # Analyze data characteristics
        entropy = self._calculate_entropy(data[:1000])  # Sample first 1KB
        
        # High entropy data (already compressed/encrypted) - use fast algorithm
        if entropy > 7.5:
            return CompressionAlgorithm.GZIP
        
        # Low entropy data with repetitive patterns - use better compression
        if entropy < 4.0:
            if data_size > 100000:  # Large files benefit from LZMA
                return CompressionAlgorithm.LZMA
            else:
                return CompressionAlgorithm.BZ2
        
        # Medium entropy - balanced approach
        return CompressionAlgorithm.ZLIB
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data sample."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        
        # Calculate entropy
        import math
        entropy = 0.0
        data_len = len(data)
        
        for count in freq.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    async def _compress_async(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Compress data asynchronously."""
        loop = asyncio.get_event_loop()
        compressor = self._compressors[algorithm]
        return await loop.run_in_executor(self.executor, compressor, data)
    
    async def _compress_sync(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Compress data synchronously."""
        compressor = self._compressors[algorithm]
        return compressor(data)
    
    async def _decompress_async(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data asynchronously."""
        loop = asyncio.get_event_loop()
        decompressor = self._decompressors[algorithm]
        return await loop.run_in_executor(self.executor, decompressor, data)
    
    async def _decompress_sync(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data synchronously."""
        decompressor = self._decompressors[algorithm]
        return decompressor(data)
    
    def _compress_gzip(self, data: bytes) -> bytes:
        """Compress using gzip."""
        return gzip.compress(data, compresslevel=self.config.level.value)
    
    def _decompress_gzip(self, data: bytes) -> bytes:
        """Decompress using gzip."""
        return gzip.decompress(data)
    
    def _compress_zlib(self, data: bytes) -> bytes:
        """Compress using zlib."""
        return zlib.compress(data, level=self.config.level.value)
    
    def _decompress_zlib(self, data: bytes) -> bytes:
        """Decompress using zlib."""
        return zlib.decompress(data)
    
    def _compress_bz2(self, data: bytes) -> bytes:
        """Compress using bz2."""
        return bz2.compress(data, compresslevel=self.config.level.value)
    
    def _decompress_bz2(self, data: bytes) -> bytes:
        """Decompress using bz2."""
        return bz2.decompress(data)
    
    def _compress_lzma(self, data: bytes) -> bytes:
        """Compress using LZMA."""
        return lzma.compress(data, preset=self.config.level.value)
    
    def _decompress_lzma(self, data: bytes) -> bytes:
        """Decompress using LZMA."""
        return lzma.decompress(data)
    
    def _get_cache_key(self, data: bytes, algorithm: Optional[CompressionAlgorithm]) -> str:
        """Generate cache key for data and algorithm."""
        import hashlib
        data_hash = hashlib.md5(data).hexdigest()
        alg_str = algorithm.value if algorithm else "auto"
        return f"{data_hash}:{alg_str}:{self.config.level.value}"
    
    def _update_algorithm_performance(self, 
                                    algorithm: CompressionAlgorithm, 
                                    ratio: float, 
                                    time_taken: float):
        """Update algorithm performance statistics."""
        perf = self._algorithm_performance[algorithm]
        count = perf["count"]
        
        # Update running averages
        perf["avg_ratio"] = (perf["avg_ratio"] * count + ratio) / (count + 1)
        perf["avg_time"] = (perf["avg_time"] * count + time_taken) / (count + 1)
        perf["count"] = count + 1
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get comprehensive compression statistics."""
        total_time = self.stats.compression_time + self.stats.decompression_time
        
        return {
            "total_compressed": self.stats.total_compressed,
            "total_decompressed": self.stats.total_decompressed,
            "bytes_saved": self.stats.bytes_saved,
            "compression_time": self.stats.compression_time,
            "decompression_time": self.stats.decompression_time,
            "total_time": total_time,
            "algorithm_usage": dict(self.stats.algorithm_usage),
            "cache_hits": self.stats.cache_hits,
            "cache_misses": self.stats.cache_misses,
            "cache_hit_rate": (
                self.stats.cache_hits / (self.stats.cache_hits + self.stats.cache_misses)
                if (self.stats.cache_hits + self.stats.cache_misses) > 0 else 0.0
            ),
            "algorithm_performance": {
                alg.value: dict(perf) for alg, perf in self._algorithm_performance.items()
                if perf["count"] > 0
            }
        }
    
    def clear_cache(self):
        """Clear compression cache."""
        cache_size = len(self._compression_cache)
        self._compression_cache.clear()
        self.logger.info(f"Cleared compression cache ({cache_size} entries)")
    
    def shutdown(self):
        """Shutdown compression middleware and cleanup resources."""
        if self.executor:
            self.executor.shutdown(wait=True)
        self.clear_cache()
        self.logger.info("Compression middleware shutdown complete")
