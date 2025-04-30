"""
File I/O Utilities

This module provides functions for reading and writing different file formats,
as well as other file system operations used throughout the application.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# YAML support is optional to avoid unnecessary dependencies
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)

def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory: Path to the directory to check/create
        
    Returns:
        Path object for the directory
    """
    path = Path(directory)
    if not path.exists():
        logger.debug(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)
    return path

def file_exists(filepath: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if the file exists, False otherwise
    """
    return Path(filepath).is_file()

def list_files(directory: Union[str, Path], pattern: Optional[str] = None) -> List[Path]:
    """
    List files in a directory, optionally matching a pattern.
    
    Args:
        directory: Path to the directory to list
        pattern: Optional glob pattern to filter files
        
    Returns:
        List of Path objects for the files
    """
    path = Path(directory)
    if not path.exists():
        logger.warning(f"Directory does not exist: {path}")
        return []
    
    if pattern:
        return list(path.glob(pattern))
    else:
        return [p for p in path.iterdir() if p.is_file()]

def read_json(filepath: Union[str, Path], default: Optional[Any] = None) -> Any:
    """
    Read JSON data from a file.
    
    Args:
        filepath: Path to the JSON file
        default: Value to return if file doesn't exist or can't be parsed
        
    Returns:
        Parsed JSON data or default value
    """
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"JSON file does not exist: {path}")
        return default
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        logger.error(f"Error reading JSON file {path}: {str(e)}")
        return default

def write_json(filepath: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """
    Write data to a JSON file.
    
    Args:
        filepath: Path to the JSON file
        data: Data to write
        indent: Indentation level for pretty-printing
        
    Returns:
        True if successful, False otherwise
    """
    path = Path(filepath)
    
    # Make sure the directory exists
    ensure_directory(path.parent)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (TypeError, OSError) as e:
        logger.error(f"Error writing JSON file {path}: {str(e)}")
        return False

def read_yaml(filepath: Union[str, Path], default: Optional[Any] = None) -> Any:
    """
    Read YAML data from a file.
    
    Args:
        filepath: Path to the YAML file
        default: Value to return if file doesn't exist or can't be parsed
        
    Returns:
        Parsed YAML data or default value
    """
    if not YAML_AVAILABLE:
        logger.error("YAML support not available. Install PyYAML to use this feature.")
        return default
    
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"YAML file does not exist: {path}")
        return default
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, UnicodeDecodeError, OSError) as e:
        logger.error(f"Error reading YAML file {path}: {str(e)}")
        return default

def write_yaml(filepath: Union[str, Path], data: Any) -> bool:
    """
    Write data to a YAML file.
    
    Args:
        filepath: Path to the YAML file
        data: Data to write
        
    Returns:
        True if successful, False otherwise
    """
    if not YAML_AVAILABLE:
        logger.error("YAML support not available. Install PyYAML to use this feature.")
        return False
    
    path = Path(filepath)
    
    # Make sure the directory exists
    ensure_directory(path.parent)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except (TypeError, OSError) as e:
        logger.error(f"Error writing YAML file {path}: {str(e)}")
        return False

def read_text(filepath: Union[str, Path], default: Optional[str] = None) -> Optional[str]:
    """
    Read text from a file.
    
    Args:
        filepath: Path to the text file
        default: Value to return if file doesn't exist or can't be read
        
    Returns:
        File contents as string or default value
    """
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Text file does not exist: {path}")
        return default
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except (UnicodeDecodeError, OSError) as e:
        logger.error(f"Error reading text file {path}: {str(e)}")
        return default

def write_text(filepath: Union[str, Path], content: str) -> bool:
    """
    Write text to a file.
    
    Args:
        filepath: Path to the text file
        content: Text content to write
        
    Returns:
        True if successful, False otherwise
    """
    path = Path(filepath)
    
    # Make sure the directory exists
    ensure_directory(path.parent)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except OSError as e:
        logger.error(f"Error writing text file {path}: {str(e)}")
        return False 