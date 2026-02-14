# tests/test_storage.py
"""Tests for Storage class"""

import pytest
from src.core.storage import Storage
from src.core.command import Command, Parameter
from src.core.flow import Flow, FlowStep


class TestStorage:
    """Test Storage class"""
    
    def test_storage_creates_directory(self, temp_dir):
        """Test storage creates data directory if it doesn't exist"""
        data_dir = temp_dir / "commands"
        storage = Storage(data_dir)
        
        assert data_dir.exists()
        assert data_dir.is_dir()
    
    def test_get_tool_file_path(self, storage):
        """Test getting tool file path"""
        file_path = storage.get_tool_file_path("nmap")
        
        assert file_path.name == "nmap.yaml"
        assert file_path.parent == storage.data_dir
    
    def test_save_and_load_tool_commands(self, storage, sample_command):
        """Test saving and loading commands"""
        # Save commands
        storage.save_tool_commands("nmap", [sample_command])
        
        # Load commands
        loaded_commands = storage.load_tool_commands("nmap")
        
        assert len(loaded_commands) == 1
        assert loaded_commands[0].id == "basic-scan"
        assert loaded_commands[0].name == "Basic Port Scan"
        assert len(loaded_commands[0].parameters) == 1
    
    def test_load_nonexistent_tool(self, storage):
        """Test loading commands for non-existent tool returns empty list"""
        commands = storage.load_tool_commands("nonexistent")
        
        assert commands == []
    
    def test_tool_exists(self, storage):
        """Test checking if tool file exists"""
        # Tool doesn't exist yet
        assert not storage.tool_exists("nmap")
        
        # Create tool file
        storage.create_tool_file("nmap", "Network scanner")
        
        # Tool now exists
        assert storage.tool_exists("nmap")
    
    def test_create_tool_file(self, storage):
        """Test creating a new tool file"""
        storage.create_tool_file("smb", "SMB enumeration tool")
        
        file_path = storage.get_tool_file_path("smb")
        assert file_path.exists()
        
        # Load and verify
        commands = storage.load_tool_commands("smb")
        assert commands == []
    
    def test_save_multiple_commands(self, storage):
        """Test saving multiple commands"""
        cmd1 = Command(
            id="scan-1",
            name="Scan 1",
            command="nmap {target}",
            explanation="First scan"
        )
        cmd2 = Command(
            id="scan-2",
            name="Scan 2",
            command="nmap -sV {target}",
            explanation="Second scan"
        )
        
        storage.save_tool_commands("nmap", [cmd1, cmd2])
        
        loaded = storage.load_tool_commands("nmap")
        assert len(loaded) == 2
        assert loaded[0].id == "scan-1"
        assert loaded[1].id == "scan-2"


class TestStorageFlows:
    """Test Storage flow-related methods."""

    def test_get_flows_dir(self, storage):
        """Test getting flows directory."""
        flows_dir = storage.get_flows_dir()
        assert flows_dir.name == "flows"
        assert flows_dir.exists()
        assert flows_dir.is_dir()

    def test_get_flow_file_path(self, storage):
        """Test getting flow file path."""
        path = storage.get_flow_file_path("my-flow")
        assert path.name == "my-flow.yaml"
        assert path.parent == storage.get_flows_dir()

    def test_load_flow_nonexistent(self, storage):
        """Test loading non-existent flow returns None."""
        assert storage.load_flow("nonexistent-flow") is None

    def test_save_and_load_flow(self, storage, sample_flow):
        """Test saving and loading a flow."""
        storage.save_flow(sample_flow)
        loaded = storage.load_flow(sample_flow.id)
        assert loaded is not None
        assert loaded.id == sample_flow.id
        assert loaded.name == sample_flow.name
        assert len(loaded.steps) == 1
        assert loaded.steps[0].command_ref == sample_flow.steps[0].command_ref
        assert len(loaded.flow_parameters) == 2

    def test_load_flows_empty(self, storage):
        """Test load_flows returns empty list when no flows exist."""
        flows = storage.load_flows()
        assert flows == []

    def test_load_flows_multiple(self, storage, sample_flow):
        """Test loading multiple flows."""
        storage.save_flow(sample_flow)
        flow2 = Flow(
            id="other-flow",
            name="Other",
            description="Other flow",
            steps=[],
            flow_parameters=[],
        )
        storage.save_flow(flow2)
        flows = storage.load_flows()
        assert len(flows) == 2
        ids = {f.id for f in flows}
        assert "smb-enumeration" in ids
        assert "other-flow" in ids

    def test_delete_flow(self, storage, sample_flow):
        """Test deleting a flow."""
        storage.save_flow(sample_flow)
        assert storage.flow_exists(sample_flow.id)
        result = storage.delete_flow(sample_flow.id)
        assert result is True
        assert not storage.flow_exists(sample_flow.id)
        assert storage.load_flow(sample_flow.id) is None

    def test_delete_flow_nonexistent(self, storage):
        """Test delete_flow on non-existent flow returns False."""
        assert storage.delete_flow("no-such-flow") is False

    def test_flow_exists(self, storage, sample_flow):
        """Test flow_exists."""
        assert not storage.flow_exists(sample_flow.id)
        storage.save_flow(sample_flow)
        assert storage.flow_exists(sample_flow.id)
