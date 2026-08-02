"""
Latency and Performance Monitoring Utility.
"""

import time
from typing import Callable, Any
from functools import wraps
from utils.logger import logger

class Timer:
    """
    Context manager to measure execution time of code blocks.
    
    Usage:
        with Timer("Speech Recognition"):
            transcribe_audio()
    """
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = 0.0
        self.elapsed_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time = time.perf_counter() - self.start_time
        logger.info(f"[Timer] {self.name} completed in {self.elapsed_time:.3f}s")


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure execution time of functions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"[Timer] Function '{func.__name__}' executed in {elapsed:.3f}s")
        return result
    return wrapper
