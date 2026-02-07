# tests/test_storage.py
"""Tests for Storage class"""

import pytest
from src.core.storage import Storage
from src.core.command import Command, Parameter


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
