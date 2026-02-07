# src/cli/utils/models.py
"""Data models for CLI interactions"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandDetails:
    """Command details collected during interactive input"""
    id: str
    name: str
    command: str
    explanation: str


@dataclass
class ExampleDetails:
    """Example details collected during interactive input"""
    input: str
    output: str
    description: Optional[str] = None
