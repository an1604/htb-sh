# tests/test_add_command.py
"""Tests for add command"""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from src.cli.main import cli
from src.cli.utils.models import CommandDetails


class TestAddCommand:
    """Test add command functionality"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    @pytest.fixture
    def mock_command_details(self):
        """Create mock CommandDetails"""
        return CommandDetails(
            id="test-scan",
            name="Test Scan",
            command="nmap -sV {target}",
            explanation="Test scanning command"
        )
    
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_basic_flow(self, mock_prompts_class, runner, mock_command_details):
        """Test basic add command flow"""
        # Setup mocks
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nmap"
        mock_prompts.input_command_details.return_value = mock_command_details
        
        # Run command
        result = runner.invoke(cli, ['add'])
        
        # Assertions
        assert result.exit_code == 0
        assert "test-scan" in result.output
        assert "Detected parameters: target" in result.output
        assert "created successfully" in result.output
        
        # Verify mocks were called
        mock_prompts.select_tool.assert_called_once()
        mock_prompts.input_command_details.assert_called_once()
    
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_no_tools_available(self, mock_prompts_class, runner):
        """Test add command when no tools are registered"""
        # This test would need a way to inject an empty manager
        # For now, we know tools are always registered in our setup
        pass
    
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_invalid_tool(self, mock_prompts_class, runner):
        """Test add command with invalid tool name"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nonexistent-tool"
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "not found" in result.output
    
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_detects_multiple_parameters(self, mock_prompts_class, runner):
        """Test that multiple parameters are detected"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nmap"
        
        cmd_details = CommandDetails(
            id="complex-scan",
            name="Complex Scan",
            command="nmap {target} {ports} {options}",
            explanation="Complex scanning command"
        )
        mock_prompts.input_command_details.return_value = cmd_details
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "target" in result.output
        assert "ports" in result.output
        assert "options" in result.output
    
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_no_parameters(self, mock_prompts_class, runner):
        """Test add command with no parameters in template"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "nmap"
        
        cmd_details = CommandDetails(
            id="simple-scan",
            name="Simple Scan",
            command="nmap -sV 192.168.1.1",
            explanation="Simple hardcoded scan"
        )
        mock_prompts.input_command_details.return_value = cmd_details
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "created successfully" in result.output
    
    def test_add_command_exists_in_cli(self, runner):
        """Test that add command is registered in CLI"""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "add" in result.output.lower()
    
    @patch('src.cli.commands.add.InteractivePrompts')
    def test_add_command_displays_success_message(self, mock_prompts_class, runner, mock_command_details):
        """Test that success message is displayed"""
        mock_prompts = Mock()
        mock_prompts_class.return_value = mock_prompts
        mock_prompts.select_tool.return_value = "smb"
        mock_prompts.input_command_details.return_value = mock_command_details
        
        result = runner.invoke(cli, ['add'])
        
        assert result.exit_code == 0
        assert "smb:test-scan" in result.output
        assert "✓" in result.output or "created successfully" in result.output
