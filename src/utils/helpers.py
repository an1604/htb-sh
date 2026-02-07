# src/utils/helpers.py
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_data_dir(config: Dict[str, Any] = None) -> Path:
    """Get data directory path from config"""
    if config is None:
        config = load_config()
    
    data_dir = Path(config.get('data_dir', 'data/commands'))
    return data_dir


def get_categories(config: Dict[str, Any] = None) -> list:
    """Get available categories from config"""
    if config is None:
        config = load_config()
    
    return config.get('categories', [])


def get_tag_suggestions(config: Dict[str, Any] = None) -> list:
    """Get tag suggestions from config"""
    if config is None:
        config = load_config()
    
    return config.get('tag_suggestions', [])
