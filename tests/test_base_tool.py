# tests/test_base_tool.py
"""Tests for BaseTool abstract class"""

import pytest
from src.core.base_tool import BaseTool
from src.core.command import Command, Parameter


class TestTool(BaseTool):
    """Concrete test tool for testing BaseTool"""
    
    @property
    def name(self) -> str:
        return "test-tool"
    
    @property
    def description(self) -> str:
        return "Test tool for testing"
    
    @property
    def category(self) -> str:
        return "testing"


class TestBaseTool:
    """Test BaseTool abstract class"""
    
    @pytest.fixture
    def tool(self, storage):
        """Create a TestTool instance"""
        return TestTool(storage)
    
    def test_tool_properties(self, tool):
        """Test tool properties"""
        assert tool.name == "test-tool"
        assert tool.description == "Test tool for testing"
        assert tool.category == "testing"
    
    def test_add_command(self, tool, sample_command):
        """Test adding a command"""
        tool.add_command(sample_command)
        
        commands = tool.get_all_commands()
        assert len(commands) == 1
        assert commands[0].id == "basic-scan"
    
    def test_get_command(self, tool, sample_command):
        """Test getting a command by ID"""
        tool.add_command(sample_command)
        
        retrieved = tool.get_command("basic-scan")
        assert retrieved is not None
        assert retrieved.id == "basic-scan"
    
    def test_get_nonexistent_command(self, tool):
        """Test getting a non-existent command returns None"""
        result = tool.get_command("nonexistent")
        assert result is None
    
    def test_update_command(self, tool):
        """Test updating a command"""
        cmd = Command(
            id="test-cmd",
            name="Original Name",
            command="test {param}",
            explanation="Original"
        )
        
        tool.add_command(cmd)
        
        updated_cmd = Command(
            id="test-cmd",
            name="Updated Name",
            command="test {param}",
            explanation="Updated"
        )
        
        result = tool.update_command("test-cmd", updated_cmd)
        assert result is True
        
        retrieved = tool.get_command("test-cmd")
        assert retrieved.name == "Updated Name"
        assert retrieved.explanation == "Updated"
    
    def test_update_nonexistent_command(self, tool, sample_command):
        """Test updating non-existent command returns False"""
        result = tool.update_command("nonexistent", sample_command)
        assert result is False
    
    def test_delete_command(self, tool, sample_command):
        """Test deleting a command"""
        tool.add_command(sample_command)
        assert len(tool.get_all_commands()) == 1
        
        result = tool.delete_command("basic-scan")
        assert result is True
        assert len(tool.get_all_commands()) == 0
    
    def test_delete_nonexistent_command(self, tool):
        """Test deleting non-existent command returns False"""
        result = tool.delete_command("nonexistent")
        assert result is False
    
    def test_search_commands_by_query(self, tool):
        """Test searching commands by query"""
        cmd1 = Command(
            id="scan-1",
            name="Basic Scan",
            command="nmap {target}",
            explanation="Basic network scan"
        )
        cmd2 = Command(
            id="scan-2",
            name="Version Scan",
            command="nmap -sV {target}",
            explanation="Service version detection"
        )
        
        tool.add_command(cmd1)
        tool.add_command(cmd2)
        
        results = tool.search_commands(query="version")
        assert len(results) == 1
        assert results[0].id == "scan-2"
    
    def test_search_commands_by_tags(self, tool):
        """Test searching commands by tags"""
        cmd1 = Command(
            id="scan-1",
            name="Scan 1",
            command="test",
            explanation="Test",
            tags=["basic", "fast"]
        )
        cmd2 = Command(
            id="scan-2",
            name="Scan 2",
            command="test",
            explanation="Test",
            tags=["advanced", "slow"]
        )
        
        tool.add_command(cmd1)
        tool.add_command(cmd2)
        
        results = tool.search_commands(tags=["basic"])
        assert len(results) == 1
        assert results[0].id == "scan-1"
    
    def test_generate_command(self, tool, sample_parameter):
        """Test generating a command with parameters"""
        cmd = Command(
            id="test-cmd",
            name="Test",
            command="nmap {target}",
            explanation="Test",
            parameters=[sample_parameter]
        )
        
        tool.add_command(cmd)
        
        generated = tool.generate_command("test-cmd", {"target": "192.168.1.1"})
        assert generated == "nmap 192.168.1.1"
    
    def test_generate_nonexistent_command(self, tool):
        """Test generating non-existent command raises error"""
        with pytest.raises(ValueError, match="Command nonexistent not found"):
            tool.generate_command("nonexistent", {})
    
    def test_execute_command_dry_run(self, tool, sample_parameter):
        """Test execute command in dry run mode"""
        cmd = Command(
            id="test-cmd",
            name="Test",
            command="nmap {target}",
            explanation="Test",
            parameters=[sample_parameter]
        )
        
        tool.add_command(cmd)
        
        result = tool.execute_command("test-cmd", {"target": "192.168.1.1"}, dry_run=True)
        
        assert result['command'] == "nmap 192.168.1.1"
        assert result['executed'] is False
        assert result['output'] is None
    
    def test_execute_command_not_implemented(self, tool, sample_parameter):
        """Test execute command without dry run raises NotImplementedError"""
        cmd = Command(
            id="test-cmd",
            name="Test",
            command="echo test",
            explanation="Test",
            parameters=[sample_parameter]
        )
        
        tool.add_command(cmd)
        
        with pytest.raises(NotImplementedError, match="Execution not yet implemented"):
            tool.execute_command("test-cmd", {"target": "test"}, dry_run=False)
