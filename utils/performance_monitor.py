"""
Performance monitoring utilities for OpenFood backend
"""
import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.slow_queries = []
        self.threshold_seconds = 2.0  # Alert if operation takes more than 2 seconds
    
    def track_time(self, operation_name: str):
        """Decorator to track execution time of functions"""
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metric(operation_name, execution_time, True)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_metric(operation_name, execution_time, False)
                    raise e
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metric(operation_name, execution_time, True)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_metric(operation_name, execution_time, False)
                    raise e
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator
    
    def _record_metric(self, operation_name: str, execution_time: float, success: bool):
        """Record performance metric"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'total_calls': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'success_count': 0,
                'error_count': 0
            }
        
        metric = self.metrics[operation_name]
        metric['total_calls'] += 1
        metric['total_time'] += execution_time
        metric['avg_time'] = metric['total_time'] / metric['total_calls']
        metric['min_time'] = min(metric['min_time'], execution_time)
        metric['max_time'] = max(metric['max_time'], execution_time)
        
        if success:
            metric['success_count'] += 1
        else:
            metric['error_count'] += 1
        
        # Log slow operations
        if execution_time > self.threshold_seconds:
            slow_query = {
                'operation': operation_name,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'success': success
            }
            self.slow_queries.append(slow_query)
            logger.warning(f"SLOW OPERATION: {operation_name} took {execution_time:.2f}s")
            
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics"""
        return {
            'metrics': self.metrics,
            'slow_queries': self.slow_queries[-10:],  # Last 10 slow queries
            'total_operations': sum(m['total_calls'] for m in self.metrics.values()),
            'avg_response_time': sum(m['avg_time'] for m in self.metrics.values()) / len(self.metrics) if self.metrics else 0
        }
    
    def get_slowest_operations(self, limit: int = 5) -> list:
        """Get slowest operations by average time"""
        sorted_ops = sorted(
            self.metrics.items(),
            key=lambda x: x[1]['avg_time'],
            reverse=True
        )
        return sorted_ops[:limit]

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# Convenience decorators
def track_performance(operation_name: str):
    """Decorator to track performance of a function"""
    return perf_monitor.track_time(operation_name)

def log_execution_time(func_name: str = None):
    """Simple decorator to log execution time"""
    def decorator(func):
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                logger.info(f"⏱️  {name}: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"❌ {name}: {duration:.3f}s (ERROR: {str(e)})")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                logger.info(f"⏱️  {name}: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"❌ {name}: {duration:.3f}s (ERROR: {str(e)})")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            logger.info(f"⏱️  {self.operation_name}: {duration:.3f}s")
        else:
            logger.error(f"❌ {self.operation_name}: {duration:.3f}s (ERROR)")

def time_operation(operation_name: str):
    """Create a timing context manager"""
    return TimingContext(operation_name)
