# tests/test_flow.py
"""Tests for Flow and FlowStep models."""

import pytest
from src.core.flow import Flow, FlowStep
from src.core.command import Parameter


class TestFlowStep:
    """Test FlowStep data class."""

    def test_create_flow_step(self):
        """Test creating a FlowStep."""
        step = FlowStep(
            id="step1",
            command_ref="nmap:basic-scan",
            parameters={"target": "{target}"},
            description="Scan target",
            notes="First step",
        )
        assert step.id == "step1"
        assert step.command_ref == "nmap:basic-scan"
        assert step.parameters == {"target": "{target}"}
        assert step.description == "Scan target"
        assert step.notes == "First step"

    def test_create_flow_step_minimal(self):
        """Test creating a FlowStep with only required fields."""
        step = FlowStep(id="s1", command_ref="tool:cmd-id")
        assert step.parameters == {}
        assert step.description is None
        assert step.notes is None

    def test_flow_step_to_dict(self, sample_flow_step):
        """Test FlowStep to_dict serialization."""
        data = sample_flow_step.to_dict()
        assert data["id"] == "list-shares"
        assert data["command_ref"] == "smbclient:lists-the-available-smb-shares"
        assert data["parameters"] == {"host": "{target}"}
        assert data["description"] == "List all SMB shares"
        assert data["notes"] == "Run first"

    def test_flow_step_from_dict(self):
        """Test FlowStep from_dict deserialization."""
        data = {
            "id": "step1",
            "command_ref": "nmap:basic-scan",
            "parameters": {"target": "{ip}"},
            "description": "Scan",
            "notes": "Optional",
        }
        step = FlowStep.from_dict(data)
        assert step.id == "step1"
        assert step.command_ref == "nmap:basic-scan"
        assert step.parameters == {"target": "{ip}"}
        assert step.description == "Scan"
        assert step.notes == "Optional"

    def test_flow_step_round_trip(self, sample_flow_step):
        """Test FlowStep to_dict -> from_dict round-trip."""
        data = sample_flow_step.to_dict()
        restored = FlowStep.from_dict(data)
        assert restored.id == sample_flow_step.id
        assert restored.command_ref == sample_flow_step.command_ref
        assert restored.parameters == sample_flow_step.parameters
        assert restored.description == sample_flow_step.description
        assert restored.notes == sample_flow_step.notes


class TestFlow:
    """Test Flow data class."""

    def test_create_flow(self, sample_flow):
        """Test creating a Flow."""
        assert sample_flow.id == "smb-enumeration"
        assert sample_flow.name == "SMB Enumeration"
        assert sample_flow.description == "List shares and connect"
        assert len(sample_flow.steps) == 1
        assert len(sample_flow.flow_parameters) == 2
        assert sample_flow.tags == ["enumeration", "smb"]
        assert sample_flow.default_format == "bash"
        assert sample_flow.add_error_handling is True
        assert sample_flow.add_comments is True

    def test_flow_to_dict(self, sample_flow):
        """Test Flow to_dict serialization."""
        data = sample_flow.to_dict()
        assert data["flow"] == "smb-enumeration"
        assert data["id"] == "smb-enumeration"
        assert data["name"] == "SMB Enumeration"
        assert len(data["flow_parameters"]) == 2
        assert data["flow_parameters"][0]["name"] == "target"
        assert data["flow_parameters"][1]["default"] == "guest"
        assert len(data["steps"]) == 1
        assert data["steps"][0]["command_ref"] == "smbclient:lists-the-available-smb-shares"
        assert data["tags"] == ["enumeration", "smb"]
        assert data["default_format"] == "bash"

    def test_flow_from_dict(self):
        """Test Flow from_dict deserialization."""
        data = {
            "id": "my-flow",
            "name": "My Flow",
            "description": "A test flow",
            "flow_parameters": [
                {"name": "target", "description": "IP", "required": True, "default": None},
            ],
            "steps": [
                {
                    "id": "s1",
                    "command_ref": "nmap:scan",
                    "parameters": {"target": "{target}"},
                },
            ],
            "tags": ["test"],
            "notes": None,
            "default_format": "python",
            "add_error_handling": False,
            "add_comments": False,
        }
        flow = Flow.from_dict(data)
        assert flow.id == "my-flow"
        assert flow.name == "My Flow"
        assert len(flow.flow_parameters) == 1
        assert flow.flow_parameters[0].name == "target"
        assert len(flow.steps) == 1
        assert flow.steps[0].command_ref == "nmap:scan"
        assert flow.default_format == "python"
        assert flow.add_error_handling is False
        assert flow.add_comments is False

    def test_flow_round_trip(self, sample_flow):
        """Test Flow to_dict -> from_dict round-trip."""
        data = sample_flow.to_dict()
        restored = Flow.from_dict(data)
        assert restored.id == sample_flow.id
        assert restored.name == sample_flow.name
        assert restored.description == sample_flow.description
        assert len(restored.steps) == len(sample_flow.steps)
        assert restored.steps[0].id == sample_flow.steps[0].id
        assert len(restored.flow_parameters) == len(sample_flow.flow_parameters)
        assert restored.flow_parameters[0].name == sample_flow.flow_parameters[0].name
        assert restored.tags == sample_flow.tags
        assert restored.default_format == sample_flow.default_format
