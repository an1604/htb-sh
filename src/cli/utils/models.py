# src/cli/utils/models.py
"""Data models for CLI interactions"""

from dataclasses import dataclass
from typing import Optional, List
from src.core.command import Parameter, Example


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


@dataclass
class CommandReviewData:
    """Command review data for confirmation panel"""
    tool: str
    id: str
    name: str
    command: str
    explanation: str
    parameters: List[Parameter]
    examples: List[Example]
    tags: List[str]
