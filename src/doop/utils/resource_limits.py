"""
Resource limitation utilities for the DOOP language.

These utilities help prevent resource exhaustion attacks.
"""

import time
import threading
from typing import TypeVar, Callable, Any, Optional, Dict, List
import signal
import resource
import sys
import os


DEFAULT_LIMITS = {
    'max_file_size': 10 * 1024 * 1024,  # 10 MB
    'max_components': 500,              # Maximum components per project
    'max_relationships': 1000,          # Maximum relationships
    'max_execution_time': 60,           # Seconds for execution timeout
    'max_memory': 1024 * 1024 * 1024,   # 1 GB memory limit
    'max_recursion_depth': 1000,        # Maximum recursion depth
}


class ResourceLimiter:
    """
    Resource limiter to prevent resource exhaustion.
    """
    
    def __init__(self, limits: Optional[Dict[str, int]] = None):
        """
        Initialize with custom or default limits.
        
        Args:
            limits: Optional dict of custom limits
        """
        self.limits = DEFAULT_LIMITS.copy()
        if limits:
            self.limits.update(limits)
    
    def check_file_size(self, file_path: str) -> bool:
        """
        Check if a file is within the size limit.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if within limits, False otherwise
        """
        size = os.path.getsize(file_path)
        return size <= self.limits['max_file_size']
    
    def check_component_count(self, count: int) -> bool:
        """
        Check if component count is within limits.
        
        Args:
            count: Number of components
            
        Returns:
            True if within limits, False otherwise
        """
        return count <= self.limits['max_components']
    
    def check_relationship_count(self, count: int) -> bool:
        """
        Check if relationship count is within limits.
        
        Args:
            count: Number of relationships
            
        Returns:
            True if within limits, False otherwise
        """
        return count <= self.limits['max_relationships']
    
    def set_process_limits(self):
        """
        Set process-wide resource limits.
        
        Note: This only works on Unix-like systems.
        """
        if sys.platform == 'win32':
            # Windows doesn't support the resource module
            return
        
        # Set memory limit
        try:
            resource.setrlimit(
                resource.RLIMIT_AS, 
                (self.limits['max_memory'], self.limits['max_memory'])
            )
        except (ValueError, resource.error):
            print("Warning: Could not set memory limit", file=sys.stderr)
        
        # Set CPU time limit
        try:
            resource.setrlimit(
                resource.RLIMIT_CPU, 
                (self.limits['max_execution_time'], self.limits['max_execution_time'])
            )
        except (ValueError, resource.error):
            print("Warning: Could not set CPU time limit", file=sys.stderr)
        
        # Set recursion limit
        sys.setrecursionlimit(self.limits['max_recursion_depth'])


T = TypeVar('T')

def with_timeout(timeout: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to apply timeout to a function.
    
    Args:
        timeout: Timeout in seconds
        
    Returns:
        Decorated function
        
    Example:
        @with_timeout(10)
        def long_running_function():
            # ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = [None]  # Mutable container for result
            exception = [None]  # Mutable container for exception
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            
            thread.start()
            thread.join(timeout)
            
            if thread.is_alive():
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
            
            if exception[0]:
                raise exception[0]
                
            return result[0]
        
        return wrapper
    
    return decorator