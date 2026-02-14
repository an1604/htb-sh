# src/core/flow.py
"""Flow and FlowStep data models for multi-step workflows."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .command import Parameter


@dataclass
class FlowStep:
    """A single step in a flow."""

    id: str
    command_ref: str  # Format: "tool:command_id"
    parameters: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization."""
        d: Dict = {
            "id": self.id,
            "command_ref": self.command_ref,
            "parameters": self.parameters,
        }
        if self.description is not None:
            d["description"] = self.description
        if self.notes is not None:
            d["notes"] = self.notes
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> "FlowStep":
        """Create FlowStep from dictionary (YAML deserialization)."""
        return cls(
            id=data["id"],
            command_ref=data["command_ref"],
            parameters=data.get("parameters", {}),
            description=data.get("description"),
            notes=data.get("notes"),
        )


@dataclass
class Flow:
    """A reusable workflow that generates scripts (no execution)."""

    id: str
    name: str
    description: str
    steps: List[FlowStep] = field(default_factory=list)
    flow_parameters: List[Parameter] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    default_format: str = "bash"
    add_error_handling: bool = True
    add_comments: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "flow": self.id,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "flow_parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                }
                for p in self.flow_parameters
            ],
            "steps": [s.to_dict() for s in self.steps],
            "tags": self.tags,
            "notes": self.notes,
            "default_format": self.default_format,
            "add_error_handling": self.add_error_handling,
            "add_comments": self.add_comments,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Flow":
        """Create Flow from dictionary (YAML deserialization)."""
        flow_params = [
            Parameter(**p) for p in data.get("flow_parameters", [])
        ]
        steps = [FlowStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            steps=steps,
            flow_parameters=flow_params,
            tags=data.get("tags", []),
            notes=data.get("notes"),
            default_format=data.get("default_format", "bash"),
            add_error_handling=data.get("add_error_handling", True),
            add_comments=data.get("add_comments", True),
        )
