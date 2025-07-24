# File: /ai_interlinq/middleware/compression.py
# Directory: /ai_interlinq/middleware

"""
Compression middleware for AI-Interlinq framework.
Provides multi-algorithm compression with auto-selection based on content type and size.
"""

import gzip
import zlib
import lz4.frame
import brotli
import json
import pickle
from typing import Dict, Any, Tuple, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Supported compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    LZ4 = "lz4"
    BROTLI = "brotli"

@dataclass
class CompressionResult:
    """Compression operation result."""
    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    data: bytes

class CompressionMiddleware:
    """
    Multi-algorithm compression middleware with intelligent selection.
    
    Features:
    - Multiple compression algorithms (gzip, zlib, LZ4, Brotli)
    - Automatic algorithm selection based on content
    - Size-based compression thresholds
    - Performance metrics tracking
    - Content-type aware compression
    """
    
    def __init__(
        self,
        min_size_threshold: int = 1024,
        max_compression_time: float = 0.5,
        preferred_algorithm: CompressionAlgorithm = CompressionAlgorithm.LZ4,
        auto_select: bool = True
    ):
        """
        Initialize compression middleware.
        
        Args:
            min_size_threshold: Minimum size in bytes to compress
            max_compression_time: Maximum compression time in seconds
            preferred_algorithm: Default compression algorithm
            auto_select: Enable automatic algorithm selection
        """
        self.min_size_threshold = min_size_threshold
        self.max_compression_time = max_compression_time
        self.preferred_algorithm = preferred_algorithm
        self.auto_select = auto_select
        
        # Algorithm configurations
        self.algorithm_configs = {
            CompressionAlgorithm.GZIP: {
                "compresslevel": 6,
                "good_for": ["text", "json", "xml"],
                "speed": "medium",
                "ratio": "high"
            },
            CompressionAlgorithm.ZLIB: {
                "level": 6,
                "good_for": ["general", "mixed"],
                "speed": "medium", 
                "ratio": "medium"
            },
            CompressionAlgorithm.LZ4: {
                "compression_level": 1,
                "good_for": ["realtime", "streaming"],
                "speed": "very_fast",
                "ratio": "low"
            },
            CompressionAlgorithm.BROTLI: {
                "quality": 4,
                "good_for": ["web", "text", "repetitive"],
                "speed": "slow",
                "ratio": "very_high"
            }
        }
        
        # Performance tracking
        self.compression_stats = {
            "total_compressions": 0,
            "total_decompressions": 0,
            "bytes_compressed": 0,
            "bytes_saved": 0,
            "avg_compression_time": 0.0,
            "algorithm_usage": {alg: 0 for alg in CompressionAlgorithm}
        }
        
    def compress(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        algorithm: Optional[CompressionAlgorithm] = None,
        content_type: Optional[str] = None
    ) -> CompressionResult:
        """
        Compress data using specified or auto-selected algorithm.
        
        Args:
            data: Data to compress
            algorithm: Compression algorithm to use
            content_type: Content type hint for algorithm selection
            
        Returns:
            CompressionResult with compressed data and metadata
        """
        start_time = time.time()
        
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
            if not content_type:
                content_type = "text"
        elif isinstance(data, dict):
            data_bytes = json.dumps(data).encode('utf-8')
            if not content_type:
                content_type = "json"
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            # Serialize using pickle for complex objects
            data_bytes = pickle.dumps(data)
            if not content_type:
                content_type = "binary"
                
        original_size = len(data_bytes)
        
        # Check size threshold
        if original_size < self.min_size_threshold:
            return CompressionResult(
                algorithm=CompressionAlgorithm.NONE,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                compression_time=0.0,
                data=data_bytes
            )
            
        # Select algorithm
        if not algorithm:
            algorithm = self._select_algorithm(data_bytes, content_type)
            
        # Perform compression
        try:
            compressed_data = self._compress_with_algorithm(data_bytes, algorithm)
            compression_time = time.time() - start_time
            
            # Check if compression is beneficial
            if len(compressed_data) >= original_size * 0.95:  # Less than 5% savings
                return CompressionResult(
                    algorithm=CompressionAlgorithm.NONE,
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=1.0,
                    compression_time=compression_time,
                    data=data_bytes
                )
                
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size
            
            # Update statistics
            self._update_compression_stats(
                algorithm, original_size, compressed_size, compression_time
            )
            
            return CompressionResult(
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                data=compressed_data
            )
            
        except Exception as e:
            logger.error(f"Compression failed with {algorithm.value}: {e}")
            # Fallback to no compression
            return CompressionResult(
                algorithm=CompressionAlgorithm.NONE,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                compression_time=time.time() - start_time,
                data=data_bytes
            )
            
    def decompress(
        self,
        compressed_data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """
        Decompress data using specified algorithm.
        
        Args:
            compressed_data: Compressed data bytes
            algorithm: Algorithm used for compression
            
        Returns:
            Decompressed data bytes
        """
        if algorithm == CompressionAlgorithm.NONE:
            return compressed_data
            
        try:
            decompressed_data = self._decompress_with_algorithm(
                compressed_data, algorithm
            )
            
            # Update statistics
            self.compression_stats["total_decompressions"] += 1
            
            return decompressed_data
            
        except Exception as e:
            logger.error(f"Decompression failed with {algorithm.value}: {e}")
            raise
            
    def _select_algorithm(
        self,
        data: bytes,
        content_type: Optional[str] = None
    ) -> CompressionAlgorithm:
        """
        Automatically select best compression algorithm.
        
        Args:
            data: Data to compress
            content_type: Content type hint
            
        Returns:
            Selected compression algorithm
        """
        if not self.auto_select:
            return self.preferred_algorithm
            
        data_size = len(data)
        
        # For very large data, prefer speed
        if data_size > 10 * 1024 * 1024:  # > 10MB
            return CompressionAlgorithm.LZ4
            
        # For real-time applications, prefer speed
        if content_type == "realtime":
            return CompressionAlgorithm.LZ4
            
        # For text/JSON, prefer compression ratio
        if content_type in ["text", "json", "xml"]:
            if data_size > 1024 * 1024:  # > 1MB
                return CompressionAlgorithm.GZIP
            else:
                return CompressionAlgorithm.BROTLI
                
        # For binary data, use balanced approach
        if content_type == "binary":
            return CompressionAlgorithm.ZLIB
            
        # Default to preferred algorithm
        return self.preferred_algorithm
        
    def _compress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """Compress data with specific algorithm."""
        if algorithm == CompressionAlgorithm.GZIP:
            config = self.algorithm_configs[algorithm]
            return gzip.compress(data, compresslevel=config["compresslevel"])
            
        elif algorithm == CompressionAlgorithm.ZLIB:
            config = self.algorithm_configs[algorithm]
            return zlib.compress(data, level=config["level"])
            
        elif algorithm == CompressionAlgorithm.LZ4:
            config = self.algorithm_configs[algorithm]
            return lz4.frame.compress(
                data,
                compression_level=config["compression_level"]
            )
            
        elif algorithm == CompressionAlgorithm.BROTLI:
            config = self.algorithm_configs[algorithm]
            return brotli.compress(data, quality=config["quality"])
            
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
            
    def _decompress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """Decompress data with specific algorithm."""
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(data)
            
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(data)
            
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.decompress(data)
            
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.decompress(data)
            
        else:
            raise ValueError(f"Unsupported decompression algorithm: {algorithm}")
            
    def _update_compression_stats(
        self,
        algorithm: CompressionAlgorithm,
        original_size: int,
        compressed_size: int,
        compression_time: float
    ):
        """Update compression statistics."""
        stats = self.compression_stats
        stats["total_compressions"] += 1
        stats["bytes_compressed"] += original_size
        stats["bytes_saved"] += (original_size - compressed_size)
        stats["algorithm_usage"][algorithm] += 1
        
        # Update average compression time
        total_compressions = stats["total_compressions"]
        current_avg = stats["avg_compression_time"]
        stats["avg_compression_time"] = (
            (current_avg * (total_compressions - 1) + compression_time) / 
            total_compressions
        )
        
    async def middleware_handler(
        self,
        message: Dict[str, Any],
        next_handler: Callable
    ) -> Dict[str, Any]:
        """
        Middleware handler for message compression.
        
        Args:
            message: Message to process
            next_handler: Next middleware in chain
            
        Returns:
            Processed message with compression metadata
        """
        # Check if compression is requested
        compress_message = message.get("compress", True)
        compression_algorithm = message.get("compression_algorithm")
        content_type = message.get("content_type")
        
        if compress_message and "data" in message:
            # Compress message data
            result = self.compress(
                data=message["data"],
                algorithm=compression_algorithm,
                content_type=content_type
            )
            
            # Update message with compressed data
            if result.algorithm != CompressionAlgorithm.NONE:
                message["data"] = result.data
                message["compression"] = {
                    "algorithm": result.algorithm.value,
                    "original_size": result.original_size,
                    "compressed_size": result.compressed_size,
                    "compression_ratio": result.compression_ratio,
                    "compression_time": result.compression_time
                }
                
                logger.debug(
                    f"Compressed message: {result.original_size} -> "
                    f"{result.compressed_size} bytes "
                    f"({result.compression_ratio:.2f}x ratio) "
                    f"using {result.algorithm.value}"
                )
                
        # Process message through next handler
        response = await next_handler(message)
        
        # Decompress response if needed
        if isinstance(response, dict) and "compression" in response:
            compression_info = response["compression"]
            algorithm = CompressionAlgorithm(compression_info["algorithm"])
            
            if algorithm != CompressionAlgorithm.NONE:
                response["data"] = self.decompress(
                    response["data"], algorithm
                )
                
                # Remove compression metadata from final response
                del response["compression"]
                
        return response
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get compression statistics."""
        stats = self.compression_stats.copy()
        stats["algorithm_usage"] = {
            alg.value: count for alg, count in stats["algorithm_usage"].items()
        }
        
        # Calculate compression efficiency
        if stats["bytes_compressed"] > 0:
            stats["compression_efficiency"] = (
                stats["bytes_saved"] / stats["bytes_compressed"]
            )
        else:
            stats["compression_efficiency"] = 0.0
            
        return stats
        
    def reset_statistics(self):
        """Reset compression statistics."""
        self.compression_stats = {
            "total_compressions": 0,
            "total_decompressions": 0,
            "bytes_compressed": 0,
            "bytes_saved": 0,
            "avg_compression_time": 0.0,
            "algorithm_usage": {alg: 0 for alg in CompressionAlgorithm}
        }
        
    def benchmark_algorithms(
        self,
        test_data: bytes,
        iterations: int = 5
    ) -> Dict[str, Dict[str, float]]:
        """
        Benchmark compression algorithms on test data.
        
        Args:
            test_data: Data to use for benchmarking
            iterations: Number of iterations to average
            
        Returns:
            Benchmark results for each algorithm
        """
        results = {}
        
        for algorithm in CompressionAlgorithm:
            if algorithm == CompressionAlgorithm.NONE:
                continue
                
            total_compression_time = 0
            total_decompression_time = 0
            compressed_size = 0
            
            for _ in range(iterations):
                # Compression benchmark
                start_time = time.time()
                compressed_data = self._compress_with_algorithm(test_data, algorithm)
                compression_time = time.time() - start_time
                
                # Decompression benchmark
                start_time = time.time()
                self._decompress_with_algorithm(compressed_data, algorithm)
                decompression_time = time.time() - start_time
                
                total_compression_time += compression_time
                total_decompression_time += decompression_time
                compressed_size = len(compressed_data)
                
            results[algorithm.value] = {
                "avg_compression_time": total_compression_time / iterations,
                "avg_decompression_time": total_decompression_time / iterations,
                "compression_ratio": len(test_data) / compressed_size,
                "compressed_size": compressed_size,
                "original_size": len(test_data)
            }
            
        return results
