"""
Data Processing Utilities

This module provides functions for processing, transforming, and
validating data structures used throughout the application.
"""

import copy
import logging
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Set, Tuple

logger = logging.getLogger(__name__)

T = TypeVar('T')

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                overwrite: bool = True) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.
    
    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge into dict1
        overwrite: Whether to overwrite existing values in dict1
        
    Returns:
        New merged dictionary
    """
    result = copy.deepcopy(dict1)
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            # Add or overwrite value
            result[key] = copy.deepcopy(value)
            
    return result

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary into a single-level dictionary with key paths.
    
    Args:
        d: Dictionary to flatten
        parent_key: Prefix for keys
        sep: Separator for key path components
        
    Returns:
        Flattened dictionary
    """
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
            
    return dict(items)

def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    Restore a flattened dictionary to its nested structure.
    
    Args:
        d: Flattened dictionary
        sep: Separator used in key paths
        
    Returns:
        Nested dictionary
    """
    result = {}
    
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        
        # Navigate to the correct nested dictionary
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            
        # Set the value in the deepest level
        current[parts[-1]] = value
        
    return result

def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a dictionary against a simple schema.
    
    Args:
        data: Dictionary to validate
        schema: Schema dictionary with keys and type hints
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    for key, expected_type in schema.items():
        # Check required fields
        if key not in data:
            errors.append(f"Missing required field: {key}")
            continue
            
        value = data[key]
        
        # Handle "any" type
        if expected_type == Any:
            continue
            
        # Handle list types with element validation
        if isinstance(expected_type, list) and len(expected_type) == 1 and isinstance(value, list):
            element_type = expected_type[0]
            for i, item in enumerate(value):
                if not isinstance(item, element_type):
                    errors.append(f"Element {i} in field '{key}' should be {element_type.__name__}, got {type(item).__name__}")
            continue
                
        # Handle dict types with nested schema
        if isinstance(expected_type, dict) and isinstance(value, dict):
            valid, nested_errors = validate_schema(value, expected_type)
            if not valid:
                errors.extend([f"{key}.{e}" for e in nested_errors])
            continue
                
        # Handle regular type validation
        if not isinstance(value, expected_type):
            errors.append(f"Field '{key}' should be {expected_type.__name__}, got {type(value).__name__}")
    
    return len(errors) == 0, errors

def filter_dict(d: Dict[str, Any], 
                condition: Callable[[str, Any], bool]) -> Dict[str, Any]:
    """
    Filter a dictionary by key-value pairs.
    
    Args:
        d: Dictionary to filter
        condition: Function that takes key and value and returns boolean
        
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in d.items() if condition(k, v)}

def transform_data(data: Any, 
                   transformation: Callable[[Any], Any]) -> Any:
    """
    Apply a transformation function to data.
    
    Args:
        data: Data to transform
        transformation: Function to apply
        
    Returns:
        Transformed data
    """
    try:
        return transformation(data)
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        return data

def extract_fields(data: Dict[str, Any], 
                   fields: List[str]) -> Dict[str, Any]:
    """
    Extract specific fields from a dictionary.
    
    Args:
        data: Source dictionary
        fields: List of field names to extract
        
    Returns:
        Dictionary with only the specified fields
    """
    return {field: data[field] for field in fields if field in data}

def sort_by_key(data: Dict[str, T], 
                reverse: bool = False) -> Dict[str, T]:
    """
    Sort a dictionary by its keys.
    
    Args:
        data: Dictionary to sort
        reverse: Whether to sort in descending order
        
    Returns:
        Sorted dictionary
    """
    return {k: data[k] for k in sorted(data.keys(), reverse=reverse)} 