"""
Caching Utilities

This module provides functions for caching API responses and computation results
to reduce API costs and improve performance.
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from functools import wraps
from typing import Any, Dict, Optional, Union, Callable, TypeVar

from .file_io import ensure_directory, read_json, write_json, file_exists

logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar('T')

# Default location for cache files
DEFAULT_CACHE_DIR = os.path.expanduser("~/.saas-pipeline/cache")

def _get_cache_key(func_name: str, args: tuple, kwargs: Dict[str, Any]) -> str:
    """
    Generate a unique cache key based on function name and arguments.
    
    Args:
        func_name: Name of the function being cached
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Unique hash string to use as cache key
    """
    # Convert args and kwargs to a string representation
    args_str = str(args) + str(sorted(kwargs.items()))
    
    # Create a hash of the function name and arguments
    hash_obj = hashlib.md5(f"{func_name}:{args_str}".encode('utf-8'))
    return hash_obj.hexdigest()

def _get_cache_path(cache_key: str, cache_dir: Optional[str] = None) -> Path:
    """
    Get the file path for a cache key.
    
    Args:
        cache_key: Cache key string
        cache_dir: Directory to store cache files
        
    Returns:
        Path object for the cache file
    """
    cache_dir = cache_dir or DEFAULT_CACHE_DIR
    ensure_directory(cache_dir)
    
    # Use a two-level directory structure to avoid too many files in one directory
    subdir = cache_key[:2]
    cache_subdir = os.path.join(cache_dir, subdir)
    ensure_directory(cache_subdir)
    
    return Path(os.path.join(cache_subdir, f"{cache_key}.json"))

def cache_result(
    ttl: int = 86400,  # Default TTL: 1 day
    cache_dir: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache function results in a JSON file.
    
    Args:
        ttl: Time-to-live for cache entries in seconds
        cache_dir: Directory to store cache files
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Check if caching is explicitly disabled
            skip_cache = kwargs.pop('skip_cache', False)
            if skip_cache:
                return func(*args, **kwargs)
                
            # Generate cache key and path
            cache_key = _get_cache_key(func.__name__, args, kwargs)
            cache_path = _get_cache_path(cache_key, cache_dir)
            
            # Try to load from cache if it exists
            if file_exists(cache_path):
                cache_data = read_json(cache_path)
                if cache_data:
                    # Check if the cache is still valid
                    timestamp = cache_data.get('timestamp', 0)
                    if time.time() - timestamp <= ttl:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cache_data.get('result')
                    else:
                        logger.debug(f"Cache expired for {func.__name__}")
            
            # Cache miss or expired, call the function
            result = func(*args, **kwargs)
            
            # Save the result to cache
            cache_data = {
                'timestamp': time.time(),
                'result': result
            }
            write_json(cache_path, cache_data)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
            
        return wrapper
    return decorator

def invalidate_cache(
    cache_key: Optional[str] = None,
    func_name: Optional[str] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    cache_dir: Optional[str] = None
) -> bool:
    """
    Invalidate a specific cache entry.
    
    Args:
        cache_key: Specific cache key to invalidate
        func_name: Function name for which to generate cache key
        args: Function args for which to generate cache key
        kwargs: Function kwargs for which to generate cache key
        cache_dir: Directory where cache files are stored
        
    Returns:
        True if cache was invalidated, False otherwise
    """
    # If cache_key is not provided, generate it from function info
    if cache_key is None:
        if func_name is None or args is None:
            logger.error("Must provide either cache_key or (func_name and args)")
            return False
        kwargs = kwargs or {}
        cache_key = _get_cache_key(func_name, args, kwargs)
    
    # Get the cache file path
    cache_path = _get_cache_path(cache_key, cache_dir)
    
    # Delete the cache file if it exists
    if file_exists(cache_path):
        try:
            os.remove(cache_path)
            logger.debug(f"Invalidated cache for key {cache_key}")
            return True
        except OSError as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return False
    else:
        logger.debug(f"No cache found for key {cache_key}")
        return False

def get_cached(
    cache_key: str,
    default: Optional[Any] = None,
    cache_dir: Optional[str] = None
) -> Any:
    """
    Retrieve a value from cache without going through the decorator.
    
    Args:
        cache_key: Cache key to retrieve
        default: Default value to return if cache entry doesn't exist
        cache_dir: Directory where cache files are stored
        
    Returns:
        Cached value or default
    """
    cache_path = _get_cache_path(cache_key, cache_dir)
    
    if file_exists(cache_path):
        cache_data = read_json(cache_path)
        if cache_data:
            return cache_data.get('result', default)
    
    return default

def cache_exists(
    cache_key: str,
    ttl: Optional[int] = None,
    cache_dir: Optional[str] = None
) -> bool:
    """
    Check if a valid cache entry exists.
    
    Args:
        cache_key: Cache key to check
        ttl: Optional time-to-live to check expiration
        cache_dir: Directory where cache files are stored
        
    Returns:
        True if valid cache exists, False otherwise
    """
    cache_path = _get_cache_path(cache_key, cache_dir)
    
    if file_exists(cache_path):
        # If no TTL specified, just check existence
        if ttl is None:
            return True
            
        # Check if cache is still valid
        cache_data = read_json(cache_path)
        if cache_data:
            timestamp = cache_data.get('timestamp', 0)
            return time.time() - timestamp <= ttl
    
    return False

def clear_cache(
    cache_dir: Optional[str] = None,
    older_than: Optional[int] = None
) -> int:
    """
    Clear all cache entries or entries older than a specified time.
    
    Args:
        cache_dir: Directory where cache files are stored
        older_than: Only clear entries older than this many seconds
        
    Returns:
        Number of cache entries cleared
    """
    cache_dir = cache_dir or DEFAULT_CACHE_DIR
    
    if not os.path.exists(cache_dir):
        return 0
        
    count = 0
    current_time = time.time()
    
    # Walk through all subdirectories in the cache
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                # Check if we should delete based on age
                if older_than is not None:
                    try:
                        cache_data = read_json(file_path)
                        if cache_data:
                            timestamp = cache_data.get('timestamp', 0)
                            if current_time - timestamp <= older_than:
                                continue  # Skip this file as it's not old enough
                    except Exception:
                        # If we can't read the file, delete it anyway
                        pass
                        
                # Delete the file
                try:
                    os.remove(file_path)
                    count += 1
                except OSError:
                    pass
                    
    logger.debug(f"Cleared {count} cache entries")
    return count 